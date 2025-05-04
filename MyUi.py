import PyQt5.uic
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QDialog, QTableWidgetItem, QTableWidget, QPushButton, QComboBox, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QObject , QCoreApplication
import pebblehostAPI
from pathlib import Path
import logic
import ctypes
import qdarkstyle

#Custom Widgets

class MyCustomPyQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(logic.resource_path(str(Path("Data") / "ico" / "Spiriponzelli_allower.ico"))))

    def applyDarkPalette(self):
        #qdarkstyle + some override
        widget = """
                QWidget {
                    background-color: #19232D;
                    color: #ffffff;
                }

                QPushButton,
                QToolButton,
                QComboBox,
                QPlainTextEdit,
                QScrollArea,
                QTabWidget::pane {
                    border: 1px solid #555555;
                }

                QPushButton:hover,
                QToolButton:hover {
                    background-color: #19232D;
                }

                QPushButton:pressed,
                QToolButton:pressed {
                    background-color: #19232D;
                }
                """
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + widget)

        #Windows bar
        hwnd = int(self.winId())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )

    def get_columnIndex_tableWidget_byName(self, tableWidget:QTableWidget, column_name:str)->int:
        column_count = tableWidget.columnCount()
        for column in range(column_count):
            header_item = tableWidget.horizontalHeaderItem(column)
            if header_item and header_item.text() == column_name:
                return column  
    
class QPushButtonWithIcon(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

    def init(self, icon_path:str, icon_size:QSize):
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.setIcon(QIcon(icon_path))
        self.setIconSize(icon_size)
        self.enterEvent = self.on_enter_event
        self.leaveEvent = self.on_leave_event
    
    def on_enter_event(self, event):
        self.setIcon(QIcon(self.tint_icon(QPixmap(self.icon_path), QColor(255, 255, 255, 100))))

    def on_leave_event(self, event):
        self.setIcon(QIcon(QPixmap(self.icon_path)))
        pass

    def tint_icon(self, pixmap, color):
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, pixmap)  # base icon
        painter.fillRect(pixmap.rect(), color)  # overlay
        painter.end()
        
        return tinted

#Windows

