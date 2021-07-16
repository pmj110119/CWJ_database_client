#coding:utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle
import numpy as np
import pymysql
import json
from os import system
from transfer_client import SocketTransferClient
from lib.sql_type_check import checkType
import time
import os,sys
import shutil
from data_upload import GUI_keyAdd, GUI_upload
import collections
SERVER = "server"
CLIENT = "client"


class Stream(QObject):
    newText = pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))
        # 实时刷新界面
        QApplication.processEvents()


def loadJson(jsonPath):
    with open(jsonPath, 'r',encoding='UTF-8') as f:
        data = json.load(f)
        return data

class SocketThread(QThread):
    result = pyqtSignal(list)  # 创建一个自定义信号，元组参数
    err = pyqtSignal(bool)  # 创建一个自定义信号，元组参数
    processbar_step = pyqtSignal(int)
    def __init__(self,ip,port):
        super(SocketThread,self).__init__()
        self.transfer = SocketTransferClient(ip=ip, port=port)
        self.transfer.processbar_step.connect(self.processbar_update)
        
        self.if_running = False
        self.task = collections.deque()

    def processbar_update(self,value):
        self.processbar_step.emit(value)

    def connect(self):
        return self.transfer.connect()
    def login(self,user,password):
        return self.transfer.login(user,password)

    def update_task(self,order,data):
        self.task.append([order,data])
    def run(self):
        try:
            self.if_running = True
            while self.task:
                order, data = self.task.popleft()
                if order=='upload':
                    res = self.transfer.upload(data[0],data[1])
                elif order=='download':
                    res = self.transfer.download(data[0],data[1])
                elif order=='delete':
                    self.transfer.delete(data)
                #self.result.emit([order,res,data])  # 发射自定义信号
                time.sleep(0.3)
            self.if_running = False
            print('>>>> '+order+'完成 <<<<')
        except:
            self.err.emit(True)
       

