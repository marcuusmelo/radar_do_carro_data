import os
import subprocess
from datetime import date
import pandas as pd


def download_car_ad_full(car_ad_full_path):
    download_command_base = 'mongoexport -h ds127983.mlab.com:27983 -d heroku_n7zq8f93 -c radar_do_carro_main_caraddata -u marcuusmelo -p Kb915597 -o {0} --csv -f car_brand,car_model_code,car_model_name,car_year,car_km,car_power,car_transmission,car_price,fipe_price_exact,fipe_price_min,fipe_price_max,phone_number,ad_date,ad_id,ad_link,fetch_datetime'
    download_command_final = download_command_base.format(car_ad_full_path)
    subprocess.call(download_command_final.split())

    return car_ad_full_path


def get_price_diff(df_row):
    if str(df_row['fipe_price_exact']) != 'nan':
        price_diff = df_row['car_price'] - df_row['fipe_price_exact']
    elif str(df_row['fipe_price_min']) != 'nan':
        price_diff = df_row['car_price'] - df_row['fipe_price_min']
    else:
        price_diff = df_row['car_price']

    return price_diff


def get_car_leads(min_km=0, max_km=40, min_year=2015, min_price_diff=-6000, max_price_diff=1000):
    today_date = str(date.today())
    storage_path = '/Users/marcusmelo/Desktop/projects/storage_car_dealer_br/00full_export/'

    car_ad_full_filename = 'car_ad_full_export_' + today_date.replace('-', '') + '.csv'
    car_ad_full_path = download_car_ad_full(storage_path + car_ad_full_filename)
    car_ad_df = pd.read_csv(car_ad_full_path)

    selected_models = ['GOL', 'UP', 'ONIX', 'HB20S', 'HB20', 'FIESTA',
                       'SANDERO', 'KA',  'CIVIC',  'COROLLA',  'UNO']

    # Filter on models, km, year
    selected_models_data_df = car_ad_df[car_ad_df['car_model_code'].isin(selected_models)]
    car_km_df = selected_models_data_df[(selected_models_data_df['car_km'] > min_km) & (selected_models_data_df['car_km'] < max_km)]
    car_year_df = car_km_df[car_km_df['car_year'] >= min_year]

    # create new empty column
    car_year_df['price_diff'] = ''


    for index, df_row in car_year_df.iterrows():
        car_year_df['price_diff'][index] = get_price_diff(df_row)

    # Filter price diff and sort on it
    car_leads_df = car_year_df[(car_year_df['price_diff'] > min_price_diff) & (car_year_df['price_diff'] < max_price_diff)].sort_values('price_diff')

    # Write output to  csv
    leads_output_path = car_ad_full_path.replace('full_export', 'leads')
    car_leads_df.to_csv(leads_output_path, index=False)


if __name__ == "__main__":
    get_car_leads()
