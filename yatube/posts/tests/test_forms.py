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
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), 0)
        form_data = {'text': 'Текст поста',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])

    def test_guest_client_create_post(self):
        """Создание записи возможно только авторизованному пользователю"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.pk,
        }
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_authorized_edit_post(self):
        """Редактирование записи автором поста"""
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.pk}
        post_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True)
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(Post.objects.count(), post_count)
        response_group = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response_group.context['page_obj']), 1)