class GUI(QMainWindow):

    def __init__(self):
        super(GUI, self).__init__()  # 调用父类的构造函数
        
        uic.loadUi("./assets/main.ui", self)
        sys.stdout = Stream(newText=self.onUpdateEdit)
        self.mysql_login = False
        self.socket_login = False

        self.loadConfig()
        self.mysqlSelfInspection()

        


        self.buttonSearch.clicked.connect(self.search)  # 设置查询按钮的回调函数
        self.buttonUpload.clicked.connect(self.uploadToServer)
        self.buttonDelete.clicked.connect(self.deleteSql)  # 设置查询按钮的回调函数
        self.buttonKeyAdd.clicked.connect(self.addKeyToServer)  # 设置查询按钮的回调函数
        self.buttonKeyDelete.clicked.connect(self.deleteKeyToServer)  # 设置查询按钮的回调函数

        self.buttonDataUpload.clicked.connect(self.dataUpload)  # 设置查询按钮的回调函数
        self.buttonDataDownload.clicked.connect(self.dataDownload)  # 设置查询按钮的回调函数



        # if self.ip=='localhost':
        #     self.mode = SERVER
        #     self.socket_login = True
        # else:
        #     self.mode = CLIENT

        if self.mode == CLIENT:     # 客户端需要和服务器进行socket通信
            #self.transfer = SocketTransferClient(ip=self.ip, port=self.socket_port)
            self.sock_thread = SocketThread(ip=self.ip, port=self.socket_port)
            self.sock_thread.processbar_step.connect(self.updateProcessBar)
            if not self.sock_thread.connect():
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '远程连接失败，请重启或联系维护人员')
                msg_box.exec_()
                return
            if not self.sock_thread.login(self.user_id,self.password):
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '用户名密码错误，请重新输入')
                msg_box.exec_()
                return
            self.socket_login = True
            self.sock_thread.result.connect(self.socketResultLog)
            self.sock_thread.err.connect(self.socketError)
        else:
            self.socket_login = True

        self.search()


    # 作为槽函数于Stream的信号连接, 内部参数于信号发射参数相同
    def onUpdateEdit(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def updateProcessBar(self,step):
        self.progressBar.setValue(step)
        #print(step,'\n')

    def socketError(self,err):  # 重启线程
        if self.sock_thread:
            del self.sock_thread
            self.sock_thread = SocketThread(ip=self.ip, port=self.socket_port)
            if not self.sock_thread.connect():
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '远程连接失败，请重启或联系维护人员')
                msg_box.exec_()
                exit()
            if not self.sock_thread.login('test','12345'):
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '用户名密码错误，请重新输入')
                msg_box.exec_()
                exit()
            #self.sock_thread.result.connect(self.socketResultLog)
            self.sock_thread.err.connect(self.socketError)
            print('----数据传输崩溃，已重连')

    def socketResultLog(self,result):
        [order,res,data] = result
        order = '上传' if order=='upload' else '下载'
        res = '成功' if res==True else '失败'
        print(order+res+':'+data[1])


  
    

    def loadConfig(self,name='softwareConfig'):
        result = loadJson(name+'.json')
        #self.mode_json = result["mode"]
        self.mode = result["mode"]
        self.user_id = result["user_id"]
        self.password = result["password"]

        self.ip = result["ip"]
        self.mysql_username = result["mysql_username"]
        self.mysql_port = int(result["mysql_port"])
        self.socket_port = int(result["socket_port"])
        self.mysql_password = result["mysql_password"]
        self.database = result["database"]
        self.key_search = result["key_search"]
        self.key_show = result["key_show"]

        self.data_root = 'data/' + self.user_id
        

        self.keys_name = []
        self.keys_type = {} # 储存对应key的数据类型
        for data in self.key_show:
            self.keys_name.append(data[0])
            self.keys_type[data[0]] = data[1]   

        
        # 表的初始化/设置表头
        #self.cellEventEnable(False)
        self.tableShow.setColumnCount(len(self.keys_name))  
        self.tableShow.setHorizontalHeaderLabels(self.keys_name)
        self.cellEventEnable(True)
        # 动态生成search表
        self.data = []
        for i in range(self.tableSearch.count()):
	        # 先清楚缓存
            self.tableSearch.itemAt(i).widget().deleteLater()
        for i, column in enumerate(self.key_search):
            data = {}
            # 用于信息输入的文本框
            line = QLineEdit()
            line.setObjectName(u'line_' + column)  # 设置name
            line.setFont(QFont("Roman times", 12, QFont.Bold))
            # 显示字段名的label
            label = QLabel()
            label.setText(column)
            label.setFont(QFont("Roman times", 12, QFont.Bold))
            label.setObjectName(u'label_' + column)
            self.tableSearch.addWidget(label, 2 * (i % 4), 2 * (i // 4) + 0)
            self.tableSearch.addWidget(line, 2 * (i % 4) + 1, 2 * (i // 4) + 0)

            data['name'] = column
            data['widget'] = line
            self.data.append(data)

    def updateConfig(self, name='softwareConfig'):
        new_config = {}
        new_config["mode"] = self.mode
        new_config["user_id"] = self.user_id
        new_config["password"] = self.password
        new_config["ip"] = self.ip
        new_config["mysql_username"] = self.mysql_username
        new_config["mysql_port"] = self.mysql_port
        new_config["mysql_password"] = self.mysql_password
        new_config["socket_port"] = self.socket_port
        new_config["database"] = self.database
        new_config["key_search"] = self.key_search
        new_config["key_show"] = self.key_show
        json_str = json.dumps(new_config, indent=4)
        with open(name + '.json', 'w') as json_file:
            json_file.write(json_str)
        
        


    # 连接数据库
    def mysqlSelfInspection(self):
        #try:
        # self.conn = pymysql.connect(host="localhost",#self.ip,
        #                         user='root',
        #                         password='751224',#self.mysql_password,
        #                         database=self.database,
        #                         port=3306)#self.mysql_port)
        self.conn = pymysql.connect(host=self.ip,
                                user=self.mysql_username,
                                password=self.mysql_password,
                                database=self.database,
                                port=self.mysql_port)

        self.cursor = self.conn.cursor()
        self.mysql_login = True
        # except Exception as e:
        #     self.log('报错：'+e)
        #     self.log("数据库连接失败!")

    # 查询按钮回调函数
    def search(self):
        time.sleep(0.1)

        # 清空表单
        self.cellEventEnable(False)
        self.tableShow.clearContents()
        self.tableShow.setRowCount(0)
        # 生成sql语句并提取执行结果
        sql = self.sqlGenerate_search()
        self.cursor.execute(sql)
        ret = np.array(self.cursor.fetchall())
        self.data_temp = ret
        # 显示在表格控件中
        a = 0
        for data in ret:
            a += 1
            self.tableShow.insertRow(0)
            time.sleep(0.01)
            for j in range(len(data)):
                if j>=len(self.key_show):
                    continue
                item_value = str(data[j])
                newItem = QTableWidgetItem(item_value)
                self.tableShow.setItem(0, j, newItem)
                
                # id = self.tableShow.item(0,0).text()
                # print('id:',id,'  ',j,self.tableShow.item(0,j).text())
        # for i in range(1,len(self.data_temp)+1):

        #     print(self.tableShow.item(i-1,0).text(),self.data_temp[-i][0])
        #     self.tableShow.setItem(i-1, 0, QTableWidgetItem(self.data_temp[-i][0]))
        self.cellEventEnable(True)


    def deleteSql(self):
        selected_items = self.tableShow.selectedItems()
        if len(selected_items)==0:
            return
        row = selected_items[0].row() 
        id = self.tableShow.item(row,0).text()
        datanum = self.tableShow.item(row,2).text()

        reply = QMessageBox.question(self, '确认', '是否确认删除\''+datanum+'\'这条数据？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        sql = self.sqlGenerate_delete(id)
        self.cursor.execute(sql)
        self.conn.commit()
        self.search()

        # 本地文件删除
        target_folder = os.path.join(self.data_root,datanum) 
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        # 服务器端文件删除
        #self.socketDetele(datanum)
        print('[id-'+id+']  数据已删除')
        

    ## 文件夹弹窗    
    #os.startfile(path)

    # 添加字段
    def addKeyToServer(self):
        self.gui_keyAdd = GUI_keyAdd()
        self.gui_keyAdd.show()
        self.gui_keyAdd.buttonAdd.clicked.connect(self.keyAddEvent)  # 设置查询按钮的回调函数
    def keyAddEvent(self):
        key_name = self.gui_keyAdd.lineEdit.text()
        key_type = self.gui_keyAdd.comboBox.currentText()
        
        if key_name.isdigit():
            self.gui_keyAdd.lineEdit.setText('')
            print('[key-'+key_name+'-'+key_type+']  字段命名不符合规范，增添失败！')
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '字段名需包含英文字母，请重新命名。')
            msg_box.exec_()
            return
        sql = 'alter table '+ self.user_id +' add '\
                + key_name+' ' + key_type + '(100)'
        
        #print(sql)
        self.cursor.execute(sql)
        self.conn.commit()
        print('[key-'+key_name+'-'+key_type+']  增添新字段成功！')
        self.key_search.append(key_name)
        self.key_show.append([key_name,key_type])
        self.updateConfig()
        self.loadConfig()

        self.search()
    
    # 删除字段
    def deleteKeyToServer(self):
        selected_items = self.tableShow.selectedItems()
        print(selected_items)
        if len(selected_items)==0:
            return
        col = selected_items[0].column() 
        
        key_name = self.keys_name[col]
        print(key_name)
        reply = QMessageBox.question(self, '确认', '是否确认删除\''+key_name+'\'这个字段？',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        sql = "alter table "+ self.user_id + ' drop column ' + key_name
        print(sql)

        # self.cursor.execute(sql)
        # self.conn.commit()

        print('[key-'+key_name+']  删除字段成功！')

        # 更新配置文件
        del self.key_show[col]
        del self.key_search[col-7]
        #print(self.key_search)

        self.updateConfig()
        self.loadConfig()

        self.search()


    # insert语句
    def uploadToServer(self):
        self.gui_upload = GUI_upload()
        self.gui_upload.show()
        self.gui_upload.buttonUpload.clicked.connect(self.uploadSqlGenerator)  # 设置查询按钮的回调函数
        self.gui_upload.buttonSelect.clicked.connect(self.uploadSelectFiles)
                #self.search()
        
        pass
    
    def uploadSelectFiles(self):
        openfiles = self.gui_upload.openfile()
        #openfile = QFileDialog.getOpenFileName(self, '选择文件')[0]#, '', 'image files(*.jpg , *.png, *.tiff, *.tif)')[0]
        for file in openfiles:
            self.gui_upload.listSelectFiles.addItem(file)   # 将此文件添加到列表中
        #self.allFiles.itemClicked.connect(self.itemClick)   #列表框关联时间，用信号槽的写法方式不起作用

    def socketUpload(self,file,target_path,batch=False):
        if self.sock_thread.if_running and not batch:
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '数据传输还未结束，请等待！')
            msg_box.exec_()
            return
        self.sock_thread.update_task('upload',[file,target_path])
        self.sock_thread.start()

    def socketDetele(self,datanum):
        if self.sock_thread.if_running:
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '数据传输还未结束，请等待！')
            msg_box.exec_()
            return
        self.sock_thread.update_task('delete',datanum)
        self.sock_thread.start()

    def socketDownload(self,client_folder,server_folder):
        if self.sock_thread.if_running:
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '数据传输还未结束，请等待！')
            msg_box.exec_()
            return
        self.sock_thread.update_task('download',[client_folder,server_folder])
        self.sock_thread.start()

    def uploadSqlGenerator(self):
        # 生成sql语句并提取执行结果
        sql, datanum = self.sqlGenerate_insert(self.gui_upload)
        if not sql:
            return
   
        self.cursor.execute(sql)
        self.conn.commit()
        print('文本数据已录入数据库，正在上传文件数据')
        self.search()

        # 生成对应文件夹
        target_folder = os.path.join(self.data_root,datanum)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        
        # 将所选文件依次复制到目标路径下
        if self.gui_upload.listSelectFiles.count()==0:
            print('>>>> upload完成 <<<< （没有数据需要上传）')
        for i in range(self.gui_upload.listSelectFiles.count()):
            file = self.gui_upload.listSelectFiles.item(i).text()
            # 根据软件模式选择文件传输方式
            if self.mode == CLIENT:
                self.socketUpload(file,datanum,batch=True)
            else:
                shutil.copyfile(file,os.path.join(target_folder,os.path.basename(file)))
                print('>>>> 本地数据拷贝完成 <<<<')
            time.sleep(0.2)
        
        self.gui_upload.listSelectFiles.clear()


    # 生成sql指令
    def sqlGenerate_search(self):
        conditions = []
        # 依次处理所有要判断的列
        for data_ in self.data:
            column_name = data_['name']
            widget = data_['widget']
            if (widget.text() != ''):
                if not checkType(widget.text(),self.keys_type[column_name]):
                    print('ERROR-- 检测到错误格式，已帮您清空错误内容，请重新输入')
                    widget.setText('')
                    continue
                #print(column_name,self.keys_type[column_name])
                conditions.append(column_name + "='" + widget.text() + "' and ")  # name = value
        base = "select * from " + self.user_id
        # 如果某列不为空，则加到sql语句中
        if (len(conditions) > 0):
            base += ' where '
            for condition in conditions:
                base += condition
            base = base[:-4]  # 去掉最后一个 'and'
        return base


    
    def sqlGenerate_insert(self,gui):
        # 插入数据工厂规范字段
        ## pid       不变
        ## datanum   自增1
        ## dealtimes 不变
        ## uploader  不变
        keys = ['pid,','datanum,','dealtimes,','uploader,']   
        values = []
        self.cursor.execute('select * from '+self.user_id)
        ret = np.array(self.cursor.fetchall())
        try:
            last_data = ret[-1]
            values.append('\''+str(last_data[1])+'\',')
            values.append('\''+'d'+str(int(last_data[2][1:])+1).zfill(5)+'\',')
            values.append('\''+str(last_data[3])+'\',')
            values.append('\''+str(last_data[4])+'\',')
            datanum = 'd'+str(int(last_data[2][1:])+1).zfill(5)
        except:
            values.append('\''+'1'+'\',')
            values.append('\''+'d00001'+'\',')
            values.append('\''+'0'+'\',')
            values.append('\''+'0'+'\',')
            datanum = 'd00001'
        # 依次处理所有要判断的字段（不包括上面的规范字段）
        check_ok = True
        for data_ in gui.data:
            column_name = data_['name']
            widget = data_['widget']
            # 若某字段内容不为空，则记录其信息
            if (widget.text() != ''):
                if not checkType(widget.text(),self.keys_type[column_name]):
                    check_ok = False
                    widget.setText('')
                    continue
                keys.append(column_name + ",")  # name = value
                values.append('\''+widget.text() + "\',")  # name = value
            
        # 校验
        if len(keys)<5:
            print('ERROR-- 有效输入的字段数为0，请检查您的输入')
            return None,None
        if not check_ok:
            print('ERROR-- 检测到错误格式，已帮您清空错误内容，请重新输入')
            return None,None
        base = "INSERT INTO " + self.user_id

        

        keys_str = "("
        values_str = " values ("
        if (len(keys) > 0):
            for key,value in zip(keys,values):
                keys_str += key
                values_str += value
            keys_str = keys_str[:-1]+')'
            values_str = values_str[:-1]+')'
        else:
            return None,None
        base = base + keys_str + values_str + ';'
        return base,datanum




    def sqlGenerate_delete(self, id):
        base = "delete from "+ self.user_id + ' where id = '
        base = base + str(id) + ';'
        return base

    def cellEventEnable(self, flag):
        if flag:
            self.tableShow.cellChanged.connect(self.cellchange)
        else:
            self.tableShow.cellChanged.disconnect()
   
    def cellchange(self,row,col):
        self.cursor.execute('select * from '+self.user_id)
        ret = np.array(self.cursor.fetchall())

        data = ret[-(row+1)]
        data_id = str(data[0])
        data_key = self.keys_name[col]
        data_content = self.tableShow.item(row,col).text()
        data_content_origin = str(data[col])

        if not checkType(data_content,self.keys_type[data_key]):
            print('[id-'+data_id+',key-'+data_key+']  不符合数据格式要求，修改失败')
            self.cellEventEnable(False)
            self.tableShow.item(row,col).setText(data_content_origin)
            self.cellEventEnable(True)
            return

        base = "update " + self.user_id +' set '
        sql = base + data_key+'=\''+data_content+'\' where id='+data_id+';'
        self.cursor.execute(sql)
        self.conn.commit()
        print('[id-'+data_id+',key-'+data_key+']  修改成功')
        #print(data_id,data_key,data_content)
        #print(self.keys_name)
       # self.settext('第%s行，第%s列 , 数据改变为:%s'%(row,col,txt))



    def dataDownload(self):
        selected_items = self.tableShow.selectedItems()
        if len(selected_items)==0:
            return
        row = selected_items[0].row() 
        datanum = self.tableShow.item(row,2).text()
        client_folder = os.path.join(self.data_root,datanum)
        if not os.path.exists(client_folder):
            os.makedirs(client_folder)
        if self.mode == CLIENT:
            self.socketDownload(self.data_root,datanum)
            #self.transfer.download(target_folder,target_folder)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '本地版本不需要下载功能')
            msg_box.exec_()
            return

    def dataUpload(self):
        selected_items = self.tableShow.selectedItems()
        if len(selected_items)==0:
            return
        row = selected_items[0].row() 
        datanum = self.tableShow.item(row,2).text()
        target_folder = os.path.join(self.data_root,datanum)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 选择文件并传输
        file = QFileDialog.getOpenFileName(self, '选择文件')[0]#, '', 'image files(*.jpg , *.png, *.tiff, *.tif)')[0]
        if self.mode == CLIENT:
            self.socketUpload(file,datanum)
            shutil.copyfile(file,os.path.join(target_folder,os.path.basename(file)))    # 本地也要拷贝下
        else:
            shutil.copyfile(file,os.path.join(target_folder,os.path.basename(file)))
            print('>>>> 本地数据拷贝完成 <<<<')

    def log(self,text):
        #print(time.strftime("[%H:%M:%S]  ")+text,time.localtime())
        #self.logBrowser.append(time.strftime("[%H:%M:%S]  "+text,time.localtime()))
        self.logBrowser.append(text)
        self.logBrowser.ensureCursorVisible()



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setFont(QFont("微软雅黑", 9))
    app.setWindowIcon(QIcon("icon.ico"))
    app.setStyleSheet(stylesheet)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())










# "序号",
# "数据格式",
#   // "数据类型",
#   // "拍摄日期",
#   // "样本来源医院",
#   // "样本编号",
#   // "拍摄位置描述",
#   // "样本动物种类",
#   // "样本处理方式",
#   // "疾病名称",
#   // "疾病分型",
#   // "激发波长",
#   // "物镜下功率",
#   // "滤光片参数",
#   // "成像视场",
#   // "单个位置拍摄数",
#   // "z轴间隔",
#   // "拼接大小"