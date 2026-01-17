import uuid
from django.conf import settings
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env

def get_phonepe_client():
    """
    Utility to get the PhonePe client instance using settings.
    """
    config = settings.PHONEPE_CONFIG
    env = Env.SANDBOX if config['ENV'] == 'SANDBOX' else Env.PRODUCTION

    # If you need to pass 'should_publish_events', add it here. Default is usually False.
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

def check_payment_status(merchant_order_id):
    """
    Checks the server-to-server status of a specific order ID using the PhonePe SDK.
    Returns the full response object containing state (response.state).
    """
    client = get_phonepe_client()

    try:
        # Check status without additional details (details=False)
        response = client.get_order_status(merchant_order_id, details=False)
        return response
    except Exception as e:
        # In a real app, log this error
        print(f"Error checking PhonePe status: {e}")
        return None