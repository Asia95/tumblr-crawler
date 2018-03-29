# -*- coding: utf-8 -*-

import sys
import time
import argparse
import urllib.parse
from urllib.parse import urlparse
from langdetect import detect
import json
import requests
import html
import hashlib
import socket
#import pysolr

class TumblrPost:

    def __init__(self, post_iid, post_id, post_url, lang, post_date, post_title, post_body):
        self.iid = post_iid
        self.id = post_id
        self.lname = "tumblr.com"
        self.post_url = post_url
        self.post_lang = lang
        self.post_date = post_date
        self.post_title = self.check_if_empty(post_title)
        self.post_body = self.check_if_empty(post_body)

    def check_if_empty(self, text):
        if text is None or text == "":
            text = ""
        return text

def save_as_json(post):
    return ({"lname": post.lname,
                       "url": post.post_url,
                       "lang": post.post_lang,
                       "iid": post.iid,
                       "id": post.id,
                       "title": post.post_title,
                       "content": post.post_body,
                       "duration_start": post.post_date,
                       "duration_end": post.post_date})

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

    try:
        # Fetch the page
        r = requests.get(url, params=args)

        # Strip the jsonp garbage
        text = r.text.strip()[22:-1]

        # Return the result as a dict
        return json.loads(text)
    except requests.exceptions.ConnectionError:
        r.status_code = 'Connection refused'
        print('Connection refused. Waiting...')
        time.sleep(50)
        print('Trying again...')
    except UnicodeError:
        print('UnicodeError: label empty or too long. Skipping...')
    except:
        print('Error in page json.')

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

def get_and_save_post(json_page, all_posts, blog_lang):
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

            body = html.unescape(remove_html_tags(u"{}".format(body)))
            lang = detect(body)
            if lang == blog_lang:

                title = create_title(body) if title == '' or title == None else title

                # Create iid, id for solr
                post_iid = int(hashlib.md5(json_page['url'].encode('utf-8')).hexdigest()[0:10], 16)
                post_id = str(post_iid) + '-1'

                # Date format for solr
                date = json_page['date-gmt'].split(' ')
                post_date = '{}T{}Z'.format(date[0], date[1])

                title = html.unescape(remove_html_tags(u"{}".format(title)))

                p = TumblrPost(post_iid, post_id, json_page['url'], lang, post_date, title, body)
                all_posts.append(p)
                # print('Got %s language. Saving.' % lang)
                return True
            else:
                print('Got %s language. Not saving.' % lang)
                print('Searching for other blogs...')
                return False

links_to_blogs = set()
count = 0

def get_posts_from_blogs(blog_name, blog_lang, count_blogs):

    print('Getting posts from ' + blog_name + '...')

    blog_url = get_blog_url(blog_name)
    json_page = get_json_page(blog_url, 0, 0)
    if json_page == None:
        print('No such blog.')
    else:
        total_count = json_page['posts-total']
        uprint('Total posts: %s' % (total_count,))

        start_time = time.time()

        # Get posts
        all_posts = []
        global links_to_blogs
        start = 0
        per_page = 50
        ln_ok = True
        while start < total_count and total_count < 10000:
            json_page = get_json_page(blog_url, start)

            if 'posts' in json_page:
                for post in json_page['posts']:
                    if ln_ok:
                        ln_ok = get_and_save_post(post, all_posts, blog_lang)

                    if 'reblogged-root-name' in post:
                        link_to_blog = post['reblogged-root-name']
                        if not 'deactivated' in link_to_blog:
                            try:
                                r = requests.get(get_blog_url(link_to_blog))
                                if  r.ok:
                                    links_to_blogs.add(link_to_blog)
                            except requests.exceptions.ConnectionError:
                                r.status_code = 'Connection refused'
                                print('Connection refused')
                                time.sleep(50)
                            except UnicodeError:
                                print('UnicodeError: label empty or too long')

                # Increment and grab the next batch of posts
                start += per_page

        # Save to file
        file_name = 'posts%s.json' % count_blogs
        with open(file_name, 'w', encoding='utf-8') as f:
            posts = {}
            posts['posts'] = []
            for post in all_posts:
                p = save_as_json(post)
                posts['posts'].append(p)
            f.write(json.dumps(posts, indent=4, ensure_ascii=False))

        # all_posts_solr = []
        # for post in all_posts:
        #     p = save_as_json(post)
        #     all_posts_solr.append(p)
        # add_to_solr(all_posts_solr)

        global count
        if len(all_posts) != 0:
            count += 1

        minutes, seconds = divmod(time.time() - start_time, 60)
        uprint('Got {count} text posts in {m:02d}m and {s:02d}s'.format(\
                count=len(all_posts), m=int(round(minutes)), s=int(round(seconds))))

def add_to_solr(posts):
    server = '150.254.78.133'
    core = 'isi'
    solr_url = 'http://%s:8983/solr/%s' % (server, core)
    solr = pysolr.Solr(solr_url)

    solr.add(posts)

def main():
    global parser
    parser = argparse.ArgumentParser(prog='tumblr-crawler',
            description='Get Tumblr blog posts')

    # Set up command-line arguments
    parser.add_argument('blog_name')
    parser.add_argument('blog_lang')

    args = parser.parse_args()
    blog_name = args.blog_name
    blog_lang = args.blog_lang

    global links_to_blogs
    links_to_blogs.add(blog_name)

    # Get posts from 100 blogs
    print('Only getting posts if total number of posts is less than 10 000.')
    while len(links_to_blogs) != 0 and count < 100:
        get_posts_from_blogs(links_to_blogs.pop(), blog_lang, count)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit()
