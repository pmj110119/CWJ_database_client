import sys
import qdarkstyle
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import json
from main import GUI
def loadJson(jsonPath):
    with open(jsonPath, 'r',encoding='UTF-8') as f:
        data = json.load(f)
        return data

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        uic.loadUi("assets/login.ui", self)

        self.buttonLogin.clicked.connect(self.login)
        self.readConfig()

    def readConfig(self,name='softwareConfig'):
        self.config = loadJson(name+'.json')
        if 'user_id' in self.config:
            self.editName.setText(self.config["user_id"])
        if 'password' in self.config:
            self.editPassword.setText(self.config["password"])
        if 'ip' in self.config:
            self.editIP.setText(self.config["ip"])
        if 'mysql_port' in self.config:
            self.editMysqlPort.setText(str(self.config["mysql_port"]))
        if 'socket_port' in self.config:
            self.editSocketPort.setText(str(self.config["socket_port"]))

    def updateConfig(self,name='softwareConfig'):
        self.config["user_id"] = self.editName.text()
        self.config["password"] = self.editPassword.text()
        self.config["ip"] = self.editIP.text()
        self.config["mysql_port"] = self.editMysqlPort.text()
        self.config["socket_port"] = self.editSocketPort.text()
        json_str = json.dumps(self.config, indent=4)
        with open(name + '.json', 'w') as json_file:
            json_file.write(json_str)

    def login(self):
        if self.editName.text()=='' or self.editPassword.text()=='' or self.editIP.text()=='' or self.editMysqlPort.text()=='' or self.editSocketPort.text()=='':
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '请填写空白处内容！')
            msg_box.exec_()
        else:
            try:
                self.updateConfig()
                self.main = GUI()
                if self.main.socket_login and self.main.mysql_login:
                    self.close()
                    self.main.show()
                    self.main.search()
                else:
                    print(111)
                    msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '请检查网络、用户名和密码！')
                    msg_box.exec_()
                    #self.close()
            except:
                msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '未知报错，请联系服务器管理员！')
                msg_box.exec_()
        
    
if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setFont(QFont("微软雅黑", 9))
    app.setWindowIcon(QIcon("icon.ico"))
    app.setStyleSheet(stylesheet)
    gui = LoginWindow()
    gui.show()
    sys.exit(app.exec_())
