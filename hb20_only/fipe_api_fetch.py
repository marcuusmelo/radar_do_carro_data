import os
import requests
import pandas as pd
from datetime import date
import time
from generic_functions import check_if_folder_exists_than_crete, check_if_file_exists


def get_car_model_year_dict(fipe_base_url):
    """ Get a dictionary from Fipe API of all models and year available in the system for a car"""
    hiunday_url = fipe_base_url + 'veiculos/26.json'
    hiunday_cars = requests.get(hiunday_url).json()

    hb20_id_list = [x['id'] for x in hiunday_cars if 'hb20' in x['key']]

    car_code_dict = {}

    for model_code in hb20_id_list:
        car_code_dict[model_code] = []

    for model_code in car_code_dict.keys():
        model_url = fipe_base_url + 'veiculo/26/' + model_code + '.json'
        model_years = requests.get(model_url).json()

        for car_year in model_years:
            car_code_dict[model_code].append(car_year['id'])

    return car_code_dict


def get_new_fipe_table(output_file):
    """ Generate a new fipe table and save as csv """
    today_date = str(date.today())
    fipe_base_url = 'http://fipeapi.appspot.com/api/1/carros/'

    #car_code_dict = get_car_model_year_dict(fipe_base_url)
    car_code_dict = {'6205': ['32000-1', '2019-1', '2018-1', '2017-1', '2016-1', '2015-1', '2014-1', '2013-1'],
                     '6207': ['32000-1', '2019-1', '2018-1', '2017-1', '2016-1', '2015-1', '2014-1', '2013-1']}

    car_fipe_details_list = []

    for model_code in car_code_dict.keys():
        for car_year in car_code_dict[model_code]:
            # time.sleep(2) # this api has a limit of 60 calls per minute
            fipe_details_url = fipe_base_url + 'veiculo/26/' + model_code + '/' + car_year + '.json'
            fipe_detail_json = requests.get(fipe_details_url).json()
            car_fipe_details_list.append(fipe_detail_json)

    for fipe_details in car_fipe_details_list:
        print fipe_details
        if fipe_details['ano_modelo'] == '32000':
            fipe_details['ano_modelo'] = 'zero km'

        fipe_details['data_tabela'] = today_date

    car_fipe_details_df = pd.DataFrame(car_fipe_details_list)

    car_fipe_details_df.to_csv(output_file)


def get_fipe_table():
    """ Get fipe table for Hiunday HB20 """
    today_date = str(date.today())[:7]
    output_path = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/'

    
    output_file = output_path + 'tabela_fipe_hb20_' + today_date + '.csv'

    if not check_if_file_exists(output_file):
        check_if_folder_exists_than_crete(output_path)
        get_new_fipe_table(output_file)
    else:
        print 'File Already Exists: ', output_file

    print 'DONE!', output_file
    return output_file


if __name__ == "__main__":
    get_fipe_table()
