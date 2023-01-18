from django.test import TestCase

from posts.models import User, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Группа',
            slug='gruppa',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            author=cls.author,
            group=cls.group,
        )

    def test_models_have_correct_object_name(self):
        """В поле __str__ объекта post записано значение поля post.title."""
        objects_expected = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
        }
        for object, expected in objects_expected.items():
            with self.subTest(value=object):
                self.assertEqual(str(object), expected)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected in field_verboses.items():
            with self.subTest(value=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Текст поста',
            'group': 'Группа поста',
        }
        for field, exptected in field_help_texts.items():
            with self.subTest(value=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, exptected)
