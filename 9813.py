# coding: utf-8
from base import *
from PySide import QtGui, QtCore
import time
import requests
import xmltodict
import xml.etree.ElementTree as ET
import math
import json
from datetime import datetime, date, timedelta
from collections import OrderedDict
from magento import Magento
import traceback


class Routine9813(WinthorRoutine):
    def __init__(self, *args):
        # super(WinthorRoutine, self).__init__('TESTE')
        print(args)
        super(Routine9813, self).__init__(args[4] or 9813, u'Integração e-commerce', *args)
        self.initUI()
        self.initWorkers()

    def initWorkers(self):
        self.priceWorker = PriceWorker()
        self.priceWorker.updateProgress.connect(self.setPriceProgress)
        self.priceWorker.start()
        self.stockWorker = StockWorker()
        self.stockWorker.updateProgress.connect(self.setStockProgress)
        self.stockWorker.start()
        self.ordersWorker = OrdersWorker()
        self.ordersWorker.updateProgress.connect(self.setOrdersProgress)
        self.ordersWorker.start()

    def initUI(self):
        super(Routine9813, self).initUI()
        self.tabControl = QtGui.QTabWidget(self)
        self.mainwindow.addWidget(self.tabControl)
        self.priceTab = QtGui.QWidget()
        self.stockTab = QtGui.QWidget()
        self.ordersTab = QtGui.QWidget()
        self.tabControl.addTab(self.priceTab,u"Preço")
        self.tabControl.addTab(self.stockTab,u"Estoque")
        self.tabControl.addTab(self.ordersTab,u"Pedidos")
        self.priceTabUI()
        self.stockTabUI()
        self.ordersTabUI()
          
    def priceTabUI(self):
        self.priceProgressBar = QtGui.QProgressBar(self)
        self.priceProgressBar.setGeometry(QtCore.QRect(20, 10, 361, 23))
        self.priceProgressBar.setProperty("value", 24)
        self.priceProgressBar.setObjectName("priceProgressBar")
        self.priceLog = QtGui.QTextEdit(self)
        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Progresso:"))
        row.addWidget(self.priceProgressBar)
        self.priceStopButton = QtGui.QPushButton('Parar', self)
        self.priceStopButton.setEnabled(False)
        self.priceStopButton.clicked.connect(self.togglePriceWorker)
        self.priceRestartButton = QtGui.QPushButton('Reiniciar', self)
        self.priceRestartButton.setEnabled(False)
        self.priceRestartButton.clicked.connect(self.resetPriceWorker)
        buttonRow = QtGui.QHBoxLayout()
        buttonRow.addStretch(1)
        buttonRow.addWidget(self.priceStopButton)
        buttonRow.addWidget(self.priceRestartButton)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(row)
        layout.addWidget(self.priceLog)
        layout.addLayout(buttonRow)
        self.priceTab.setLayout(layout)

    def stockTabUI(self):
        self.stockProgressBar = QtGui.QProgressBar(self)
        self.stockProgressBar.setGeometry(QtCore.QRect(20, 10, 361, 23))
        self.stockProgressBar.setProperty("value", 24)
        self.stockProgressBar.setObjectName("stockProgressBar")
        self.stockLog = QtGui.QTextEdit(self)
        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Progresso:"))
        row.addWidget(self.stockProgressBar)
        self.stockStopButton = QtGui.QPushButton('Parar', self)
        self.stockStopButton.setEnabled(False)
        self.stockStopButton.clicked.connect(self.toggleStockWorker)
        self.stockRestartButton = QtGui.QPushButton('Reiniciar', self)
        self.stockRestartButton.setEnabled(False)
        self.stockRestartButton.clicked.connect(self.resetStockWorker)
        buttonRow = QtGui.QHBoxLayout()
        buttonRow.addStretch(1)
        buttonRow.addWidget(self.stockStopButton)
        buttonRow.addWidget(self.stockRestartButton)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(row)
        layout.addWidget(self.stockLog)
        layout.addLayout(buttonRow)
        self.stockTab.setLayout(layout)
          
    def ordersTabUI(self):
        self.ordersProgressBar = QtGui.QProgressBar(self)
        self.ordersProgressBar.setGeometry(QtCore.QRect(20, 10, 361, 23))
        self.ordersProgressBar.setProperty("value", 24)
        self.ordersProgressBar.setObjectName("ordersProgressBar")
        self.ordersHeader = [u'Integração', u'Num. pedido', u'Comprado Em', u'Status', u'Cliente', u'CPF/CNPJ', u'Items', u'Total', u'CEP']
        self.ordersTable = QtGui.QTableView(self)
        self.ordersTable.setModel(QTableModel(self, [[]], self.ordersHeader))
        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Progresso:"))
        row.addWidget(self.ordersProgressBar)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(row)
        layout.addWidget(self.ordersTable)
        self.ordersTab.setLayout(layout)

    def setPriceProgress(self, progress, log):
        self.priceProgressBar.setValue(progress)
        self.priceLog.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')  + ': ' + log)
        cursor = self.priceLog.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.priceLog.setTextCursor(cursor)

    def togglePriceWorker(self):
        self.priceWorker.toggle()
        if self.priceWorker.isRunning:
            self.tabControl.setTabText(0, u'Preço')
            self.priceStopButton.setText('Parar')
        else:
            self.tabControl.setTabText(0, u'Preço (parado)')
            self.priceStopButton.setText('Continuar')

    def resetPriceWorker(self):
        self.priceWorker.reset()
        self.tabControl.setTabText(0, u'Preço')
        self.priceStopButton.setText('Parar')

    def setStockProgress(self, progress, log):
        self.stockProgressBar.setValue(progress)
        self.stockLog.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')  + ': ' + log)
        cursor = self.stockLog.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.stockLog.setTextCursor(cursor)

    def toggleStockWorker(self):
        self.stockWorker.toggle()
        if self.stockWorker.isRunning:
            self.tabControl.setTabText(1, u'Estoque')
            self.stockStopButton.setText('Parar')
        else:
            self.tabControl.setTabText(1, u'Estoque (parado)')
            self.stockStopButton.setText('Continuar')

    def resetStockWorker(self):
        self.stockWorker.reset()
        self.tabControl.setTabText(1, u'Estoque')
        self.stockStopButton.setText('Parar')

    def setOrdersProgress(self, progress, ordersData):
        self.ordersProgressBar.setValue(progress)
        data = json.loads(ordersData)
        self.ordersTable.setModel(QTableModel(self, data, self.ordersHeader))

    def closeEvent(self, event):
        self.priceWorker.finish()
        self.stockWorker.finish()
        self.ordersWorker.finish()
        event.accept()


