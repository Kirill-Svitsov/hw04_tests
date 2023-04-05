from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..views import num_of_pub

User = get_user_model()
TEXT_ONE = 'Текст поста один'
TEXT_TWO = 'Текст поста два'
FIRST_TITLE = 'Тестовая группа'
SECOND_TITLE = 'Вторая группа'
SLUG = 'test_slug'
SECOND_SLUG = 'test_slug_second'
DESCRIPTION = 'Тестовое описание'
SECOND_DESCRIPTION = 'Тестовое описание 2'
USER_ONE = 'HasNoName'
USER_TWO = 'Second_User'
POSTS_OF_FIRST_AUTHOR = 13
POSTS_OF_SECOND_AUTHOR = 2
POST_ID_ONE = 13
POST_ID_TWO = 14
POSTS_PAGINATOR_SECOND_PAGE = 5
POSTS_OF_GROUP_PAGE = 2


# python3 manage.py test posts.tests.test_views для запуска локальных тестов

class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_ONE)
        cls.second_user = User.objects.create(username=USER_TWO)
        cls.group = Group.objects.create(
            title=FIRST_TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.second_group = Group.objects.create(
            title=SECOND_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_DESCRIPTION
        )
        for post in range(POSTS_OF_FIRST_AUTHOR):
            cls.post = Post.objects.create(
                text=TEXT_ONE,
                author=cls.user,
                group=cls.group
            )
        for post in range(POSTS_OF_SECOND_AUTHOR):
            cls.post = Post.objects.create(
                text=TEXT_TWO,
                author=cls.second_user,
                group=cls.second_group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.second_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile',
                    kwargs={'username': USER_TWO}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': POST_ID_ONE}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': POST_ID_TWO}): 'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post_group_list = list(Post.objects.filter(
            group_id=self.group.id
        )[:10])
        self.assertEqual(list(response.context['page_obj']), post_group_list)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': USER_TWO}))
        first_post = response.context['page_obj'][0]
        post_author_0 = first_post.author
        self.assertEqual(post_author_0, PostViewsTests.post.author)
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_SECOND_AUTHOR
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_post = response.context['post']
        self.assertEqual(first_post.pk, PostViewsTests.post.pk)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), num_of_pub)

    def test_paginator_second_page_contains_five_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_PAGINATOR_SECOND_PAGE
        )

    def test_paginator_group_list_contains_two_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug_second'})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_GROUP_PAGE
        )

    def test_paginator_profile_contains_two_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': USER_TWO})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_SECOND_AUTHOR
        )
