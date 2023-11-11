import json
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from blog.models import ArticleViewCounter
from blog.serializers import PaginatedListParamsSerializer
from blog.widgets import construct_widgets, convert_widgets_in_content
from blog.wp_client import get_wp_client
from common.cache import cache_method, simple_cache_by_static_key


logger = logging.getLogger(__name__)


class BlogMixin:
    """
    Common blog methods. Inherit any blog-related view from it!
    And don't forget to use respond() method when returning response.
    """
    _wp_client = None

    @property
    def wp(self):
        if self._wp_client is None:
            self._wp_client = get_wp_client()
        return self._wp_client

    def get_side_categories(self):
        categories = []
        for category in self.wp.get_categories(orderby='count', order='desc')['results']:
            if category['count']:
                categories.append(category)
        return categories

    def get_popular_articles(self, quantity=5):
        popular = []

        for counter in ArticleViewCounter.objects.order_by('-count'):
            if article := self.wp.get_post(post_id=counter.article_id):
                article['view_count'] = counter.count
                article.pop('content')
                article.pop('description')
                popular.append(article)
            if len(popular) >= quantity:
                break

        return popular

    # @simple_cache_by_static_key('blog.views.BlogMixin.get_common_data')
    def get_common_data(self):
        return {
            'side_categories': self.get_side_categories(),
            'popular_articles': self.get_popular_articles(),
        }

    def _add_page_to_title(self, data, page):
        if (page or 1) >= 2:
            title = data.get('meta', {}).get('title', '')
            data['meta']['title'] = f'{(title or "")} - Page {page}'

    def respond(self, data=None, status=status.HTTP_200_OK):
        """
        Post process the response:
        - replace WordPress media URLs with our custom URLs
        """
        if not isinstance(data, str):
            data = json.dumps(data)

        orig_media_url = f'https://{settings.WP_API_HOST}/wp-content/uploads/'
        media_url = f'https://{settings.PROJECT_DOMAIN}/blogfiles/'
        data = data.replace(orig_media_url, media_url)

        orig_posts_url = f'https://{settings.WP_API_HOST}/rsprjposts/'
        posts_url = f'https://{settings.PROJECT_DOMAIN}/blog/'
        data = data.replace(orig_posts_url, posts_url)

        # And, after all, replace the base of the blog URL
        orig_host_url = f'https://{settings.WP_API_HOST}'
        host_url = f'https://{settings.PROJECT_DOMAIN}'
        data = data.replace(orig_host_url, host_url)

        return Response(json.loads(data), status=status)


class HomeView(RetrieveAPIView, BlogMixin):
    """
    Retrieve data for a Home blog page
    """
    show_articles = 2  # how many articles to show for each category

    # @cache_method
    def retrieve(self, request):
        last_post = None
        posts = self.wp.get_posts()
        if posts and posts.get('results'):
            last_post = posts['results'][0]

        home = {
            'categories': [],
            'last_article': last_post,
            **self.get_common_data(),
        }
        if last_post is None:
            return home

        for category in self.wp.get_categories(per_page=100)['results']:
            if posts := self.get_category_posts(category, last_post['id']):
                home['categories'].append({
                    'name': category['name'],
                    'slug': category['slug'],
                    'articles': posts,
                })

        return self.respond(home, status=status.HTTP_200_OK)

    def get_category_posts(self, category, exclude_id):
        posts = []

        if category['count']:
            category_posts = self.wp.get_posts(categories=category['id'])['results']
            posts = category_posts[:self.show_articles + 1]

            # skip the post if it's the 'last_post' or if it's the last item in the list
            skip_post_idx = self.show_articles
            for idx, post in enumerate(posts):
                if post['id'] == exclude_id:
                    skip_post_idx = idx
                    break

            if skip_post_idx < len(posts):
                posts.pop(skip_post_idx)

        return posts


class TabView(RetrieveAPIView, BlogMixin):
    """
    Retrieve data for a Blog tab on the main page
    """
    # @cache_method
    def retrieve(self, request):
        tab = {
            'articles': self.get_popular_articles(3),
        }
        return self.respond(tab, status=status.HTTP_200_OK)


class SlugsView(RetrieveAPIView, BlogMixin):
    """
    Retrieve slugs of all the objects in WordPress
    """
    # @cache_method
    def retrieve(self, request):
        slugs = self.wp.get_all_slugs(nonempty=True)
        data = {
            'articles': slugs['posts'],
            'authors': slugs['users'],
            'categories': slugs['categories'],
        }
        return self.respond(data, status=status.HTTP_200_OK)


class ArticleView(RetrieveAPIView, BlogMixin):
    """
    Retrieve an article data
    """
    def retrieve(self, request, id_or_slug=None):
        common = self.get_common_data()

        if id_or_slug.isdigit():
            article = self.wp.get_post(post_id=int(id_or_slug), authed=True)
        else:
            article = self.wp.get_post(slug=id_or_slug)

        if article is None:
            return self.respond(common, status=status.HTTP_404_NOT_FOUND)

        article = {**article, **common}
        widgets = construct_widgets(article['content'])
        article['view_count'] = ArticleViewCounter.objects.increase(article['id'])
        article['ofirio_widgets'] = [i for i in widgets if not i['is_empty']]
        article['content'] = convert_widgets_in_content(article['content'], widgets)
        article['image'] = article.get('image', {}).get('sizes', {}).get('full')

        return self.respond(article, status=status.HTTP_200_OK)


class ArticleListView(ListAPIView, BlogMixin):
    """
    Retrieve articles
    """
    params_serializer_class = PaginatedListParamsSerializer

    # @cache_method
    def list(self, request, *args, **kwargs):
        params_serializer = self.params_serializer_class(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        page = params_serializer.validated_data['page']

        posts = self.wp.get_posts(page=page)
        posts = {**posts, **self.get_common_data()}

        return self.respond(posts, status=status.HTTP_200_OK)


class AuthorView(RetrieveAPIView, BlogMixin):
    """
    Retrieve an author data
    """
    params_serializer_class = PaginatedListParamsSerializer

    # @cache_method
    def retrieve(self, request, id_or_slug=None):
        params_serializer = self.params_serializer_class(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        page = params_serializer.validated_data['page']

        common = self.get_common_data()

        if id_or_slug.isdigit():
            author = self.wp.get_user(user_id=int(id_or_slug))
        else:
            author = self.wp.get_user(slug=id_or_slug)

        if author is None:
            return self.respond(common, status=status.HTTP_404_NOT_FOUND)

        author['articles'] = self.wp.get_posts(
            author=author['id'], full_author=author.copy(), page=page,
        )
        author = {**author, **common}
        self._add_page_to_title(author, page)

        return self.respond(author, status=status.HTTP_200_OK)


class CategoryView(RetrieveAPIView, BlogMixin):
    """
    Retrieve a category data
    """
    params_serializer_class = PaginatedListParamsSerializer

    # @cache_method
    def retrieve(self, request, id_or_slug=None):
        params_serializer = self.params_serializer_class(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        page = params_serializer.validated_data['page']

        common = self.get_common_data()

        if id_or_slug.isdigit():
            category = self.wp.get_category(category_id=int(id_or_slug))
        else:
            category = self.wp.get_category(slug=id_or_slug)

        if category is None or not category['count']:
            return self.respond(common, status=status.HTTP_404_NOT_FOUND)

        category = {**category, **common}
        category['articles'] = self.wp.get_posts(categories=category['id'], page=page)
        self._add_page_to_title(category, page)

        return self.respond(category, status=status.HTTP_200_OK)
