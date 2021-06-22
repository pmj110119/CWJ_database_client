# coding:utf-8
'''
	@DateTime: 	2021-05-16
	@Version: 	1.0
	@Author: 	pmj
'''
import socket
import struct
import operator
import time
import os


class SocketTransferClient():
    def __init__(self, ip='3jk9901196.qicp.vip', port=18486):
        ip = 'localhost'
        port=18486
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        print('socket连接成功！')
        line = self.sock.recv(1024)
        print(line)
        #self.sock.send("jrk.com".encode())
        #line = self.sock.recv(1024)
        #print(line)
        #print(line.decode())

    # 实现下载功能
    def download(self,target_folder,local_folder='.'):
        self.sock.send('1'.encode())
        self.sock.send(target_folder.encode())

        # 从服务端接收文件列表
        filelist = self.sock.recv(1024).decode()
        if operator.eq(filelist, '-1'):
            print('没有可以下载的文件')
            return
        print('可下载的文件有：',filelist)
        files = filelist.split('\n')

        for file in files:
            if file=='' or file==' ' or file=='\n':
                break
            self.sock.send(file.encode())
            # 获取包大小，并解压
            FILEINFO_SIZE = struct.calcsize('128sI')
            try:
                #fhead = self.sock.recv(1024)
                fhead = self.sock.recv(FILEINFO_SIZE)
                filename, filesize = struct.unpack('128sI', fhead)
    
                # 接收文件
                with open(filename.decode().strip('\00'), 'wb') as f:
                #with open('xxxx.py', 'wb') as f:
                    ressize = filesize
                    while True:
                        if ressize > 1024:
                            filedata = self.sock.recv(1024)
                        else:
                            filedata = self.sock.recv(ressize)
                            f.write(filedata)
                            break
                        if not filedata:
                            break
                        f.write(filedata)
                        ressize = ressize - len(filedata)
                        if ressize <= 0:
                            break
                print(filename.decode()+' 传输成功!')
            except Exception as e:
                print(e)
                print('文件传输失败!')
        self.sock.send('-1'.encode())

    # 实现上传功能
    def upload(self,filepath,target_folder):
        self.sock.send('2'.encode())
        #self.sock.send(target_folder.encode())
        # 获取文件路径，并将文件信息打包发送给服务端
        filename = os.path.basename(filepath)
        fhead = struct.pack('128sI', target_folder.encode(), os.stat(filepath).st_size)
        self.sock.send(fhead)
        # 传送文件
        with open(filepath, 'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                self.sock.send(filedata)
        print('文件传输结束')

    def listen(self):
        line = self.sock.recv(1024)
        print(line.decode())
    def stop(self):
        self.sock.close()



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
