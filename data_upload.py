from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import json


class GUI_upload(QMainWindow):

    def __init__(self):
        super(GUI_upload, self).__init__()  # 调用父类的构造函数


        uic.loadUi("./assets/upload.ui", self)


        self.data = []

        # 表的初始化/显示表头
        table = self.loadJson("softwareConfig.json")
        self.table_select = table['key_search']

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

    def openfile(self):
        openfile = QFileDialog.getOpenFileNames(self, '选择文件')[0]#, '', 'image files(*.jpg , *.png, *.tiff, *.tif)')[0]
        return openfile

    
    def loadJson(self, jsonPath):
        with open(jsonPath, 'r',encoding='UTF-8') as f:
            data = json.load(f)
            return data


class GUI_keyAdd(QMainWindow):

    def __init__(self):
        super(GUI_keyAdd, self).__init__()  # 调用父类的构造函数
        uic.loadUi("./assets/keyAdd.ui", self)
        





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