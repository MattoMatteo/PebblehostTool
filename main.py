import sys
import PyQt5.QtWidgets
import MyUi

def main():
    
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    mainWindow = MyUi.MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())   

if __name__ == "__main__":
    main()

