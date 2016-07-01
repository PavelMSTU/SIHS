# -*- coding: utf-8 -*-
"""
    Module of SIHS
    
    Created in 2016.06.29  19:52 
    Autor: 'PavelMSTU'

    I am SOMBE!
"""

import os
import sys
import datetime
import sqlite3
import ConfigParser
from time import sleep
from functools import partial

# you can use another hash. See sihs_hash docstring
import hashlib

__author__ = u'PavelMSTU'

TEST_MESSAGE = u'Хабрахабр'

# Out folder. Выходная папка
IMAGE_HASH_FOLDER = u'image_hash_stego'

# Input folder. Входная папка
IMAGE_STORE = u'image_store'

DB_PATH = os.path.join(IMAGE_STORE, u'IMAGEDB.sqlite.db')


def sihs_hash(file_path, count_bytes=1):
    """
    Some hash func.
    You can CHANGE it, if you want.

    For example, you can use IMAGE-HASH,
        not cryptography hash.
    If you do it, you can build ROBUST
    steganography system.

    :param file_path:
    path of some some bytes
    :param count_bytes: count of bytes
    :return:
    return hash
    """

    d = hashlib.md5()
    with open(file_path, 'rb') as file_b:
        for buf in iter(partial(file_b.read, 128), b''):
            d.update(buf)

    a = d.hexdigest()
    val = a[0:count_bytes*2]
    return int(val, 16)


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


def make_db(
    image_store_folder=IMAGE_STORE,
    db_path=DB_PATH,
):
    """
    Function for build DB

    ATTANTION:
        when you added some image files to IMAGE_STORE
        you must call this function

    :param image_store_folder: folder, where images is store.
    :param db_path: path of DB
    :return:
    return count of images in DB
    """

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(IMAGE_STORE, u'README'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        u"""
        CREATE TABLE IMAGES
                -- Table of image path and its HASH value. Using for Hash-steganography
            (
                id INTEGER PRIMARY KEY,
                img_path TEXT, -- Path of image regarding IMAGE_STORE={0} folder
                img_hash_1b INTEGER -- ONE byte of hash
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """.format(image_store_folder)
    )
    conn.commit()

    count_insert = 0
    for file_ in os.listdir(IMAGE_STORE):
        file_path = os.path.join(IMAGE_STORE, file_)

        if file_path.split('.')[-1] not in config.get('main', 'format'):
            # this file is not correct format
            continue

        # read all bytes of some file
        hash_ = sihs_hash(file_path)
        cursor.execute(
            u"""
            INSERT INTO IMAGES
                (img_path, img_hash_1b)
                VALUES

                ('{0}', {1})
            """.format(file_path, hash_)
        )
        conn.commit()
        # TODO check the errors of cursor.execute!
        count_insert += 1
        print u"{0}: Add '{1}' image to DB".format(count_insert, file_path)

    conn.close()
    return count_insert


if __name__ == u"__main__":
    print u"TEST Core " + unicode(datetime.datetime.now())
    sleep(3)

    make_db()
    # __test1()


