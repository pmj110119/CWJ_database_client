#coding:utf-8
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import pymysql
import json
from os import system
from transfer_client import SocketTransferClient
import time

from data_upload import GUI_upload
class GUI(QMainWindow):

    def __init__(self):
        super(GUI, self).__init__()  # 调用父类的构造函数
        
        uic.loadUi("./assets/main.ui", self)

        self.mysqlSelfInspection()

        self.buttonSearch.clicked.connect(self.search)  # 设置查询按钮的回调函数
        self.buttonUpload.clicked.connect(self.uploadToServer)

        


        self.data = []

        # 表的初始化/显示表头
        table = self.loadJson("softwareConfig.json")
        self.table_select = table['select']
        self.table_show = table['show']
        self.tableShow.setColumnCount(len(self.table_show))
        self.tableShow.setHorizontalHeaderLabels(self.table_show)
        for i, column in enumerate(self.table_select):
            data = {}

            line = QLineEdit()
            line.setObjectName(u'line_' + column)  # 设置name
            line.setFont(QFont("Roman times", 12, QFont.Bold))

            label = QLabel()
            label.setText(column)
            label.setFont(QFont("Roman times", 12, QFont.Bold))
            label.setObjectName(u'label_' + column)
            self.tableSearch.addWidget(label, 2 * (i % 4), 2 * (i // 4) + 0)
            self.tableSearch.addWidget(line, 2 * (i % 4) + 1, 2 * (i // 4) + 0)

            data['name'] = column
            data['widget'] = line
            self.data.append(data)




        #self.transfer = SocketTransferClient()


    def loadJson(self, jsonPath):
        with open(jsonPath, 'r',encoding='UTF-8') as f:
            data = json.load(f)
            return data
 
    # 连接数据库
    def mysqlSelfInspection(self):

        self.log('正在连接数据库...')
        try:
            result = self.loadJson("softwareConfig.json")
            ip = result["ip"]
            port = int(result["port"])
            username = result["username"]
            password = result["password"]
            database = result["database"]
            self.table_name = result["table"]
            conn = pymysql.connect(host=ip,
                                   user=username,
                                   password=password,
                                   database=database,
                                   port=port)

            self.cursor = conn.cursor()
            self.log("success")
        except Exception as e:
            self.log('报错：'+e)
            self.log("数据库连接失败!")

    # 查询按钮回调函数
    def search(self):
        # 清空表单
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
    

       

    # 绘图按钮回调函数
    def uploadToServer(self):
        self.gui_upload = GUI_upload()
        self.gui_upload.show()
        self.gui_upload.buttonUpload.clicked.connect(self.uploadSqlGenerator)  # 设置查询按钮的回调函数
        
        # openfile = QFileDialog.getOpenFileName(self, '选择文件', '', 'image files(*.jpg , *.png, *.tiff, *.tif)')[0]
 
        #self.transfer.upload(openfile)

        pass
    
    def uploadSqlGenerator(self):
        self.log('进upload喽！')



    # 生成sql指令
    def sqlGenerate_search(self):
        conditions = []
        # 依次处理所有要判断的列
        for data_ in self.data:
            column_name = data_['name']
            widget = data_['widget']
            if (widget.text() != ''):
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

        # 生成sql指令
    
    def sqlGenerate_insert(self):
        conditions = []
        # 依次处理所有要判断的列
        for data_ in self.data:
            column_name = data_['name']
            widget = data_['widget']
            if (widget.text() != ''):
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

    def sqlGenerate_delete(self):
        base = "select * from " + self.table_name
        print(base)
        return base



    def log(self,text):
        #print(time.strftime("[%H:%M:%S]  ")+text,time.localtime())
        #self.logBrowser.append(time.strftime("[%H:%M:%S]  "+text,time.localtime()))
        self.logBrowser.append(text)
        self.logBrowser.ensureCursorVisible()



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
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