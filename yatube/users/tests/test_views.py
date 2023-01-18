from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import User


class UserViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        pages_template_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change_form',
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done',
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form',
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done',
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                args=('uidb64', 'token'),
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete',
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for url, template in pages_template_names.items():
            with self.subTest(value=url):
                request = self.auth_client.get(url)
                self.assertTemplateUsed(request, template)

    def test_signup_page_show_correct_context(self):
        """Страница регистрации сформирована с правильным контекстом."""
        form_fields = {
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.CharField,
        }
        response = self.client.get(reverse('users:signup'))
        for field, expected in form_fields.items():
            with self.subTest(value=field):
                value = response.context['form'].fields[field]
                self.assertIsInstance(value, expected)
