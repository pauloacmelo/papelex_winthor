# coding: utf-8
from base import *
from PySide import QtGui, QtCore
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, date, timedelta


class Routine9814(WinthorRoutine):
    def __init__(self, *args):
        print(args)
        super(Routine9814, self).__init__(args[4] or 9814, u'Alertas da Telefonia', *args)
        self.initUI()
        self.initWorkers()

    def initWorkers(self):
        self.serverWorker = ServerWorker()
        self.serverWorker.logToScreen.connect(self.appendToServerLog)
        self.serverWorker.start()

    def initUI(self):
        super(Routine9814, self).initUI()
        self.serverLog = QtGui.QTextEdit(self)
        self.mainwindow.addWidget(self.serverLog)

    def appendToServerLog(self, message):
        self.serverLog.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')  + ': ' + message + '\n')
        cursor = self.serverLog.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.serverLog.setTextCursor(cursor)


class ServerWorker(QtCore.QThread):
    logToScreen = QtCore.Signal(str)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def makeCustomHandler(self, customPrint):
        class CustomHandler(BaseHTTPRequestHandler, object):
            def __init__(self, *args, **kwargs):
                self.customPrint = customPrint
                super(CustomHandler, self).__init__(*args, **kwargs)

            def do_GET(self):
                request_path = self.path
                self.customPrint("\n----- Request Start ----->\n")
                self.customPrint("Path: " + request_path)
                self.customPrint("Headers: %s" % self.headers)
                self.customPrint("<----- Request End -----\n")
                self.send_response(200)
                # self.send_header("Set-Cookie", "foo=bar")
                # self.end_headers()
                
            def do_POST(self):
                request_path = self.path
                self.customPrint("\n----- Request Start ----->\n")
                self.customPrint(request_path)
                request_headers = self.headers
                content_length = request_headers.getheaders('content-length')
                length = int(content_length[0]) if content_length else 0
                self.customPrint(request_headers)
                self.customPrint(self.rfile.read(length))
                self.customPrint("<----- Request End -----\n")
                self.send_response(200)

            do_PUT = do_POST
            do_DELETE = do_GET
        return CustomHandler

    def customPrint(self, message):
        
        print(message)

    def run(self):
        ip = '127.0.0.1'
        port = 81
        self.logToScreen.emit('Listening on http://127.0.0.1:%s' % port)
        def customPrint(x):
            self.logToScreen.emit(x)
            print(x)
        HandlerClass = self.makeCustomHandler(customPrint)
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
