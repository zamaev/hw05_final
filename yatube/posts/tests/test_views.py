import shutil
import tempfile
from math import ceil

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.follower = User.objects.create(username='follower')
        cls.unfollower = User.objects.create(username='unfollower')
        Follow.objects.create(user=cls.follower, author=cls.user)
        cls.empty_group = Group.objects.create(
            title='Пустая',
            slug='empty',
            description='Без постов',
        )
        cls.main_group = Group.objects.create(
            title='Основная',
            slug='main',
            description='Для общих постов',
        )
        cls.post_without_group = Post.objects.create(
            text='Текст поста без группы',
            author=cls.user
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.post_with_group = Post.objects.create(
            text='Текст поста с группой',
            group=cls.main_group,
            author=cls.user,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.unfollower)

    def tearDown(self):
        cache.clear()

    def test_index_page_view_cache(self):
        """Проверка кэширования на главной странице."""
        response1 = self.client.get(reverse('posts:index'))
        Post.objects.create(
            text='test',
            author=self.user,
        )
        response2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response2.content, response3.content)

    def test_pages_uses_correct_templates(self):
        """URL адреса используют соответствующий шаблон."""
        pages_template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                args=(self.main_group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(self.user.username,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=(self.post_without_group.pk,)
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=(self.post_without_group.pk,)
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create',
            ): 'posts/create_post.html',
        }
        for url, template in pages_template_names.items():
            with self.subTest(value=url):
                request = self.auth_client.get(url)
                self.assertTemplateUsed(request, template)

    def test_list_pages_show_correct_context(self):
        """На всех страницах со списком постов отображается
        необходимый пост.
        """
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.main_group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertIn('page_obj', response.context)
                self.assertGreaterEqual(len(response.context['page_obj']), 1)
                self.check_posts_are_same(
                    response.context['page_obj'][0],
                    self.post_with_group
                )

    def test_empty_group_page_list_is_0(self):
        """На странице группы без добавления постов нет постов."""
        response = self.client.get(
            reverse('posts:group_list', args=(self.empty_group.slug,)))
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы профиля сформирован с правильным конекстом."""
        response = self.client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post_without_group.pk,)))
        self.check_posts_are_same(
            response.context['post'],
            self.post_without_group,
        )

    def test_post_pages_with_form_show_correct_context(self):
        """Страницы с формами сформированы с правильным контекстом."""
        pages = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post_without_group.pk,)),
        ]
        for page in pages:
            response = self.auth_client.get(page)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for field, expected in form_fields.items():
                with self.subTest(value=field):
                    self.assertIsInstance(
                        response.context['form'].fields[field],
                        expected
                    )

    def test_post_edit_form_show_correct_context_instance(self):
        """Страница редактирования поста сформирована с правильным контекстом
        с нужным постом для редактирования.
        """
        response = self.auth_client.get(
            reverse('posts:post_edit', args=(self.post_without_group.pk,)))
        instance = response.context['form'].instance
        self.check_posts_are_same(instance, self.post_without_group)

    def test_list_pages_post_image_in_context(self):
        """Страницы со списком постов сформированы с правильным контекстом."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.main_group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertIn('page_obj', response.context)
                self.assertGreaterEqual(len(response.context['page_obj']), 1)
                self.assertEqual(self.post_with_group.image.name,
                                 response.context['page_obj'][0].image.name)

    def test_post_page_post_image_in_context(self):
        """Страница поста имеет корректный контекст."""
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post_with_group.pk,)))
        self.assertIn('post', response.context)
        self.assertEqual(self.post_with_group.image.name,
                         response.context['post'].image.name)

    def test_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        follower_count = self.unfollower.follower.count()
        self.unfollower_client.get(
            reverse('posts:profile_follow', args=(self.user.username,)))
        self.assertEqual(self.unfollower.follower.count(), follower_count + 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписаться
        от других пользователей.
        """
        follower_count = self.follower.follower.count()
        self.follower_client.get(
            reverse('posts:profile_unfollow', args=(self.user.username,)))
        self.assertEqual(self.follower.follower.count(), follower_count - 1)

    def test_following_post_in_followers_page(self):
        """Новая запись автора появляется в ленте тех,
        кто на него подписан.
        """
        response = self.follower_client.get(
            reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        self.assertGreaterEqual(len(response.context['page_obj']), 1)
        self.check_posts_are_same(
            response.context['page_obj'][0],
            self.user.posts.first(),
        )

    def test_following_post_not_in_unfollowers_page(self):
        """Новая запись автора не появляется в ленте тех,
        кто на него не подписан.
        """
        response = self.unfollower_client.get(
            reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)

    def check_posts_are_same(self, post1, post2):
        """Проверка постов на идентичность."""
        fields_for_check = [
            'text',
            'created',
            'author',
            'group',
        ]
        for field in fields_for_check:
            with self.subTest(value=field):
                self.assertEqual(
                    getattr(post1, field),
                    getattr(post2, field)
                )


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='user')
        cls.follower = User.objects.create(username='follower')
        Follow.objects.create(user=cls.follower, author=cls.author)
        cls.group = Group.objects.create(
            title='Группа',
            slug='group',
            description='Для постов',
        )
        cls.posts_count_for_test = 13
        for i in range(cls.posts_count_for_test):
            Post.objects.create(
                text='Длинный текст поста ' + str(i),
                group=cls.group,
                author=cls.author,
            )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_list_pages_check_records_count(self):
        """Кол-во постов в пагинации на каждой из страниц со списками."""
        url_clients = {
            reverse('posts:index'): self.client,
            reverse('posts:group_list', args=(self.group.slug,)): self.client,
            reverse('posts:profile',
                    args=(self.author.username,)): self.client,
            reverse('posts:follow_index'): self.follower_client,
        }
        for url, client in url_clients.items():
            with self.subTest(value=url):
                pages = ceil(
                    self.posts_count_for_test / settings.POSTS_PER_PAGE
                )
                for page in range(1, pages + 1):
                    response = client.get(url, {'page': page})
                    self.assertIn('page_obj', response.context)
                    if page == pages:
                        posts_count_on_page = (self.posts_count_for_test
                                               % settings.POSTS_PER_PAGE)
                    else:
                        posts_count_on_page = settings.POSTS_PER_PAGE
                    self.assertEqual(
                        len(response.context['page_obj']),
                        posts_count_on_page,
                    )