class PriceWorker(QtCore.QThread):
    updateProgress = QtCore.Signal(int, str)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.reset()

    def run(self):
        while True:
            try:
                self.reset()
                self.updateProgress.emit(0, 'Progress: ' + str(0) + '%.')

                # Get Winthor data
                self.updateProgress.emit(0, 'Searching product prices on Winthor...')
                w = Winthor()
                winthor_products = w.getPrices()
                winthor_sku_to_price = dict([(p['codigo_produto'], p['preco_venda']) for p in winthor_products])
                self.updateProgress.emit(4, 'Found ' + str(len(winthor_products)) + ' product prices on Winthor!')
                self.updateProgress.emit(4, 'Progress: ' + str(4) + '%.')

                # Get Magento data
                self.updateProgress.emit(4, 'Connecting to Magento platform...')
                magento = Magento()
                self.updateProgress.emit(13, 'Connected!')
                self.updateProgress.emit(13, 'Progress: ' + str(13) + '%.')
                self.updateProgress.emit(13, 'Searching products on Magento...')
                magento_products = sorted(
                    [p for p in magento.getProducts() if p['sku'].isdigit()],
                    key=lambda p: int(p['sku'])
                )
                self.updateProgress.emit(23, 'Found ' + str(len(magento_products)) + ' products on Magento!')

                # Update magento data
                steps = len(magento_products)
                for i, magento_product in enumerate(magento_products):
                    self.updateProgress.emit(23 + i*77.0/steps, 'Progress: ' + str(23 + i*77.0/steps) + '%.')
                    old_price = round(float(magento.getProductPrice(magento_product['sku'])['price']), 2)
                    new_price = round(float(winthor_sku_to_price[magento_product['sku']]), 2)
                    if old_price == new_price: continue
                    self.updateProgress.emit(23 + i*77.0/steps, 'Updating price on item #%s from %s to %s...' % (magento_product['sku'], old_price, new_price))
                    magento.setProductPrice({
                        'sku': magento_product['sku'],
                        'product_id': magento_product['product_id'],
                        'price': str(new_price),
                        'old_price': old_price,
                    })

                self.updateProgress.emit(100, 'Progress: ' + str(100) + '%.')
                self.updateProgress.emit(100, '=========================')
                self.updateProgress.emit(100, '')
                self.updateProgress.emit(100, '')
                self.reset()
            except Exception as e:
                self.updateProgress.emit(0, 'Error: %s' % str(e).encode('utf-8'))
                self.updateProgress.emit(100, '=========================')
                self.updateProgress.emit(100, '')
                self.updateProgress.emit(100, '')

    def toggle(self):
        self.isRunning = not self.isRunning

    def reset(self):
        self.isRunning = True
        self.iteration = 0

    def finish(self):
        self.terminate()


