#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import json


URL = "http://jakzawszetazla.tumblr.com/"
LNAME = 'Tumblr'
POST_IID = 1
NUMBER_OF_PAGES = 50
CHUNK_SIZE = 50


class Post(object):
    def __init__(self):
        self.lname = ''
        self.url = ''
        self.iid = 0
        self.id = 0
        self.category = ''
        self.title = ''
        self.date = ''
        self.text = ''

        self.more_link = ''
        self.full_text = ''

    def __str__(self):
        return '; '.join((str(self.lname),
                          str(self.url),
                          str(self.iid),
                          str(self.id),
                          str(self.category),
                          str(self.title),
                          str(self.date),
                          str(self.text)))


def save_as_json(post):
    return json.dumps({"lname": post.lname,
                       "url": post.url,
                       "iid": post.iid,
                       "id": post.id,
                       "category": post.category,
                       "title": post.title,
                       "date": post.date,
                       "text": post.text}, sort_keys=True, indent=4)


def extract_post(main_div, url):
    """Extract post from main div
    """
    post = Post()
    global LNAME
    post.lname = LNAME
    global POST_IID
    post.iid = POST_IID
    POST_IID += 1
    post.id = post.iid - 1
    post.url = url

    for div in main_div.find_all('div'):
        print('found2')
        if 'post-excerpt__category' in div.get('class'):
            post.category = div.contents[0].strip()
        elif 'date-note-wrapper' in div.get('class'):
            post.date = div.contents[0].strip()
        elif 'post-content' in div.get('class'):
            print('found')
            for fill in div.find_all('a'):
                post.text = ''.join(fill.findAll(text=True))
                #post.text = fill.contents[0].strip()

    for header in main_div.find_all('h2'):
        if 'title' in header.get('class'):
            #for link in header.find_all('a'): 
            post.title = header.contents[0]

    return save_as_json(post)


def crawl_page(url):
    """Retrieve whole page data
    """
    request = requests.get(url)
    data = request.text
    soup = BeautifulSoup(data, 'html.parser')

    posts = []
    for div in soup.find_all('div'):
        if div.get('class') == None:
            continue
        elif 'data-page-id' in div.get('class'):
            print('found3')
            post = extract_post(div, url)
            posts.append(post)
    return posts


def save_to_file(chunk, chunk_no):
    fname = 'uj_posts_{}'.format(chunk_no)
    with open(fname, 'w') as f:
        for post in chunk:
            f.write(str(post) + '\n')


def split_into_chunks(l, n):
    """Yield successive n-sized chunks from a list.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main():
    """Main function
    """
    print('Crawling {} pages from http://www.uj.edu.pl ...'.format(NUMBER_OF_PAGES))
    all_posts = []
    for page_no in range(1, 51): #575
        url = '{0}&strona={1}'.format(URL, page_no)
        posts = crawl_page(url)
        all_posts.extend(posts)

    if all_posts:
        print('Number of posts extracted: {}'.format(len(all_posts)))
        print('Saving posts to files ...')
        chunks = split_into_chunks(all_posts, CHUNK_SIZE)
        for chunk_no, chunk in enumerate(chunks):
            save_to_file(chunk, chunk_no + 1)
        print('Posts saved.')
    else:
        print('No posts extracted.')


if __name__ == '__main__':
    #main()
	print('crawling...')
	post = crawl_page(URL)
	print('saving...')
	with open('test', 'w') as f:
		f.write(str(post))
	print('done')
