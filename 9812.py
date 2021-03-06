# coding: utf-8
from base import *
from PySide import QtGui, QtCore
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
        # self.form = QFormLayout(self)
        self.orderLabel = QtGui.QLabel(self)
        self.orderLabel.setText('Pedido:')
        self.mainwindow.addWidget(self.orderLabel)
        self.orderInput = QtGui.QLineEdit(self)
        self.mainwindow.addWidget(self.orderInput)
        self.estimateLabel = QtGui.QLabel(self)
        self.estimateLabel.setText(u'Orçamento:')
        self.mainwindow.addWidget(self.estimateLabel)
        self.estimateInput = QtGui.QLineEdit(self)
        self.mainwindow.addWidget(self.estimateInput)
        but = QtGui.QPushButton('CALCULAR', self)
        but.clicked.connect(self.buttonAction)
        self.mainwindow.addWidget(but)
        self.table_view = QtGui.QTableView(self)
        self.header = [u'Transportadora', u'Preço', u'Cubagem', u'Prazo', u'Volumes']
        self.table_view.setModel(QTableModel(self, [[]], self.header))
        self.mainwindow.addWidget(self.table_view)

    def buttonAction(self):
        order_id = self.orderInput.text()
        estimate_id = self.estimateInput.text()
        if order_id and len(order_id) > 0:
            products = self.db.query("select PCPRODUT.PESOLIQ weight, PCPEDI.PVENDA cost_of_goods, PCPRODUT.LARGURAM3 width, PCPRODUT.ALTURAM3 height, PCPRODUT.COMPRIMENTOM3 length, PCPEDI.QT quantity, PCPRODUT.CODPROD sku_id, PCPRODUT.DESCRICAO description, 'true' can_group from PCPEDI, PCPRODUT where 1=1 and PCPEDI.CODPROD = PCPRODUT.CODPROD and NUMPED = %s" % order_id)
            products = [dict(p) for p in products]
            result = self.db.query("select regexp_replace(nvl(PCCLIENTENDENT.CEPENT, PCCLIENT.CEPENT), '[^0-9]', '') cep from PCPEDC inner join PCCLIENT on PCPEDC.CODCLI = PCCLIENT.CODCLI left join PCCLIENTENDENT on PCPEDC.CODCLI = PCCLIENTENDENT.CODCLI and PCPEDC.CODENDENTCLI = PCCLIENTENDENT.CODENDENTCLI where PCPEDC.NUMPED = %s" % order_id)
            volumes = self.db.query("select papelex_totalvolumes(%s) result from dual" % order_id)[0]['result']
            print(volumes)
            if len(result) == 0:
                QtGui.QMessageBox.critical(self,
                    "Erro!",
                    u"Preencha o número do pedido ou do orçamento.")
                return;
            cep = result[0]['cep']
            cep = cep[:5] + '-' + cep[-3:]
            quote = self.quotation(cep, products)
            result = [[row['description'], row['final_shipping_cost'], row['cubic_weight'], row['delivery_estimate_business_days'], volumes] for row in quote['content']['delivery_options']]
            self.updateTable(result)
        elif estimate_id and len(estimate_id) > 0:
            products = self.db.query("select PCPRODUT.PESOLIQ weight, PCORCAVENDAI.PVENDA cost_of_goods, PCPRODUT.LARGURAM3 width, PCPRODUT.ALTURAM3 height, PCPRODUT.COMPRIMENTOM3 length, PCORCAVENDAI.QT quantity, PCPRODUT.CODPROD sku_id, PCPRODUT.DESCRICAO description, 'true' can_group from PCORCAVENDAI, PCPRODUT where 1=1 and PCORCAVENDAI.CODPROD = PCPRODUT.CODPROD and NUMORCA = %s" % estimate_id)
            products = [dict(p) for p in products]
            result = self.db.query("select regexp_replace(nvl(PCCLIENTENDENT.CEPENT, PCCLIENT.CEPENT), '[^0-9]', '') cep from PCORCAVENDAC inner join PCCLIENT on PCORCAVENDAC.CODCLI = PCCLIENT.CODCLI left join PCCLIENTENDENT on PCORCAVENDAC.CODCLI = PCCLIENTENDENT.CODCLI and PCORCAVENDAC.CODENDENT = PCCLIENTENDENT.CODENDENTCLI where PCORCAVENDAC.NUMORCA = %s" % estimate_id)
            if len(result) == 0:
                QtGui.QMessageBox.critical(self,
                    "Erro!",
                    u"Preencha o número do pedido ou do orçamento.")
                return;
            cep = result[0]['cep']
            cep = cep[:5] + '-' + cep[-3:]
            quote = self.quotation(cep, products)
            result = [[row['description'], row['final_shipping_cost'], row['cubic_weight'], row['delivery_estimate_business_days'], 0] for row in quote['content']['delivery_options']]
            self.updateTable(result)
        else:
            QtGui.QMessageBox.critical(self,
                "Erro!",
                u"Preencha o número do pedido ou do orçamento.")

    def updateTable(self, data):
        self.table_view.setModel(QTableModel(self, data, self.header))

    # destination_zip_code example: '20756-200'
    # products example: [{"weight": 2.1,"cost_of_goods": 101.23,"width": 13,"height": 10,"length": 10,"quantity": 1,"sku_id": "1","description": "descrição do item","can_group": "true"}]
    def quotation(self, destination_zip_code, products):
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
        print data
        print json.dumps(data)
        req = urllib2.Request('https://api.intelipost.com.br/api/v1/quote_by_product', json.dumps(data))
        req.add_header('Content-Type', 'application/json')
        req.add_header('api_key', 'ca770671cccc21b75bea36130145f11e8ef92d4fcb186aff6e91bdb6cab20a26')
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
