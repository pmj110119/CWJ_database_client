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


class SocketTransferClient():
    def __init__(self, ip='3jk9901196.qicp.vip', port=18486):
        # ip = 'localhost'
        # port=1111
        self.ip = ip
        self.port = port

        


    # 实现下载功能
    def download(self,target_folder,local_folder='.'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        print(sock.recv(1024).decode())
        sock.send('1'.encode())
        sock.send(target_folder.encode())

        # 从服务端接收文件列表
        filelist = sock.recv(1024).decode()
        if operator.eq(filelist, '-1'):
            print('没有可以下载的文件')
            return False
        print('可下载的文件有：',filelist)
        files = filelist.split('\n')

        for file in files:
            if file=='' or file==' ' or file=='\n':
                break
            sock.send(file.encode())
            # 获取包大小，并解压
            FILEINFO_SIZE = struct.calcsize('128sI')
            try:
                #fhead = sock.recv(1024)
                fhead = sock.recv(FILEINFO_SIZE)
                filename, filesize = struct.unpack('128sI', fhead)
    
                # 接收文件
                with open(filename.decode().strip('\00'), 'wb') as f:
                #with open('xxxx.py', 'wb') as f:
                    ressize = filesize
                    while True:
                        if ressize > 1024:
                            filedata = sock.recv(1024)
                        else:
                            filedata = sock.recv(ressize)
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
                return False
        sock.send('-1'.encode())
        sock.send('3'.encode())
        sock.close()
        return True

    # 实现上传功能
    def upload(self,filepath,target_folder):
        if not os.path.exists(filepath):
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        print(sock.recv(1024).decode())
        sock.send('2'.encode())
        time.sleep(0.2)
        # 获取文件路径，并将文件信息打包发送给服务端
        filename = os.path.basename(filepath)
        fhead = struct.pack('128sI', target_folder.encode(), os.stat(filepath).st_size)
        #print('send:',fhead)
        sock.send(fhead)
        # 传送文件
        with open(filepath, 'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                sock.send(filedata)


        # 给服务端发送结束信号
        sock.send('quit'.encode())
        time.sleep(0.1)
        
        res = sock.recv(1024).decode()
        sock.send('3'.encode())
        sock.close()
        if 'success' in res:
            print('发送成功！')
            return True
        else:
            print('发送失败！')
            return False

        





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
