from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Заглавие')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный URL')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Изложите свои мысли здесь')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Выберите группу'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)