class StockWorker(QtCore.QThread):
    updateProgress = QtCore.Signal(int, str)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.reset()

    def run(self):
        while True:
            try:
                self.reset()
                self.updateProgress.emit(0, 'Progress: ' + str(0) + '%.')

                # Get Winthor data
                self.updateProgress.emit(0, 'Searching product quantities on Winthor...')
                w = Winthor()
                winthor_products = w.getQuantities()
                winthor_products_skus = [p['codigo_produto'] for p in winthor_products]
                self.updateProgress.emit(4, 'Found ' + str(len(winthor_products)) + ' product quantities on Winthor!')
                self.updateProgress.emit(4, 'Progress: ' + str(4) + '%.')

                # Get Magento data
                self.updateProgress.emit(4, 'Connecting to Magento platform...')
                magento = Magento()
                self.updateProgress.emit(13, 'Connected!')
                self.updateProgress.emit(13, 'Progress: ' + str(13) + '%.')
                self.updateProgress.emit(13, 'Searching product quantities on Magento...')
                magento_products = magento.getProductQuantities(winthor_products_skus)
                magento_sku_to_qty = dict([(p['sku'], p['qty']) for p in magento_products])
                magento_sku_to_id = dict([(p['sku'], p['product_id']) for p in magento_products])
                self.updateProgress.emit(23, 'Found ' + str(len(magento_products)) + ' product quantities on Magento!')
                self.updateProgress.emit(23, 'Progress: ' + str(23) + '%.')

                # Update Magento data
                products_qty = sorted([
                    {
                        'product_id': magento_sku_to_id[q['codigo_produto']],
                        'sku': q['codigo_produto'],
                        'qty': int(q['quantidade_disponivel']),
                        'old_qty': int(float(magento_sku_to_qty[q['codigo_produto']]))
                    }
                    for q in winthor_products
                    if q['codigo_produto'] in magento_sku_to_id
                        and float(q['quantidade_disponivel']) != float(magento_sku_to_qty[q['codigo_produto']])
                ], key=lambda p: p['sku'])
                self.updateProgress.emit(23, 'Preparing to update ' + str(len(products_qty)) + ' products on Magento...')
                STEP = 100.0
                steps = int(math.ceil(len(products_qty)/STEP))
                for i in range(steps):
                    prods = products_qty[int(i*STEP):int(i*STEP+STEP)]
                    magento.setProductQuantities(prods)
                    self.updateProgress.emit(23 + (i+1)*77.0/steps, 'Progress: ' + str(23 + (i+1)*77.0/steps) + '%.')
                    self.updateProgress.emit(23 + (i+1)*77.0/steps, 'Updated ' + str(len(prods)) + ' products on Magento!')
                self.updateProgress.emit(100, 'Progress: ' + str(100) + '%.')
                self.updateProgress.emit(100, '=========================')
                self.updateProgress.emit(100, '')
                self.updateProgress.emit(100, '')
            except Exception as e:
                self.updateProgress.emit(0, 'Error: %s' % str(e).encode('utf-8'))
                self.updateProgress.emit(100, '=========================')
                self.updateProgress.emit(100, '')
                self.updateProgress.emit(100, '')


    def toggle(self):
        self.isRunning = not self.isRunning

    def reset(self):
        self.isRunning = True
        self.iteration = 0

    def finish(self):
        self.terminate()


