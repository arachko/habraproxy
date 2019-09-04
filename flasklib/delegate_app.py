import html.parser
import re
import urllib.error
import urllib.request

from bs4 import BeautifulSoup
from flask import Response
from lxml import html as lhtml, etree

from flasklib.svg_path import svg_path

target_url = 'https://habr.com'


def href_update_lxml(full_html):
    full_html = full_html.decode('utf-8').replace('xlink', 'link').encode('utf-8')
    tree = lhtml.fromstring(full_html)
    for i in range(len(tree.xpath('//*[@href]'))):
        url = tree.xpath('//*[@href]')[i].get('href')
        url_to_local = 'https://habr.com/'
        if url.startswith(url_to_local):
            tree.xpath('//*[@href]')[i].set('href', f'http://127.0.0.1:5000/{url[len(url_to_local)::]}')
    return etree.tostring(tree)


def habr_words_update(soup):
    tags_list = ['div', 'a', 'h1', 'h2', 'h3', 'p', 'span', 'li', 'ul']
    for elem_g in soup.find_all({tag: True for tag in tags_list}):
        for elem_l in elem_g.find_all(text=re.compile('\w')):
            if len(re.findall(r'\b\w[a-zA-Zа-яА-Я]{5}\b', elem_l)) > 0:
                if '™' in elem_l or 'function' in elem_l or 'window' in elem_l or 'config' in elem_l:
                    break
                el_copy = str(elem_l)
                text_list = re.findall(r'\b\w[a-zA-Zа-яА-Я]{5}\b', elem_l)
                for i in range(len(text_list)):
                    if text_list[i].endswith('\n'):
                        text_list[i] = text_list[i].replace('\n', '')
                    if len(text_list[i]) == 6 and not re.search('\W', text_list[i]):
                        el_copy = re.sub(r'\b%s\b' % text_list[i], f'{text_list[i]}™', el_copy)
                elem_l.replaceWith(el_copy)


def habr_code_str_update(soup):
    for code in soup.find_all('code'):
        code.replaceWith(str(code))


def habr_tags_update(soup):
    svg_names = ['eye', 'comment', 'vote-arrow', 'book', 'arrow-bold', 'slug', 'anchor', 'tree', 'rounded-arrow']
    for use in soup.find_all('use'):
        for svg in svg_names:
            if f'svg#{svg}' in str(use):
                use.replaceWith(svg_path[f'svg_{svg}'])


def text_update_soup(full_html):
    soup = BeautifulSoup(full_html)

    habr_words_update(soup)
    habr_code_str_update(soup)
    habr_tags_update(soup)

    return soup.prettify("utf-8")


def query_params(url, params):
    first_param = True
    for param in params:
        val = f'%{"%".join("{:02x}".format(c) for c in params[param].encode("utf-8"))}'
        if first_param:
            url = f'{url}?{param}={val}'
            first_param = False
        else:
            url = f'{url}&{param}={val}'
    return url


def habr(request, uris=[]):
    url = target_url
    request_query_params = request.args.to_dict()
    for uri in uris:
        url = f'{url}/{uri}' if uri else url
    if request_query_params:
        url = query_params(url, request_query_params)
    try:
        response = urllib.request.urlopen(
            urllib.request.Request(url=url, method='GET')
        )

        response_data = response.read()
        if response_data.startswith(b'<!DOCTYPE html>'):
            response_data = href_update_lxml(response_data)
            response_data = text_update_soup(response_data)

            parser = html.parser.HTMLParser()
            response_data = parser.unescape(response_data.decode('utf-8'))

        return Response(response_data,
                        headers={"Content-Type": response.headers.get_all('Content-Type'),
                                 "Access-Control-Allow-Origin": "*"})

    except urllib.error.HTTPError as e:
        return Response(e.read(), headers={"Content-Type": e.headers.get_all('Content-Type')})

    except Exception as e:
        print(f'internal server error, error={e}')
        return Response('internal server error', headers={"Content-Type": "text/plain"})
