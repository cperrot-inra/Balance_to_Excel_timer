#-------------------------------------------------------------------------------
# Name:        Interface Balances - Excel
# Author:      C. PERROT
# Created:     13/07/2016
# Version:     1.0
#-------------------------------------------------------------------------------

import threading, os, sys
import ConfigParser

import serial, time, re, datetime

import serial.tools.list_ports

import winsound

from PyQt4 import QtGui, QtCore
from Balances_UI import Ui_MainWindow
from Config_balances_UI import Ui_Dialog

import Config_port_COM

# Variables a renseigner
Config_file = 'Config_Balances.txt'

choix_balance = ""
sens_deplacement = "bas"
glob_txt_log = ""
status_port_com = False
ser_bal = serial.Serial()
auto_read = False
delay_auto_read = 10
command = ""

#############################
# Classe IHM
#############################

class Config_balances(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Config_balances, self).__init__(parent)
        # QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.connect(self.ui.BP_Ouvrir_gest_periph, QtCore.SIGNAL("clicked()"),self.BP_Ouvrir_gest_periph)
        self.connect(self.ui.BP_Suppr_balance, QtCore.SIGNAL("clicked()"),self.BP_Suppr_balance)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),self.BP_ok)

        # Remplissage Tab_param
        try:
            self.conf = ConfigParser.RawConfigParser()
            self.conf.read(Config_file)
        except : pass

        try:
            self.ui.Tab_param.clearContents()

            l = 0
            for sec in sorted(Liste_mat().keys()):
                item = QtGui.QTableWidgetItem()
                item.setText(sec)
                self.ui.Tab_param.setItem(l,0, item)
                self.ui.Tab_param.item(l,0).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)

                c = 1
                for val in Liste_mat()[sec]:
                    item = QtGui.QTableWidgetItem()
                    item.setText(val)
                    self.ui.Tab_param.setItem(l,c, item)
                    self.ui.Tab_param.item(l,c).setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
                    c += 1

                l += 1
        except:
            pass

    def BP_Ouvrir_gest_periph(self):
        os.system("devmgmt.msc")

    def BP_Suppr_balance(self):
        self.ligne = int(self.ui.Tab_param.currentRow())
        self.ui.Tab_param.removeRow(self.ui.Tab_param.currentRow())
        self.ui.Tab_param.selectRow(self.ligne)

    def BP_ok(self):
        try:
            with open(Config_file, "w"): pass

            self.conf = ConfigParser.RawConfigParser()
            self.conf.read(Config_file)

            for l in range(self.ui.Tab_param.rowCount()):

                try:
                    sec = str(self.ui.Tab_param.item(l,0).data(0).toString()).upper()
                    if sec != '' :

                        if not self.conf.has_section(sec) :
                            print sec
                            self.conf.add_section(sec)
                        for c in range(1,self.ui.Tab_param.columnCount()):
                            if c == 1 : opt = "port"
                            if c == 2 : opt = "baudrate"
                            if c == 3 : opt = "bytesize"
                            if c == 4 : opt = "parity"
                            if c == 5 : opt = "stopbits"
                            if c == 6 : opt = "timeout"
                            if c == 7 : opt = "xonxoff"
                            if c == 8 : opt = "rtscts"
                            if c == 9 : opt = "command"
                            try:
                                if not c == 9:
                                    val = str(self.ui.Tab_param.item(l,c).data(0).toString()).upper()
                                else:
                                    val = str(self.ui.Tab_param.item(l,c).data(0).toString())
                            except : val =''

                            try :
                                self.conf.set(sec,opt,val)
                                with open(os.path.join(os.path.abspath(os.curdir), Config_file),'wb') as configfile:
                                    self.conf.write(configfile)
                            except:
                                print 'Err;Ecriture [' + str(sec) + '] ' + str(opt) + str(val)
                except : pass
        except: pass


class App_IHM(QtGui.QMainWindow):

    def __init__( self, parent = None ):
        super(App_IHM, self).__init__(parent)

        try:
            QtGui.QMainWindow.__init__(self)
