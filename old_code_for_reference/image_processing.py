def get_phone_number(ad_soup):
    st_time = time.time()
    phone_img_link = ad_soup.find_all('span', {'id': 'visible_phone'})[0].find_all('img')[0]['src']

    # this is super slow (75s to execute)
    # try to speedup
    urllib.urlretrieve(phone_img_link, 'test_olx_img.gif')

    phone_img_file = Image.open('test_olx_img.gif').convert('RGB')
    phone_img_text = pytesseract.image_to_string(phone_img_file)

    # special cases formatting:
    phone_img_text.replace('/7', '7').replace('7/', '7')
    print('GET_PHONE_NUMBER TIME', time.time() - st_time)
    return phone_img_text
