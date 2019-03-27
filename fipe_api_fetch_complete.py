import os
import requests
import pandas as pd
from datetime import date
import time
import random
import csv


def format_ano(ano):
    if ano == '32000':
        ano = str(date.today().year)
    return ano

def format_preco(preco):
    return preco.replace('R$ ', '').replace(',00', '').replace('.', '')

fipe_api_base_url = 'http://fipeapi.appspot.com/api/1/carros/veiculo/{0}/{1}/{2}.json'

fipe_attrib_file = 'fipe_prep_list_03_2019.csv'
fipe_attrib_open = open(fipe_attrib_file, 'rb')
fipe_attrib_reader = csv.reader(fipe_attrib_open)
fipe_attrib_reader.next()
fipe_attrib_list = list(fipe_attrib_reader)

marca_to_code = {
    '21': 'FIAT',
    '22': 'FORD',
    '23': 'CHEVROLET',
    '25': 'HONDA',
    '26': 'HYUNDAI',
    '29': 'JEEP',
    '43': 'NISSAN',
    '48': 'RENAULT',
    '56': 'TOYOTA',
    '59': 'VOLKSWAGEN',
}

output_fipe_headers = ['marca', 'modelo_code', 'modelo_nome', 'ano', 'preco']

fipe_data_list = []

counter = 0
for fipe_index, fipe_attributes in enumerate(fipe_attrib_list):
    if fipe_index >= 672:
        counter += 1
        print counter, fipe_attributes
        for date_to_fetch in eval(fipe_attributes[4]):
            fetch_url = fipe_api_base_url.format(fipe_attributes[1], fipe_attributes[2], date_to_fetch)
            #print fetch_url
            try:
                fipe_detail_json = requests.get(fetch_url).json()
                #print fipe_detail_json['ano_modelo'], fipe_detail_json['preco']
                modelo_fipe_data = [
                    marca_to_code[fipe_attributes[1]],
                    fipe_attributes[0].upper(),
                    fipe_detail_json['veiculo'],
                    format_ano(fipe_detail_json['ano_modelo']),
                    format_preco(fipe_detail_json['preco']),
                ]
                fipe_data_list.append(modelo_fipe_data)
                time.sleep(random.randint(1, 5))
            except Exception as e:
                try:
                    # try it one more time, sometimes the link do not open o the firs time
                    time.sleep(15)
                    fipe_detail_json = requests.get(fetch_url).json()
                    #print fipe_detail_json['ano_modelo'], fipe_detail_json['preco']
                    modelo_fipe_data = [
                        marca_to_code[fipe_attributes[1]],
                        fipe_attributes[0].upper(),
                        fipe_detail_json['veiculo'],
                        format_ano(fipe_detail_json['ano_modelo']),
                        format_preco(fipe_detail_json['preco']),
                    ]
                fipe_data_list.append(modelo_fipe_data)
                except Exception as e:
                    print '- - - - - - Error - - - - - -'
                    print fipe_attributes, date_to_fetch
                    print fetch_url
                    print e

df_fipe_data = pd.DataFrame(fipe_data_list, columns=output_fipe_headers)

df_fipe_data.to_csv('fipe_complete_03_2019_new.csv', index=False, encoding='utf-8')

fipe_attrib_file.close()
