#!/usr/bin/env python
#coding=utf-8
__author__ = 'yinjia'


from hashlib import new
import os,sys,socket
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib.clientFTP import settings
from lib.clientFTP import code
from lib.clientFTP import common
import time


class client(object):
    def __init__(self,server_addr, server_port):
        self.username =""
        self.totalspace = 0
        self.userspace = 0
        self.client = socket.socket()
        self.__server = (server_addr, server_port)
    def connect(self):
        """
        客户端连接验证
        :return: 连接成功返回1000；连接失败返回1001
        """
        try:
            self.client.connect(self.__server)
            ret_bytes = self.client.recv(1024)
            #接收服务端消息
            ret_str = str(ret_bytes, encoding='utf-8')
            if ret_str == "OK":
                return code.CONN_SUCC
            else:
                return code.CONN_FAIL
        except Exception as e:
            pass


    def check_auth(self,user, passwd):
        """
        客户端状态发送给服务端验证，并返回结果
        :param user: 用户名
        :param passwd: 密码
        :return:
        """
        sendmsg = "{cmd}|{user}|{passwd}".format(cmd="auth",
                                                 user=user,
                                                 passwd=passwd)
        self.client.sendall(bytes(sendmsg,encoding='utf-8'))
        ret_bytes = self.client.recv(1024)
        #获取服务端返回的认证状态信息
        auth_info = str(ret_bytes, encoding='utf-8')
        if auth_info == "success":
            self.username = user
            #获取服务端返回用户空间信息
            user_info = str(self.client.recv(1024),encoding='utf-8')
            self.totalspace = int(user_info.split("|")[0])
            self.userspace = int(user_info.split("|")[1])
            return code.AUTH_SUCC
        if auth_info == "user_error":
            return code.AUTH_USER_ERROR
        if auth_info == "fail":
            return code.AUTH_FAIL

    def login(self,username,password):
        #对密码进行md5加密
        password = common.md5(password)
        #登录认证
        auth_status = self.check_auth(username,password)
        if auth_status == code.AUTH_SUCC:
            common.message(">>>>>>>登录成功","INFO")
            return True
        elif auth_status == code.AUTH_USER_ERROR:
            common.message(">>>>>>>用户名不存在","ERROR")
            return False
        else:
            common.message(">>>>>>>用户名或密码错误！","ERROR")
            return False

    def mk(self,command):
        """
        创建目录
        :param command: 发送命令消息格式；mk|test或mk|/test/yj
        :return:
        """
        #发送命令消息给服务端
        self.client.sendall(bytes(command,encoding='utf-8'))
        #接收服务端发来的回应消息
        mk_msg = str(self.client.recv(1024), encoding='utf-8')
        mk_msg = int(mk_msg)
        if mk_msg == code.FILE_MK_SUCC:
            common.message(">>>>>>>创建目录成功","INFO")
        elif mk_msg == code.FILE_MK_FAIL:
            common.message(">>>>>>>创建目录失败","ERROR")
        else:
            common.message(">>>>>>>请输入文件夹名","ERROR")

    def delete(self,command):
        """
        删除目录或文件名
        :param command: delete|PycharmProjects/untitled/project/FTPv1/FTPServer/upload/admin/test/aa
        :return:
        """
        # 发送命令消息给服务端
        self.client.sendall(bytes(command, encoding='utf-8'))
        # 接收服务端发来的回应消息
        del_msg = str(self.client.recv(1024), encoding='utf-8')
        reve_status = int(del_msg.split("|")[0])
        reve_delfilename_fsize = int(del_msg.split("|")[1])

        if del_msg == code.FOLDER_DEL_SUCC:
            common.message(">>>>>>>删除目录成功","INFO")
        elif reve_status == code.FILE_DEL_SUCC:
            #更新用户空间配额大小
            self.userspace -= reve_delfilename_fsize
            common.message(">>>>>>>删除文件名成功","INFO")
        elif reve_status == code.FILE_DEL_FAIL:
            common.message(">>>>>>>删除目录或文件名失败","ERROR")
        elif reve_status == code.FILE_DEL_EMPTY:
            common.message(">>>>>>>当前目录下不是空目录，无法删除！","ERROR")
        else:
            common.message(">>>>>>>命令行请输入需要删除的路径目录或文件名!","ERROR")

    def cd(self,command):
        """
        切换目录路径
        :param command: cd|.. 或cd|foldername
        :return: 返回状态信息
        """
        # 发送命令消息给服务端
        self.client.sendall(bytes(command, encoding='utf-8'))
        # 接收服务端发来的回应消息
        cd_msg = str(self.client.recv(1024), encoding='utf-8')
        result_status,result_folder = cd_msg.split("|")
        if result_status == "0":
            result_value = "当前是根目录"
        elif result_status == "1":
            result_value = "目录已切换到:{0}".format(result_folder)
        elif result_status == "2":
            result_value = "切换失败, {0} 不是一个目录".format(result_folder)
        elif result_status == "3":
            result_value = "命令无效：{0}".format(result_folder)
        common.message(result_value,"INFO")

    def ls(self,*args):
        """
        显示客户端的文件列表详细信息
        :param args:
        :return: 返回文件列表
        """
        print(11111111111)
        try:
            # 发送命令到服务端
            self.client.send(bytes("ls|", encoding='utf-8'))
            # 接收服务端发送结果的大小
            print(22222222)
            total_data_len = self.client.recv(1024).decode()
            print(33333333)
            # 收到了并发送一个ready标识给服务端
            self.client.send(bytes("ready", 'utf-8'))

            # 开始接收数据
            total_size = int(total_data_len)  # 文件总大小
            has_recv = 0  # 已经接收的文件大小
            exec_result = bytes("", 'utf8')
            while True:
                # 如果文件总大小等于已经接收的文件大小，则退出
                if total_size == has_recv:
                    break
                data = self.client.recv(1024)
                has_recv += len(data)
                exec_result += data
            # 获取结果中文件及文件夹的数量
            return_result = str(exec_result, 'utf-8')
            file_count = int(return_result.split("|")[0])
            if file_count == 0:
                return_result = "目前无上传记录"
            else:
                return_result = return_result.split("|")[1]
            common.message(return_result,"INFO")
        except Exception as e:
            print("client ls:{0}".format(e))

    def put(self,command):
        """
        上传文件
        :param command: put|folderfile
        :return:
        """
        file_name = command.split("|")[1]
        target_path = command.split("|")[2]
        if os.path.isfile(file_name):
            filename = os.path.basename(file_name)
            fsize = os.stat(file_name).st_size
            fmd5 = common.md5sum(file_name)

            # 将基本信息发给服务端
            file_msg = "{cmd}|{file}|{filesize}|{filemd5}|{file_target_path}".format(cmd='put',
                                                                  file=filename,
                                                                  filesize=fsize,
                                                                  filemd5=fmd5,
                                                                  file_target_path=target_path)
            print(file_msg)
            self.client.send(bytes(file_msg, encoding='utf8'))
            print("send file info: {0}".format(file_msg))
            #接收来自服务端数据
            put_msg = str(self.client.recv(1024),encoding='utf-8')
            try:
                #正常上传文件
                if put_msg == "ok":
                    #判断是否超过用户空间配额
                    if self.userspace + fsize > self.totalspace:
                        common.message("用户磁盘空间不足,无法上传文件,请联系管理员!","ERROR")
                    else:
                        self.userspace += fsize
                        new_size = 0
                        with open(file_name,'rb') as f:
                            for line in f:
                                self.client.sendall(line)
                                new_size += len(line)
                                # 打印上传进度条
                                common.progress_bar(new_size,fsize)
                                if new_size >= fsize:
                                    break
                #断点续传文件
                if put_msg.split("|")[0] == "continue":
                    send_size = int(put_msg.split("|")[1])
                    common.message("服务端存在此文件，但未上传完，开始断点续传......(TODO)","INFO")
                    new_size = 0
                    with open(file_name,'rb') as f:
                        #用seek来进行文件指针的偏移，实现断点续传的功能
                        f.seek(send_size)
                        while fsize - new_size > 1024:
                            revedata = f.read(1024)
                            self.client.sendall(revedata)
                            new_size += len(revedata)
                            #打印上传进度条
                            common.progress_bar(new_size, fsize)
                        else:
                            revedata = f.read(fsize - send_size)
                            self.client.sendall(revedata)
                            # 打印上传进度条
                            common.progress_bar(new_size, fsize)

                #不存在断点文件情况，询问是否覆盖掉原文件
                if put_msg == "full":
                    inp_msg = common.message("服务端存在完整文件，将其覆盖","INFO")
       
                    with open(file_name, 'rb') as f:
                        new_size = 0
                        for line in f:
                            self.client.sendall(line)
                            new_size += len(line)
                            #打印上传进度条
                            common.progress_bar(new_size, fsize)
                            if new_size >= fsize:
                                break


                print("upload file<{0}> successful".format(file_name))
                common.message("文件上传成功", "INFO")
                return True
            except Exception as e:
                print("文件上传失败:{0}".format(e))
                common.message("文件上传失败！", "ERROR")
                return False
        else:
            common.message("文件不存在！", "ERROR")
            return False

    def getFolder(self,command):
        file_folder = command.split("|")[1]
        self.client.send(bytes(command, encoding='utf-8'))
        # 文件存在,开始接收文件基本信息(大小,文件名)
        file_info = self.client.recv(1024).decode().split("|")
        if len(file_info)==0:
            return False
        print('====',file_info)
        file_num = int(file_info[0])
        file_names = file_info[1].split(",")
        
        if file_num == 0:
            return False
        for file in file_names:
            file_fullname = os.path.join(file_folder,file)
            if os.path.exists(file_fullname):
                print('文件已存在：',file_fullname)
                continue
            if '.' not in file: # 文件夹，非文件
                continue
            time.sleep(0.2)
            print('get|'+file_fullname)
            self.get('get|'+os.path.join(file_folder,file))

    def get(self,command):
        """
        下载文件
        :param command:
        :return:
        """
        return_result = ""
        # 发送基本信息到服务端 (command,username,file)
        print('get:',command)
        self.client.send(bytes(command, encoding='utf-8'))
        # 先接收到命令是否正确标识,1 文件存在, 0 文件不存在
        ack_by_server = self.client.recv(1024)
        try:
            # 文件名错误,当前路径下找不到
            if str(ack_by_server, encoding='utf-8') == "0":
                return_result = "\n当前目录下未找到指定的文件,请到存在目录下执行get操作!"
            else:
                # 给服务端回应收到，防止粘包
                self.client.send(bytes("ok", 'utf8'))

                # 文件存在,开始接收文件基本信息(大小,文件名)
                #file_info = self.client.recv(1024).decode()
                file_info = self.client.recv(2048).decode().split("|")
                print('file_info:',file_info)
                if len(file_info)<3:
                    return False
                file_size = int(file_info[0])
                file_name = file_info[1]
                file_md5 = file_info[2]
                if file_size==0:
                    return False
                # 2 发送 ready 标识，准备开始接收文件
                self.client.send(bytes("ready", 'utf8'))

                # 3 开始接收数据了
                has_recv = 0
                with open(file_name, 'wb') as f:
                    while True:
                        # 如果文件总大小等于已经接收的文件大小，则退出
                        if file_size == has_recv:
                            break
                        data = self.client.recv(1024)
                        f.write(data)
                        has_recv += len(data)
                        # 打印下载进度条
                        common.progress_bar(has_recv, file_size)
                return_result = "\n文件下载成功"
                print("download file<{0}> from server successful".format(file_name))
                # md5文件验证
                check_md5 = common.md5sum(os.path.join(settings.DOWNLOAD_FILE_PATH, file_name))
                if check_md5 == file_md5:
                    print("md5 check for file<{0}> succ!".format(file_name))
                    return_result += ", MD5 验证成功! "
                else:
                    return_result += ", MD5 验证文件不匹配! "
            common.message(return_result,"INFO")
        except Exception as e:
            print(e)
