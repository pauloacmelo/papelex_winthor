from base import *

class Routine9805(WinthorRoutine):
    def __init__(self, *args):
        super(WinthorRoutine, self).__init__()
        self.initUI()

    def initUI(self):
        super(Routine9805, self).initUI()
        # but = QtGui.QButton('TEST', self)
        # self.mainwindow.addWidget(but)

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Routine9805(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