class MainWindow(QMainWindow, MyCustomPyQt):

    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi(logic.resource_path(str(Path("Data") / "ui_template" / "main_gui.ui")), self)
        if logic.is_windows() and logic.windows_dark_mode_enabled():
            self.applyDarkPalette()
        self.edit_delete_size = QSize(70,30)

        #Esplicate some object in main_gui.ui
        self.tableWidget_rules:QTableWidget
        self.pushButton_Salva:QPushButtonWithIcon
        self.pushButton_addRule:QPushButtonWithIcon
        self.pushButton_ripristina:QPushButtonWithIcon
        self.label_IP:QLabel

        #Post modify QWidget
        self.pushButton_Salva.init(logic.resource_path(str(Path("Data") / "ico" / "save.png")),
                                                                 QSize(self.pushButton_Salva.width(), self.pushButton_Salva.height()))                                                     
        self.pushButton_Salva.clicked.connect(self.save_clicked)

        self.pushButton_addRule.init((logic.resource_path(str(Path("Data") / "ico" / "add_rule.png"))),
                                     QSize(self.pushButton_addRule.width(), self.pushButton_addRule.height()))
        self.pushButton_addRule.clicked.connect(self.addRule_click)

        self.pushButton_ripristina.init(logic.resource_path(str(Path("Data") / "ico" / "restore.png")),
                                        QSize(self.pushButton_ripristina.width(), self.pushButton_ripristina.height()))
        self.pushButton_ripristina.clicked.connect(self.restore_from_db)
        
        #Init from database
        self.update_table()
        self.adjustSize()

    def update_table(self):
        #Clear table
        self.tableWidget_rules.setRowCount(0)
        #Add rows with info
        for i, rule in enumerate(logic.firewall.rules):
            notEditable = False
            if str(rule["IP Address"]) == "0.0.0.0/0":
                notEditable = True

            self.tableWidget_rules.insertRow(i)

            item = QTableWidgetItem(str(rule["Name"]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
            self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Player"), item)
            
            item = QTableWidgetItem(str(rule["IP Address"]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
            self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "IP Address"), item)

            item = QTableWidgetItem(str(rule["Port"]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
            self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Port"), QTableWidgetItem(item))
            
            #Priority always not editable
            item = QTableWidgetItem(str(rule["Priority"]))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  
            self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Priority"), item)
            
            if rule["Action"]:
                action_text = "Allow"
            else:
                action_text = "Block"
            item = QTableWidgetItem(action_text)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Action"), item)

            if notEditable == True:
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Edit"), item)
            else:
                item = QPushButtonWithIcon()
                item.init(logic.resource_path(str(Path("Data") / "ico" / "edit.png")),
                                                         self.edit_delete_size)
                
                item.clicked.connect(lambda x, r=i: self.edit_clicked(r))
                self.tableWidget_rules.setCellWidget(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Edit"), item)

            if notEditable == True:
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tableWidget_rules.setItem(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Delete"), item)
            else:
                item = QPushButtonWithIcon()
                item.init(logic.resource_path(str(Path("Data") / "ico" / "delete.png")),
                                                         self.edit_delete_size)
                item.clicked.connect(lambda x, r=i: self.delete_clicked(r))
                self.tableWidget_rules.setCellWidget(i, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Delete"), item)

        self.update_ipLabel()
        self.tableWidget_rules.resizeColumnsToContents()
    #Slot

    def addRule_click(self):
        dialog = AddRuleWindow()
        result = dialog.exec()
        if result == 1:
            self.update_table()

    def edit_clicked(self, row:str):
        dialog = AddRuleWindow(row = row, name=self.tableWidget_rules.item(row, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Player")).text(),
                                ip = self.tableWidget_rules.item(row, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "IP Address")).text(),
                                port = self.tableWidget_rules.item(row, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Port")).text(),
                                action = self.tableWidget_rules.item(row, self.get_columnIndex_tableWidget_byName(self.tableWidget_rules, "Action")).text())
        result = dialog.exec()
        if result == 1:
            self.update_table()

    def delete_clicked(self, row:str):
        #delete from data
        logic.firewall.delete_rule(row)
        self.update_table()

    def save_clicked(self):
        dialog = InfoBox("Now Loading, don't close this window...")
        dialog.pushButton_OK.setEnabled(False)
        dialog.pushButton_OK.setFixedSize(QSize(0,0))
        dialog.setWindowTitle("Saving")

        self.my_thread = QThread()
        worker = QWorker(lambda: logic.firewall.upload_firewall_data())
        worker.moveToThread(self.my_thread)

        self.my_thread.started.connect(worker.run)

        worker.finished.connect(dialog.accept)
        worker.finished.connect(self.my_thread.quit)
        worker.finished.connect(worker.deleteLater)

        self.my_thread.finished.connect(self.my_thread.deleteLater)

        self.my_thread.start()
        dialog.exec_()
        self.restore_from_db()

    def restore_from_db(self):
        logic.firewall.import_firewall_data()
        self.update_table()

    def update_ipLabel(self):
        if self.checkIpAllowed(pebblehostAPI.my_public_ip):
            self.label_IP.setText("Your public ip: " + pebblehostAPI.my_public_ip + "\t" + '<span style="color: green;">ALLOW</span>')
        else:
            self.label_IP.setText("Your public ip: " + pebblehostAPI.my_public_ip + "\t" + '<span style="color: red;">BLOCK</span>')

    def checkIpAllowed(self, ip:str)->bool:
        for rule in logic.firewall.rules:
            if rule['IP Address'] == ip and rule['Action'] == True:
                return True
        return False

class AddRuleWindow(QDialog, MyCustomPyQt):

    def __init__(self, row:int=None, name:str="", ip:str="", port:str="25578", action:str="Allow"):
        super().__init__()
        PyQt5.uic.loadUi(logic.resource_path(str(Path("Data") / "ui_template" / "add_rule.ui")), self)
        if logic.is_windows() and logic.windows_dark_mode_enabled():
            self.applyDarkPalette()
        self.row = row
        self.name = name
        self.ip = ip
        self.port = port
        self.action = action

        #Esplicate some object in main_gui.ui
        self.lineEdit_Name:QLineEdit
        self.lineEdit_IP_Address:QLineEdit
        self.lineEdit_Port:QLineEdit
        self.comboBox_Action:QComboBox
        self.pushButton_Cancel:QPushButton
        self.pushButton_OK:QPushButton
        self.pushButton_UseYourIp:QPushButton

        #Post modify QWidget
        self.lineEdit_Name.setText(name)
        self.lineEdit_IP_Address.setText(ip)
        self.lineEdit_Port.setText(port)
        self.comboBox_Action.setCurrentText(action)

        self.pushButton_Cancel.clicked.connect(self.cancel_clicked)
        self.pushButton_OK.clicked.connect(self.ok_clicked)
        self.pushButton_UseYourIp.clicked.connect(self.use_my_ip)

    def cancel_clicked(self):
        self.done(-1)

    def ok_clicked(self):
        #check every field
        check_result = True

        #IP Address check
            #Already used
        blacklist_IP =logic.firewall.get_all_ip()
        try:
            blacklist_IP.remove(self.ip)
        except:
            pass
        if self.lineEdit_IP_Address.text() in blacklist_IP:
            check_result = False
            infoBox = InfoBox(message = "IP già presente!")
            infoBox.exec()
            #Not valid ipv4 with notation CIDR
        if not logic.is_a_valid_ipv4_cidr(self.lineEdit_IP_Address.text()):
            check_result = False
            infoBox = InfoBox(message = "IP inserito non è formalmente correto!")
            infoBox.exec()

        #Port check
        if any(x.isalpha() for x in self.lineEdit_Port.text()):
            check_result = False
            infoBox = InfoBox(message = "Porta deve contenere solo numeri!")
            infoBox.exec()

        if self.comboBox_Action.currentText() == "Allow":
            action = True
        else:
            action = False

        #If all checks pass
        if check_result:
            if self.row:
                logic.firewall.edit_rule(row=self.row, name=self.lineEdit_Name.text(), ip=self.lineEdit_IP_Address.text(),
                            port=self.lineEdit_Port.text(), action=action)
            else:
                logic.firewall.add_rule(name=self.lineEdit_Name.text(), ip=self.lineEdit_IP_Address.text(),
                            port=self.lineEdit_Port.text(), action=action)
            self.done(1)
     
    def use_my_ip(self):
        self.lineEdit_IP_Address.setText(pebblehostAPI.my_public_ip)

class InfoBox(QDialog, MyCustomPyQt):

    def __init__(self, message:str):
        super().__init__()
        PyQt5.uic.loadUi(logic.resource_path(str(Path("Data") / "ui_template" / "info_box.ui")), self)
        
        #Esplicate some object in main_gui.ui
        self.label_Message:QLabel
        self.pushButton_OK:QPushButton

        #Post modify QWidget
        self.label_Message.setText(message)
        self.adjustSize()
        self.pushButton_OK.clicked.connect(self.ok_clicked)
    
    def ok_clicked(self):
        self.done(1)

class QWorker(QObject): 
    finished = pyqtSignal()
    def __init__(self, func):
        super().__init__()
        self.func = func
        
    def run(self):
        self.func()
        self.finished.emit()
