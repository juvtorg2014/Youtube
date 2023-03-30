import re
import time
from urllib import parse

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import selenium.webdriver.chrome.options as options

CHROMEDRIVER_PATH = 'C:\\Windows\\system32\\'
DOCUMENT = 'https://docs.python.org/'
DOWNLOAD = 'D:\\Downloads\\'

def get_selenium_url(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url=url)
        text = driver.page_source
        return text
    except Exception as e:
        print(e)



def parsing_youtube(download, url):
    html = get_selenium_url(url)
    soup = bs(html, 'html.parser')
    name_video = soup.text.split('YouTube')[0]
    name_video = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', name_video).replace(' ', '_')
    soup_class = soup.find('span', class_="yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap")
    text = soup.find('span', class_="yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap").text
    # text2 = soup.find('a', class_='yt-core-attributed-string__link yt-core-attributed-string__link--display-type
    # yt-core-attributed-string__link--call-to-action-color').attrs['href'].split('=https')[1]
    # url_text = "https" + urllib.parse.unquote(text2)
    url_list = soup_class.findAll('a')
    list_url = []
    for url_item in url_list:
        u_list = url_item.attrs['href'].split('=https')
        for u_l in u_list:
            if u_l[:9] == '%3A%2F%2F':
                list_url.append("https" + parse.unquote(u_l))
    n =0
    with open(name_video + ".txt", 'w', encoding='utf-8') as f:
        try:
            while n < len(list_url):
                f.writelines(list_url[n] + '\n')
            f.writelines('\n')
        except Exception as e:
            print(e)
        try:
            for line in text.split('\n'):
                f.write(line + '\n')
                print('Записан файл ')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # play_smth = input("Введите плейлист, видео или канал:\n")
    url_smth = 'https://www.youtube.com/watch?v=V1_8dbZFmm0&list=PLrzHY9riBq3bu8xnTqukuj_6JpWD8LFB5&index=16'
    parsing_youtube(DOWNLOAD, url_smth)
