from functools import partial

from bs4 import BeautifulSoup, SoupStrainer
import requests
import os
import urllib.request
import time
import multiprocessing

s = time.time()
img_list = ['.jpg', '.png', '.gif', '.jpeg']
img_url_From = 'http://image.dcinside.com/download'
img_url_To = 'http://dcimg7.dcinside.co.kr/viewimage'


class IMG_crawl:
    def __init__(self, markup='lxml', timeout=5, include_comments=False):
        self._view_url = 'http://gall.dcinside.com/board/view'
        self._session = requests.Session()
        self._timeout = timeout
        self._markup = markup
        self._strainer = SoupStrainer('div', attrs={
            'class': [
                's_write',
                'box_file',
                're_gall_box_3',
            ]})
        self._include_comments = include_comments

    def get_post(self, gall_id, post_no, minor=True):
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        url = self._view_url
        if minor: url = 'http://gall.dcinside.com/mgallery/board/view'
        r = self._session.get('%s/?id=%s&no=%d' % (url, gall_id, post_no), timeout=self._timeout, headers=header)
        parse_post(r.text, 'lxml', self._strainer, gall_id, post_no)


def parse_post(markup, parser, strainer: SoupStrainer, gall_id, post_no):
    soup = BeautifulSoup(markup, parser, parse_only=strainer)
    if not str(soup):
        soup = BeautifulSoup(markup, parser)
        if str(soup) in '/error/deleted/':
            return {'deleted': True}
        elif str(soup) in '해당 갤러리는 존재하지 않습니다':
            raise NoSuchGalleryError
        else:
            pass

    print('post_no : ' + str(post_no))
    try:
        if soup.find('div', {"class": 'box_file'}).find_all('a') is not None:
            img_all = soup.find('div', {"class": 'box_file'}).find_all('a')

        print('post_img_cnt : ' + str(len(img_all)))

        img_no = 0

        for img_all_src in img_all:
            url = str.replace(img_all_src.get('href'), img_url_From, img_url_To)
            get_img(gall_id, post_no, img_no, url)
            img_no = img_no + 1

        print('complete')
    except:
        print('fail...')
        pass

    print('---------------')


class NoSuchGalleryError(Exception):
    pass


def get_img(gall_id, post_no, no, url):
    name = gall_id + '_' + str(post_no) + '_' + str(no)
    full_name = str(name) + ".jpg"
    path = os.path.join(gall_id)
    urllib.request.urlretrieve(url, path + '/' + full_name)


if __name__ == '__main__':

    gall_id = 'micateam'
    start_post_no = 474075
    end_post_no = 474175

    interval = []
    for i in range(start_post_no, end_post_no + 1):
        interval.append(i)
    print(interval)

    try:
        if not (os.path.isdir(gall_id)):
            os.makedirs(os.path.join(gall_id))
    except OSError as e:
        pass

    img = IMG_crawl()
    func = partial(img.get_post, gall_id)

    pool = multiprocessing.Pool(processes=4)
    pool.map(func, interval)
    pool.close()
    pool.join()

    e = time.time()
    print("{0:.2f}초 걸렸습니다".format(e - s))
    print("현재까지 %s개의 이미지를 크롤링 했습니다." % len(os.listdir(gall_id)))
