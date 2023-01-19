from django.db import models


class CreatedModel(models.Model):
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class TextModel(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст',
    )

    class Meta:
        abstract = True
