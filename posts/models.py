from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=200,
        help_text='Дайте короткое название группе',
    )
    slug = models.SlugField(
        'Слаг',
        max_length=20,
        unique=True,
        help_text=('Укажите адрес для страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания'),
    )
    description = models.TextField(
        'Описание',
        help_text='Опишите группу',
    )

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Опишите новость',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Выберите группу'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий к посту',
        on_delete=models.CASCADE,
        related_name='comments_post',
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        'Текст',
        help_text='Ваш коментарий',
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписывающийся',
        on_delete=models.CASCADE,
        related_name='follower',
        null=True,
    )

    author = models.ForeignKey(
        Post,
        verbose_name='Автор на которого подписываются',
        on_delete=models.CASCADE,
        related_name='to_follow',
        null=True,
    )