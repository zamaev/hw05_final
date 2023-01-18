from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutUrlTests(TestCase):

    def test_static_pages(self):
        """Страницы доступны любому пользователю."""
        urls = [
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_templates(self):
        """URL-адреса имеют соответствующий шаблон."""
        urls_template_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for url, template in urls_template_names.items():
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)


class AboutViewTest(TestCase):
    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        pages_template_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for url, template in pages_template_names.items():
            with self.subTest(value=url):
                request = self.client.get(url)
                self.assertTemplateUsed(request, template)
