#!/usr/bin/env python
from mnemonic import Mnemonic
from django.utils.crypto import pbkdf2
from hashlib import sha256, sha512
import binascii
import json
from getenv import env
import argparse
import bcrypt
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

BCRYPT_ROUNDS =int(env('BCRYPT_ROUNDS',13))
BCRYPT_SALT = b'$2b$13$GamJ8w9ryKQ2cSmwQ0f.Pe'
SHA2_512_SALT = env('SHA2_512_SALT','')




def bcrypt_salt(workfactor=BCRYPT_ROUNDS):
    salt = bcrypt.gensalt(rounds=workfactor).decode()
    result ={"salt": salt,
             "id":  salt.rsplit('$',1)[-1]}
    return result

if __name__ == "__main__":

    # Parse CLI args
    parser = argparse.ArgumentParser(
        description="""A command line tool to generate a bcrypt salt.""")


    parser.add_argument(
        '--workfactor',
        dest='workfactor',
        default=13,
        action='store',
        help="BCrypt workfactor. Default is 13.")

    args = parser.parse_args()
    try:
        wf = int(args.workfactor)
        if wf>3:
            response = bcrypt_salt(workfactor=wf)
            print(response['salt'])
        else:
            print("You must supply an integer between 4 and 31 for Bcrypt rounds/workfactor.")

    except ValueError:
        print("You must supply an integer between 4 and 31 for Bcrypt rounds/workfactor.")

    