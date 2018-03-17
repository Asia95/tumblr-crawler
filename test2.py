# -*- coding: utf-8 -*-
import oauth2
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import parse_qsl
import pytumblr
import sys
import json
import requests

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

class TumblrPost:
    def __init__(self, post_url, post_date, post_text, post_source, post_title):
        self.post_url = post_url
        self.post_date = post_date
        self.post_text = post_text
        self.post_source = post_source
        if post_title is None or post_title == '':
            self.post_title = ''
        else:
            self.post_title = post_title

if __name__ == '__main__':

    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    AUTHORIZATION_URL = 'http://www.tumblr.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
    CONSUMER_KEY = 'g0O4zsc8t13R1QfxhDyHUMI5cacguSgDA5RkcODvmAXB0roSxw'
    CONSUMER_SECRET = 'efAKZwZAoYFadDQdOwcFMZDeRs0DdTURnF21AUBNt1UEB6SL9H'

    # consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    # client = oauth2.Client(consumer)

    # resp, content = client.request(REQUEST_TOKEN_URL, "GET")

    # request_token = dict(urllib.parse.parse_qsl(content))
    # OAUTH_TOKEN = request_token['oauth_token']
    # OAUTH_TOKEN_SECRET = request_token['oauth_token_secret']

    # print("Request Token:")
    # print("    - oauth_token        = %s" % OAUTH_TOKEN)
    # print("    - oauth_token_secret = %s" % OAUTH_TOKEN_SECRET)

    # client = pytumblr.TumblrRestClient(
        # CONSUMER_KEY,
        # CONSUMER_SECRET,
        # OAUTH_TOKEN,
        # OAUTH_TOKEN_SECRET
    # )
    
    client = pytumblr.TumblrRestClient(
        'g0O4zsc8t13R1QfxhDyHUMI5cacguSgDA5RkcODvmAXB0roSxw',
        'efAKZwZAoYFadDQdOwcFMZDeRs0DdTURnF21AUBNt1UEB6SL9H',
        'yxtXBt1QpDcFBNcDnrkuWAUQ21DGqvMWBvbTp8XUgbErR5bbbO',
        'hcexmraSPytPGtQDxZ14TYYHf06wvSKdbbgRRGlNwqKXUFV2Ka'
    )

    
 
    request_url = 'http://api.tumblr.com/v2/blog/jakzawszetazla.tumblr.com/posts/text?api_key=fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4'
    offset = 0
    posts_still_left = True
    all_posts = []
    
    while posts_still_left:
        request_url += "&offset=" + str(offset)
        #response = requests.get(request_url)
        #tumblr_response = json.loads(response.text)
        #uprint(tumblr_response)
        tumblr_response = requests.get(request_url).json()
        print(str(tumblr_response))
        total_posts = tumblr_response["response"]["total_posts"]
        for post in tumblr_response['response']['posts']:
            # Do something with the JSON info here
            p = TumblrPost(post['post_url'], post['date'], post['body'], '', post['title'])
            all_posts.append(p)
            all_posts.append(post)
        offset = offset + 20
        if offset > total_posts:
            posts_still_left = False

    with open('test3', 'w', encoding='utf-8') as f:
        for post in all_posts:
            f.write(str(post))
    # info = client.blog_info('jakzawszetazla')
    # #post = client.posts('jakzawszetazla')
    
    # with open('test3', 'w', encoding='utf-8') as f:
    #     f.write(str(info))
    #     f.write((all_posts))
