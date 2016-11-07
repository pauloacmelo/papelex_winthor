import requests
import xml.etree.ElementTree as ET

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
print [dict([(child.tag, child.text) for child in i]) for i in root[0][0][1]]

products = [{'sku': '1674', 'set': '4', 'product_id': '836', 'category_ids': ['6', '7', '134', '348', '395'], 'website_ids': ['1'], 'type': 'simple', 'name': u'VASSOURA PIA\xc7AVA 40CM - 31 FUROS - GARI'}, {'sku': '4498', 'set': '4', 'product_id': '837', 'category_ids': ['6', '7', '116', '136', '202', '348', '395', '426'], 'website_ids': ['1'], 'type': 'simple', 'name': 'VEJA PERFUME DA NATUREZA - LAVANDA - 500ML'}, {'sku': '3142', 'set': '4', 'product_id': '838', 'category_ids': ['6', '111', '116', '136', '202', '348', '395', '426', '505'], 'website_ids': ['1'], 'type': 'simple', 'name': 'VEJA CLORO ATIVO 500ML'}, {'sku': '1261', 'set': '4', 'product_id': '839', 'category_ids': ['6', '7', '116', '136', '202', '348', '395', '595'], 'website_ids': ['1'], 'type': 'simple', 'name': 'VEJA LIMPEZA PESADA 500ML'}, {'sku': '8551', 'set': '4', 'product_id': '840', 'category_ids': ['7', '139', '150', '203', '348', '411', '594'], 'website_ids': ['1'], 'type': 'simple', 'name': 'BANDEJA EUROPA - PLASVALE'}, {'sku': '8560', 'set': '4', 'product_id': '841', 'category_ids': ['7', '139', '203', '348', '411'], 'website_ids': ['1'], 'type': 'simple', 'name': 'CAIXA PARA LEGUMES E FRUTAS 42 LITROS - BRANCA - PLASVALE'}, {'sku': '8561', 'set': '4', 'product_id': '842', 'category_ids': ['7', '139', '203', '348', '411'], 'website_ids': ['1'], 'type': 'simple', 'name': 'CAIXA PARA LEGUMES E FRUTAS 42L PRETA - PLASVALE'}, {'sku': '8556', 'set': '4', 'product_id': '843', 'category_ids': ['6', '7', '201', '339', '348', '411', '426', '605'], 'website_ids': ['1'], 'type': 'simple', 'name': 'LIXEIRA BASCULANTE 14L - BRANCA - PLASVALE'}, {'sku': '8558', 'set': '4', 'product_id': '844', 'category_ids': ['6', '201', '339', '348', '411'], 'website_ids': ['1'], 'type': 'simple', 'name': 'LIXEIRA BASCULANTE 30 LITROS -  PRETA - REF.: 1243 - PLASVALE'}, {'sku': '8559', 'set': '4', 'product_id': '845', 'category_ids': ['6', '7', '201', '339', '348', '411', '426', '677'], 'website_ids': ['1'], 'type': 'simple', 'name': 'LIXEIRA BASCULANTE 50 LITROS - PLASVALE'}]
products_hash = dict([(p['sku'], p['product_id']) for p in products])
quantities = [{'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '1674', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '4498', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '3142', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '1261', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8551', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8560', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8561', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8556', 'quantidade_disponivel': '20'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8558', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '8559', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2252', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2253', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2254', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2255', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2364', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2366', 'quantidade_disponivel': '4'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2475', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2476', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2477', 'quantidade_disponivel': '0'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2587', 'quantidade_disponivel': '1'}, {'codigo_filial': '1', 'totalEstoque': '0', 'codigo_produto': '2588', 'quantidade_disponivel': '0'}]
[{'product_id': products_hash[q['codigo_produto']], 'qty': q['quantidade_disponivel']} for q in quantities if q['codigo_produto'] in products_hash]