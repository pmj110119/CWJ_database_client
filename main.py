#coding:utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont
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
import os
import shutil
from data_upload import GUI_upload

SERVER = 0
CLIENT = 1

class GUI(QMainWindow):

    def __init__(self):
        super(GUI, self).__init__()  # 调用父类的构造函数
        
        uic.loadUi("./assets/main.ui", self)

        self.loadConfig()
        self.mysqlSelfInspection()

        self.buttonSearch.clicked.connect(self.search)  # 设置查询按钮的回调函数
        self.buttonUpload.clicked.connect(self.uploadToServer)

        self.buttonDelete.clicked.connect(self.deleteSql)  # 设置查询按钮的回调函数
        

        self.cellEventEnable(True)

        self.data = []

        # 表的初始化/设置表头
        keys = self.loadJson("softwareConfig.json")
        self.keys_search = keys['search']
    
        self.keys_name = []
        self.keys_type = {} # 储存对应key的数据类型
        for data in keys['show']:
            self.keys_name.append(data[0])
            self.keys_type[data[0]] = data[1]   
        
        self.cellEventEnable(False)
        self.tableShow.setColumnCount(len(self.keys_name))  
        self.tableShow.setHorizontalHeaderLabels(self.keys_name)
        self.cellEventEnable(True)
        # 动态生成search表
        for i, column in enumerate(self.keys_search):
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

        if self.ip=='localhost':
            self.mode = SERVER
        else:
            self.mode = CLIENT
        self.mode = SERVER      # 先强制为服务器版，解决socket端口映射问题后再改掉


        if self.mode == CLIENT:     # 客户端需要和服务器进行socket通信
            self.transfer = SocketTransferClient(ip=self.ip, port=self.port)


    def loadJson(self, jsonPath):
        with open(jsonPath, 'r',encoding='UTF-8') as f:
            data = json.load(f)
            return data
    

    def loadConfig(self):
        result = self.loadJson("softwareConfig.json")
        self.project_id = result["project_id"]
        self.data_root = './data/' + self.project_id
        self.ip = result["ip"]
        self.port = int(result["port"])
        self.mysql_username = result["username"]
        self.mysql_password = result["password"]
        self.database = result["database"]
        self.table_name = result["table"]


    # 连接数据库
    def mysqlSelfInspection(self):
        self.log('正在连接数据库...')
        try:
            self.conn = pymysql.connect(host=self.ip,
                                   user=self.mysql_username,
                                   password=self.mysql_password,
                                   database=self.database,
                                   port=self.port)

            self.cursor = self.conn.cursor()
            self.log("success")
        except Exception as e:
            self.log('报错：'+e)
            self.log("数据库连接失败!")

    # 查询按钮回调函数
    def search(self):
        # 清空表单
        self.cellEventEnable(False)
        self.tableShow.clearContents()
        self.tableShow.setRowCount(0)
        # 生成sql语句并提取执行结果
        sql = self.sqlGenerate_search()
        self.cursor.execute(sql)
        ret = np.array(self.cursor.fetchall())
        # 显示在表格控件中
        for data in ret:
            
            self.tableShow.insertRow(0)
            for j in range(len(data)):
                item_value = str(data[j])
                newItem = QTableWidgetItem(item_value)
                self.tableShow.setItem(0, j, newItem)
        self.cellEventEnable(True)



    def deleteSql(self):
        sql, datanum = self.sqlGenerate_delete()
        self.cursor.execute(sql)
        self.conn.commit()
        self.search()

        
        target_folder = os.path.join(self.data_root,datanum) 
        print(target_folder)
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)

    ## 文件夹弹窗    
    #os.startfile(path)


    # insert语句
    def uploadToServer(self):
        self.gui_upload = GUI_upload()
        self.gui_upload.show()
        self.gui_upload.buttonUpload.clicked.connect(self.uploadSqlGenerator)  # 设置查询按钮的回调函数
        self.gui_upload.buttonSelect.clicked.connect(self.uploadSelectFiles)
                #self.search()
        
        pass
    
    def uploadSelectFiles(self):
        openfile = self.gui_upload.openfile()
        #openfile = QFileDialog.getOpenFileName(self, '选择文件')[0]#, '', 'image files(*.jpg , *.png, *.tiff, *.tif)')[0]
        #for file in openfiles:
        self.gui_upload.listSelectFiles.addItem(openfile)   # 将此文件添加到列表中
        #self.allFiles.itemClicked.connect(self.itemClick)   #列表框关联时间，用信号槽的写法方式不起作用

    def uploadSqlGenerator(self):
        # 生成sql语句并提取执行结果
        sql, datanum = self.sqlGenerate_insert(self.gui_upload)
        if not sql:
            return
   
        self.cursor.execute(sql)
        self.conn.commit()
        self.log('-- 录入成功')
        self.search()

        
        # 生成对应文件夹
        target_folder = os.path.join(self.data_root,datanum)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        
        # 将所选文件依次复制到目标路径下
        for i in range(self.gui_upload.listSelectFiles.count()):
            file = self.gui_upload.listSelectFiles.item(i).text()
            # 根据软件模式选择文件传输方式
            if self.mode == CLIENT:
                self.transfer.upload(file)
            else:
                shutil.copyfile(file,os.path.join(target_folder,os.path.basename(file)))

    # 生成sql指令
    def sqlGenerate_search(self):
        conditions = []
        # 依次处理所有要判断的列
        for data_ in self.data:
            column_name = data_['name']
            widget = data_['widget']
            if (widget.text() != ''):
                if not checkType(widget.text(),self.keys_type[column_name]):
                    self.log('ERROR-- 检测到错误格式，已帮您清空错误内容，请重新输入')
                    widget.setText('')
                    continue
                #print(column_name,self.keys_type[column_name])
                conditions.append(column_name + "='" + widget.text() + "' and ")  # name = value
        base = "select * from " + self.table_name
        # 如果某列不为空，则加到sql语句中
        if (len(conditions) > 0):
            base += ' where '
            for condition in conditions:
                base += condition
            base = base[:-4]  # 去掉最后一个 'and'
        print(base)
        return base


    
    def sqlGenerate_insert(self,gui):
        # 插入数据工厂规范字段
        ## pid       不变
        ## datanum   自增1
        ## dealtimes 不变
        ## uploader  不变
        keys = ['pid,','datanum,','dealtimes,','uploader,']   
        values = []
        self.cursor.execute('select * from '+self.table_name)
        ret = np.array(self.cursor.fetchall())
        last_data = ret[-1]
        values.append('\''+str(last_data[1])+'\',')
        values.append('\''+'d'+str(int(last_data[2][1:])+1).zfill(5)+'\',')
        values.append('\''+str(last_data[3])+'\',')
        values.append('\''+str(last_data[4])+'\',')
  
        datanum = 'd'+str(int(last_data[2][1:])+1).zfill(5)

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
            self.log('ERROR-- 有效输入的字段数为0，请检查您的输入')
            return None,None
        if not check_ok:
            self.log('ERROR-- 检测到错误格式，已帮您清空错误内容，请重新输入')
            return None,None
        base = "INSERT INTO " + self.table_name

        

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
        print(base)
        return base,datanum




    def sqlGenerate_delete(self):
        base = "delete from "+ self.table_name + ' where id = '
        self.cursor.execute('select * from '+self.table_name)
        ret = np.array(self.cursor.fetchall())
        id = ret[-1][0]
        datanum = ret[-1][2]
        base = base + str(id) + ';'
        return base, datanum

    def cellEventEnable(self, flag):
        if flag:
            self.tableShow.cellChanged.connect(self.cellchange)
        else:
            self.tableShow.cellChanged.disconnect()
   
    def cellchange(self,row,col):
        self.cursor.execute('select * from '+self.table_name)
        ret = np.array(self.cursor.fetchall())

        data = ret[-(row+1)]
        data_id = str(data[0])
        data_key = self.keys_name[col]
        data_content = self.tableShow.item(row,col).text()
        data_content_origin = str(data[col])

        if not checkType(data_content,self.keys_type[data_key]):
            self.log('[id-'+data_id+',key-'+data_key+']  不符合数据格式要求，修改失败')
            self.cellEventEnable(False)
            self.tableShow.item(row,col).setText(data_content_origin)
            self.cellEventEnable(True)
            return

        base = "update " + self.table_name +' set '
        sql = base + data_key+'=\''+data_content+'\' where id='+data_id+';'
        print(sql)
        self.cursor.execute(sql)
        self.conn.commit()
        self.log('[id-'+data_id+',key-'+data_key+']  修改成功')
        #print(data_id,data_key,data_content)
        #print(self.keys_name)
       # self.settext('第%s行，第%s列 , 数据改变为:%s'%(row,col,txt))


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