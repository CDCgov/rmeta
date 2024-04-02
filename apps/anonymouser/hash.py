#!/usr/bin/env python
from hashlib import sha512
import binascii
import json
import argparse
import bcrypt
from getenv import env

BCRYPT_ROUNDS =int(env('BCRYPT_ROUNDS',13))

def hash(passphrase, bcrypt_salt, prefix=""):
    result ={}
    if prefix:
        passphrase ="%s^%s" %(prefix, passphrase)
    hash = sha512(passphrase.encode('utf-8')).hexdigest()
    sha512_passphrase = str.encode(hash)
    salt = bcrypt_salt.encode('utf-8')
    hashval = bcrypt.hashpw(sha512_passphrase, salt)
    result["value"] = passphrase
    result["hash"] = hashval.decode()
    result["id"] = result["hash"].rsplit(bcrypt_salt,1)[-1]
    result["algo"] = result["hash"].rsplit('$',1)[0]
    del result["hash"]
    return result

if __name__ == "__main__":

    # Parse CLI args
    parser = argparse.ArgumentParser(
        description="""A command line tool to generate a hash""")
    
    
    parser.add_argument(
        'input',
        default='',
        action='store',
        help=" Input text to hash.")
    
    parser.add_argument(
        'salt',
        default='',#'$2b$12$AfV2hHuYm935XO1ASNrC9u',
        action='store',
        help="BCrypt salt as decoded (ASCII). Should begin with algorithm and rounds (e.g. '$b2$12').")

    parser.add_argument(
        '--prefix',
        dest='prefix',
        default='',
        action='store',
        help="""A prefix to the value to be hashed by SHA2-512.""")

    args = parser.parse_args()
    if not args.salt:
        args.salt= bcrypt.gensalt(rounds=BCRYPT_ROUNDS).decode()
    result = hash(args.input, args.salt, prefix=args.prefix)
    print(json.dumps(result, indent=2))
