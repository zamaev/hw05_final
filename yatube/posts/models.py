from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy

from core.models import CreatedTextModel

User = get_user_model()


class Group(models.Model):
    """Model for a group of posts."""

    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='ЧПУ',
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return f'{self.title}'


class Post(CreatedTextModel):
    """Model for posts."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа поста',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.text[:15]}'

    def get_absolute_url(self):
        return reverse_lazy('posts:post_detail', args=(self.pk,))


class Comment(CreatedTextModel):
    """Model of comments."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text}'


class Follow(models.Model):
    """Model of followers."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
