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





def generate_password_recovery_phrase(strength=256):
    m = Mnemonic('english')
    mywords = m.generate(strength)
    return "%s" % (mywords)


def get_passphrase_salt(salt=env('PASSPHRASE_SALT')):
    """
    Assumes `USER_ID_SALT` is a hex encoded value. Decodes the salt val,
    returning binary data represented by the hexadecimal string.
    :param: salt
    :return: bytes
    """
    return binascii.unhexlify(salt)


def passphrase_hash(passphrase):
    return binascii.hexlify(pbkdf2(passphrase,
                                   get_passphrase_salt(),
                                   int(env('PASSPHRASE_ITERATIONS')))).decode("ascii")

def pprl_sha512_bcrypt(passphrase, bcrypt_salt="", bcrypt_rounds=BCRYPT_ROUNDS, pepper=""):
    result ={}
    passphrase ="%s^%s" %(pepper, passphrase)
    result["pepper_and_value"] = passphrase
    hash = sha512(passphrase.encode('utf-8')).hexdigest()
    sha512_passphrase = str.encode(hash)
    # print("SHA2-512 hash=",sha512_passphrase.decode())
    result['sha2_512_hash'] = sha512_passphrase.decode()
    if bcrypt_salt:
        # result['bcrypt_salt']= bcrypt_salt
        print("dfdg")
        salt = bcrypt_salt.encode('utf-8')
    else:
        # print("No bcrypt salt supplied, so generating a new salt")
        salt = bcrypt.gensalt(rounds=bcrypt_rounds)
        # result['bcrypt_salt']= salt.decode()
    hash = bcrypt.hashpw(sha512_passphrase, salt)
    result["sha2_512_bcrypt_hash"] = hash.decode()
    print(len(hash.decode()))
    result["id"] = result["sha2_512_bcrypt_hash"].rsplit('$',1)[-1]

    return result

if __name__ == "__main__":

    # Parse CLI args
    parser = argparse.ArgumentParser(
        description="""A command line tool to generate various hashes""")
    parser.add_argument(
        '--pepper',
        dest='pepper',
        default='',
        action='store',
        help="""A value to prepend to the value to be hashed.""")
    
    parser.add_argument(
        '--crypt',
        dest='crypt',
        default='sha512-bcrypt',
        action='store',
        help="'pbkdf2', 'sha256', 'sha512', 'bcrypt', 'sha256-bcrypt' or 'scrypt'")
    
    parser.add_argument(
        '--input',
        dest='input',
        default='',
        action='store',
        help=" Input text to hash.  If not supplied, a mnumonic will be generated and hashed.")
    
    parser.add_argument(
        '--rounds',
        dest='rounds',
        default=13,
        action='store',
        help="Rounds of iterations for bcrypt salt.")

    parser.add_argument(
        '--bcryptsalt',
        dest='bcrypt_salt',
        default='',#'$2b$12$AfV2hHuYm935XO1ASNrC9u',
        action='store',
        help="BCrypt salt as decoded (ASCII). Should begin with algorithm and rounds (e.g. '$b2$12').")

    args = parser.parse_args()

    if args.input:
        passphrase = args.input
    else:
        passphrase = generate_password_recovery_phrase()

    if args.crypt=='pbkdf2':
        hash = passphrase_hash(passphrase)
        print(hash)
    if args.crypt=='sha256':
        hash = sha256(passphrase.encode('utf-8')).hexdigest()
        print(hash)
    if args.crypt=='sha512':
        hash = sha512(passphrase.encode('utf-8')).hexdigest()
        print(hash)


    if args.crypt=='bcrypt':
        #passphrase = (bytes((passphrase, 'utf-8')))
        passphrase = str.encode(passphrase)
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hash = bcrypt.hashpw(passphrase, salt)
        print(hash.decode())

    if args.crypt =="sha512-bcrypt":
        result = pprl_sha512_bcrypt(passphrase, bcrypt_salt=args.bcrypt_salt, bcrypt_rounds=int(args.rounds), pepper=args.pepper)
        print(json.dumps(result, indent=2))
        #print("With Origin ID=", result['pepper_and_passphrase'])
        #print("SHA2-512 hash=",result['sha2_512_hash'])
        #print("Bcrypt salt is", result["bcrypt_salt_type"])
        #print("Final Hashed Value", result["sha2_512_bcrypt_hash"])

    #if args.crypt=='scrypt':
    #    #passphrase = (bytes((passphrase, 'utf-8')))
    #    passphrase = str.encode(passphrase)
    #    salt = get_random_bytes(16)
    #    hash = scrypt(passphrase, salt, 16, N=2**14, r=8, p=1)
    #    print(hash.decode())