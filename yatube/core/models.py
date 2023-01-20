from django.db import models


class CreatedTextModel(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