class OrdersWorker(QtCore.QThread):
    updateProgress = QtCore.Signal(int, str)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        db = DatabaseAdapter(user='PAPELEXTESTE', password='PAPELEXTESTE', alias='TESTE')
        orders = {}
        self.updateProgress.emit(50, json.dumps([[]]))
        while True:
            try:
                self.reset()
                m = Magento()
                response = m.getOrders(today=True)
                result = dict([(order['increment_id'], order) for order in response])
                for key in result:
                    if key in orders:
                        orders[key].update(result[key])
                    else:
                        orders[key] = result[key]

                for order_id, order in orders.iteritems():
                    print m.getOrder(order['increment_id'])
                    if 'integration' not in order:
                        # check PCCLIENTFV
                        query = "select count(*) COUNT from PCCLIENTFV where CGCENT = '" + order['customer_taxvat'] + "'"
                        print query
                        count = db.query(query)[0]['count']
                        if count == 0:
                            today = date.today().strftime('%Y-%m-%d')
                            query = '''
                                insert into PCCLIENTFV (IMPORTADO,TIPOOPERACAO,CGCENT,CLIENTE,IEENT,TELENT,CEPENT,CODUSUR1,CODPRACA,OBS,EMAIL,OBSERVACAO_PC,DTINCLUSAO,CODCLI,DTALTERACAO,DTNASC)
                                values
                                (
                                    9,                                              -- IMPORTADO
                                    'I',                                            -- TIPOOPERACAO
                                    '%s',                                           -- CGCENT
                                    '%s',                                           -- CLIENTE
                                    'ISENTO',                                       -- IEENT
                                    '%s',                                           -- TELENT
                                    '%s',                                           -- CEPENT
                                    1,                                              -- CODUSUR1
                                    999999,                                         -- CODPRACA
                                    'P',                                            -- OBS
                                    '%s',                                           -- EMAIL
                                    'Pedido Site %s',                               -- OBSERVACAO_PC
                                    to_date('%s', 'YYYY-MM-DD'),                    -- DTINCLUSAO
                                    null,                                           -- CODCLI
                                    to_date('%s', 'YYYY-MM-DD'),                    -- DTALTERACAO
                                    to_date('%s','YYYY-MM-DD')                      -- DTNASC
                                )
                            ''' % (order['customer_taxvat'], order['billing_name'], order['telephone'][-13:],
                                    order['postcode'], order['customer_email'], order['increment_id'], today, today,
                                    order['customer_dob'][:10] if 'customer_dob' in order else '1900-01-01')
                            print query
                            db.execute(query)
                        order['integration'] = 'Pre-cadastro completo'
                    if order['integration'] == 'Pre-cadastro completo':
                        # check PCCLIENT
                        query = "select count(*) count from PCCLIENT where regexp_replace(CGCENT, '[^0-9]', '') = '" + order['customer_taxvat'] + "'"
                        print query
                        count = db.query(query)[0]['count']
                        if count > 0:
                            order['integration'] = 'Cliente cadastrado'

                    if order['integration'] == 'Cliente cadastrado':
                        # check Address on PCCLIENT
                        query = '''
                            select CODCLI
                            from PCCLIENT
                            where regexp_replace(CGCENT, '[^0-9]', '') = '%s'
                                and regexp_replace(CEPENT, '[^0-9]', '') = '%s'
                        ''' % (order['customer_taxvat'], order['postcode'].replace('-', ''))
                        print query
                        result = db.query(query)
                        if len(result) > 0:
                            order['CODCLI'] = result[0]['codcli']
                            order['CODENDENTCLI'] = None
                            order['integration'] = 'Endereco cadastrado'
                        # check Address on PCCLIENTENDENT
                        query = '''
                            select PCCLIENT.CODCLI, CODENDENTCLI
                            from PCCLIENTENDENT, PCCLIENT
                            where PCCLIENTENDENT.CODCLI = PCCLIENT.CODCLI
                                and regexp_replace(PCCLIENT.CGCENT, '[^0-9]', '') = '%s'
                                and regexp_replace(PCCLIENTENDENT.CEPENT, '[^0-9]', '') = '%s'
                        ''' % (order['customer_taxvat'], order['postcode'].replace('-', ''))
                        print query
                        result = db.query(query)
                        if len(result) > 0:
                            order['CODENDENTCLI'] = result[0]['codendentcli']
                            order['CODCLI'] = result[0]['codcli']
                            order['integration'] = 'Endereco cadastrado'

                    if order['integration'] == 'Endereco cadastrado':
                        query = '''
                            select 1
                            from PCPEDCFV
                            where NUMPEDRCA = '%s'
                        ''' % (order['increment_id'])
                        print query
                        result = db.query(query)
                        if len(result) == 0:
                            # check PCPEDCFV
                            query = '''
                                insert into PCPEDCFV (IMPORTADO, NUMPEDRCA, CODUSUR, CGCCLI, DTABERTURAPEDPALM, DTFECHAMENTOPEDPALM, CODFILIAL, CODCOB, CODPLPAG, CONDVENDA, ORIGEMPED)
                                values
                                (
                                    1,                                              -- IMPORTADO
                                    '%s',                                           -- NUMPEDRCA
                                    1,                                              -- CODUSUR
                                    '%s',                                           -- CGCCLI
                                    to_date('%s', 'YYYY-MM-DD'),                    -- DTABERTURAPEDPALM
                                    to_date('%s', 'YYYY-MM-DD'),                    -- DTFECHAMENTOPEDPALM
                                    1,                                              -- CODFILIAL
                                    'SITE',                                         -- CODCOB
                                    1,                                              -- CODPLPAG
                                    1,                                              -- CONDVENDA
                                    'F'                                             -- ORIGEMPED
                                )
                            ''' % (order['increment_id'], order['customer_taxvat'], order['created_at'][:10],
                                    order['created_at'][:10])
                            print query
                            db.execute(query)
                        order['integration'] = 'Pedido criado'
                    if order['integration'].startswith('Pedido rejeitado') or order['integration'].startswith('Pedido criado'):
                        query = '''
                            select IMPORTADO, observacao_pc
                            from PCPEDCFV
                            where NUMPEDRCA = '%s'
                        ''' % (order['increment_id'])
                        print query
                        result = db.query(query)[0]
                        if result['importado'] == 2:
                            # check PCPEDIFV
                            order['integration'] = 'Concluido'
                        elif result['importado'] == 3:
                            order['integration'] = 'Pedido rejeitado: ' + result['observacao_pc']
    
                    sorted_orders = [
                        [i.get('integration') or '', i['increment_id'], i['created_at'], i['status'], i['billing_name'], i['customer_taxvat'], i['total_item_count'], i['base_grand_total'], i['postcode'].replace('-', '')]
                        for i in sorted(orders.values(), key=lambda x: x['created_at'])
                    ]
                    self.updateProgress.emit(50, json.dumps(sorted_orders))


            except Exception as e:
                print str(e)
                traceback.print_exc()

    def toggle(self):
        self.isRunning = not self.isRunning

    def reset(self):
        self.isRunning = True
        self.iteration = 0

    def finish(self):
        self.terminate()


