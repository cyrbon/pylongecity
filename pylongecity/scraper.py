from pyquery import PyQuery as pq
from typing import List
import requests
from joblib import Memory
import concurrent
from concurrent import futures
import re
from datetime import datetime
import os

memory = Memory(cachedir=os.path.expanduser('~') + '/.cache/pylongecity')

class Post:
    def __init__(self):
        self.author = None
        self.date = None
        self.rating = None
        self.html = None
        self.content = None
        self.id = None

def scrape_page(url: str, verbose: bool) -> str:
    if verbose: print('Downloading: ' + url)
    return requests.get(url).text

def parse_posts(page: str) -> List['Post']:
    unparsed_posts = pq(page).find('.post_block')
    posts = []
    for post_el in unparsed_posts:
        spost = pq(post_el)
        # If it's an ad placeholder, then we skip it
        if spost.attr('id') == 'post_id_': continue

        post = Post()

        post.id = int(spost.find('.post_id').text().strip('#'))
        post.author = spost.find('.author').text()
        date_str = spost.find('.published').attr('title')
        # '2014-02-15T01:10:16+00:00'
        post.date = datetime.strptime(date_str.split('+')[0], '%Y-%m-%dT%H:%M:%S')
        rating_text = spost.find('.rating_totals').text()
        post.rating = {}
        # 'like x 23 dislike x 1 Enjoying the show x 1'
        matches = re.findall('([A-z\s]+) x ([0-9]+)', rating_text)
        for rating_key, rating_value in matches:
            post.rating[rating_key.strip()] = int(rating_value)

        scontent = spost.find('.entry-content')
        post.content = scontent.text()
        post.html = spost.outerHtml()

        posts.append(post)
    return posts

def scrape_posts(url: str, verbose: bool) -> List['Post']:
    return parse_posts(scrape_page(url, verbose))

def scrape_all_posts_unflat(url: str, verbose: bool, cache: bool) -> List[List['Post']]:
    unflat_posts = []

    fget = requests.get if not cache else memory.cache(requests.get)
    page = fget(url).text # Downloads the page twice.
    # ^ we can scrape_page(page), .append, [urls - url], but KISS.
    n_of_pages = pq(page).find('.pagejump > a').eq(0).text().strip().split(' ')[-1] # Gets '10' from 'Page 1 of 10'

    # If there is only one page
    if(n_of_pages is ''):
        urls = [url]
    else:
        url_prefix_match = re.match('(.*)(page-[0-9]+)', url)
        url_prefix = url if url_prefix_match is None else url_prefix_match.group(1)
        if(url_prefix[-1] != '/'): url_prefix += '/'
        urls = [(url_prefix + 'page-' + str(n + 1)) for n in range(int(n_of_pages))]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        fscrape = scrape_posts if not cache else memory.cache(scrape_posts, ignore=['verbose'])
        futures = [executor.submit(fscrape, url, verbose) for url in urls]
        results, _ = concurrent.futures.wait (futures)
        for result in results:
            unflat_posts.append(result.result())
    return unflat_posts

def scrape_all_posts(url: str, verbose: bool = False, cache: bool = True) -> List['Post']:
    # We want a list, not an iterable, to have len and other methods available.
    posts = [v for slist in scrape_all_posts_unflat(**locals()) for v in slist]
    return sorted(posts, key= lambda p: p.id)

def get_posts(*urls : List[str], **kwargs):
    '''
    Args:
        *urls (List[str]): Url, where each url is a unique thread
        verbose (bool): Verbosity
        cache (bool): Cache results across calls
        disambiguate_threads (bool): When scraping multiple threads will add url to html of the first post to show thread.
    '''
    posts_unflat = []
    disambiguate_threads = True if 'disambiguate_threads' not in kwargs else kwargs['disambiguate_threads']
    kwargs.pop('disambiguate_threads', None)
    for url in urls:
        posts = scrape_all_posts(url, **kwargs)
        # Displaying a link title to show which posts come from which thread if
        # we are getting multiple threads.
        if(disambiguate_threads and len(urls) > 1):
            posts[0].html = '''
            <div style="background-color: #3B6796;">
                <a href="{0}"><h1 style="font-size: 40px; color: white;">{0}</h1></a>
            </div>'''.format(url) + posts[0].html
        posts_unflat.append(posts)

    return [p for slist in posts_unflat for p in slist]
