from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from .test_views import TEXT_ONE, FIRST_TITLE, SLUG, DESCRIPTION

User = get_user_model()


# python3 manage.py test posts.tests.test_forms для запуска локальных тестов

class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title=FIRST_TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT_ONE,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostCreateFormTests.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.user,
                text='Текст'
            ).exists()
        )

    def test_guest_client_create_post(self):
        """Создание записи возможно только авторизованному пользователю"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.pk,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        response = self.client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_authorized_edit_post(self):
        """Редактирование записи автором поста"""
        form_data = {
            'text': 'Текст',
            'group': self.group.pk,
        }
        # Лишний запрос - пост можно создать при помощи ORM - к сожалению не понял каким образом реализовать
        # И в спешке был вынужден отправить такую версию кода, тк смогу внести корректировки не скоро
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.post.pk)
        self.client.get(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_edit.pk
                    }),
        )
        form_data = {
            'text': 'Новый текст',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_edit.pk
                    }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.post.pk)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, 'Новый текст')
        self.assertEqual(post_edit.group, self.group)


