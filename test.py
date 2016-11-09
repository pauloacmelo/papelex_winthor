import requests
import xml.etree.ElementTree as ET
from datetime import date, timedelta

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

    def getProductPrice(self, product_sku):
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:catalogProductInfo>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:productId>%s</urn:productId>
                        <urn:identifierType>sku</urn:identifierType>
                        <urn:attributes>
                            <urn:attributes>
                                <item>sku</item>
                                <item>product_id</item>
                                <item>price</item>
                                <item>special_price</item>
                                <item>special_from_date</item>
                                <item>special_to_date</item>
                            </urn:attributes>
                            <urn:additional_attributes/>
                        </urn:attributes>
                    </urn:catalogProductInfo>
                </x:Body>
            </x:Envelope>
            ''' % (self.session, product_sku),
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        return dict([
            (prop.tag, prop.text)
            if 'ns1:ArrayOfString' not in prop.attrib.values()
            else (prop.tag, [subprop.text for subprop in prop])
            for prop in root[0][0][0]
        ])


    def setProductPrice(self, product):
        query = ''
        for field in ['price', 'special_price', 'special_from_date', 'special_to_date']:
            if field not in product: continue
            query += '<urn:%s>%s</urn:%s>' % (field, product[field], field)
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:catalogProductUpdate>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:product>%s</urn:product>
                        <urn:identifierType>sku</urn:identifierType>
                        <urn:productData>
                            %s
                        </urn:productData>
                    </urn:catalogProductUpdate>
                </x:Body>
            </x:Envelope>
            ''' % (self.session, product['sku'], query),
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        return root[0][0][0].text == 'true'

    def getOrders(self, today=False):
        today_filter = '''
            <filters>
                <complex_filter>
                    <item>
                        <key>created_at</key>
                        <value>
                            <key>gteq</key>
                            <value>%s 00:00:00</value>
                        </value>
                    </item>
                </complex_filter>
            </filters>
        ''' % (date.today() - timedelta(1)).strftime('%Y-%m-%d')
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:salesOrderList>
                        <urn:sessionId>%s</urn:sessionId>
                        %s
                    </urn:salesOrderList>
                </x:Body>
            </x:Envelope>
            ''' % (self.session, today_filter if today else ''),
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

    def getOrder(self, incrementId):
        response = requests.post('http://papelex.lojaemteste.com.br/index.php/api/v2_soap/index/',
            data='''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:Magento">
                <x:Header/>
                <x:Body>
                    <urn:salesOrderInfo>
                        <urn:sessionId>%s</urn:sessionId>
                        <urn:orderIncrementId>%s</urn:orderIncrementId>
                    </urn:salesOrderInfo>
                </x:Body>
            </x:Envelope>''' % (self.session, incrementId),
            headers={
                'Host': 'papelex.lojaemteste.com.br',
                'SOAPAction': 'urn:Action',
                'Content-Type': 'text/xml; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        root = ET.fromstring(response.text.encode('utf-8'))
        return dict([
            (prop.tag, prop.text)
            if 'ns1:ArrayOfString' not in prop.attrib.values()
            else (prop.tag, [subprop.text for subprop in prop])
            for prop in root[0][0][0]
        ])


if __name__ == '__main__':
    m = Magento()
    # print len(m.getOrders())
    print m.getOrders(True)
    # print m.getOrder(100011314)

    # print m.getProductPrice(11448)
    # print m.setProductPrice({'sku': '11448', 'product_id': '5601', 'old_price': '42.69', 'price': '52.69'})
    # print m.getProductPrice(11448)

# {'sku': '11448', 'product_id': '5601', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11441', 'product_id': '5603', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11447', 'product_id': '5604', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11444', 'product_id': '5605', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11446', 'product_id': '5606', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11210', 'product_id': '5607', 'is_in_stock': '1', 'qty': '1674.0000'},
# {'sku': '11208', 'product_id': '5609', 'is_in_stock': '1', 'qty': '2944.0000'},
# {'sku': '11203', 'product_id': '5612', 'is_in_stock': '1', 'qty': '1647.0000'},
# {'sku': '11533', 'product_id': '5617', 'is_in_stock': '1', 'qty': '1.0000'},
# {'sku': '11532', 'product_id': '5618', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11546', 'product_id': '5620', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11537', 'product_id': '5621', 'is_in_stock': '0', 'qty': '0.0000'},
# {'sku': '11531', 'product_id': '5622', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11530', 'product_id': '5623', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11529', 'product_id': '5624', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11528', 'product_id': '5625', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11541', 'product_id': '5626', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11540', 'product_id': '5627', 'is_in_stock': '1', 'qty': '2.0000'},
# {'sku': '11535', 'product_id': '5630', 'is_in_stock': '1', 'qty': '2.0000'}
