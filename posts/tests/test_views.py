from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.cache = caches['default']
        cls.user = User.objects.create_user(username='Anton')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.response_before = cls.authorized_client.get(
            reverse('posts:index'))

        cls.group = Group.objects.create(
            title='Название Группы',
            slug='test_slug',
            description='Описание',
        )
        cls.group2 = Group.objects.create(
            title='Название Группы 2',
            slug='test_slug_2',
            description='Описание 2',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('posts:index'),
            'group.html': (
                reverse('posts:group', kwargs={'slug': self.group.slug})
            ),
            'new_post.html': reverse('posts:new_post'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон <new_post> сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_page_shows_correct_context(self):
        """Шаблон <group> сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug}))
        first_object = response.context['group']
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_description_0 = first_object.description
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_description_0, self.group.description)

    def test_index_page_shows_correct_context(self):
        """Шаблон <index> сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        task_author_0 = first_object.author
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_group_0, self.group)
        self.assertEqual(task_author_0, self.user)

    def test_new_post_shows_correct(self):
        """
        1. Новый пост отображается на странице выбранной группы
        2. Новый пост не отображается на странице другой группы
        """
        # 1
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group.slug}))
        first_object = response.context['posts'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        # 2
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group2.slug}))
        with self.assertRaises(IndexError, msg='list index out of range'):
            response.context['posts'][0]

    def test_caches(self):
        """ Проверка работы кэша index"""
        response_after = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(self.response_before, response_after)
