# from requests_oauthlib import OAuth1 as OAuth
import requests
import sys
# import simplejson
from time import time
import xmltodict

# Reference: http://devdocs.magento.com/guides/m1x/api/rest-api-index.html
# Reference GET Filters: http://devdocs.magento.com/guides/m1x/api/rest/get_filters.html

# Parameters
class MagentoAPI(object):
    def __init__(self, user=False, password=False, endpoint=False):
        super(MagentoAPI, self).__init__()
        # self.client_user = user or 'paulo.andre'
        # self.client_password = password or '8+esetHep?4H'
        # self.endpoint = endpoint or 'http://www.papelex.com.br/index.php/api/xmlrpc?type=xmlrpc'
        self.client_user = user or 'api.papelex'
        self.client_password = password or 'teste123'
        self.endpoint = endpoint or 'http://papelex.lojaemteste.com.br/index.php/api/xmlrpc/?type=xmlrpc'
        self.login()

    def initialize_xml(self):
        self.xml = ''
        self.xmlTags = []

    def open_tag(self, tag_name):
        self.xmlTags.append(tag_name)
        self.xml += '<%s>' % tag_name

    def openclose_tag(self, tag_name, tag_value=False):
        if tag_value:
            self.xml += '<%s>' % tag_name
            self.xml += str(tag_value)
            self.xml += '</%s>' % tag_name
        else:
            self.xml += '<%s/>' % tag_name

    def closeTag(self):
        self.xml += '</%s>' % self.xmlTags.pop()

    def mountXml(self, method, params=[]):
        self.initialize_xml()
        self.open_tag('methodCall')
        self.openclose_tag('methodName', method)
        if params:
            self.open_tag('params')
            for p in params:
                self.openclose_tag('string', p)
            self.close_tag()
        else:
            self.openclose_tag('params', params)
        self.closeTag() # methodCall
        return self.xml

    def _parse(self, response):
        print response
        return xmltodict.parse(response)

    def _call(self, method, params=[]):
        response = requests.post(self.endpoint, self.mountXml(method, params))
        return self._parse(response.text)

    def list_methods(self):
        return self._call('system.listMethods')

    def login(self):
        pass

    def read(self, endpoint, id, params={}, buffer_size=100, debug=False):
        pass

    def read_all(self, endpoint, filters=[], params={}, buffer_size=100, maxitems=9999999, debug=False):
        pass

    def update(self, endpoint, id, filters=[], params={}, data={}, debug=False):
        pass


# Test api
def main():
    api = MagentoAPI()
    print(api.list_methods())

if __name__ == '__main__':
    main()
