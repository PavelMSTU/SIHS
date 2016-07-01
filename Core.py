# -*- coding: utf-8 -*-
"""
    Module of SIHS
    
    Created in 2016.06.29  19:52 
    Autor: 'PavelMSTU'

    I am SOMBE!
"""

import sys
import datetime
from time import sleep

__author__ = u'PavelMSTU'

TEST_MESSAGE = u'Хабрахабр'

# Out folder. Выходная папка
IMAGE_HASH_FOLDER = u'image_hash_stego'

# Input folder. Входная папка
IMAGE_STORE = u'image_store'


def generate_message_chain(
    message_bytes,
    image_folder=IMAGE_STORE,
    image_folder_out=IMAGE_HASH_FOLDER,
):
    """
    This function,
    get random images from image_folder,
    push it to image_folder_out,
    generating Hash Steganography message message_bytes

    :param message_bytes: message for input (list of bytes)
    :param image_folder: folder, where exists some images
    :param image_folder_out: folder for out stegocontainer
    (chain of images)
    :return:
    path of message folder
    """

    raise NotImplementedError(u'This function is not implement')


def read_massege_chain(
    image_folder_in,
):
    """
    This function read image chain in image_folder_out
    and return message_bytes
    :param image_folder_in: folger of message chain
    :return:
    list of bytes
    """

    raise NotImplementedError(u'This function is not implement')


def __test1():
    message = [0x02, 0x00]

    message_folder = generate_message_chain(message)
    message2 = read_massege_chain(message_folder)

    for m1, m2 in zip(message, message2):
        if m1 != m2:
            raise RuntimeError(u'Core is not work!')
    return True

if __name__ == u"__main__":
    print u"TEST Core " + unicode(datetime.datetime.now())
    sleep(3)

    __test1()


