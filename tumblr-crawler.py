# -*- coding: utf-8 -*-

# TO DO:
#     html5 entities
#     html - beautifulsoup
#     data - zmienić format
#     id i iid - użyć md5
#     title - 6 wyrazów z body
#     povrać posty z 100 blogów
 
import sys
import time
import argparse
import urllib.parse
from urllib.parse import urlparse
import json
import requests
 
class TumblrPost:
    def __init__(self, post_url, post_date, post_title, post_body):
        self.iid = 0
        self.id = 0
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
    return json.dumps({"lname": post.lname,
                       "url": post.post_url,
                       "iid": post.iid,
                       "id": post.id,
                       "title": post.post_title,
                       "content": post.post_body,
                       "duration_start": post.post_date,
                       "duration_end": post.post_date}, sort_keys=False, indent=4, ensure_ascii=False)
 
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
 
def print_post(json, all_posts):
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
            p = TumblrPost(json['url'], json['date-gmt'], title, body)
            all_posts.append(p)
 
def main():
    # Create our parser
    #global parser
    #parser = argparse.ArgumentParser(prog='tumblr-scraper',
            #description='Get Tumblr blog posts')
 
    # Set up our command-line arguments
    #parser.add_argument('blog_name')   
 
    # Get our arguments
    #args = parser.parse_args()
 
    # Get our args
    #blog_name = args.blog_name
    blog_name = 'czytanki'
    blog_url = get_blog_url(blog_name)
 
    # Get the total post count
    json = get_json_page(blog_url, 0, 0)
    total_count = json['posts-total']
 
    # INFO
    uprint('Total posts: %s' % (total_count,))
 
    # Start our elapsed timer
    start_time = time.time()
 
    # This is the main loop. We'll loop over each page of post
    # results until we've archived the entire blog.
    all_posts = []
    start = 0
    per_page = 50
    while start < total_count:
        json = get_json_page(blog_url, start)
 
        # Loop over each post in this batch
        for post in json['posts']:
            print_post(post, all_posts)
 
        # Increment and grab the next batch of posts
        start += per_page
 
    with open('posts.json', 'w', encoding='utf-8') as f:
        for post in all_posts:
            f.write(save_as_json(post))
            f.write('\n')
 
    # INFO
    minutes, seconds = divmod(time.time() - start_time, 60)
    uprint('Got {count} posts in {m:02d}m and {s:02d}s'.format(\
            count=total_count, m=int(round(minutes)), s=int(round(seconds))))
 
if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()