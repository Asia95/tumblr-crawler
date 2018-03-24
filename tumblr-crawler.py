# -*- coding: utf-8 -*-

# TO DO:
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

    def __init__(self, post_iid, post_url, post_date, post_title, post_body):
        self.iid = post_iid
        self.id = post_iid + "-1"
        self.lname = "tumblr.com"
        self.post_url = post_url
        self.post_date = post_date
        self.post_title = self.check_if_empty(post_title)
        self.post_body = self.check_if_empty(post_body)

    def check_if_empty(self, text):
        if text is None or text == "":
            text = ""
        return text

def save_as_json(post):
    post_lname = post.lname
    post_url = post.post_url
    post_iid = post.iid
    post_id = post.id
    post_title = post.post_title
    post_content = post.post_body
    post_date = post.post_date
    return ({"lname": post.lname,
                       "url": post.post_url,
                       "iid": post.iid,
                       "id": post.id,
                       "title": post.post_title,
                       "content": post.post_body,
                       "duration_start": post.post_date,
                       "duration_end": post.post_date})
    # post_dict = OrderedDict(
    #     lname= post_lname,
    #     url= post_url,
    #     iid= post_iid,
    #     id= post_id,
    #     title= post_title,
    #     content= post_content,
    #     duration_start= post_date,
    #     duration_end= post_date
    # )
    # #return json.dumps(post_dict, indent=4, ensure_ascii=False)
    # return post_dict

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
 
    # Return the result as a dict
    return json.loads(text)
 
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def create_title(body):
    words_body = body.split()
    if len(words_body) > 6:
        title = " ".join(words_body[:6])
    else:
        title = body
    title += "..."
    return title

def get_and_save_post(json_page, all_posts):
    found = False
    if 'tags' in json_page:
        
        if json_page['type'] == 'quote':
            
            body = json_page['quote-text']
            title = ""
            found = True
 
        if json_page['type'] == 'regular':

            body = json_page['regular-body'] if "regular-body" in json_page else ""
            title = json_page['regular-title'] if "regular-title" in json_page else ""
            found = True
 
        if found:
            title = create_title(body) if title == '' else title

            # Create iid for solar
            post_iid = hashlib.md5(json_page['url'].encode('utf-8')).hexdigest()
            # Date format for solar
            date = json_page['date-gmt'].split(' ')
            post_date = '{}T{}Z'.format(date[0], date[1])

            body = html.unescape(remove_html_tags(u"{}".format(body)))
            title = html.unescape(remove_html_tags(u"{}".format(title)))

            p = TumblrPost(post_iid, json_page['url'], post_date, title, body)
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
    json_page = get_json_page(blog_url, 0, 0)
    total_count = json_page['posts-total'] 
    uprint('Total posts: %s' % (total_count,))
 
    start_time = time.time()

    # Get posts
    all_posts = []
    start = 0
    per_page = 50
    while start < total_count:
        json_page = get_json_page(blog_url, start)
 
        for post in json_page['posts']:
            get_and_save_post(post, all_posts)
 
        # Increment and grab the next batch of posts
        start += per_page

    # Save to file
    with open('posts.json', 'w', encoding='utf-8') as f:
        posts = {}
        posts['posts'] = []
        for post in all_posts:
            posts['posts'].append(save_as_json(post))
        f.write(json.dumps(posts, indent=4, ensure_ascii=False))
 
    minutes, seconds = divmod(time.time() - start_time, 60)
    uprint('Got {count} posts in {m:02d}m and {s:02d}s'.format(\
            count=total_count, m=int(round(minutes)), s=int(round(seconds))))

    add_to_solar()

def add_to_solar():
    # server = 
    # core = 'isi'
    # url = 'http://%s:8983/solr/%s/update/json/docs?commit=true' % (server, core)

    posts = []
    with open('posts.json', encoding='utf-8') as get_post:
        tmp = json.load(get_post)

    for p in tmp['posts']:
        posts.append(p)

        # data = json.dumps(p, ensure_ascii=False)
        # req = urllib2.Request(url, data)
        # req.add_header('Content-type', 'application/json')
        # response = urllib2.urlopen(req)
        # the_page = response.read()
        # print(the_page)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()