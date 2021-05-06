from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User, Comment, Follow

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

        cls.user2 = User.objects.create_user(username='Pavel')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

        cls.user3 = User.objects.create_user(username='Misha')
        cls.authorized_client3 = Client()
        cls.authorized_client3.force_login(cls.user3)

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

        cls.comments = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='тестовый коментарий'
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
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        # 2
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': self.group2.slug}))
        with self.assertRaises(IndexError, msg='list index out of range'):
            response.context['page'][0]

    def test_caches(self):
        """ Проверка работы кэша index"""
        response_after = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(self.response_before, response_after)

    def test_authorized_client_follows(self):
        """
        1. Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок
        2. Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него
        """
        # 1
        # посчитаем к-во всех подписок
        follows_0 = Follow.objects.all().count()
        # user2 подписывается на user'a
        Follow.objects.create(user=PostsPagesTests.user2,
                              author=PostsPagesTests.user)
        # посчитаем к-во всех подписок
        follows_1 = Follow.objects.all().count()

        # ==2==
        # посчитаем к-во постов избранных авторов  у user2 и user3
        count_user2_follow_posts = Post.objects.filter(
            author__following__user=PostsPagesTests.user2).count()
        count_user3_follow_posts = Post.objects.filter(
            author__following__user=PostsPagesTests.user3).count()
        # user публикует НОВЫЙ ПОСТ!
        PostsPagesTests.post1 = Post.objects.create(
            text='user публикует НОВЫЙ ПОСТ!',
            group=PostsPagesTests.group,
            author=PostsPagesTests.user,)
        # посчитаем к-во постов избранных авторов  у user2 и user3 еще раз
        count_user2_follow_posts_2 = Post.objects.filter(
            author__following__user=PostsPagesTests.user2).count()
        count_user3_follow_posts_2 = Post.objects.filter(
            author__following__user=PostsPagesTests.user3).count()
        self.assertEqual(count_user2_follow_posts, 1)
        self.assertEqual(count_user3_follow_posts, 0)
        self.assertEqual(count_user2_follow_posts_2, 2)
        self.assertEqual(count_user3_follow_posts_2, 0)
        # ==end 2==

        # user2 отписывается от user'a (видимо НОВЫЙ ПОСТ не так уж и хорош)
        Follow.objects.filter(user=PostsPagesTests.user2,
                              author=PostsPagesTests.user).delete()
        follows_2 = Follow.objects.all().count()
        self.assertEqual(follows_0, 0)
        self.assertEqual(follows_1, 1)
        self.assertEqual(follows_2, 0)

    def test_only_authorized_client_comments(self):
        """ Только авторизированный пользователь может комментировать
        посты"""
        # посчитаем число комментов
        count_comments_first = Comment.objects.all().count()
        # добавим коммент от user'a
        Comment.objects.create(author=PostsPagesTests.user,
                               post=PostsPagesTests.post,
                               text='lalalalala')
        # посчитаем число комментов
        count_comments_user_add = Comment.objects.all().count()
        # ожидаем ошибку
        with self.assertRaises(ValueError, msg='автор комента д.б. user'):
            # попробуем добавить коммент от guest'a
            Comment.objects.create(author=PostsPagesTests.guest_client,
                                   post=PostsPagesTests.post,
                                   text='lalalalala')
        # посчитаем число комментов
        count_comments_guest_add = Comment.objects.all().count()
        self.assertNotEqual(count_comments_first, count_comments_user_add)
        self.assertEqual(count_comments_user_add, count_comments_guest_add)
