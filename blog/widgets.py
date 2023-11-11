import json
import re
from base64 import b64decode

import requests
from django.conf import settings
from requests.exceptions import RequestException

from blog.wp_client import get_wp_client
from common.utils import to_num


class Widget:
    """
    Base blog Widget class
    """
    _wp_client = None

    def __init__(self, input_):
        self.name = input_.pop('widget_name')
        self.input = input_
        self.output = {}

    @property
    def wp(self):
        if self._wp_client is None:
            self._wp_client = get_wp_client()
        return self._wp_client

    def get_output(self):
        raise NotImplementedError


class RelatedPostsWidget(Widget):

    def get_output(self):
        articles = []
        for post_id in self.input['post_ids']:
            if post_id:
                if article := self.wp.get_post(post_id=post_id):
                    article.pop('content', None)
                    articles.append(article)

        return articles


class FaqWidget(Widget):

    def get_output(self):
        return self.input['qas']


class RecommendationsWidget(Widget):

    def request_search(self, url):
        """
        Convert the search URL to search results
        """
        try:
            resp = requests.get(f'http://localhost:{settings.LOCAL_FRONTEND_PORT}/api/search{url}')
        except RequestException:
            return

        if resp.status_code == 200:
            return resp.json()

    def get_output(self):
        """
        Place all the input fields + search results
        """
        output = {
            'url': self.input['url'],
            'count': to_num(self.input['count']),
            'title': self.input['title'],
            'seo-tag': self.input['seo-tag'],
            'search': self.request_search(self.input['url']),
        }

        if not output['search'] or (output['search'] or {}).get('dto', {}).get('search', {}).get('total') == 0:
            return None
        return output


def construct_widgets(body):
    """
    Take article content, read widget input fields,
    gather all required info for each, and return it as a list in the same order
    """
    widgets = []
    for input_ in extract_widget_inputs(body):
        widget = None
        name = input_['widget_name']
        widget_dict = {'name': name}
        widget = KNOWN_WIDGETS[name](input_)

        if widget is not None:
            widget_dict['body'] = widget.get_output()

        if widget_dict.get('body'):
            widget_dict['is_empty'] = False
        else:
            widget_dict['is_empty'] = True

        widgets.append(widget_dict)
    return widgets


def extract_widget_inputs(content):
    """
    Find base64-encoded widgets, decode them, add name, and return as a list
    """
    widgets = []
    for match in re.finditer('{{.+?{{/', content):
        name, encoded = content[match.start():match.end()].split('{{')[1].split('}}')
        widget = {
            'widget_name': name,
            **json.loads(b64decode(encoded).decode('utf-8')),
        }
        widgets.append(widget)

    return widgets


def convert_widgets_in_content(body, widgets):
    """
    Convert widgets that are inside content to a format the front end understands
    """
    if body:
        for widget in widgets:
            regex_pattern = r'{{(' + widget['name'] + r')}}.*{{/' + widget['name'] + r'}}'
            if widget['is_empty']:
                body = re.sub(regex_pattern, '', str(body), count=1)
            else:
                body = re.sub(regex_pattern, r'{{WIDGET}}\1{{/WIDGET}}', str(body), count=1)
    return body


KNOWN_WIDGETS = {
    'RELATED-POSTS': RelatedPostsWidget,
    'FAQ-BLOCK': FaqWidget,
    'RECOMMENDATIONS': RecommendationsWidget,
}
