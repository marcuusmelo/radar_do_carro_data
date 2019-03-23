from datetime import datetime
import pandas as pd
import urllib2
from bs4 import BeautifulSoup
from generic_functions import check_if_folder_exists_than_crete
from fipe_api_fetch import get_fipe_table


def get_olx_link_list(quote_page, page_number):
    """ Get a list of links for a olx ad search """
    quote_page = quote_page.format(page_number)
    page = urllib2.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')

    page_link = soup.find_all('a', attrs={'class':'OLXad-list-link'})
    link_list = [x.get('href') for x in page_link]

    return link_list


def get_ad_date(ad_soup):
    """ Get the date that the ad was published """
    month_dict = {'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'mai': '05', 'jun': '06',
                  'jul': '07', 'ago': '08', 'aet': '09', 'out': '10', 'nov': '11', 'dez': '12'}

    ad_date_section = ad_soup.find('div', attrs={'class':'OLXad-date'})
    ad_date_raw = ''.join(ad_date_section.contents[1]).encode('utf-8').strip().replace('Inserido em: ', '').split(' ')

    ad_date_day = ad_date_raw[0]
    if len(ad_date_day) == 1:
        ad_date_day = '0' + ad_date_day

    ad_date_month = month_dict[ad_date_raw[1].lower()[0:3]]

    ad_date_time = ad_date_raw[3] + ':00'

    ad_date_year = str(datetime.now().year)
    date_now_month = datetime.now().month
    if int(ad_date_month) > date_now_month:
        ad_date_year = str(int(ad_date_year)-1)

    ad_date_complete = ad_date_day + '-' + ad_date_month + '-' + ad_date_year + ' ' + ad_date_time

    return ad_date_complete


def get_car_age(car_year):
    """ Get car age given its year and actual date """
    this_year = datetime.now().year
    car_age = this_year - int(car_year)

    return car_age


def get_car_power(car_model):
    """ Get car power from model description """
    car_power = ''
    if '1.0' in car_model:
        car_power = '1.0'
    elif '1.6' in car_model:
        car_power = '1.6'

    return car_power



def get_preco_fipe(car_power, car_year):
    """ Get preco fipe from fipe table file previously generated """
    if car_power != '':
        fipe_data = FIPE_DF.loc[(FIPE_DF['veiculo'].str.contains(car_power)) & (FIPE_DF['ano_modelo'] == car_year)]

        if fipe_data.shape[0] > 0:
            preco_fipe = fipe_data['preco'].iloc[0].replace('R$ ', '').replace('.', '').replace(',00', '')
            return preco_fipe

    else:
        return ''


def try_get_data(details_dict, key1, key2='', key3='', key4=''):
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


def get_ad_details(ad_link, today_date):
    """ Get relevant info from ad """
    ad_page = urllib2.urlopen(ad_link)
    ad_soup = BeautifulSoup(ad_page, 'html.parser')

    ad_date = get_ad_date(ad_soup)

    ad_details = ad_soup.find('script', attrs={'type':'application/ld+json'})

    details_raw = ad_details.contents[0]
    details_clean = ''.join(details_raw).encode('utf-8').strip()
    details_dict = eval(details_clean)

    details_formatted = [''] * 22

    details_formatted[0] = ad_link.split('-')[-1]
    details_formatted[1] = ad_date
    details_formatted[2] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'brand')
    details_formatted[3] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'vehicleEngine', 'name')
    details_formatted[4] = get_car_power(details_formatted[3])
    details_formatted[5] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'modelDate')
    details_formatted[6] = get_car_age(details_formatted[5])
    details_formatted[7] = try_get_data(details_dict, 'makesOffer', 'priceSpecification', 'price')
    details_formatted[8] = get_preco_fipe(details_formatted[4], details_formatted[5])
    details_formatted[9] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'mileageFromOdometer').split('.')[0]
    details_formatted[10] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'vehicleTransmission')
    details_formatted[11] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'description')
    details_formatted[16] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'bodyType')
    details_formatted[17] = try_get_data(details_dict, 'makesOffer', 'itemOffered', 'numberOfDoors')
    details_formatted[18] = ad_link
    details_formatted[19] = try_get_data(details_dict, 'name')
    details_formatted[21] = today_date

    return details_formatted


def get_car_leads():
    """ Get relevant info from up to 200 ads of OLX  """
    today_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    model_link = 'https://df.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/hyundai/hb20?f=p&o={0}&rs=34'
    car_model = 'HB20'

    link_list = []

    for page_number in range(1, 5):
        link_list += get_olx_link_list(model_link, page_number)

    headers = ['id_anuncio', 'data_anuncio', 'marca', 'modelo', 'motor', 'ano',
               'idade', 'preco', 'fipe', 'km_odometro', 'transmissao', 'descricao',
               'unico_dono', 'so_bsb', 'garantia', 'revisoes_em_dia', 'hatch/sedan',
               'portas', 'link', 'vendedor', 'contato', 'data_scan']

    ad_details_list = []

    for index, ad_link in enumerate(link_list):
        print ad_link
        ad_details_list.append(get_ad_details(ad_link, today_date))

    ad_details_df = pd.DataFrame(ad_details_list, columns=headers)

    output_path = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/'
    output_file = '{0}olx_scan_{1}_{2}.csv'.format(output_path, car_model, today_date.split()[0])
    check_if_folder_exists_than_crete(output_path)

    ad_details_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    FIPE_FILE = get_fipe_table()
    FIPE_DF = pd.read_csv(FIPE_FILE)
    FIPE_DF['veiculo'] = FIPE_DF['veiculo'].str.lower()

    get_car_leads()
