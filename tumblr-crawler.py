# -*- coding: utf-8 -*-

# TO DO:
#     data - zmienić format
#     iid
#     pobrać posty z 100 blogów
#     json order not working
 
import sys
import time
import argparse
import urllib.parse
from urllib.parse import urlparse
import json
import requests
import html
from collections import OrderedDict
import hashlib 
 
class TumblrPost:
    def __init__(self, post_id, post_url, post_date, post_title, post_body):
        self.iid = 0
        self.id = post_id
        self.lname = "tumblr.com"
        self.post_url = post_url
        self.post_date = post_date        
        if post_title is None or post_title == '':
            self.post_title = ''
        else:
            self.post_title = post_title
        if post_body is None or post_body == '':
            self.post_body = ''
        else:
            self.post_body = post_body
 
def save_as_json(post):
    post_lname = post.lname
    post_url = post.post_url
    post_iid = post.iid
    post_id = post.id
    post_title = post.post_title
    post_content = post.post_body
    post_date = post.post_date
    post_dict = OrderedDict(lname= post_lname, url= post_url, iid= post_iid, id= post_id, title= post_title, content= post_content, duration_start= post_date, duration_end= post_date)
    # return json.dumps({"lname": post.lname,
    #                    "url": post.post_url,
    #                    "iid": post.iid,
    #                    "id": post.id,
    #                    "title": post.post_title,
    #                    "content": post.post_body,
    #                    "duration_start": post.post_date,
    #                    "duration_end": post.post_date}, object_pairs_hook=OrderedDict, sort_keys=False, indent=4, ensure_ascii=False)
    return json.dumps(post_dict, indent=4, ensure_ascii=False)

def remove_html_tags(text):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_blog_url(name):
    return "http://{name}.tumblr.com/api/read/json".format(name=name)
 
def get_json_page(url, start=0, num=50):
    args = {}
    args['start'] = start
    args['num'] = num
 
    # Fetch the page
    r = requests.get(url, params=args)
 
    # Strip the jsonp garbage
    text = r.text.strip()[22:-1]
    if "regular-title" in text:
        print("ok")
 
    # Return the result as a dict
    return json.loads(text)
 
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
 
def get_post(json, all_posts):
    found = False
    if 'tags' in json:
        tags = json['tags']
        #uprint(tags)
        if json['type'] == 'quote':
            body = json['quote-text']
            body = u"{}".format(body)
            #print(u"{}".format(body))
            title = ''
            found = True
 
        if json['type'] == 'regular':
            if "regular-body" in json:
                body = json['regular-body']
                body = u"{}".format(body)
            else:
                body = ''
            if "regular-title" in json:
                title = json['regular-title']
                title = u"{}".format(title)
            else:
                title = ''
            found = True
 
        if found:
            if title == '':
                words_body = body.split()
                if len(words_body) >= 6:
                    title = ' '.join(words_body[:6])
                else:
                    title = body
                title += '...'

            #m = hashlib.md5()
            post_id = hashlib.md5(json['url'].encode('utf-8')).hexdigest()

            p = TumblrPost(post_id, json['url'], json['date-gmt'], html.unescape(remove_html_tags(title)), html.unescape(remove_html_tags(body)))
            all_posts.append(p)
 
def main():
    #global parser
    #parser = argparse.ArgumentParser(prog='tumblr-scraper',
            #description='Get Tumblr blog posts')
 
    # Set up our command-line arguments
    #parser.add_argument('blog_name')   
 
    #args = parser.parse_args()
 
    #blog_name = args.blog_name
    blog_name = 'czytanki'
    blog_url = get_blog_url(blog_name)
 
    json = get_json_page(blog_url, 0, 0)
    total_count = json['posts-total']
 
    uprint('Total posts: %s' % (total_count,))
 
    start_time = time.time()

    all_posts = []
    start = 0
    per_page = 50
    while start < total_count:
        json = get_json_page(blog_url, start)
 
        for post in json['posts']:
            get_post(post, all_posts)
 
        # Increment and grab the next batch of posts
        start += per_page
 
    with open('posts.json', 'w', encoding='utf-8') as f:
        for post in all_posts:
            f.write(save_as_json(post))
            f.write('\n')
 
    minutes, seconds = divmod(time.time() - start_time, 60)
    uprint('Got {count} posts in {m:02d}m and {s:02d}s'.format(\
            count=total_count, m=int(round(minutes)), s=int(round(seconds))))
 
if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()