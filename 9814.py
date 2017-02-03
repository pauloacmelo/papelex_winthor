# coding: utf-8
from base import *
from PySide import QtGui, QtCore
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, date, timedelta
import random
import subprocess

class Routine9814(WinthorRoutine):
    def __init__(self, *args):
        print(args)
        super(Routine9814, self).__init__(args[4] or 9814, u'Alertas de Telefonia', *args)
        self.initUI()
        self.initWorkers()

    def initUI(self):
        super(Routine9814, self).initUI()
        self.searchClientNameLineEdit = QtGui.QLineEdit()
        self.searchClientNameLabel = QtGui.QLabel("Nome Cliente:")
        self.searchClientIDLineEdit = QtGui.QLineEdit()
        self.searchClientIDLabel = QtGui.QLabel(u"Cód. Cliente:")
        self.searchClientPhoneLineEdit = QtGui.QLineEdit()
        self.searchClientPhoneLabel = QtGui.QLabel("Telefone:")
        self.searchSubmitButton = QtGui.QPushButton('Pesquisar', self)
        self.searchLayout = QtGui.QGridLayout()
        self.searchLayout.addWidget(self.searchClientNameLabel, 0, 0)
        self.searchLayout.addWidget(self.searchClientNameLineEdit, 0, 1, 1, 4)
        self.searchLayout.addWidget(self.searchClientPhoneLabel, 1, 0)
        self.searchLayout.addWidget(self.searchClientPhoneLineEdit, 1, 1)
        self.searchLayout.addWidget(self.searchClientIDLabel, 1, 2)
        self.searchLayout.addWidget(self.searchClientIDLineEdit, 1, 3, 1, 2)
        self.searchLayout.addWidget(self.searchSubmitButton, 2, 4)
        self.searchGroupBox = QtGui.QGroupBox("Busca")
        self.searchGroupBox.setLayout(self.searchLayout)
        self.mainwindow.addWidget(self.searchGroupBox)
        self.callLogsTreeView = MyTreeView()
        self.callLogsTreeView.setRootIsDecorated(False)
        self.callLogsTreeView.setAlternatingRowColors(True)
        self.callLogsTreeView.setSortingEnabled(True)
        self.callLogsTreeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.callLogsTreeView.doubleClicked.connect(self.openCustomer)
        self.callLogsTreeView.onPressEnter.connect(self.openCustomer)
        self.mainwindow.addWidget(self.callLogsTreeView)
        self.dataModel = QtGui.QStandardItemModel(0, 4, self.mainwindow)
        self.dataModel.setHeaderData(0, QtCore.Qt.Horizontal, u"Data/Hora")
        self.dataModel.setHeaderData(1, QtCore.Qt.Horizontal, u"Cód. Cliente")
        self.dataModel.setHeaderData(2, QtCore.Qt.Horizontal, u"Telefone")
        self.dataModel.setHeaderData(3, QtCore.Qt.Horizontal, u"Cliente")
        # for i in range(5):
        #     self.dataModel.insertRow(i)
        #     self.dataModel.setData(self.dataModel.index(i, 0), '31/01/2017 12:34:56')
        #     self.dataModel.setData(self.dataModel.index(i, 1), str(random.randint(1, 100000)))
        #     self.dataModel.setData(self.dataModel.index(i, 2), '(21) 2234-5678')
        #     self.dataModel.setData(self.dataModel.index(i, 3), u'FUNDAÇÂO BENÇÃOS DO SENHOR')
        # self.dataModel.insertRow(5)
        # self.dataModel.setData(self.dataModel.index(i, 0), '31/01/2017 12:34:55')
        # self.dataModel.setData(self.dataModel.index(i, 1), None)
        # self.dataModel.setData(self.dataModel.index(i, 2), '(21) 2234-5678')
        # self.dataModel.setData(self.dataModel.index(i, 3), None)
        self.callLogsTreeView.setModel(self.dataModel)
        self.callLogsTreeView.sortByColumn(0, QtCore.Qt.DescendingOrder)

    def formatPhoneNumber(self, phone):
        if len(phone) <= 4:
            return phone
        return '(%s) %s-%s' % (phone[:3], phone[3:-4], phone[-4:])

    def appendToServerLog(self, completePhoneNumber):
        if len(completePhoneNumber) <= 4:
            phoneNumber = completePhoneNumber
            clients = self.db.query('''
                select '' CODCLI, NOME CLIENTE
                from PCEMPR
                where regexp_replace(RAMAL, '[^0-9]', '') = :tel
                union all
                select null, null from dual
                order by CODCLI desc, CLIENTE desc
            ''', tel=completePhoneNumber)
        else:
            phoneNumber = completePhoneNumber[3:]
            clients = self.db.query('''
                select
                  CODCLI, CLIENTE
                from PCCLIENT
                where
                  regexp_replace(TELCONJUGE, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELEMPR, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELCOM, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELENT1, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELENT, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELCOB, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELCELENT, '[^0-9]', '') like '%' || :tel
                union all
                select
                  CODCLI, CLIENTE
                from PCCLIENTFV
                where
                  regexp_replace(TELENT1, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELCOM, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELCOB, '[^0-9]', '') like '%' || :tel or
                  regexp_replace(TELENT, '[^0-9]', '') like '%' || :tel
                union all
                select
                  PCCLIENT.CODCLI, PCCLIENT.CLIENTE
                from PCCONTATO
                left join PCCLIENT on PCCLIENT.CODCLI = PCCONTATO.CODCLI
                where regexp_replace(TELEFONE, '[^0-9]', '') like '%' || :tel
                union all
                select null, null from dual
                order by CODCLI desc, CLIENTE desc
            ''', tel=phoneNumber)
        index = min(len(clients)-1, 1)
        self.dataModel.insertRow(0)
        self.dataModel.setData(self.dataModel.index(0, 0), datetime.now().strftime('%d/%m/%Y %H:%M'))
        self.dataModel.setData(self.dataModel.index(0, 1), clients[index]['codcli'])
        self.dataModel.setData(self.dataModel.index(0, 2), self.formatPhoneNumber(completePhoneNumber))
        self.dataModel.setData(self.dataModel.index(0, 3), clients[index]['cliente'])
        self.toast(
            self.formatPhoneNumber(completePhoneNumber),
            u'%s%s%s' % (clients[index]['codcli'] or '',' - ' if clients[index]['codcli'] else '', clients[index]['cliente']) if clients[index]['cliente'] else u'Número desconhecido')

    def initWorkers(self):
        self.serverWorker = ServerWorker()
        self.serverWorker.logToScreen.connect(self.appendToServerLog)
        self.serverWorker.start()

    def openCustomer(self):
        index = self.callLogsTreeView.selectedIndexes()[0]
        selectedId = index.model().itemFromIndex(index.sibling(index.row(), 1)).text()
        if not selectedId or selectedId == '':
            return
        OpenSalesRoutineWorker(selectedId, self.username, self.db_pass, self.db_alias, self.db_user)


