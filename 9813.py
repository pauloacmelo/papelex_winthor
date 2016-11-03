# coding: utf-8
from base import *
from PySide import QtGui, QtCore
import time
import requests
import xmltodict
import xml.etree.ElementTree as ET
import math
from datetime import datetime

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
        self.priceStopButton.clicked.connect(self.togglePriceWorker)
        self.priceRestartButton = QtGui.QPushButton('Reiniciar', self)
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
        self.stockStopButton.clicked.connect(self.toggleStockWorker)
        self.stockRestartButton = QtGui.QPushButton('Reiniciar', self)
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
        self.ordersLog = QtGui.QTextEdit(self)
        row = QtGui.QHBoxLayout()
        row.addWidget(QtGui.QLabel("Progresso:"))
        row.addWidget(self.ordersProgressBar)
        self.ordersStopButton = QtGui.QPushButton('Parar', self)
        self.ordersStopButton.clicked.connect(self.toggleOrdersWorker)
        self.ordersRestartButton = QtGui.QPushButton('Reiniciar', self)
        self.ordersRestartButton.clicked.connect(self.resetOrdersWorker)
        buttonRow = QtGui.QHBoxLayout()
        buttonRow.addStretch(1)
        buttonRow.addWidget(self.ordersStopButton)
        buttonRow.addWidget(self.ordersRestartButton)
        layout = QtGui.QVBoxLayout()
        layout.addLayout(row)
        layout.addWidget(self.ordersLog)
        layout.addLayout(buttonRow)
        self.ordersTab.setLayout(layout)

    def setPriceProgress(self, progress, log):
        self.priceProgressBar.setValue(progress)
        self.priceLog.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')  + ': ' + log)

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

    def setOrdersProgress(self, progress, log):
        self.ordersProgressBar.setValue(progress)
        self.ordersLog.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S')  + ': ' + log)

    def toggleOrdersWorker(self):
        self.ordersWorker.toggle()
        if self.ordersWorker.isRunning:
            self.tabControl.setTabText(2, u'Pedidos')
            self.ordersStopButton.setText('Parar')
        else:
            self.tabControl.setTabText(2, u'Pedidos (parado)')
            self.ordersStopButton.setText('Continuar')

    def resetOrdersWorker(self):
        self.ordersWorker.reset()
        self.tabControl.setTabText(2, u'Pedidos')
        self.ordersStopButton.setText('Parar')

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
            self.reset()
            while self.iteration <= 100:
                if self.isRunning:
                    self.iteration = self.iteration + 1
                    self.updateProgress.emit(
                        self.iteration, 'updateProgress ' + str(self.iteration) + '...')
                time.sleep(0.05)
            print 'Ended!'

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
            self.reset()
            self.updateProgress.emit(0, 'Progress: ' + str(0) + '%.')
            self.updateProgress.emit(0, 'Connecting to Magento platform...')
            magento = Magento()
            self.updateProgress.emit(2, 'Progress: ' + str(2) + '%.')
            self.updateProgress.emit(2, 'Connected!')
            self.updateProgress.emit(2, 'Searching products on Magento...')
            magento_products = magento.getProducts()
            self.updateProgress.emit(12, 'Progress: ' + str(12) + '%.')
            self.updateProgress.emit(12, 'Found ' + str(len(magento_products)) + ' products on Magento!')
            magento_sku_to_id = dict([(p['sku'], p['product_id']) for p in magento_products])
            magento_product_ids = [p['product_id'] for p in magento_products]
            self.updateProgress.emit(12, 'Searching products on Magento...')
            magento_qtys = magento.getProductQuantities(magento_product_ids)
            qtys_hash = dict([(p['sku'], p['qty']) for p in magento_qtys])
            self.updateProgress.emit(22, 'Progress: ' + str(22) + '%.')
            self.updateProgress.emit(22, 'Found ' + str(len(magento_qtys)) + ' product quantities on Magento!')
            print [id for id in magento_sku_to_id.values() if id not in [q['product_id'] for q in magento_qtys]]
            self.updateProgress.emit(22, 'Searching product quantities on Magento...')
            w = Winthor()
            quantities = w.getQuantities()
            self.updateProgress.emit(29, 'Progress: ' + str(29) + '%.')
            self.updateProgress.emit(29, 'Found ' + str(len(quantities)) + ' product quantities on Winthor!')
            products_qty = sorted([
                {
                    'product_id': magento_sku_to_id[q['codigo_produto']],
                    'sku': q['codigo_produto'],
                    'qty': int(q['quantidade_disponivel']),
                    'old_qty': int(float(qtys_hash[q['codigo_produto']]))
                }
                for q in quantities
                if q['codigo_produto'] in magento_sku_to_id
                    and q['codigo_produto'] in qtys_hash
                    and float(q['quantidade_disponivel']) != float(qtys_hash[q['codigo_produto']])
                    and q['codigo_produto'] in ['1001', '1002', '1003']
            ], key=lambda p: p['sku'])
            self.updateProgress.emit(29, 'Preparing to update ' + str(len(products_qty)) + ' products on Magento!')
            STEP = 50.0
            steps = int(math.ceil(len(products_qty)/STEP))
            for i in range(steps):
                prods = products_qty[int(i*STEP):int(i*STEP+STEP)]
                print prods
                magento.setProductQuantities(prods)
                self.updateProgress.emit(29 + (i+1)*71.0/steps, 'Progress: ' + str(29 + (i+1)*71.0/steps) + '%.')
                self.updateProgress.emit(29 + (i+1)*71.0/steps, 'Updated ' + str(len(prods)) + ' products on Magento!')
            self.updateProgress.emit(100, 'Progress: ' + str(100) + '%.')
            self.updateProgress.emit(100, '=========================')
            self.updateProgress.emit(100, '')
            self.updateProgress.emit(100, '')
            self.reset()
            print 'Ended!'

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
        while True:
            self.reset()
            while self.iteration <= 100:
                if self.isRunning:
                    self.iteration = self.iteration + 1
                    self.updateProgress.emit(
                        self.iteration, 'updateProgress ' + str(self.iteration) + '...')
                time.sleep(0.05)
            print 'Ended!'

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
        root = ET.fromstring(r.text)
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
        root = ET.fromstring(r.text)
        return [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]

    def getPrice(self, productId):
        r = requests.post(
            'http://192.168.24.13/PCSIS2699.EXE/soap/PC_Estoque',
            data='''
            <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn3="urn:uPCPrecoIntf-PC_Preco">
                <x:Header/>
                <x:Body>
                    <urn3:Pesquisar>
                        <urn3:Codigo_Produto>%s</urn3:Codigo_Produto>
                    </urn3:Pesquisar>
                </x:Body>
            </x:Envelope>
            ''' % productSku,
            headers={'Content-Type': 'text/xml; charset=utf-8'})
        root = ET.fromstring(r.text)
        return dict([(child.tag, child.text) for child in root[0][0][1][0]])


