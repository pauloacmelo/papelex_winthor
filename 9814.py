# coding: utf-8
from base import *
from PySide import QtGui, QtCore
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, date, timedelta
import random
import subprocess
import re

# -- Query to create log table
# create table PAPELEX_LOG_LIGACOES (
#   NOME_GUERRA VARCHAR(30) NOT NULL,
#   DATAHORA TIMESTAMP,
#   TELEFONE VARCHAR(30),
#   CODCLI NUMBER(10),
#   CLIENTE VARCHAR(100)
# );

class Routine9814(WinthorRoutine):
    def __init__(self, *args):
        print(args)
        super(Routine9814, self).__init__(args[4] or 9814, u'Alertas de Telefonia', *args)
        self.initUI()
        self.initWorkers()
        self.loadCallHistory()

    def initUI(self):
        super(Routine9814, self).initUI()
        self.searchClientNameLineEdit = QtGui.QLineEdit()
        self.searchClientNameLabel = QtGui.QLabel("Nome Cliente:")
        self.searchClientNameLineEdit.returnPressed.connect(self.search)
        self.searchClientIDLineEdit = QtGui.QLineEdit()
        self.searchClientIDLabel = QtGui.QLabel(u"Cód. Cliente:")
        self.searchClientIDLineEdit.returnPressed.connect(self.search)
        self.searchClientPhoneLineEdit = QtGui.QLineEdit()
        self.searchClientPhoneLabel = QtGui.QLabel("Telefone:")
        self.searchClientPhoneLineEdit.returnPressed.connect(self.search)
        self.searchSubmitButton = QtGui.QPushButton('Pesquisar', self)
        self.searchSubmitButton.clicked.connect(self.search)
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
        self.callLogsProxyModel = CustomSortFilterProxyModel()
        self.callLogsProxyModel.setDynamicSortFilter(True)
        self.callLogsProxyModel.addFilterFunction(
            lambda row, filterStrings: not not re.search(filterStrings[0].lower().replace('%', '.*'), row[1].lower()) if len(filterStrings) > 0 and len(row) > 1 else True)
        self.callLogsProxyModel.addFilterFunction(
            lambda row, filterStrings: not not re.search(filterStrings[1].lower().replace('%', '.*'), row[2].lower()) if len(filterStrings) > 1 and len(row) > 2 else True)
        self.callLogsProxyModel.addFilterFunction(
            lambda row, filterStrings: not not re.search(filterStrings[2].lower().replace('%', '.*'), row[3].lower()) if len(filterStrings) > 2 and len(row) > 3 else True)
        self.mainwindow.addWidget(self.callLogsTreeView)
        self.dataModel = QtGui.QStandardItemModel(0, 4, self.mainwindow)
        self.dataModel.setHeaderData(0, QtCore.Qt.Horizontal, u"Data/Hora")
        self.dataModel.setHeaderData(1, QtCore.Qt.Horizontal, u"Cód. Cliente")
        self.dataModel.setHeaderData(2, QtCore.Qt.Horizontal, u"Telefone")
        self.dataModel.setHeaderData(3, QtCore.Qt.Horizontal, u"Cliente")
        self.callLogsProxyModel.setSourceModel(self.dataModel)
        self.callLogsTreeView.setModel(self.callLogsProxyModel)
        self.callLogsTreeView.sortByColumn(0, QtCore.Qt.DescendingOrder)
    
    def initWorkers(self):
        self.serverWorker = ServerWorker()
        self.serverWorker.logToScreen.connect(self.appendToServerLog)
        self.serverWorker.start()
        self.openSalesRoutineThreads = []

    def loadCallHistory(self):
        try:
            logs = self.db.query('''
                select DATAHORA, CODCLI, TELEFONE, CLIENTE
                from PAPELEX_LOG_LIGACOES
                where DATAHORA > trunc(sysdate) - 7
            ''')
            for index, log in enumerate(logs):
                self.dataModel.insertRow(index)
                self.dataModel.setData(self.dataModel.index(index, 0), log['datahora'].strftime('%Y-%m-%d %H:%M:%S'))
                self.dataModel.setData(self.dataModel.index(index, 1), log['codcli'])
                self.dataModel.setData(self.dataModel.index(index, 2), self.formatPhoneNumber(log['telefone']))
                self.dataModel.setData(self.dataModel.index(index, 3), log['cliente'])
        except Exception as e:
            ErrorMessage("Erro!",
                u"Ligação recebida de %s.\nErro ao conectar no banco de dados para buscar informações." % self.formatPhoneNumber(completePhoneNumber))

    def closeEvent(self, event):
        super(Routine9814, self).closeEvent(event)
        self.serverWorker.terminate()
        for openSalethread in self.openSalesRoutineThreads:
            openSalethread.terminate()
        event.accept()

    def search(self):
        self.callLogsProxyModel.setFilterStrings(
            self.searchClientIDLineEdit.text(),
            self.searchClientPhoneLineEdit.text(),
            self.searchClientNameLineEdit.text())

    def formatPhoneNumber(self, phone):
        if len(phone) <= 4:
            return phone
        return '(%s) %s-%s' % (phone[:3], phone[3:-4], phone[-4:])

    def appendToServerLog(self, completePhoneNumber):
        try:
            if len(completePhoneNumber) <= 4:
                phoneNumber = completePhoneNumber
                clients = self.db.query('''
                    select '' CODCLI, NOME CLIENTE
                    from PCEMPR
                    where regexp_replace(FONE, '[^0-9]', '') = :tel
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
            self.dataModel.setData(self.dataModel.index(0, 0), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.dataModel.setData(self.dataModel.index(0, 1), clients[index]['codcli'])
            self.dataModel.setData(self.dataModel.index(0, 2), self.formatPhoneNumber(completePhoneNumber))
            self.dataModel.setData(self.dataModel.index(0, 3), clients[index]['cliente'])
            self.toast(
                self.formatPhoneNumber(completePhoneNumber),
                u'%s%s%s' % (clients[index]['codcli'] or '',' - ' if clients[index]['codcli'] else '', clients[index]['cliente']) if clients[index]['cliente'] else u'Número desconhecido')
        except Exception as e:
            print e
            ErrorMessage("Erro!",
                u"Ligação recebida de %s.\nErro ao conectar no banco de dados para buscar informações." % self.formatPhoneNumber(completePhoneNumber))
        try:
            self.db.execute('''
                insert into PAPELEX_LOG_LIGACOES (NOME_GUERRA, DATAHORA, TELEFONE, CODCLI, CLIENTE)
                values (:routineuser, sysdate, :tel, :clientid, :clientname)
            ''', routineuser=self.username, tel=completePhoneNumber, clientid=clients[index]['codcli'], clientname=clients[index]['cliente'])
        except Exception as e:
            print e
            ErrorMessage("Erro!",
                u"Ligação recebida de %s.\nErro ao conectar no banco de dados para salvar informações." % self.formatPhoneNumber(completePhoneNumber))

    def openCustomer(self):
        model = self.callLogsTreeView.model().sourceModel()
        filteredIndex = self.callLogsTreeView.selectedIndexes()[0]
        row_num = self.callLogsProxyModel.mapToSource(filteredIndex).row()
        selectedId = model.item(row_num,1).text() if model.item(row_num,1) is not None else ''
        print 'Opening sales routine for client #%s.' % selectedId
        if not selectedId or selectedId == '':
            return
        worker = OpenSalesRoutineWorker(
            selectedId, self.username, self.db_pass, self.db_alias, self.db_user)
        worker.reportError.connect(self.reportSalesRoutineError)
        worker.start()
        self.openSalesRoutineThreads.append(worker)
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(selectedId, mode=cb.Clipboard)

    def reportSalesRoutineError(self):
        ErrorMessage('Erro!', u"Não foi possível abrir a rotina 1906.\n"+
            u"Verifique se o Drive W:/ está mapeado em seu computador.")


class OpenSalesRoutineWorker(QtCore.QThread):
    reportError = QtCore.Signal()

    def __init__(self, selectedId, username, db_pass, db_alias, db_user):
        self.selectedId = selectedId
        self.username = username
        self.db_pass = db_pass
        self.db_alias = db_alias
        self.db_user = db_user
        QtCore.QThread.__init__(self)

    def run(self):
        args = [
            'W:\PCPPL\PCPPL1906.exe',
            self.username,
            self.db_pass,
            self.db_alias,
            self.db_user, '1906']
        try:
            subprocess.call(args)
        except Exception as e:
            self.reportError.emit()


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
            if x not in ['favicon.ico']:
                self.logToScreen.emit(x)
        HandlerClass = self.makeCustomHandler(logCall)
        server = HTTPServer((ip, port), HandlerClass)
        server.serve_forever()


# Available at https://gist.githubusercontent.com/dbridges/4732790/raw/5ee0b3825435c8f98cc47519cc1ab8cc3db7d2a7/CustomSortFilterProxyModel.py
# Explanation at http://www.dayofthenewdan.com/2013/02/09/Qt_QSortFilterProxyModel.html
class CustomSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CustomSortFilterProxyModel, self).__init__(parent)
        self.filterStrings = []
        self.filterFunctions = [] 

    def setFilterStrings(self, *texts):
        self.filterStrings = texts
        self.invalidateFilter()

    def addFilterFunction(self, new_func):
        self.filterFunctions.append(new_func)
        self.invalidateFilter()

    def filterAcceptsRow(self, row_num, parent):
        model = self.sourceModel()
        row = [model.item(row_num,c).text() for c in xrange(model.columnCount()) if model.item(row_num,c) is not None]
        tests = [func(row, self.filterStrings)
                 for func in self.filterFunctions]
        return not False in tests

class ErrorMessage(QtGui.QWidget):
    def __init__(self, title, message):
        QtGui.QWidget.__init__(self)
        QtGui.QMessageBox.critical(self, title, message)
        self.close()


# Expected call: routine.exe USER DB_PASS DB_ALIAS DB_USER ROUTINE_NUMBER
def main(args):
    app = QtGui.QApplication([])
    if len(args) != 6:
        print('Erro! Número de parâmetros diferente do esperado.')
        print('Esperado: 6. Encontrado: %s' % len(args))
        ErrorMessage("Erro!", "Utilize a rotina a partir do menu.")
        return
    args = args[1:]
    ex = Routine9814(*args)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
