import sys
import PyQt5.QtWidgets
import MyUi
import pebblehostAPI
import logic

def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    if not pebblehostAPI.check_internet():
        infobox_credentialError = MyUi.InfoBox(message = "Unable to connect. Please check your internet connection and try again")
        infobox_credentialError.show()
    elif not pebblehostAPI.test_credentials():
        infobox_credentialError = MyUi.InfoBox(message = "Wrong API key or Server ID")
        infobox_credentialError.show()
    else:
        logic.firewall.import_firewall_data()
        mainWindow = MyUi.MainWindow()
        mainWindow.show()

    sys.exit(app.exec_())   

if __name__ == "__main__":
    main()

