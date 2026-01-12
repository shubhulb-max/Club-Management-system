from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env
 
client_id = "M23VC340MZKCY_2512111424"
client_secret = "NDExY2I3YWEtNjc1Ni00ZmFiLTliZWEtYTZiNDNjNjRmZDdk"
client_version = 1 # Insert your client version here
env = Env.SANDBOX  # Change to Env.PRODUCTION when you go live
should_publish_events = False
 
client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                              client_secret=client_secret,
                                                              client_version=client_version,
                                                              env=env,
                                                              should_publish_events=should_publish_events)
 
unique_order_id = str(uuid4())
ui_redirect_url = "https://www.merchant.com/redirect"
amount = 100
meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3") 
standard_pay_request = StandardCheckoutPayRequest.build_request(merchant_order_id=unique_order_id,
                                                                amount=amount,
                                                                redirect_url=ui_redirect_url,
                                                                meta_info=meta_info,
    orderid = str(uuid.uuid4())
    enabled_modes_data = [
        UpiIntentPaymentModeConstraint(PgV2InstrumentType.UPI_INTENT),
        NetBankingPaymentModeConstraint(PgV2InstrumentType.NET_BANKING),
        CardPaymentModeConstraint(card_types=[CardType.DEBIT_CARD, CardType.CREDIT_CARD]),
    ]
    meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")
    payment_mode_config = PaymentModeConfig(enabled_payment_modes=enabled_modes_data)
    pay_page_build = StandardCheckoutPayRequest.build_request(
        merchant_order_id=orderid,
        amount=100,
        meta_info=meta_info,
        payment_mode_config=payment_mode_config,
        redirect_url="https://www.merchant.com/redirect",
        message="Message that will be shown for UPI collect transaction",
        expire_after=3600,
        disable_payment_retry=True
    )
standard_pay_response = client.pay(standard_pay_request)
checkout_page_url = standard_pay_response.redirect_url