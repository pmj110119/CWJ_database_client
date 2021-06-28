#!/usr/bin/env python
#coding=utf-8
__author__ = 'yinjia'

import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import settings,template,code
from lib import common
from lib.client import client



def run():

    
    client_obj = client(settings.FTP_SERVER_IP,settings.FTP_SERVER_PORT)    #创建对象
    conn_result = client_obj.connect()  #连接服务器，返回结果
    if conn_result != code.CONN_SUCC:
        return
    print("连接成功！")
    #客户端登录
    if not client_obj.login('test','12345') :
        return
    #获取命令
    client_obj.put('put|test.jpg')




run()