# coding:utf-8
'''
	@DateTime: 	2021-06-28
	@Version: 	1.0
	@Author: 	pmj
'''
import socket
import struct
import operator
import time
import os
import sys
from PyQt5.QtCore import pyqtSignal,QObject
sys.path.append('./lib/client/')

from lib.clientFTP.client import client
from lib.clientFTP import code

class ClientInfo():
    connect_ok = False
    login_ok = False
    user_id = None
    password = None

class SocketTransferClient(QObject):
    processbar_step = pyqtSignal(int)
    def __init__(self, ip='3jk9901196.qicp.vip', port=18486):
        super(SocketTransferClient,self).__init__()
        # ip = 'localhost'
        # port=1111
        self.ip = ip
        self.port = port
        self.login_ok = False
        self.client_obj = client(ip,port)    #创建对象
        self.client_obj.processbar_step.connect(self.processbar_update)
        processbar_step = pyqtSignal(int)
        self.info = ClientInfo()

    def processbar_update(self,value):
        self.processbar_step.emit(value)


    def connect(self):
        # 连接服务器
        conn_result = self.client_obj.connect()  #连接服务器，返回结果
        if conn_result != code.CONN_SUCC:
            return False
        self.info.connect_ok = True
        return True

    def login(self,user='test',password='12345'):
        # 登录账号
        if not self.client_obj.login(user,password) :
            print('['+user+'] 登录失败')
            return False
        self.info.login_ok = True
        print('>>>>>> '+user+' <<<<<< 登录成功')
        return True
        #return True


    # 实现下载功能
    def download(self,client_root,server_folder):
        if not os.path.exists(client_root):
            return
        res = self.client_obj.getFolder('getFolder|'+client_root+'|'+server_folder)
        return res


    # 实现上传功能
    def upload(self,filepath,target_folder):
        
        if not os.path.exists(filepath):
            return
        res = self.client_obj.put('put|'+filepath+'|'+target_folder)
        time.sleep(0.5)
        return res
       
        
    def delete(self,datanum):
        self.client_obj.delete('delete|'+datanum)




if __name__ == '__main__':

    transfer = SocketTransferClient() # 建立socket并连接8002端口
    while True:
        order = input()
        if operator.eq(order, '1'):
            transfer.download()
        elif operator.eq(order, '2'):
            path = input('请输入要上传的文件路径\n')
            transfer.upload(path)
        elif operator.eq(order, '3'):
            print('正在关闭连接...')
            time.sleep(0.5)
            transfer.send(order.encode())
            break
        else:
            print('命令错误,请重新输入！')
            continue
        transfer.listen()
    transfer.close()
