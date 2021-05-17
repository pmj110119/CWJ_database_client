# -*- coding: utf-8 -*-
 

import re
 
 
def check_tinyint(column, if_none=True, if_sign=False):
    """
    Check if it is valid of data to be written to satisfy TINYINT(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :param if_sign: whether integer values signed or not.
    :return: Boolean.
    """
    if if_none:
        if re.match("^$", column):
            return True
        else:
            pass
    elif not if_none:
        if re.match("^$", column):
            return False
        else:
            pass
    try:
        int(column)
    except ValueError:
        return False
    min_check = None
    max_check = None
    if if_sign:
        min_check = -128
        max_check = 127
    elif not if_sign:
        min_check = 0
        max_check = 255
    int_column = int(column)
    if max_check >= int_column >= min_check:
        return True
    else:
        return False
 
 
def check_smallint(column, if_none=True, if_sign=False):
    """
    Check if it is valid of data to be written to satisfy SMALLINT(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :param if_sign: whether integer values signed or not.
    :return: Boolean.
    """
    if if_none:
        if re.match("^$", column):
            return True
        else:
            pass
    elif not if_none:
        if re.match("^$", column):
            return False
        else:
            pass
    try:
        int(column)
    except ValueError:
        return False
    min_check = None
    max_check = None
    if if_sign:
        min_check = -32768
        max_check = 32767
    elif not if_sign:
        min_check = 0
        max_check = 65535
    int_column = int(column)
    if max_check >= int_column >= min_check:
        return True
    else:
        return False
 
 
def check_mediumint(column, if_none=True, if_sign=False):
    """
    Check if it is valid of data to be written to satisfy MEDIUMINT(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :param if_sign: whether integer values signed or not.
    :return: Boolean.
    """
    if if_none:
        if re.match("^$", column):
            return True
        else:
            pass
    elif not if_none:
        if re.match("^$", column):
            return False
        else:
            pass
    try:
        int(column)
    except ValueError:
        return False
    min_check = None
    max_check = None
    if if_sign:
        min_check = -8388608
        max_check = 8388607
    elif not if_sign:
        min_check = 0
        max_check = 16777215
    int_column = int(column)
    if max_check >= int_column >= min_check:
        return True
    else:
        return False
 
 
def check_int(column, if_none=True, if_sign=False):
    """
    Check if it is valid of data to be written to satisfy INT(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :param if_sign: whether integer values signed or not.
    :return: Boolean.
    """
    if if_none:
        if re.match("^$", column):
            return True
        else:
            pass
    elif not if_none:
        if re.match("^$", column):
            return False
        else:
            pass
    try:
        int(column)
    except ValueError:
        return False
    min_check = None
    max_check = None
    if if_sign:
        min_check = -2147483648
        max_check = 2147483647
    elif not if_sign:
        min_check = 0
        max_check = 4294967295
    int_column = int(column)
    if max_check >= int_column >= min_check:
        return True
    else:
        return False
 
 
def check_bigint(column, if_none=True, if_sign=False):
    """
    Check if it is valid of data to be written to satisfy BIGINT(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :param if_sign: whether integer values signed or not.
    :return: Boolean.
    """
    if if_none:
        if re.match("^$", column):
            return True
        else:
            pass
    elif not if_none:
        if re.match("^$", column):
            return False
        else:
            pass
    try:
        int(column)
    except ValueError:
        return False
    min_check = None
    max_check = None
    if if_sign:
        min_check = -9223372036854775808
        max_check = 9223372036854775807
    elif not if_sign:
        min_check = 0
        max_check = 18446744073709551615
    int_column = int(column)
    if max_check >= int_column >= min_check:
        return True
    else:
        return False
 
 
def check_char(column, length, if_none=True):
    """
    Check if it is valid of data to be written to satisfy CHAR(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param length: design of data length.
    :param if_none: whether none value is valid or not.
    :return: Boolean.
    """
    pattern = None
    if if_none:
        pattern = "(^.{%d}$)|(^$)" % length
    elif not if_none:
        pattern = "^.{%d}$" % length
    if re.match(pattern, column):
        return True
    else:
        return False
 
 
def check_varchar(column, length, if_none=True):
    """
    Check if it is valid of data to be written to satisfy VARCHAR(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param length: design of data length.
    :param if_none: whether none value is valid or not.
    :return: Boolean.
    """
    pos = None
    if if_none:
        pos = 0
    elif not if_none:
        pos = 1
    pattern = "^.{%d,%d}$" % (pos, length)
    if re.match(pattern, column):
        return True
    else:
        return False
 
 
def check_datetime(column, if_none=True):
    """
    Check if it is valid of data to be written to satisfy DATETIME / TIMESTAMP(MySQL / MariaDB) type columns.
    :param column: column(data) to write into MySQL / MariaDB.
    :param if_none: whether none value is valid or not.
    :return: Boolean.
    """
    pattern = None
    if if_none:
        pattern = r"(^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$)|(^\d{4}-\d{2}-\d{2})|(^\d{4}-\d{1}-\d{2})|(^\d{4}-\d{2}-\d{1})|(^\d{4}-\d{1}-\d{1})|(^$)"
    elif not if_none:
        pattern = r"(^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$)|(^\d{4}-\d{2}-\d{2})|(^\d{4}-\d{1}-\d{2})|(^\d{4}-\d{2}-\d{1})|(^\d{4}-\d{1}-\d{1})"
    if re.match(pattern, column):
        return True
    else:
        return False

# 目前只有对错，日后改为错误码的形式
def checkType(data,type,length=255):
    if type == 'int':
        return check_int(data)
    elif type == 'varchar':
        return check_varchar(data,length)
    elif type == 'datetime':
        return check_datetime(data)

    return True
    