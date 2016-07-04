# -*- coding: utf-8 -*-
"""
    Simple Image Hash Steganoghraphy
    Protocol 1
    
    Module of SIHS
    
    Created in 2016.07.02  01:49 
    Autor: 'pavel'
"""
SIHS = '1'
SIHS1_VERSION = '{0}.0.6'.format(SIHS)


from Core import make_db
from optparse import OptionParser
import sys
import datetime
from time import sleep
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(u'config')

# Name of popular russian IT-forum: https://habrahabr.ru/
TEST_MESSAGE = u'Хaбр'

# you can use another hash. See sihs_hash docstring
import hashlib
from Crypto.Cipher.XOR import XORCipher

from Core import generate_message_chain
from Core import read_massage_chain
from Core import IMAGE_HASH_FOLDER

__author__ = 'PavelMSTU'

ENCODING = config.get('SIHS1', 'ENCODING')

SALT = u'В недрах тундры выдры в гетрах тырят в ведра ядра кедра.'\
       +u'ЫВлапУоаы4dвы'


def make_key_by_passwd(passwd):
    def __hash(a):
        d = hashlib.sha512()
        b = a.encode(ENCODING)
        d.update(b)
        return d.hexdigest()

    key = __hash(__hash(passwd) + SALT)
    return key[:32]


def generate(
    message,
    passwd,
    image_folder_out=IMAGE_HASH_FOLDER,
):
    """
    Function for generate message
    by hash-steganography

    :param message: message of unicode to generate hash-stego
    :param passwd: password for key generating in cryptography
    :param image_folder_out: folder, where will be make folder
    of hash-stego images
    :return:
    folder_out path
    """
    m_str = message.encode(ENCODING)

    key = make_key_by_passwd(passwd)
    cipher = XORCipher(key)
    crypt_message = cipher.encrypt(m_str)

    message_bytes = [ord(ch) for ch in crypt_message]
    print u"message_bytes={0}".format(message_bytes)

    try:
        folder_out = generate_message_chain(
            message_bytes,
            image_folder_out=image_folder_out,
            folder_message=message,
        )
    except Exception, error:
        return None, error
    return folder_out, None


def extract(
    folder_in,
    passwd,
):
    """
    Function for extract message for hash-steganography

    :param folder_in: folder of images
    :param passwd: password for cryptography
    :return:
    message
    or None, if passwd is wrong
    """
    message_bytes = read_massage_chain(folder_in)

    crypt_message = ''.join([chr(ch) for ch in message_bytes])

    key = make_key_by_passwd(passwd)
    cipher = XORCipher(key)
    str_message = cipher.encrypt(crypt_message)

    try:
        message = str_message.decode(ENCODING)
    except Exception, error:
        message = None
    return message


def __test2():

    passwd = u'PUTIN'
    message1 = TEST_MESSAGE

    folder_out, _ = generate(message=message1, passwd=passwd)
    message2 = extract(folder_out, passwd=passwd)

    print u"message1={0} message2={1}"\
        .format(message1, message2)
    if message1 != message2:
        error = u'{0}=message1 != message2={1}'\
            .format(message1, message2)
        raise RuntimeError(error)
    print u"All is good!"


def main(options):

    if options.need_make_db:
        if options.verbose:
            print u"Make DB:"
        # make_db(verbose=options.verbose)
        make_db()

    if options.mode_generate and options.mode_extract:
        print u"ERROR: You cant use both -g -e."
        return -100
    elif not options.mode_generate and not options.mode_extract\
            and not options.need_make_db:
        print u"Simple Image Hash-steganography, protocol №1"
        print u"Use '-g', '-e' or '-b' options. See --help"
        return 0
    elif not options.mode_generate and not options.mode_extract:
        print u"BD is build"
        return 0

    if options.password is None:
        print u"ERROR: password is None. Use '-p STRING' option"
        return -1
    options.password = options.password.decode(u'utf-8')

    blind_password = u''.join([u'*' for _ in options.password])

    if options.mode_generate:
        if options.message is None:
            print u"ERROR: message is None. Use '-m STRING' option"
            return -2
        options.message = options.message.decode(u'utf-8')

        if options.verbose:
            print u'Generate message={0} and password={1}'\
                .format(options.message, blind_password)
        folder_out, error = generate(message=options.message, passwd=options.password)

        if error:
            print u"ERROR:", error
            return -4

        if options.verbose:
            print u"All is Success! See folder '{0}'".format(folder_out)
        else:
            print folder_out
        return 0

    if options.mode_extract:
        if options.folder is None:
            print u"ERROR: message is None. Use '-m STRING' option"
            return -3
        options.folder = options.folder.decode(u'utf-8')

        if options.verbose:
            print u"Extract from '{0}' folder by password={1} "\
                .format(options.folder, blind_password)

        message = extract(options.folder, options.password)

        if options.verbose:
            print u"All is Success (if password is correct)!\nmessage='{0}'".format(message)
        else:
            print message
        return 0


def console():
    from Core import DB_PATH, IMAGE_STORE, DB_ADD_FORMAT

    usage = u"""usage: %prog [options]
SIHS1 -- Simple Image Hash-Steganograhpy, protocol №1
version = {VERSION}

author: PavelMSTU <PavelMSTU@stego.su>
source in GitHub: https://github.com/PavelMSTU/SIHS
see also config file for configure this Python script
""".format(VERSION=SIHS1_VERSION)

    parser = OptionParser(usage=usage)
    parser.add_option(
        u"-b", u"--makedb",
        dest=u"need_make_db",
        action=u"store_true",
        help=u"Make base in {0}, using {1} files in {2}"
            .format(DB_PATH, DB_ADD_FORMAT, IMAGE_STORE),
        default=False,
    )
    parser.add_option(
        u"-q", u"--quiet",
        dest=u"verbose",
        action=u"store_false",
        help=u"be quiet (return ONLY result and errors)",
        default=True,
    )

    parser.add_option(
        u"-m", u"--message",
        dest=u"message",
        help=u"Message to generate (see -g) by SIHS1",
        default=None,
        metavar=u"STRING",
    )

    parser.add_option(
        u"-p", u"--password",
        dest=u"password",
        help=u"Password for generate by SIHS1 or extract by SIHS1",
        default=None,
        metavar=u"STRING",
    )

    parser.add_option(
        u"-f", u"--folder",
        dest=u"folder",
        help=u"Folder for extract (see -e) by SIHS1",
        default=None,
        metavar=u"PATH",
    )

    parser.add_option(
        u"-g", u"--generate",
        dest=u"mode_generate",
        action=u"store_true",
        default=False,
        help=u"Mode for generate message (see -m)",
    )
    parser.add_option(
        u"-e", u"--extract",
        dest=u"mode_extract",
        action=u"store_true",
        default=False,
        help=u"Mode for extract message from folder (see -f). Return MESSAGE, if nothing errors occur",
    )

    (options, args) = parser.parse_args()
    main(options)

if __name__ == "__main__":
    # __test2()
    console()
