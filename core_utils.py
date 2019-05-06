import errno
from time import sleep

import json
import logging
import os
import re
import csv
import requests
import random
from bs4 import BeautifulSoup

from banned_exception import BannedException
from constants import AMAZON_BASE_URL

OUTPUT_DIR = 'comments'

HEADERS_LIST = [
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def get_reviews_filename(product_id):
    filename = os.path.join(OUTPUT_DIR, '{}.json'.format(product_id))
    exist = os.path.isfile(filename)
    return filename, exist


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def write_to_csv(reviews, product_id):
    if len(reviews) == 0:
        return False
    filepath = os.path.join('reviews', '{}.csv'.format(product_id))
    with open(filepath, "w", encoding="utf-8", newline='') as output:
        f = csv.writer(output)
        f.writerow(["author", "author_url", "title", "rating", "verified", "types", "body", "product_id", "review_url", "review_date", "helpful"])
        for r in reviews:
            f.writerow([r['author'], r['author_url'], r['title'], r['rating'], r['verified'],
                r['types'], r['body'], r['product_id'],
                r['review_url'], r['review_date'], r['helpful']])

def persist_comment_to_disk(reviews):
    if len(reviews) == 0:
        return False
    product_id_set = set([r['product_id'] for r in reviews])
    assert len(product_id_set) == 1, 'all product ids should be the same in the reviews list.'
    product_id = next(iter(product_id_set))
    output_filename, exist = get_reviews_filename(product_id)
    if exist:
        return False
    mkdir_p(OUTPUT_DIR)
    # https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence/18337754
    with open(output_filename, 'w', encoding='utf-8') as fp:
        json.dump(reviews, fp, sort_keys=True, indent=4, ensure_ascii=False)
    return True


def extract_product_id(link_from_main_page):
    # e.g. B01H8A7Q42
    p_id = -1
    tags = ['/dp/', '/gp/product/']
    for tag in tags:
        try:
            p_id = link_from_main_page[link_from_main_page.index(tag) + len(tag):].split('/')[0]
        except:
            pass
    m = re.match('[A-Z0-9]{10}', p_id)
    if m:
        return m.group()
    else:
        return None


def get_soup(url):
    if AMAZON_BASE_URL not in url:
        url = AMAZON_BASE_URL + url
    nap_time_sec = 1
    logging.debug('Script is going to sleep for {} (Amazon throttling). ZZZzzzZZZzz.'.format(nap_time_sec))
    sleep(nap_time_sec)
    header = {
        'User-Agent': random.choice(HEADERS_LIST)
    }
    logging.debug('-> to Amazon : {}'.format(url))
    out = requests.get(url, headers=header)
    assert out.status_code == 200
    soup = BeautifulSoup(out.content, 'lxml')
    if 'captcha' in str(soup):
        raise BannedException('Your bot has been detected. Please wait a while.')
    return soup
