# coding:utf-8
'''
	@DateTime: 	2021-05-16
	@Version: 	1.0
	@Author: 	pmj
'''
import threading
import socket
import time
import operator
import os
import struct


# 实现下载功能
def download(connect):
    # 获取文件目录
    files = os.listdir()
    # 用于传输文件目录的字符串
    liststr = ''
    # 将所有文件名传入字符串中
    for i in files:
        liststr += i + '\n'
    # 如果文件列表为空，将不继续执行下载任务
    if operator.eq(liststr, ''):
        connect.send(''.encode())
    # 如果文件列表不为空，开始下载任务
    else:
        # 向客户端传送文件列表
        connect.send(liststr.encode())
        while True:
            # 获取客户端要下载的文件名，如果不存在就继续输入
            filename = connect.recv(100).decode()
            if filename not in files:
                connect.send('文件不存在！'.encode())
            else:
                connect.send('开始文件传输！'.encode())
                break
        # 将文件信息打包发送给客服端
        fhead = struct.pack('128sI', filename.encode(), os.stat(filename).st_size)
        connect.send(fhead)
        # 传送文件信息
        with open(filename, 'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                connect.send(filedata)
        # 存储到日志中
        print('%s\n下载文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n下载文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('files')


# 实现上传功能
def upload(connect):
    FILEINFO_SIZE = struct.calcsize('128sI')
    try:
        # 获取打包好的文件信息，并解包
        fhead = connect.recv(FILEINFO_SIZE)
        filename, filesize = struct.unpack('128sI', fhead)
        filename = filename.decode().strip('\00')
        # 文件名必须去掉\00，否则会报错，此处为接收文件
        with open(filename, 'wb') as f:
            ressize = filesize
            while True:
                if ressize > 1024:
                    filedata = connect.recv(1024)
                else:
                    filedata = connect.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize < 0:
                    break
        # 存储到日志
        print('%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('files')
    except Exception as e:
        print('%s\n传输文件:\n%s\n成功\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('..')
        with open('data.log', 'a') as f:
            f.write(
                '%s\n传输文件:\n%s\n失败\n\n' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), filename))
        os.chdir('files')


def handle(connect, address):
    print('%s:%s is connectting...' % (address))
    while True:
        order = connect.recv(100).decode()  # 首先接收客户端发来的命令码
        if operator.eq(order, '1'):
            download(connect)
        elif operator.eq(order, '2'):
            upload(connect)
        elif operator.eq(order, '3'):
            connect.close()
            break
        #connect.send('\n[server] :成功！\n'.encode())


if __name__ == '__main__':
    if not os.path.exists('files'):
        os.mkdir('files')
    # 工作目录换到files文件夹
    os.chdir('files')
    # 建立socket链接，并监听8002端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 18486))
    sock.listen(100)
    while True:
        connect, address = sock.accept()
        connect.send('\n您已成功连接服务器，请进行上传或下载！\n'.encode())
        t = threading.Thread(target=handle, args=(connect, address))
        t.setDaemon(True)
        t.start()
    sock.close()