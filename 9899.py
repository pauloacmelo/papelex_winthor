# coding: utf-8
from base import *
from PySide import QtGui, QtCore
import cx_Oracle

class Routine9899(WinthorRoutine):
    def __init__(self, *args):
        super(WinthorRoutine, self).__init__()
        self.initUI()

    def get_all_users(self):
        conn = cx_Oracle.connect("papelex", "FG2hu3DV4T", "WINT")
        cur = conn.cursor()
        cur.execute('select MATRICULA, NOME from PCEMPR')
        header = [desc[0] for desc in cur.description]
        data = [[e.encode('utf-8') if isinstance(e, basestring) else e for e in row] for row in cur]
        cur.close()
        conn.close()
        return header, data


    def initUI(self):
        super(Routine9899, self).initUI()
        # saself.form = QFormLayout(self)
        textInput = QtGui.QLineEdit(self)
        self.mainwindow.addWidget(textInput)
        combo = QtGui.QComboBox(self)
        self.mainwindow.addWidget(combo)
        combo.addItem(u'Opção 1', combo)
        combo.addItem(u'Opção 2', combo)
        but = QtGui.QPushButton('TEST', self)
        self.mainwindow.addWidget(but)
        table_view = QtGui.QTableView(self)
        # header = ['Column 1', 'Column 2', 'Column 3']
        # data = [
        #     ['1, 1', '1, 2', '1, 3'],
        #     ['2, 1', '2, 2', '2, 3'],
        #     ['3, 1', '3, 2', '3, 3'],]
        header, data = self.get_all_users()
        table_view.setModel(QTableModel(self, data, header))
        self.mainwindow.addWidget(table_view)
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Routine9899(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
