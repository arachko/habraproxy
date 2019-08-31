import urllib.request
import urllib.error
from lxml import html, etree
from bs4 import BeautifulSoup
from flask import Response
import re
import json

target_url = 'https://habr.com'


def href_update_lxml(tree):
    for i in range(len(tree.xpath('//*[@href]'))):
        url = tree.xpath('//*[@href]')[i].get('href')
        url_to_local = 'https://habr.com/ru/'
        if url.startswith(url_to_local):
            tree.xpath('//*[@href]')[i].set('href', f'http://127.0.0.1:5000/{url[len(url_to_local)::]}')


def text_update_soup(soup):
    reg = re.compile('\w')
    tags = ['h1', 'p', 'a', 'h2', 'h3', 'span', 'br', 'div', 'li', 'ul', '#text']
    for elem_g in soup.find_all({tag: True for tag in tags}):
        for elem_l in elem_g.find_all(text=reg):
            if len(re.findall(r'\b\w[a-zA-Zа-яА-Я]{5}\b', elem_l)) > 0:
                text_list = elem_l.split(' ')
                for i in range(len(text_list)):
                    if len(text_list[i]) == 6 and not re.search('\W', text_list[i]):
                        text_list[i] += '™'
                i = ' '.join(text_list)
                elem_l.replaceWith(i)


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
        full_html = urllib.request.urlopen(
            urllib.request.Request(url=url, method='GET')
        ).read()

        tree = html.fromstring(full_html)
        href_update_lxml(tree)

        soup = BeautifulSoup(etree.tostring(tree))
        text_update_soup(soup)

        return Response(soup.prettify("utf-8"),
                        headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

    except urllib.error.HTTPError as e:
        error_message = json.loads(e.read())
        print(f'an error occurred while getting target page, error_response={error_message}')
        return Response('an error occurred while getting target page', headers={"Content-Type": "text/plain"})

    except Exception as e:
        print(f'internal server error, error={e}')
        return Response('internal server error', headers={"Content-Type": "text/plain"})
