import time
from random import randint
from datetime import datetime, timedelta
from difflib import get_close_matches
import urllib
import urllib2
from PIL import Image
import pytesseract
from urlgrabber.keepalive import HTTPHandler
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

from general_car_functions import get_car_power, get_car_transmission, \
                                  get_car_model_code_fixed, get_brand_from_model
from fipe_api_fetch import get_fipe_table


class OLXScrape():

    def __init__(self):
        keepalive_handler = HTTPHandler()
        opener = urllib2.build_opener(keepalive_handler)
        urllib2.install_opener(opener)

        fipe_path = get_fipe_table()

        self.tabela_fipe_df = pd.read_csv(fipe_path, dtype=str)
        self.model_list_fipe = [x.upper() for x in self.tabela_fipe_df['modelo_nome'].tolist()]
        self.storage_dir = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/'
        self.output_filename = 'olx_scrape_{0}_{1}_{2}.csv'
        self.today_date = datetime.now()
        self.file_date = self.today_date.strftime('%Y%m%d%H%M%S')
        self.base_olx_url = 'https://df.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{0}/{1}?f=p&o={2}&rs=28'

        self.driver = webdriver.Chrome(executable_path='/Users/marcusmelo/Desktop/projects/radar_do_carro_data/chromedriver')


    def get_model_olx_url(self, car_model): # MAY BE UNECESSARY
        """ Get model olx url from car model name """
        if car_model == 'KA+':
            car_model = 'ka-mais'

        brand = get_brand_from_model(car_model.lower()).lower()
        model_olx_url = self.base_olx_url.format(brand, car_model.lower(), '1')
        return model_olx_url


    def get_number_of_ad_pages(self, car_brand, car_model):
        """ Get total of ad pages from olx firt search page """
        model_olx_url = self.base_olx_url.format(car_brand, car_model, '1')
        page = urllib2.urlopen(model_olx_url)
        soup = BeautifulSoup(page, 'html.parser')
        total_ads_raw = soup.find_all('span', attrs={'class': 'qtd'})[2].contents[0]
        total_ads_int = int(total_ads_raw.replace('(', '').replace(')', '').replace('.', ''))
        pages = (total_ads_int / 50) + 1
        return pages


    def format_ad_date(self, date_time_element):
        month_dict = {'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
                      'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'}

        hour_element, min_element = date_time_element[1].split(':')

        if date_time_element[0] == 'Hoje':
            ad_date = datetime(self.today_date.year,
                               self.today_date.month,
                               self.today_date.day,
                               int(hour_element),
                               int(min_element))

        elif date_time_element[0] == 'Ontem':
            ontem_date = self.today_date - timedelta(days=1)
            ad_date = datetime(ontem_date.year,
                               ontem_date.month,
                               ontem_date.day,
                               int(hour_element),
                               int(min_element))

        else:
            day_element, month_raw = date_time_element[0].split()
            month_element = month_dict[month_raw.lower()]
            year_element = self.today_date.year

            if int(month_element) > self.today_date.month:
                year_element = str(int(year_element)-1)

            ad_date = datetime(int(year_element),
                               int(month_element),
                               int(day_element),
                               int(hour_element),
                               int(min_element))

        return ad_date


    def get_page_ad_info(self, car_brand, car_model, page_range):
        ad_info_list = []
        for page_number in range(page_range):
            model_olx_url = self.base_olx_url.format(car_brand, car_model, str(page_number))

            page = urllib2.urlopen(model_olx_url)
            soup = BeautifulSoup(page, 'html.parser')

            page_a_tags = soup.find_all('a', attrs={'class':'OLXad-list-link'})

            for a_tag in page_a_tags:
                raw_ad_date = [x.text for x in a_tag.find_all('p', class_='text mb5px')]
                ad_info = [
                    a_tag.get('href'),
                    a_tag.get('id'),
                    self.format_ad_date(raw_ad_date)
                ]

                ad_info_list.append(ad_info)

        return ad_info_list


    def get_pages_to_fetch(self, ad_info_list, last_fetch_date=None):
        if last_fetch_date is None:
            # If not specified, fetch only the ads created in the last 6 months
            last_fetch_date = self.today_date - timedelta(days=180)

        pages_to_fetch_list = []
        for ad_info_element in ad_info_list:
            if ad_info_element[2] >= last_fetch_date:
                pages_to_fetch_list.append(ad_info_element)

        return pages_to_fetch_list


    def get_active_id_list(self, ad_info_list):
        return [x[1] for x in ad_info_list]


    def try_get_data(self, details_dict, key1, key2='', key3='', key4=''):
        """ Try to get data and put and ampty string if data can't be found """
        try:
            data_extracted = details_dict[key1]
            if key2:
                data_extracted = data_extracted[key2]
            if key3:
                data_extracted = data_extracted[key3]
            if key4:
                data_extracted = data_extracted[key4]

            return data_extracted

        except KeyError:
            return ''


    def get_phone_number(self):
        return self.driver.find_element_by_class_name('sc-fYiAbW').text


    def get_fipe_price(self, marca, modelo_code, modelo_nome, ano, potencia, transm):
        modelo_code = get_car_model_code_fixed(modelo_code)
        preco_fipe_modelo, preco_fipe_base_min, preco_fipe_base_max = '', '', ''

        closest_names_list = get_close_matches(modelo_nome, self.model_list_fipe)
        if closest_names_list:
            closest_modelo_nome = closest_names_list[0]

            fipe_modelo = self.tabela_fipe_df[
                (self.tabela_fipe_df['marca'] == marca.upper()) &
                (self.tabela_fipe_df['modelo_code'] == modelo_code.upper()) &
                (self.tabela_fipe_df['modelo_nome'] == closest_modelo_nome.upper()) &
                (self.tabela_fipe_df['ano'] == ano) &
                (self.tabela_fipe_df['potencia'] == potencia) &
                (self.tabela_fipe_df['transm'] == transm)
            ]

            if not fipe_modelo.empty:
                preco_fipe_modelo = fipe_modelo.iloc[0]['preco']

        fipe_base = self.tabela_fipe_df[
            (self.tabela_fipe_df['marca'] == marca.upper()) &
            (self.tabela_fipe_df['modelo_code'] == modelo_code.upper()) &
            (self.tabela_fipe_df['ano'] == ano) &
            (self.tabela_fipe_df['potencia'] == potencia) &
            (self.tabela_fipe_df['transm'] == transm)
        ]

        if not fipe_base.empty:
            preco_fipe_base_min = fipe_base['preco'].min()
            preco_fipe_base_max = fipe_base['preco'].max()

        return preco_fipe_modelo, preco_fipe_base_min, preco_fipe_base_max


    def get_ad_details(self, pages_to_fetch_list, car_brand, car_model):
        olx_data = []
        for ad_info in pages_to_fetch_list:
            try:
                st4_1 = time.time()
                ad_link = ad_info[0]
                ad_id = ad_info[1]
                ad_date = ad_info[2]
                print('AD LINK', ad_link)

                st4_2 = time.time()
                self.driver.get(ad_link)
                button = self.driver.find_element_by_class_name('sc-krvtoX')
                button.click()

                ad_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                print('Soup time', time.time() - st4_2)

                ad_details = ad_soup.find('script', attrs={'type':'application/ld+json'})

                details_raw = ad_details.contents[0]
                details_clean = ''.join(details_raw).encode('utf-8').strip()
                details_dict = eval(details_clean)

                car_model_name = self.try_get_data(details_dict, 'makesOffer', 'itemOffered', 'vehicleEngine', 'name')
                car_year = self.try_get_data(details_dict, 'makesOffer', 'itemOffered', 'modelDate')
                car_km = self.try_get_data(details_dict, 'makesOffer', 'itemOffered', 'mileageFromOdometer').split('.')[0]
                car_power = get_car_power(car_model_name)
                car_transmission = get_car_transmission(car_model_name)
                car_ad_price = self.try_get_data(details_dict, 'makesOffer', 'priceSpecification', 'price')
                car_fipe_exact, car_fipe_min, car_fipe_max = self.get_fipe_price(car_brand,
                                                                                 car_model,
                                                                                 car_model_name,
                                                                                 car_year,
                                                                                 car_power,
                                                                                 car_transmission)
                car_ad_phone = self.get_phone_number()

                details_formatted = [
                    car_brand,
                    car_model,
                    car_model_name,
                    car_year,
                    car_km,
                    car_power,
                    car_transmission,
                    car_ad_price,
                    car_fipe_exact,
                    car_fipe_min,
                    car_fipe_max,
                    car_ad_phone,
                    ad_date,
                    ad_id,
                    ad_link,
                    self.today_date
                ]

                time.sleep(randint(1, 2))
                print('GET_AD_DETAILS TIME', time.time() - st4_1)
                print details_formatted

                olx_data.append(details_formatted)

            except Exception as e:
                print('ERROR', e)

        return olx_data


    def get_olx_data(self):
        """
        This function should fetch data from olx and write it to a file
        """
        # First, I will set a specific car to fetch, just for test purposes
        # Second, I will set 2 cars to fetch in a list, just for test purposes
        # Finally, I will set it to fetch all cars for FIPE or a specifc one if the args say so
        car_model_list = list(self.tabela_fipe_df.modelo_code.unique())

        for car_index, car_model in enumerate(car_model_list):
            if car_index >= 19:
                car_model = get_car_model_code_fixed(car_model.lower())
                car_brand = get_brand_from_model(car_model).lower()

                page_range = self.get_number_of_ad_pages(car_brand, car_model)

                ad_info_list = self.get_page_ad_info(car_brand, car_model, page_range)
                print('LEN AD INFO LIST', len(ad_info_list))

                pages_to_fetch_list = self.get_pages_to_fetch(ad_info_list)
                print('LEN PAGES TO FETCH LIST', len(pages_to_fetch_list))

                olx_data_list = self.get_ad_details(pages_to_fetch_list, car_brand, car_model)

                headers = [
                    'car_brand', 'car_model_code', 'car_model_name', 'car_year', 'car_km', 'car_power',
                    'car_transmission', 'car_price', 'fipe_price_exact', 'fipe_price_min', 'fipe_price_max',
                    'phone_number', 'ad_date', 'ad_id', 'ad_link', 'fetch_datetime'
                ]

                old_data_df = pd.DataFrame(olx_data_list, columns=headers)

                output_key = self.storage_dir + self.output_filename.format(car_brand,
                                                                            car_model,
                                                                            self.file_date)
                old_data_df.to_csv(output_key , index=False)


if __name__ == "__main__":
    olx_scrape = OLXScrape()
    olx_scrape.get_olx_data()