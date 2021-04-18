from django.test import TestCase
from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test text',
            description='Тестовый текст',
            slug='test-group'
        )
        cls.post = Post.objects.create(
            text='test text',
            group=cls.group,
            author=User.objects.create(username='vasya'),
        )

    def test_title_label(self):
        """verbose_name поля group.title совпадает с ожидаемым."""
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEquals(verbose, 'Заголовок')

    def test_verbose_name(self):
        """verbose_name полей post.text, group совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text полей post.text, group совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Опишите новость',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )
