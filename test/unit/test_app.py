import re
from copy import copy

import pytest

from flasklib.delegate_app import href_update_lxml, text_update_soup


@pytest.fixture(scope='function')
def rnd_html():
    rnd_html = """
        <html>
            <body>
                <div>
                    <a href="https://habr.com/ru/news"> Ссылка на новости </a>
                    <span> Пример текста в теге span </span>
                </div>
                <div>
                    Пример текста в теге div
                </div>
            </body>
        </html>
    """
    yield rnd_html


def test_url_update(rnd_html):
    html_href_updated_str = href_update_lxml(rnd_html).decode('utf-8')
    assert 'https://habr.com' not in html_href_updated_str
    assert '127.0.0.1:5000' in html_href_updated_str


def test_text_update(rnd_html):
    updated_words = list()
    rnd_html_copy = copy(rnd_html)
    text_list = rnd_html_copy.split(' ')
    for i in range(len(text_list)):
        if len(text_list[i]) == 6 and not re.search('\W', text_list[i]):
            text_list[i] += '™'
            updated_words.append(text_list[i])
    html_text_updated = text_update_soup(rnd_html).decode('utf-8')

    for word in updated_words:
        assert word in html_text_updated
    text_list_after_html_update = html_text_updated.split(' ')
    for elem in text_list_after_html_update:
        elem = re.sub('\\n', '', elem) if '\n' in elem else elem
        if not re.search('\W', elem) and len(elem) > 0:
            assert len(elem) != 6
