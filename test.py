import requests
import xml.etree.ElementTree as ET

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
        print len(root[0][0][0])
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

if __name__ == '__main__':
    m = Magento()

    print m.getProductQuantities([1002])
    print m.setProductQuantities([
        {'sku': '1002', 'product_id': '3852', 'old_qty': 0, 'qty': 52}
    ])
    print m.getProductQuantities([1002])

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
