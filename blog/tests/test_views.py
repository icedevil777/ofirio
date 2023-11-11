from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from blog.tests.base import BlogBaseTest


class ArticleDetailTest(BlogBaseTest):

    def test_get_article_ok(self):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('title', response.data)
        self.assertIn('slug', response.data)
        self.assertIn('content', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('author', response.data)
        self.assertIn('date', response.data)
        self.assertIn('modified', response.data)
        self.assertIn('status', response.data)
        self.assertIn('description', response.data)

        self.assertEqual(response.data['author']['id'], 1)
        self.assertEqual(response.data['author']['full_name'], 'Ofirio Author')
        self.assertEqual(response.data['categories'][0]['slug'], 'uncategorized')

        self.assertIsInstance(response.data['image'], str)
        self.assertIsInstance(response.data['thumbnail'], str)
        self.assertIsInstance(response.data['reading_time'], str)
        self.assertIsInstance(response.data['side_categories'], list)
        self.assertIsInstance(response.data['popular_articles'], list)

        self.assertTrue(response.data['meta']['title'])
        self.assertTrue(response.data['meta']['description'])

    def test_article_view_count_increased(self):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)
        self.assertEqual(response.data['view_count'], 1)
        response = self.client.get(url)
        self.assertEqual(response.data['view_count'], 2)

    def test_get_article_by_slug_ok(self):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': 'hello-world'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Hello world!')

    def test_get_article_not_found(self):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('blog.widgets.RecommendationsWidget.request_search')
    def test_get_article_with_widget(self, request_search):
        request_search.return_value = {}
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '3'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArticleListTest(BlogBaseTest):
    URL = reverse('blog:article-list')

    def test_get_articles_ok(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['pages'], 2)
        self.assertEqual(response.data['results'][0]['id'], 1)

        self.assertIsInstance(response.data['popular_articles'], list)

    def test_get_articles_by_page_ok(self):
        response = self.client.get(self.URL + '?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['pages'], 2)
        self.assertEqual(response.data['results'][0]['id'], 1)


class AuthorDetailTest(BlogBaseTest):

    def test_get_author_not_found(self):
        url = reverse('blog:author-detail', kwargs={'id_or_slug': '2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIsInstance(response.data['popular_articles'], list)

    def test_get_author_ok(self):
        url = reverse('blog:author-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('id', response.data)
        self.assertIn('slug', response.data)
        self.assertIn('full_name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('avatar', response.data)

        self.assertTrue(response.data['articles']['results'])
        self.assertIsInstance(response.data['articles']['results'], list)
        self.assertIsInstance(response.data['side_categories'], list)

        self.assertNotIn('side_categories', response.data['articles']['results'][0])
        self.assertNotIn('side_categories',
                         response.data['articles']['results'][0]['categories'][0])

        self.assertIsInstance(response.data['popular_articles'], list)

    def test_get_author_by_slug_ok(self):
        url = reverse('blog:author-detail', kwargs={'id_or_slug': 'ofirio_author'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_author_by_slug_with_page(self):
        url = reverse('blog:author-detail', kwargs={'id_or_slug': 'ofirio_author'}) + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_articles_inside_category_and_author_articles(self):
        url = reverse('blog:author-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)

        for article in response.data['articles']['results']:
            for category in article['categories']:
                self.assertNotIn('articles', category)
            self.assertNotIn('articles', article['author'])


class CategoryDetailTest(BlogBaseTest):

    def test_get_category_not_found(self):
        url = reverse('blog:category-detail', kwargs={'id_or_slug': '2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIsInstance(response.data['popular_articles'], list)
        self.assertIsInstance(response.data['side_categories'], list)

    def test_get_empty_category(self):
        """
        If category has no articles, it should be shown as 404
        """
        url = reverse('blog:category-detail', kwargs={'id_or_slug': '3'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIsInstance(response.data['popular_articles'], list)
        self.assertIsInstance(response.data['side_categories'], list)

    def test_get_category_ok(self):
        url = reverse('blog:category-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('id', response.data)
        self.assertIn('slug', response.data)
        self.assertIn('description', response.data)

        self.assertTrue(response.data['articles']['results'])
        self.assertIsInstance(response.data['articles']['results'], list)
        self.assertIsInstance(response.data['side_categories'], list)
        self.assertIsInstance(response.data['popular_articles'], list)

        self.assertNotIn('side_categories', response.data['articles']['results'][0])
        self.assertNotIn('side_categories',
                         response.data['articles']['results'][0]['categories'][0])

    def test_get_category_by_slug_ok(self):
        url = reverse('blog:category-detail', kwargs={'id_or_slug': 'uncategorized'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_category_by_slug_with_page(self):
        url = reverse('blog:category-detail', kwargs={'id_or_slug': 'uncategorized'}) + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_articles_inside_author_and_category_articles(self):
        url = reverse('blog:category-detail', kwargs={'id_or_slug': '1'})
        response = self.client.get(url)

        for article in response.data['articles']['results']:
            for category in article['categories']:
                self.assertNotIn('articles', category)
            self.assertNotIn('articles', article['author'])


class HomeTest(BlogBaseTest):

    def test_get_ok(self):
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('categories', response.data)
        self.assertIn('last_article', response.data)
        self.assertTrue(response.data['categories'][0]['articles'][0]['id'])
        self.assertIsInstance(response.data['categories'], list)
        self.assertIsInstance(response.data['side_categories'], list)

        self.assertIn('slug', response.data['categories'][0])

        self.assertNotIn('side_categories', response.data['categories'][0]['articles'][0])
        self.assertNotIn('side_categories',
                         response.data['categories'][0]['articles'][0]['categories'][0])

        self.assertIsInstance(response.data['popular_articles'], list)


class BlogTabTest(BlogBaseTest):
    """
    Test API endpoint that return blog articles for the Blog tab on main page
    """
    def test_get_ok(self):
        response = self.client.get(reverse('blog:tab'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsInstance(response.data['articles'], list)


@patch('blog.widgets.RecommendationsWidget.request_search', return_value={'dto': {'search': {'total': 15}}})
class WidgetTest(BlogBaseTest):

    def test_widgets_are_converted(self, request_search):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '3'})
        response = self.client.get(url)
        self.assertEqual(
            response.data['content'],
            ('\n<p>Awesome houses</p>\n\n\n\n    {{WIDGET}}RELATED-POSTS{{/WIDGET}}\n'
             '{{WIDGET}}RECOMMENDATIONS{{/WIDGET}} '),
        )

    def test_related_posts_in_article(self, request_search):
        request_search.return_value = {}
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '3'})
        response = self.client.get(url)

        self.assertIn('{{WIDGET}}RELATED-POSTS{{/WIDGET}}', response.data['content'])

        widget = response.data['ofirio_widgets'][0]
        self.assertEqual(widget['name'], 'RELATED-POSTS')
        self.assertEqual(widget['body'][0]['slug'], 'hello-world')

    def test_recommendations_in_article(self, request_search):
        url = reverse('blog:article-detail', kwargs={'id_or_slug': '3'})
        response = self.client.get(url)
        self.assertIn('{{WIDGET}}RECOMMENDATIONS{{/WIDGET}}', response.data['content'])

        widget = response.data['ofirio_widgets'][1]

        self.assertEqual(widget['name'], 'RECOMMENDATIONS')
        self.assertEqual(widget['body']['url'], '/buy/ca/brisbane')
        self.assertEqual(widget['body']['count'], 9)
        self.assertEqual(widget['body']['seo-tag'], 'span')

        self.assertIn('search', widget['body'])


class SlugsTest(BlogBaseTest):
    """
    Test API endpoint that return all the slugs of blog's articles, authors, and categories
    """
    def test_get_ok(self):
        response = self.client.get(reverse('blog:slugs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsInstance(response.data['articles'], list)
        self.assertIsInstance(response.data['authors'], list)
        self.assertIsInstance(response.data['categories'], list)
