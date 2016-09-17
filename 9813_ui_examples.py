# coding: utf-8
from base import *
from PySide import QtGui, QtCore
import requests
import json
import urllib2

class Routine9812(WinthorRoutine):
    def __init__(self, *args):
        # super(WinthorRoutine, self).__init__('TESTE')
        print(args)
        super(Routine9812, self).__init__(args[4] or 9812, u'Cálculo de Frete', *args)
        self.initUI()

    def initUI(self):
        super(Routine9812, self).initUI()
        # saself.form = QFormLayout(self)
        textInput = QtGui.QLineEdit(self)
        self.mainwindow.addWidget(textInput)
        combo = QtGui.QComboBox(self)
        self.mainwindow.addWidget(combo)
        combo.addItem(u'Opção 1', combo)
        combo.addItem(u'Opção 2', combo)
        but = QtGui.QPushButton('TEST', self)
        but.clicked.connect(self.buttonAction)
        self.mainwindow.addWidget(but)
        table_view = QtGui.QTableView(self)
        header = [u'Transportadora', u'Preço', u'Cubagem', u'Prazo']
        data = [
            ['1, 1', '1, 2', '1, 3'],
            ['2, 1', '2, 2', '2, 3'],
            ['3, 1', '3, 2', '3, 3'],]
        table_view.setModel(QTableModel(self, data, header))
        self.mainwindow.addWidget(table_view)

    def buttonAction(self):
        print self.db.query('select CODPROD from PCPEDI where NUMPED = %s' % 224010951)

    def quote_order_shipping(order_id):
        self.quotation()

    # destination_zip_code example: '20756-200'
    # products example: [{"weight": 2.1,"cost_of_goods": 101.23,"width": 13,"height": 10,"length": 10,"quantity": 1,"sku_id": "1","description": "descrição do item","can_group": "true"}]
    def quotation(destination_zip_code, products):
        data = {
          "origin_zip_code": "21010-410",
          "destination_zip_code": destination_zip_code,
          "products": products,
          "quoting_mode": "DYNAMIC_BOX_ALL_ITEMS",
          "additional_information": {
            "free_shipping": False,
            "extra_cost_absolute": 0,
            "extra_cost_percentage": 0,
            "lead_time_business_days": 0,
            "sales_channel": "hotsite",
            "tax_id": "22337462000127",
            "client_type": "gold",
            "payment_type": "",
            "is_state_tax_payer": False,
            "delivery_method_ids": []
          },
          "identification": {
            "session": "04e5bdf7ed15e571c0265c18333b6fdf1434658753",
            "page_name": "carrinho",
            "ip": "000.000.000.000",
            "url": "http://www.intelipost.com.br/checkout/cart/"
          }
        }
        req = urllib2.Request('https://api.intelipost.com.br/api/v1/quote_by_product', json.dumps(data))
        req.add_header('Content-Type', 'application/json')
        req.add_header('api_key', '36a3fa0d4108231864a60988a15272b9fd692c3320206ceb3e85e61688e11d79')
        res = urllib2.urlopen(req)
        return json.loads(res.read())



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
    ex = Routine9812(*args)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
