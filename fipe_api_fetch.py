import os
import requests
import pandas as pd
from datetime import date
import time
from generic_functions import check_if_folder_exists_than_crete, check_if_file_exists


def get_new_fipe_table(output_file):
    """ Generate a new fipe table and save as csv """
    today_date = str(date.today())
    fipe_base_url = 'http://fipeapi.appspot.com/api/1/carros/'

    car_code_list = [
        ['hb20', '26', '6205', '32000-1'],
        ['hb20', '26', '6205', '2019-1'],
        ['hb20', '26', '6205', '2018-1'],
        ['hb20', '26', '6205', '2017-1'],
        ['hb20', '26', '6205', '2016-1'],
        ['hb20', '26', '6205', '2015-1'],
        ['hb20', '26', '6205', '2014-1'],
        ['hb20', '26', '6205', '2013-1'],
        ['hb20', '26', '6207', '32000-1'],
        ['hb20', '26', '6207', '2019-1'],
        ['hb20', '26', '6207', '2018-1'],
        ['hb20', '26', '6207', '2017-1'],
        ['hb20', '26', '6207', '2016-1'],
        ['hb20', '26', '6207', '2015-1'],
        ['hb20', '26', '6207', '2014-1'],
        ['hb20', '26', '6207', '2013-1'],
        ['onix', '23', '6232', '32000-1'],
        ['onix', '23', '6232', '2019-1'],
        ['onix', '23', '6232', '2018-1'],
        ['onix', '23', '6232', '2017-1'],
        ['onix', '23', '6232', '2016-1'],
        ['onix', '23', '6232', '2015-1'],
        ['onix', '23', '6232', '2014-1'],
        ['onix', '23', '6232', '2013-1'],
        ['onix', '23', '6233', '32000-1'],
        ['onix', '23', '6233', '2019-1'],
        ['onix', '23', '6233', '2018-1'],
        ['onix', '23', '6233', '2017-1'],
        ['onix', '23', '6233', '2016-1'],
        ['onix', '23', '6233', '2015-1'],
        ['onix', '23', '6233', '2014-1'],
        ['onix', '23', '6233', '2013-1']
    ]

    car_fipe_details_list = []

    for car_code in car_code_list:
        # time.sleep(2) # this api has a limit of 60 calls per minute
        fipe_details_url = '{0}/veiculo/{1}/{2}/{3}.json'.format(fipe_base_url,
                                                                 car_code[1],
                                                                 car_code[2],
                                                                 car_code[3])

        fipe_detail_json = requests.get(fipe_details_url).json()
        car_fipe_details_list.append(fipe_detail_json)

    for fipe_details in car_fipe_details_list:
        if fipe_details['ano_modelo'] == '32000':
            fipe_details['ano_modelo'] = 'zero km'

        fipe_details['data_tabela'] = today_date

    car_fipe_details_df = pd.DataFrame(car_fipe_details_list)

    del car_fipe_details_df['referencia']

    car_fipe_details_df.to_csv(output_file)


def get_fipe_table():
    """ Get fipe table for Hiunday HB20 """
    today_date = str(date.today())[:7]
    output_path = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/'

    output_file = output_path + 'tabela_fipe_' + today_date + '.csv'

    if not check_if_file_exists(output_file):
        check_if_folder_exists_than_crete(output_path)
        get_new_fipe_table(output_file)
    else:
        print 'File Already Exists: ', output_file

    print 'DONE!', output_file

    return output_file


if __name__ == "__main__":
    get_fipe_table()
