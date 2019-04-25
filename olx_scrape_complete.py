import time
from datetime import datetime
import pandas as pd
import urllib2
from urlgrabber.keepalive import HTTPHandler
from bs4 import BeautifulSoup
from general.file_management import check_if_folder_exists_than_crete
from general.car_attributes import get_car_age, get_car_power, get_car_transmission, \
                                   get_car_model_code_fixed
from fipe_api_fetch import get_fipe_table


def get_car_leads():
    



if __name__ == "__main__":
    total_time = time.time()

    st1 = time.time()
    FIPE_FILE = get_fipe_table()
    FIPE_DF = pd.read_csv(FIPE_FILE)
    FIPE_DF['veiculo'] = FIPE_DF['veiculo'].str.lower()
    print('FIPE Time', time.time() - st1)

    get_car_leads()
    print('OLX SCRAPE EXECUTION TIME', time.time() - total_time)
