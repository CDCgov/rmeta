import os
from 1cdp_facade_rd_poc_sdk import FoundryClient
from foundry_sdk_runtime.auth import UserTokenAuth


auth = UserTokenAuth(hostname="https://dcipher.cdc.gov", token=os.environ["FOUNDRY_TOKEN"])


client = FoundryClient(auth=auth, hostname="https://dcipher.cdc.gov")


ChunkObject = client.ontology.objects.Chunk

print(ChunkObject.take(1))