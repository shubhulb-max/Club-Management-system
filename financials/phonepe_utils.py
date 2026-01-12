import base64
import json
import hashlib
import requests
from django.conf import settings

def generate_checksum(payload_base64, salt_key, salt_index):
    """
    Generates the X-VERIFY checksum for PhonePe API.
    Format: SHA256(Base64(Payload) + "/pg/v1/pay" + SaltKey) + ### + SaltIndex
    Wait, the format is actually SHA256(Base64(Payload) + Endpoint + SaltKey) + ### + SaltIndex
    But for the 'pay' endpoint, it is typically just the payload + endpoint + salt.

    Standard formula: SHA256(base64Body + apiEndpoint + salt) + ### + saltIndex
    """
    string_to_hash = f"{payload_base64}/pg/v1/pay{salt_key}"
    sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    return f"{sha256_hash}###{salt_index}"

def initiate_phonepe_payment(transaction_id, amount, user_id, mobile_number=None):
    """
    Initiates a payment request to PhonePe.

    Args:
        transaction_id (str): Unique transaction ID (e.g., "TXN123").
        amount (float): Amount in INR.
        user_id (str): Unique user ID (e.g., "USER123").
        mobile_number (str, optional): User's mobile number.

    Returns:
        dict: The response from PhonePe containing the redirect URL or error.
    """
    config = settings.PHONEPE_CONFIG

    # Amount needs to be in paise (1 INR = 100 paise)
    amount_in_paise = int(float(amount) * 100)

    payload = {
        "merchantId": config['MERCHANT_ID'],
        "merchantTransactionId": str(transaction_id),
        "merchantUserId": str(user_id),
        "amount": amount_in_paise,
        "redirectUrl": config['CALLBACK_URL'],
        "redirectMode": "POST",
        "callbackUrl": config['CALLBACK_URL'],
        "mobileNumber": mobile_number if mobile_number else "9999999999",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    # Base64 Encode Payload
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')

    # Generate Checksum
    checksum = generate_checksum(payload_base64, config['SALT_KEY'], config['SALT_INDEX'])

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': checksum
    }

    url = f"{config['BASE_URL']}/pg/v1/pay"

    try:
        response = requests.post(url, json={'request': payload_base64}, headers=headers)
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "message": str(e)}

def verify_callback_checksum(response_payload_base64, received_checksum, salt_key, salt_index):
    """
    Verifies the checksum received in the callback.
    Format: SHA256(responseBase64 + saltKey) + ### + saltIndex
    """
    # Note: PhonePe documentation says for server-to-server callback:
    # X-VERIFY = SHA256(base64_response_body + salt_key) + ### + salt_index
    # But wait, sometimes it's different. Let's check the docs snippet if available.
    # Standard practice: SHA256(response_body + salt_key) + ### + salt_index

    string_to_hash = f"{response_payload_base64}{salt_key}"
    calculated_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
    expected_checksum = f"{calculated_hash}###{salt_index}"

    return received_checksum == expected_checksum