##            QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)

            # Configure l'interface utilisateur.
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            self.connect(self.ui.BP_Edit_fichier_config, QtCore.SIGNAL("clicked()"),self.BP_Edit_fichier_config)
            self.connect(self.ui.comboBox_balances, QtCore.SIGNAL("currentIndexChanged(const QString&)"),self.Choix_balance)
            self.connect(self.ui.comboBox_deplacement, QtCore.SIGNAL("currentIndexChanged(const QString&)"),self.Sens_deplacement)

            self.connect(self.ui.auto_read_check, QtCore.SIGNAL("clicked()"), self.auto_read_change)
            self.connect(self.ui.auto_read_start, QtCore.SIGNAL("clicked()"), self.start_stop_auto_read)
            self.connect(self.ui.auto_read_delay, QtCore.SIGNAL("textChanged()"), self.delay_changed)
            self.ui.auto_read_delay.setValidator(QtGui.QIntValidator(3, 6000))
            self.ui.comboBox_balances.setEditable(True)
            self.ui.comboBox_balances.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
            self.ui.comboBox_balances.lineEdit().setReadOnly(True)

            self.ui.comboBox_deplacement.setEditable(True)
            self.ui.comboBox_deplacement.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
            self.ui.comboBox_deplacement.lineEdit().setReadOnly(True)

            self.config()

            #############################
            # Declaration des threads
            #############################

            self.Th_log = ThreadLog()
            self.Th_Port_COM = ThreadPortCOM()
            self.Th_main = ThreadMain()

            self.Th_log.update_log.connect(self.Affich_log_IHM)
            self.Th_main.update_main.connect(self.Affich_log_IHM)
            self.Th_Port_COM.update_config.connect(self.config)

        except:
            print "Erreur classe App_IHM"

    def config(self):

        try:
            self.id_bal = self.ui.comboBox_balances.currentIndex()
            self.id_dep = self.ui.comboBox_deplacement.currentIndex()
        except: pass
        if self.id_bal < 0 : self.id_bal = 0
        if self.id_dep < 0 : self.id_dep = 0

        self.ui.comboBox_balances.blockSignals(True)
        self.ui.comboBox_balances.clear()
        for mat in sorted(Liste_mat().keys()):
            self.ui.comboBox_balances.addItem(mat)
        self.ui.comboBox_balances.blockSignals(False)

        self.ui.comboBox_balances.setCurrentIndex(self.id_bal)
        self.Choix_balance()

        self.ui.comboBox_deplacement.setCurrentIndex(self.id_dep)
        self.Sens_deplacement()

    def BP_Edit_fichier_config(self):
        self.config_bal = Config_balances()
        self.config_bal.show()

    def Choix_balance(self):
        global choix_balance
        choix_balance = self.ui.comboBox_balances.currentText()

    def Sens_deplacement(self):
        global sens_deplacement
        sens_deplacement = str(self.ui.comboBox_deplacement.currentText())

    def auto_read_change(self):
        status = self.ui.auto_read_check.isChecked()
        self.ui.auto_read_delay.setDisabled(not status)
        self.ui.auto_read_text.setDisabled(not status)
        self.ui.auto_read_start.setDisabled(not status)

    def start_stop_auto_read(self):
        global auto_read, delay_auto_read
        if int(self.ui.auto_read_delay.text()) < 3:
            self.ui.auto_read_delay.setText('3')
        delay_auto_read = int(self.ui.auto_read_delay.text())
        auto_read = not auto_read
        self.ui.auto_read_start.setText("stop" if auto_read else "start")
        self.ui.comboBox_balances.setDisabled(auto_read)

    def delay_changed(self):
        global delay_auto_read
        if int(self.ui.auto_read_delay.text()) < 3:
            self.ui.auto_read_delay.setText('3')
        delay_auto_read = int(self.ui.auto_read_delay.text())

    def Affich_log_IHM(self):
        global glob_txt_log
        try:
            self.ui.Affich_log.setText(glob_txt_log)
        except:
            pass

    def stop_thread(self):
        self.Th_Port_COM.stop()
        self.Th_log.stop()
        self.Th_main.stop()

    def closeEvent(self,event):
        try:
            result = QtGui.QMessageBox.question(self,"Confirmer...","Etes vous sur de vouloir quitter le programme ?",QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            event.ignore()

            if result == QtGui.QMessageBox.Yes:
                try: ser_bal.close()
                except : print 'Erreur close port COM'

                event.accept()
        except: pass


#############################
# Classes Thread
#############################

class ThreadLog(QtCore.QThread):
    update_log  = QtCore.pyqtSignal()

    def __init__(self,interval=0.1):
        QtCore.QThread.__init__(self)
        self.interval = interval
        self.running = False
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.interval)
            try:
                self.update_log.emit()

            except: print 'Err - ThreadLog.run'

    def stop(self):
        self.running = False


