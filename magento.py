import requests
import xmltodict
import xml.etree.ElementTree as ET
import math
from datetime import datetime, date, timedelta

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
        ''' % (date.today() - timedelta(4)).strftime('%Y-%m-%d')
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
            (prop.tag, prop.text) if 'Entity' not in ''.join(prop.attrib.values())
            else (
                (prop.tag, dict([(subprop.tag, subprop.text) for subprop in prop])) if 'EntityArray' not in ''.join(prop.attrib.values())
                else (prop.tag, [dict([(subsubprop.tag, subsubprop.text) for subsubprop in subprop]) for subprop in prop])
            )
            for prop in root[0][0][0]
        ])

