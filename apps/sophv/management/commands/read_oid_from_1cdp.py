import os
import json
from osdk_connection_read_write_sdk import FoundryClient
from foundry_sdk_runtime.auth import ConfidentialClientAuth
from osdk_connection_read_write_sdk.ontology.objects import VocabularyOption2ValueSetAllVersions
from foundry_sdk_runtime.errors.palantir_rpc_exception import PalantirRPCException
ONECDP_MDN_OID_CLIENT_SECRET = os.getenv("ONECDP_MDN_OID_CLIENT_SECRET", '<fill in CLIENT_SECRET>')
ONECDP_MDN_OID_CLIENT_ID = os.getenv("ONECDP_MDN_OID_CLIENT_ID", '<fill in CLIENT_ID>')




def get_by_oid_and_value(oid, value): 
    # TODO -implement caching
    auth = ConfidentialClientAuth(client_id=ONECDP_MDN_OID_CLIENT_ID,
    client_secret=ONECDP_MDN_OID_CLIENT_SECRET,
    hostname="https://1cdp.cdc.gov",
    should_refresh=True,)
    auth.sign_in_as_service_user()
    client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")
    pk = oid+":"+value
    try:

        #result = client.ontology.objects.MdnCodesetsByOid.get(pk)
        VocabularyOption2ValueSetLatestVersionObjectSet = \
            client.ontology.objects.VocabularyOption2ValueSetAllVersions.where(VocabularyOption2ValueSetAllVersions.value_set_code.starts_with(["foo"]))
        print(dir(VocabularyOption2ValueSetLatestVersionObjectSet))
        resultdict = {} #result._asdict()
    except PalantirRPCException as e:
        resultdict= {"status":"fail", "msg":f"Code {value} is invalid for {oid}", "errorName":e.name}
    print(resultdict)
    return resultdict

def validate_codeset_value(object_dict, message_type, value):
    results ={}

    if object_dict.get("status", "") == "fail":
        return object_dict
    if message_type == "hl7v2" or message_type == "csv":
        code = object_dict.get("code", "")
        oid = object_dict.get("oid", "")
        if code:
            msg = "Code %s is valid value for %s in a %s message." % (value, oid, message_type)
            results ={"status":"pass", "msg":msg}
        else:
            msg = "Code %s is invalid for %s in a %s message" % (value, oid, message_type)
            results ={"status":"fail", "msg":msg}
    return results

 
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description='Check value against an Valueset in 1CDP lookup table by OID')
 
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


    #result = validate_codeset_value(args.oid, args.message_type, args.value)
    
    result = get_by_oid_and_value(args.oid, args.value)
    result = validate_codeset_value(result, args.message_type, args.value)
    print(json.dumps(result, indent=4, default=str))