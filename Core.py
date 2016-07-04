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
import random
import sqlite3
import shutil
import ConfigParser
from time import sleep
from functools import partial

# you can use another hash. See sihs_hash docstring
import hashlib

__author__ = u'PavelMSTU'

config = ConfigParser.RawConfigParser()
config.read(u'config')

# Out folder. Выходная папка
IMAGE_HASH_FOLDER = config.get(u'image_store', u'OUT_FOLDER').decode(u'utf-8')

# Input folder. Входная папка
IMAGE_STORE = config.get(u'image_store', u'IN_FOLDER').decode(u'utf-8')

DB_PATH = config.get(u'image_store', u'DB_PATH').decode(u'utf-8')

DB_ADD_FORMAT = config.get(u'image_store', u'DB_ADD_FORMAT').decode(u'utf-8')


def make_folder_message(
    message,
):
    """
    Make name of out folder by message.

    :param message: list of bytes
    :return:
    unicode name of folder
    """
    def __int_to_hex(m):
        if m < 10:
            return u"0" + hex(m)[2:]
        else:
            return hex(m)[2:]

    return u'0x' + u'-'.join([u'{0}'.format(__int_to_hex(m)) for m in message])


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
    image_folder_in=IMAGE_STORE,
    image_folder_out=IMAGE_HASH_FOLDER,
    db_path=DB_PATH,
    folder_message=None,
):
    """
    This function,
    get random images from image_folder,
    push it to image_folder_out,
    generating Hash Steganography message message_bytes

    :param message_bytes: message for input (list of bytes)
    :param image_folder_in: folder, where exists some images
    :param image_folder_out: folder for out stegocontainer
    (chain of images)
    :param db_path: path od SQLite DB
    (This DB must be build by make_db)
    :return:
    path of message folder
    """

    def __get_random(all_list):
        j = random.randint(0, len(all_list)-1)
        return all_list[j]

    def one_name(file_, i):
        name = u'{0}'.format(i)
        if len(name) > 3:
            raise NotImplementedError(u"You can't send more then 999 stego bytes!")
        if len(name) == 1:
            name = u'00' + name
        elif len(name) == 2:
            mane = u'0' + name

        name += u'.' + file_.split(u'.')[-1]
        return name

    if folder_message is None:
        folder_message = make_folder_message(message_bytes)
    folder_out = os.path.join(image_folder_out, folder_message)

    if os.path.exists(folder_out):
        print u"WARNING. Folder {0} is also exists. Delete it with all files".format(folder_out)
        shutil.rmtree(folder_out)
    os.mkdir(folder_out)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    delete_img_paths = list()
    delete_id_list = list()
    for i, one_message_byte in enumerate(message_bytes):
        cursor.execute(
            u"""
            SELECT id, img_path
              from IMAGES
                  where img_hash_1b={0}
              LIMIT 1000
            """.format(one_message_byte)
        )
        all_list = cursor.fetchall()
        if not all_list:
            # TODO We can use Error Correction Codes BEFORE steganography and make some errors
            # if this event occurs!... This will be a good feature!
            error = u'There are nothing images with hash={0} in DB! Please download MORE images!' \
                .format(one_message_byte)
            raise EnvironmentError(error)

        # TODO move random logic to SQLite
        one_record = __get_random(all_list)

        id_ = one_record[0]
        file_ = one_record[1]

        file_in_path = os.path.join(image_folder_in, file_)
        file_out_path = os.path.join(folder_out, one_name(file_, i))
        shutil.copy(file_in_path, file_out_path)

        delete_img_paths.append(file_in_path)
        delete_id_list.append(id_)

    # delete used images
    for id_ in delete_id_list:
        cursor.execute(
            u"""
            DELETE from IMAGES
              where id={0}
            """.format(id_)
        )
        conn.commit()
    for file_path in delete_img_paths:
        os.remove(file_path)

    conn.close()
    return folder_out


def read_massage_chain(
    image_folder_in,
):
    """
    This function read image chain in image_folder_out
    and return message_bytes
    :param image_folder_in: folger of message chain
    :return:
    list of bytes
    """
    file_list = os.listdir(image_folder_in)
    file_list.sort()

    message = list()
    for file_ in file_list:
        file_path = os.path.join(image_folder_in, file_)

        m = sihs_hash(file_path)
        message.append(m)

    return message


def __test1():
    message = [133, 18]

    print u"generate_message_chain(message={0}):".format(message),
    message_folder = generate_message_chain(message)
    print u"DONE ({0})".format(datetime.datetime.now())

    print u"read_massege_chain(message_folder='{0}'):".format(message_folder),
    message2 = read_massage_chain(message_folder)
    print u"DONE ({0})".format(datetime.datetime.now())

    print u"Check message1={0} and message2={1}".format(message, message2)
    for m1, m2 in zip(message, message2):
        if m1 != m2:
            raise RuntimeError(u'Core is not work!')
    print u"all is correct! Good!"
    return True


def make_db(
    image_store_folder=IMAGE_STORE,
    db_path=DB_PATH,
):
    """
    Function for build DB

    ATTENTION:
        when you added some image files to IMAGE_STORE
        you must call this function

    :param image_store_folder: folder, where images is store.
    :param db_path: path of DB
    :return:
    return count of images in DB
    """

    # config = ConfigParser.RawConfigParser()
    # config.read(os.path.join(IMAGE_STORE, u'README'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        u"""
        DROP TABLE IF EXISTS IMAGES
        """
    )

    cursor.execute(
        u"""
        CREATE TABLE IMAGES
                -- Table of image path and its HASH value. Using for Hash-steganography
            (
                id INTEGER PRIMARY KEY ,
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

        if file_path.split('.')[-1] not in DB_ADD_FORMAT:
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
            """.format(file_, hash_)
        )
        conn.commit()
        # TODO check the errors of cursor.execute!
        count_insert += 1
        print u"{0}: Add '{1}' image to DB".format(count_insert, file_)

    conn.close()
    return count_insert


if __name__ == u"__main__":
    print u"This is Core. Use $>python SIHS1.py --help"