class Magento():

    def __init__(self):
        self.url='http://papelex.lojaemteste.com.br/index.php/api/v2_soap/?wsdl=1'
        self.user='api.papelex'
        self.password='teste123'
        self.session = self.getSession()

    def getSession(self):
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
            <x:Header/>
            <x:Body>
                <urn:login>
                    <urn:username>api.papelex</urn:username>
                    <urn:apiKey>teste123</urn:apiKey>
                </urn:login>
            </x:Body>
        </x:Envelope>''',
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text)
        print root[0][0][0].text
        return root[0][0][0].text

    def getProducts(self):
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:catalogProductList>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:filters>
                            <urn:filter/>
                            <urn:complex_filter/>
                        </urn:filters>
                        <urn:storeView></urn:storeView>
                    </urn:catalogProductList>
                </x:Body>
            </x:Envelope>''' % self.session,
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        print len(root[0][0][0])
        return [
            dict([
                (prop.tag, prop.text)
                if 'ns1:ArrayOfString' not in prop.attrib.values()
                else (prop.tag, [subprop.text for subprop in prop])
                for prop in item
            ])
            for storeView in root[0][0]
            for item in storeView
        ]

    def getProductQuantities(self, product_skus=[]):
        if len(product_skus) == 0:
            products = self.getProducts()
            product_skus = [p['sku'] for p in products]
        query_skus = ['<item xsi:type="xsd:string">%s</item>' % i for i in product_skus]
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:catalogInventoryStockItemList>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:products>
                            %s
                        </urn:products>
                    </urn:catalogInventoryStockItemList>
                </x:Body>
            </x:Envelope>
            ''' % (self.session, '\n'.join(query_skus)),
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        return [
            dict([
                (prop.tag, prop.text)
                if 'ns1:ArrayOfString' not in prop.attrib.values()
                else (prop.tag, [subprop.text for subprop in prop])
                for prop in item
            ])
            for item in root[0][0][0]
        ]

    def setProductQuantities(self, products):
        if len(products) == 0:
            return False
        product_query_skus = ['<item xsi:type="xsd:string">%s</item>' % p['sku'] for p in products]
        qty_query_ids = ['<urn:data>\n<urn:qty>%s</urn:qty>\n</urn:data>' % p['qty'] for p in products]
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:catalogInventoryStockItemMultiUpdate>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:productIds>
                            %s
                        </urn:productIds>
                        <urn:productData>
                            %s
                        </urn:productData>
                    </urn:catalogInventoryStockItemMultiUpdate>
                </x:Body>
            </x:Envelope>
            ''' % (self.session, '\n'.join(product_query_skus), '\n'.join(qty_query_ids)),
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        return root[0][0][0].text == 'true'

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
