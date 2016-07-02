# -*- coding: utf-8 -*-
"""
    Simple Image Hash Steganoghraphy
    Protocol 1
    
    Module of SIHS
    
    Created in 2016.07.02  01:49 
    Autor: 'pavel'
"""

import sys
import datetime
from time import sleep

# Name of popular russian IT-forum: https://habrahabr.ru/
TEST_MESSAGE = u'Хaбр'

# you can use another hash. See sihs_hash docstring
import hashlib
from Crypto.Cipher.XOR import XORCipher

from Core import generate_message_chain
from Core import read_massage_chain
from Core import IMAGE_HASH_FOLDER

__author__ = 'PavelMSTU'

ENCODING = u'koi8-r'


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

    cipher = XORCipher(passwd)
    crypt_message = cipher.encrypt(m_str)

    message_bytes = [ord(ch) for ch in crypt_message]
    print u"message_bytes={0}".format(message_bytes)

    folder_out = generate_message_chain(
        message_bytes,
        image_folder_out=image_folder_out,
        folder_message=message,
    )
    return folder_out


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

    cipher = XORCipher(passwd)
    str_message = cipher.encrypt(crypt_message)

    try:
        message = str_message.decode(ENCODING)
    except Exception, error:
        message = None
    return message


def __test2():

    passwd = u'PUTIN'
    message1 = TEST_MESSAGE

    folder_out = generate(message=message1, passwd=passwd)
    message2 = extract(folder_out, passwd=passwd)

    print u"message1={0} message2={1}"\
        .format(message1, message2)
    if message1 != message2:
        error = u'{0}=message1 != message2={1}'\
            .format(message1, message2)
        raise RuntimeError(error)
    print u"All is good!"


if __name__ == "__main__":
    __test2()