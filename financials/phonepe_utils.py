import uuid
from django.conf import settings
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env

def get_phonepe_client():
    config = settings.PHONEPE_CONFIG
    env = Env.SANDBOX if config['ENV'] == 'SANDBOX' else Env.PRODUCTION

    return StandardCheckoutClient.get_instance(
        client_id=config['CLIENT_ID'],
        client_secret=config['CLIENT_SECRET'],
        client_version=config['CLIENT_VERSION'],
        env=env
    )

def initiate_phonepe_payment(transaction_id, amount, user_id):
    """
    Initiates a payment request to PhonePe using the SDK.
    """
    config = settings.PHONEPE_CONFIG
    client = get_phonepe_client()

    unique_order_id = str(transaction_id)
    amount_in_paise = int(float(amount) * 100)

    request = StandardCheckoutPayRequest.build_request(
        merchant_order_id=unique_order_id,
        amount=amount_in_paise,
        redirect_url=config['CALLBACK_URL'],
        meta_info=MetaInfo()
    )

    response = client.pay(request)
    return response

def verify_callback_checksum(response_payload_base64, received_checksum):
    """
    Verifies the callback request using the SDK.
    It uses the SDK's validate_callback method.
    """
    client = get_phonepe_client()

    try:
        # Assuming we don't have Basic Auth enabled for callbacks in Sandbox, passing empty strings.
        # This method typically validates the X-VERIFY header (received_checksum) against the payload.
        response = client.validate_callback(
            username="",
            password="",
            callback_header_data=received_checksum,
            callback_response_data=response_payload_base64
        )
        return response.status
    except Exception as e:
        # Logging the error would be ideal here
        return False
