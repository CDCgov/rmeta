from cdc_submission_spec_api_sdk import FoundryClient
from foundry_sdk_runtime.auth import ConfidentialClientAuth
import os

ONECDP_SUBMISSION_API_CLIENT_ID =    os.getenv("ONECDP_SUBMISSION_API_CLIENT_ID", '<fill in CLIENT_ID>')
ONECDP_SUBMISSION_API_CLIENT_SECRET= os.getenv("ONECDP_SUBMISSION_API_CLIENT_SECRET", '<fill in CLIENT_SECRET>')

auth = ConfidentialClientAuth(

    client_id=ONECDP_SUBMISSION_API_CLIENT_ID,
    client_secret=ONECDP_SUBMISSION_API_CLIENT_SECRET,
    hostname="https://1cdp.cdc.gov",
    should_refresh=True,
)

auth.sign_in_as_service_user()

client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")

def sign_in():
    
    auth = ConfidentialClientAuth(
        client_id=ONECDP_SUBMISSION_API_CLIENT_ID,
        client_secret=ONECDP_SUBMISSION_API_CLIENT_SECRET,
        hostname="https://1cdp.cdc.gov",
        should_refresh=True)
    auth.sign_in_as_service_user()
    client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")
    return client





