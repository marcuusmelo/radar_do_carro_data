import os
import sys
import requests
import pandas as pd
from datetime import date
import time
import random
import csv

from general_car_functions import get_car_power, get_car_transmission, get_brand_from_id
from general_file_management import check_if_file_exists, check_if_folder_exists_than_crete


def format_ano(ano):
    if ano == '32000':
        ano = 'ZERO KM'
    return ano


def format_preco(preco):
    return preco.replace('R$ ', '').replace(',00', '').replace('.', '')


def get_new_fipe_table(output_file, year_min):
    fetch_date = date.today()
    fipe_api_base_url = 'http://fipeapi.appspot.com/api/1/carros/veiculo/{0}/{1}/{2}.json'

    fipe_attrib_path = 'static_data/fipe_prep_list_03_2019.csv'
    fipe_attrib_file = open(fipe_attrib_path, 'rb')
    fipe_attrib_reader = csv.reader(fipe_attrib_file)
    fipe_attrib_reader.next()
    fipe_attrib_list = list(fipe_attrib_reader)

    output_fipe_headers = ['marca', 'modelo_code', 'modelo_nome', 'ano',
                           'potencia', 'transm', 'preco', 'data_processamento']

    fipe_data_list = []

    counter = 0
    for fipe_index, fipe_attributes in enumerate(fipe_attrib_list):
        counter += 1
        # print counter, fipe_attributes
        date_to_fetch_list = [x for x in eval(fipe_attributes[4]) if x >= year_min]

        for date_to_fetch in date_to_fetch_list:
            fetch_data_attempts = 0
            fetch_url = fipe_api_base_url.format(fipe_attributes[1],
                                                 fipe_attributes[2],
                                                 date_to_fetch)

            while fetch_data_attempts < 2:
                fetch_data_attempts += 1
                try:
                    fipe_detail_json = requests.get(fetch_url).json()
                    #print fipe_detail_json['ano_modelo'], fipe_detail_json['preco']
                    modelo_fipe_data = [
                        get_brand_from_id(fipe_attributes[1]),
                        fipe_attributes[0].upper(),
                        fipe_detail_json['veiculo'],
                        format_ano(fipe_detail_json['ano_modelo']),
                        get_car_power(fipe_detail_json['veiculo']),
                        get_car_transmission(fipe_detail_json['veiculo']),
                        format_preco(fipe_detail_json['preco']),
                        fetch_date
                    ]

                    fipe_data_list.append(modelo_fipe_data)

                    time.sleep(random.randint(1, 3))
                    break

                except Exception as e:
                    print '- - - - - - Error - - - - - -'
                    print fipe_attributes, date_to_fetch
                    print fetch_url
                    print e
                    time.sleep(15)

    df_fipe_data = pd.DataFrame(fipe_data_list, columns=output_fipe_headers)

    df_fipe_data.to_csv(output_file, index=False, encoding='utf-8')

    fipe_attrib_file.close()


def get_fipe_table(year_min='2009'):
    """ Get fipe table for Hiunday HB20 """
    today_date = str(date.today())[:7]
    output_path = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/'

    output_file = output_path + 'tabela_fipe_' + today_date + '.csv'

    if not check_if_file_exists(output_file):
        check_if_folder_exists_than_crete(output_path)
        get_new_fipe_table(output_file, year_min)

    else:
        print 'File Already Exists: ', output_file

    print 'DONE!', output_file

    return output_file


if __name__ == '__main__':
    get_fipe_table()
