from datetime import datetime


def get_car_age(car_year):
    """ Get car age given its year and actual date """
    this_year = datetime.now().year
    car_age = this_year - int(car_year)

    return car_age


def get_car_power(car_model):
    """ Get car power from model description """
    power_list = ['1.0', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8',
                  '2.0', '2.2', '2.3', '2.4', '2.5', '2.7', '2.8',
                  '3.0', '3.2', '3.4', '4.0']
    car_power = '1.0'
    found = False
    for power_element in power_list:
        if power_element in car_model:
            found = True
            car_power = power_element
    #if found == False:
    #    print 'Car Power Not Found', car_model

    return car_power


def get_car_transmission(car_model):
    """ Get car transmission from model description """
    transm_list = ['Aut', 'AUT', 'Mec', 'MEC']

    transm_final = 'MEC'
    found = False

    for transm_element in transm_list:
        if transm_element in car_model:
            found = True
            transm_final = transm_element[:3].upper()
    #if found == False:
    #    print 'Transmission Type Not Found', car_model

    return transm_final


def get_car_model_code_fixed(car_model_code):
    """ Fix car codes to olx standard """
    car_fix_dict = {
        'ka+': 'ka-mais',
        'renegade1-8': 'renegade',
        'ka-mais': 'ka+',

    }

    if car_model_code in car_fix_dict.keys():
        car_model_code = car_fix_dict[car_model_code]

    return car_model_code


def get_brand_from_model(car_model):
    """ Model to Brand lookup """
    model_to_brand = {
        'cobalt': 'GM-CHEVROLET',
        'cruze': 'GM-CHEVROLET',
        'onix': 'GM-CHEVROLET',
        'prisma': 'GM-CHEVROLET',
        's10': 'GM-CHEVROLET',
        'spin': 'GM-CHEVROLET',
        'tracker': 'GM-CHEVROLET',
        'argo': 'FIAT',
        'cronos': 'FIAT',
        'mobi': 'FIAT',
        'siena': 'FIAT',
        'strada': 'FIAT',
        'toro': 'FIAT',
        'uno': 'FIAT',
        'ecosport': 'FORD',
        'fiesta': 'FORD',
        'focus': 'FORD',
        'fusion': 'FORD',
        'ka': 'FORD',
        'ka+': 'FORD',
        'ka-mais': 'FORD',
        'ranger': 'FORD',
        'city': 'HONDA',
        'civic': 'HONDA',
        'fit': 'HONDA',
        'hr-v': 'HONDA',
        'wr-v': 'HONDA',
        'creta': 'HYUNDAI',
        'hb20': 'HYUNDAI',
        'hb20s': 'HYUNDAI',
        'compass': 'JEEP',
        'renegade': 'JEEP',
        'renegade1-8': 'JEEP',
        'kicks': 'NISSAN',
        'sentra': 'NISSAN',
        'versa': 'NISSAN',
        'captur': 'RENAULT',
        'duster': 'RENAULT',
        'kwid': 'RENAULT',
        'logan': 'RENAULT',
        'sandero': 'RENAULT',
        'corolla': 'TOYOTA',
        'etios': 'TOYOTA',
        'hilux': 'TOYOTA',
        'yaris': 'TOYOTA',
        'amarok': 'VW-VOLKSWAGEN',
        'crossfox': 'VW-VOLKSWAGEN',
        'fox': 'VW-VOLKSWAGEN',
        'gol': 'VW-VOLKSWAGEN',
        'golf': 'VW-VOLKSWAGEN',
        'jetta': 'VW-VOLKSWAGEN',
        'polo': 'VW-VOLKSWAGEN',
        'saveiro': 'VW-VOLKSWAGEN',
        'up': 'VW-VOLKSWAGEN',
        'virtus': 'VW-VOLKSWAGEN',
        'voyage': 'VW-VOLKSWAGEN'
    }

    return model_to_brand[car_model]


def get_brand_from_id(code):
    """ ID to Brand lookup """
    id_to_brand = {
        '21': 'FIAT',
        '22': 'FORD',
        '23': 'GM-CHEVROLET',
        '25': 'HONDA',
        '26': 'HYUNDAI',
        '29': 'JEEP',
        '43': 'NISSAN',
        '48': 'RENAULT',
        '56': 'TOYOTA',
        '59': 'VW-VOLKSWAGEN',
    }

    return id_to_brand[code]
