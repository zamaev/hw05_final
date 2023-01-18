from django.test import TestCase
from django.urls import reverse

from posts.models import User


class UserFormTest(TestCase):

    def test_create_user(self):
        """Валидная форма создает пользователя в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'test_user',
            'email': 'test_user@ya.ru',
            'password1': '123456SDF@#',
            'password2': '123456SDF@#',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
