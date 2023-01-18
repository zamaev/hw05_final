from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User


class UserUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_accessible_urls_guest(self):
        """Страницы доступны любому пользователю."""
        accessible_urls = {
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_confirm', args=('uidb64', 'token')),
            reverse('users:password_reset_complete'),
            reverse('users:logout'),
        }
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_inuccessible_urls_guest(self):
        """Страницы не доступны не авторизованному пользователю."""
        inaccessible_urls = {
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
        }
        for url in inaccessible_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_accessible_urls_user(self):
        """Страницы доступны авторизованному пользователю."""
        accessible_urls = {
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
        }
        for url in accessible_urls:
            with self.subTest(value=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        urls_template_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change_form'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                args=('uidb64', 'token')
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for url, template in urls_template_names.items():
            with self.subTest(template, value=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