class OpenSalesRoutineWorker(QtCore.QThread):
    def __init__(self, selectedId, username, db_pass, db_alias, db_user):
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(selectedId, mode=cb.Clipboard)
        args = ['W:\PCPPL\PCPPL1906.exe', username, db_pass, db_alias, db_user, '1906']
        subprocess.call(args)


class MyTreeView(QtGui.QTreeView):
    onPressEnter = QtCore.Signal()

    def __init__(self):
        QtGui.QTreeView.__init__(self)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.onPressEnter.emit()
        QtGui.QTreeView.keyPressEvent(self, event)


class ServerWorker(QtCore.QThread):
    logToScreen = QtCore.Signal(str)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def makeCustomHandler(self, logCall):
        class CustomHandler(BaseHTTPRequestHandler, object):
            def __init__(self, *args, **kwargs):
                self.logCall = logCall
                super(CustomHandler, self).__init__(*args, **kwargs)

            def do_GET(self):
                self.logCall(self.path[1:])
                self.send_response(200)
                
            def do_POST(self):
                pass

            do_PUT = do_POST
            do_DELETE = do_GET
        return CustomHandler

    def run(self):
        ip = '127.0.0.1'
        port = 8001
        def logCall(x):
            self.logToScreen.emit(x)
        HandlerClass = self.makeCustomHandler(logCall)
        server = HTTPServer((ip, port), HandlerClass)
        server.serve_forever()


class ErrorMessage(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        QtGui.QMessageBox.critical(self,
            "Erro!",
            "Utilize a rotina a partir do menu.")
        self.close()


# Expected call: routine.exe USER DB_PASS DB_ALIAS DB_USER ROUTINE_NUMBER
def main(args):
    app = QtGui.QApplication([])
    if len(args) != 6:
        print('Erro! Número de parâmetros diferente do esperado.')
        print('Esperado: 6. Encontrado: %s' % len(args))
        ErrorMessage()
        return
    args = args[1:]
    ex = Routine9814(*args)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
