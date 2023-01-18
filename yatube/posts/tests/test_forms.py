import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Группа для постов',
        )
        cls.new_group = Group.objects.create(
            title='Новая группа',
            slug='new_group',
            description='Новая группа для постов',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='post_form_test.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        with self.subTest(value='redirect_after_add'):
            self.assertRedirects(
                response,
                reverse('posts:profile', args=(self.user.username,))
            )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        fileds_for_check = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.user,
        }
        for field, expected in fileds_for_check.items():
            with self.subTest(velue=post):
                self.assertEqual(field, expected)
        self.assertNotEqual(post.image.name, '')

    def test_guest_cannot_create_post(self):
        """Неавторизованный пользователь не может создавать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        with self.subTest(value='posts_count'):
            self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create',)
        )

    def test_edit_post(self):
        """Валидная форма создает изменяет в Post."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.new_group.pk,
        }
        self.auth_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(pk=self.post.pk)
        fileds_for_check = {
            post.text: form_data['text'],
            post.group.pk: form_data['group'],
            post.author: self.post.author,
        }
        for field, expected in fileds_for_check.items():
            with self.subTest(velue=post):
                self.assertEqual(field, expected)

    def test_guest_cannot_edit_post(self):
        """Неавторизованный пользователь не может редактировать пост."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.new_group.pk,
        }
        response = self.client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_edit',
                                                        args=(self.post.pk,))
        )

    def test_guest_cannot_create_comment(self):
        """Неавторизованный пользователь не может создать комментарий."""
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:add_comment',
                                                        args=(self.post.pk,))
        )
        self.assertEqual(comments_count, self.post.comments.count())

    def test_post_page_has_comment_context(self):
        """После успешной отправки формы
        комментарий появляется на странице поста.
        """
        form_data = {
            'text': 'Новые комментарий',
        }
        response = self.auth_client.post(
            reverse('posts:add_comment', args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertGreaterEqual(len(response.context['comments']), 1)
        self.assertEqual(response.context['comments'][0].text,
                         form_data['text'])
