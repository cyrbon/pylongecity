import webbrowser
from tempfile import NamedTemporaryFile
from pylongecity.styles import head
from typing import List, Optional, Iterable
from pylongecity.scraper import Post
from pyquery import PyQuery as pq
import re


def render_to_html(posts: List[Post]) -> str:
    ''' Creates human viewable .html with posts, includes <head> with styles. '''
    posts_html = ''
    for p in posts: posts_html += p.html

    body = '<body>' + posts_html + '</body>'
    return head + body

def write_and_open_in_browser(html: str, filepath: Optional[str]):
    ''' Writes html to filepath and opens it. '''
    file = NamedTemporaryFile('w', encoding='utf-8', delete=False) if filepath is None else open(filepath, 'w', encoding='utf-8')
    file.write(html)
    file.close()
    webbrowser.open(file.name)

def render(posts: Iterable[Post], output_filepath: Optional[str] = None):
    ''' Puts html from posts into output_filepath (.html) and opens that in a specified browser '''
    posts = list(posts)
    if posts:
        write_and_open_in_browser(render_to_html(posts), output_filepath)
    else: print('Nothing found')

def has(ls, elems):
    '''
    >>> has("will find this and also this in a string", ['find this', 'also this'])
    True

    '''
    return all(s in ls for s in elems)

def has_any(ls, elems):
    return any(s in ls for s in elems)

def search(posts: List[Post], *words: List[str]):
    ''' Searches posts for words and displays filtered results in a browser. '''
    render(filter(lambda p: has(p.content, words), posts))

#######################################################################################################################

def parse_links(post: Post) -> List[str]:
    return [pq(l).attr('href') for l in pq(post.html).find('.post_body').find('a[href!="#ipboard_body"]')]

def match_links(post: Post, *re_patterns: List[str], **kwargs) -> List[str]:
    not_ = kwargs.pop('not_', [])

    links = parse_links(post)
    matches = []
    for l in links:
        if(any([re.compile(r).search(l)
                and not any(re.compile(r_).search(l) for r_ in not_)
                for r in re_patterns])):
            matches.append(l)
    return matches

def has_links(posts: List[Post], *patterns, **kwargs) -> Iterable[Post]:
    '''
    Returns all posts which have matching links in them.
    Args:
        post (List[Post]): Posts to filter
        *patterns (List[str]): Patterns which links should match
        not (List[str]) : Patterns which links should not match. E.g., not=['google', 'longecity', 'amazon']

    '''
    return filter(lambda p: (len(match_links(p, *patterns, **kwargs)) > 0), posts)