class ThreadPortCOM(QtCore.QThread):
    update_config = QtCore.pyqtSignal()

    def __init__(self, interval=0.1):
        QtCore.QThread.__init__(self)
        self.interval = interval
        self.running = False
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        global ser_bal, status_port_com, choix_balance, command

        self.bal_pre = choix_balance
        self.d_mat_pre = {}
        cpt_status_port_bal = 0

        def init_port_com(ser, port, txt_port, bal_command, status_port=False):
            try:
                if self.bal_pre != choix_balance:
                    try :
                        ser_bal.close()
                    except : pass
                    self.bal_pre = choix_balance
                    raise

                self.d_mat = Liste_mat()
                if self.d_mat_pre != self.d_mat:
                    self.d_mat_pre = self.d_mat
                    self.update_config.emit()
                    raise

                if not ser.isOpen(): raise
                for i in list(serial.tools.list_ports.comports()):
                    if port in i :
                        status_port = True
                if status_port == False : raise
            except:
                try:
                    ser, bal_command, msg_erreur = Config_port_COM.open_port_COM(Config_file,txt_port)
                    if msg_erreur != '':
                        try:
                            if choix_balance != '' : w_log(msg_erreur)
                        except: print msg_erreur
                    if ser != None:
                        status_port = True
                except:
                    try:
                        if choix_balance != '' : w_log('Erreur Port ' + txt_port)
                    except:
                        print 'Err;ThreadPortCOM.run'

            return ser, status_port, txt_port, port, bal_command

        self.running = True
        while self.running:

            try:
                port_bal = 'COMx'
                #------- Config Port COM -------
                port_bal = Liste_mat().get(str(choix_balance))[0]
            except: pass

            # Balance
            ser_bal, status_port_bal, txt_port, port, command = init_port_com(ser_bal, port_bal, str(choix_balance), command)
            if status_port_bal : cpt_status_port_bal += 1
            else : cpt_status_port_bal -= 1
            if cpt_status_port_bal > 1 : cpt_status_port_bal = 2
            if cpt_status_port_bal < 0 : cpt_status_port_bal = 0
            if cpt_status_port_bal == 1 :
                try:
                    ser_bal.flush()
                    w_log(txt_port.upper() + ' initialise sur port ' + port)
                except:
                    print 'Port balance intialise'
            if cpt_status_port_bal == 0 :
                try:
                    if choix_balance != '' : w_log('Pb ouverture port ' + port_bal)
                    else : w_log('Aucune balance')
                except:
                    print 'Err;ThreadPortCOM.run;Pb ouverture port balance'

            status_port_com = status_port_bal
            time.sleep(self.interval)

    def stop(self):
        self.running = False


class ThreadMain(QtCore.QThread):
    update_main = QtCore.pyqtSignal()

    def __init__(self, interval=0.1):
        QtCore.QThread.__init__(self)
        self.interval = interval
        time.sleep(self.interval)
        self.running = False
        self.begin_delay = 0
        self.last_weight_txt = ""
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):

        global ser_bal, status_port_com, sens_deplacement, \
            auto_read, delay_auto_read, command

        from Excel import Excel_write_relatif
        self.running = True
        while self.running:
            try:
                if status_port_com :
                    try:
                        rp = ""
                        if auto_read:
                            # print self.begin_delay
                            w_log(self.last_weight_txt + " (" +
                                  str(delay_auto_read -
                                      int((time.time() - self.begin_delay))) + "s)")
                            if time.time() - self.begin_delay >= delay_auto_read:
                                # self.begin_delay += delay_auto_read
                                self.begin_delay = time.time()
                                ser_bal.reset_input_buffer()
                                ser_bal.write(command.decode('string_escape'))
                                rp = ser_bal.readline()
                            self.update_main.emit()
                        else:
                            rp = ser_bal.readline()


                        if rp != "":
                            print 'rp ', rp
                            try:
                                signe = ''
                                if '-' in rp : signe = '-'
                                valeur = re.findall(r"\d*\.\d+|\d+",rp)
                                data = signe + valeur[0]
                                signe = valeur = ""
                                datetext = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print datetext + "\t" + str(data)

                            except:
                                self.last_weight_txt = "Erreur '" + data + \
                                                       "' depuis la balance"
                                winsound.PlaySound('SystemHand', winsound.SND_ALIAS)

                            try:
                                flag_excel, address_cell = Excel_write_relatif(data,sens_deplacement,IHM.ui.Save_continu.isChecked(),IHM.ui.Del_cell.isChecked(), auto_read)
                                print flag_excel
                                if flag_excel : raise
                                self.last_weight_txt = address_cell.replace('$','') + ' : ' + rp.replace('\n','')
                                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
                            except :
                                self.last_weight_txt = "Erreur transfert '" + \
                                                       data + "' vers  Excel"
                                winsound.PlaySound('SystemHand', winsound.SND_ALIAS)
                            if auto_read:
                                w_log(self.last_weight_txt + " (" +
                                      str(delay_auto_read - int((time.time() - self.begin_delay))) + "s)")
                            else:
                                w_log(self.last_weight_txt)
                            self.update_main.emit()

                    except:
                        print 'Err;ThreadMain.run'
            except: pass
            time.sleep(self.interval)
            # IHM.show()

    def stop(self):
        self.running = False


#Liste materiels fichiers de config
def Liste_mat():
    d_mat = {}
    try:
        fic = open(Config_file,'r')
        conf = ConfigParser.RawConfigParser()
        conf.read(Config_file)
        try:
            for sec in conf.sections():
                opt_mat = []
                for opt in conf.options(sec):
                    opt_mat.append(conf.get(sec,opt))
                d_mat[sec] = opt_mat
        except:
            w_log("Aucun materiel dans le fichier de config")
    except:
        w_log("Erreur Lecture fichier " +  Config_file)

    return d_mat


def w_log(txt_log):
    global glob_txt_log
    glob_txt_log = txt_log


def main():
    IHM.show()
    a = app.exec_()
    IHM.stop_thread()
    sys.exit(a)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    IHM = App_IHM()
    main()
