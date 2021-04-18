from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Post, Group, User

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anton')
        cls.group = Group.objects.create(
            title='Название Группы',
            slug='test_slug',
            description='Описание',)

        for i in range(0, 13):
            Post.objects.create(
                text=f'Тестовый текст {i}',
                group=cls.group,
                author=cls.user,)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
