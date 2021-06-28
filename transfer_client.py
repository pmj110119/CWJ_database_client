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
import sys;
sys.path.append('./lib/client/')

from lib.clientFTP.client import client
from lib.clientFTP import code

class SocketTransferClient():
    def __init__(self, ip='3jk9901196.qicp.vip', port=18486):
        # ip = 'localhost'
        # port=1111
        self.ip = ip
        self.port = port
        
        self.client_obj = client(ip,port)    #创建对象
        conn_result = self.client_obj.connect()  #连接服务器，返回结果
        if conn_result != code.CONN_SUCC:
            print(False)
        print("连接成功！")
        #客户端登录
        if not self.client_obj.login('test','12345') :
            print(False)
            #return False

        #return True

        

        


    # 实现下载功能
    def download(self,target_folder):
        if not os.path.exists(target_folder):
            return
        res = self.client_obj.getFolder('getFolder|'+target_folder)
        return res


    # 实现上传功能
    def upload(self,filepath,target_folder):
        
        if not os.path.exists(filepath):
            return
        print('put ',filepath)
        res = self.client_obj.put('put|'+filepath+'|'+target_folder)
        time.sleep(0.5)
        return res
       
        





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