class Winthor():
    def getQuantities(self):
        r = requests.post(
            'http://192.168.24.13/PCSIS2699.EXE/soap/PC_Estoque',
            data='''
            <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn3="urn:uPCEstoqueIntf-PC_Estoque">
                <x:Header/>
                <x:Body>
                    <urn3:Pesquisar>
                        <urn3:Codigo_Filial>1</urn3:Codigo_Filial>
                    </urn3:Pesquisar>
                </x:Body>
            </x:Envelope>''',
            headers={'Content-Type': 'text/xml; charset=utf-8'})
        root = ET.fromstring(r.text.encode('utf-8'))
        return [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]

    def getProducts(self):
        r = requests.post(
            'http://192.168.24.13/PCSIS2699.EXE/soap/PC_Estoque',
            data='''
            <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn3="urn:uPCProdutoIntf-PC_Produto">
                <x:Header/>
                <x:Body>
                    <urn3:Pesquisar>
                        <urn3:Somente_Produtos_Ativos>S</urn3:Somente_Produtos_Ativos>
                    </urn3:Pesquisar>
                </x:Body>
            </x:Envelope>''',
            headers={'Content-Type': 'text/xml; charset=utf-8'})
        root = ET.fromstring(r.text.encode('utf-8'))
        return [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]

    def getPrices(self):
        r = requests.post(
            'http://192.168.24.13/PCSIS2699.EXE/soap/PC_Preco',
            data='''
            <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn3="urn:uPCPrecoIntf-PC_Preco">
                <x:Header/>
                <x:Body>
                    <urn3:Pesquisar>
                    </urn3:Pesquisar>
                </x:Body>
            </x:Envelope>
            ''',
            headers={'Content-Type': 'text/xml; charset=utf-8'})
        root = ET.fromstring(r.text.encode('utf-8'))
        return [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]

    def getOrder(self, incrementId):
        r = requests.post(
            'http://192.168.24.13/PCSIS2699.EXE/soap/PC_Pedido',
            data='''
                <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn12="urn:uPCPedidoIntf-PC_Pedido">
                    <x:Header/>
                    <x:Body>
                        <urn12:PesquisarSituacaoPedido>
                            <urn12:Numero_Pedido_Ecommerce>%s</urn12:Numero_Pedido_Ecommerce>
                        </urn12:PesquisarSituacaoPedido>
                    </x:Body>
                </x:Envelope>
            ''' % incrementId,
            headers={'Content-Type': 'text/xml; charset=utf-8'})
        root = ET.fromstring(r.text.encode('utf-8'))
        return [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]


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
    ex = Routine9813(*args)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
