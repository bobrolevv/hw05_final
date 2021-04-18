from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='Vasya')  # noqa
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test text',
            description='Тестовый текст',
            slug='test_group'
        )
        self.post = Post.objects.create(
            text='test text',
            group=self.group,
            author=self.user,
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 123',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data['text'],
                                            group=self.group))

    def test_edit_post(self):
        """Проверка возможности редактирования поста"""
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст, длиннее 15 символов',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'username': self.user,
                                               'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_view',
                                     kwargs={
                                         'username': self.user,
                                         'post_id': self.post.id}))
        self.assertFalse(
            Post.objects.filter(
                author=self.user,
                text=self.post.text,
                group=self.group.id,
            ).exists()
        )
