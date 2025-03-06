import os
import json
from osdk_connection_read_write_sdk import FoundryClient
from foundry_sdk_runtime.auth import ConfidentialClientAuth
import argparse

ONECDP_MDN_OID_CLIENT_SECRET = os.getenv("ONECDP_MDN_OID_CLIENT_SECRET", '<fill in CLIENT_SECRET>')
ONECDP_MDN_OID_CLIENT_ID = os.getenv("ONECDP_MDN_OID_CLIENT_ID", '<fill in CLIENT_ID>')



def get_by_oid_and_value(oid, value): 
    # TODO -implement caching
    auth = ConfidentialClientAuth(
    client_id=ONECDP_MDN_OID_CLIENT_ID,
    client_secret=ONECDP_MDN_OID_CLIENT_SECRET,
    hostname="https://1cdp.cdc.gov",
    should_refresh=True,)
    auth.sign_in_as_service_user()
    client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")
    pk = oid+":"+value
    result = client.ontology.objects.MdnCodesetsByOid.get(pk)
    resultdict = result._asdict()
    return resultdict

def validate_codeset_value(object_dict, message_type, value):
    results ={}
    if message_type == "hl7v2" or message_type == "csv":
        code = object_dict.get("code", "")
        oid = object_dict.get("oid", "")
        if code:
            msg = "Code %s is valid for %s in a %s message." % (value, oid, message_type)
            results ={"status":"pass", "msg":msg}
        else:
                msg = "Code %s is invalid for %s in a %s message" % (value, oid, message_type)
                results ={"status":"fail", "msg":msg}
    return results

 
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description='Check value against an OID lookup table')
 
    parser.add_argument(
        dest='oid',
        action='store',
        help="OID to lookup.")
 
    parser.add_argument(
        dest='message_type',
        action='store',
        default='hl7v2',
        help="Must be 'csv' or 'hl7v2'.")
 
    parser.add_argument(
        dest='value',
        action='store',
        help="The coded value to check.")
 
    args = parser.parse_args()
    result = validate_codeset_value(args.oid, args.message_type, args.value)
    print(json.dumps(result, indent=4, default=str))