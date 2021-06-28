#!/usr/bin/env python
#coding=utf-8
__author__ = 'yinjia'


import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# 服务端地址
FTP_SERVER_IP = "3jk9901196.qicp.vip"
FTP_SERVER_PORT = 46364

# 文件下载保存路径
DOWNLOAD_FILE_PATH = os.path.join(BASE_DIR, "download")

# 日志文件存放路径
LOGS = os.path.join(BASE_DIR, "logs","ftpclient.log")

