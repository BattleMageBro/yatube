from django.test import TestCase, Client, override_settings
from .models import User, Post, Group, Follow
from django.urls import reverse
TEST_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
# Create your tests here.


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pupa', email='pupa@mail.ru', password='12345678')
        self.post = Post.objects.create(text="Привет, давно не виделись!", author=self.user)    

    def test_profile_view(self):
        response = self.client.get('/pupa/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_count'], 1)
        self.assertIsInstance(response.context['user_profile'], User)
        self.assertEqual(response.context['user_profile'].username, self.user.username)

    def test_new_post(self):
        self.client.login(username='pupa', password='12345678')
        response = self.client.post('/new/', {'text': 'Создаю Новый пост!'}, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_count'],2)
        self.assertIsInstance(response.context['user_profile'], User)
        self.assertEqual(response.context['user_profile'].username, self.user.username)

    def test_new_post_no_auth(self):
        response = self.client.post(reverse('new_post'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=%2Fnew%2F')

    def test_tripple_post_index(self):
        self.client.login(username='pupa', password='12345678')
        response = self.client.get('/')
        self.assertContains(response, self.post.text, count=1)

    def test_tripple_post_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, self.post.text, count=1)

    def test_tripple_post_post_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('posts', kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertContains(response, self.post.text, count=1)
        
    @override_settings(CACHES=TEST_CACHE)
    def test_tripple_post_edit_index(self):
        self.client.login(username='pupa', password='12345678')
        self.client.post(f'/{self.user.username}/{self.post.id}/edit/', {'text': 'О, это снова Вы!'}, follow=False)
        response = self.client.get('/')
        self.assertContains(response, 'О, это снова Вы!', count=1)
    
    @override_settings(CACHES=TEST_CACHE)
    def test_tripple_post_edit_profile(self):
        self.client.force_login(self.user)
        self.client.post(f'/{self.user.username}/{self.post.id}/edit/', {'text': 'О, это снова Вы!'}, follow=False)
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, 'О, это снова Вы!', count=1)
    
    @override_settings(CACHES=TEST_CACHE)
    def test_tripple_post_edit_post_view(self):
        self.client.force_login(self.user)
        self.client.post(f'/{self.user.username}/{self.post.id}/edit/', {'text': 'О, это снова Вы!'}, follow=False)
        response = self.client.get(reverse('posts', kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertContains(response, 'О, это снова Вы!', count=1)


class FollowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='pupa', email='pupa@mail.ru', password='12345')
        self.user2 = User.objects.create_user(username='lupa', email='lupa@mail.ru', password='54321')
        self.user3 = User.objects.create_user(username='kamon', email='kam@mail.ru', password='15243')
        self.post = Post.objects.create(text='Для всех моих подписчиков', author=self.user2)

    def test_follow(self):
        self.client.force_login(self.user1)
        self.client.get(reverse('profile_follow', kwargs={'username': self.user2.username}))
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow(self):
        self.client.force_login(self.user1)
        self.client.get(reverse('profile_follow', kwargs={'username': self.user2.username}))
        self.client.get(reverse('profile_unfollow', kwargs={'username': self.user2.username}))
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_post(self):
        self.client.force_login(self.user1)
        self.client.get(reverse('profile_follow', kwargs={'username': self.user2.username}))
        response = self.client.get('/follow/')
        self.assertContains(response, self.post.text, status_code=200)
        self.client.force_login(self.user3)
        response = self.client.get('/follow/')
        self.assertNotContains(response, self.post.text, status_code=200)


class CommentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pupa', email='pupa@mail.ru', password='12345')
        self.post = Post.objects.create(text='Для комментиков=)', author=self.user)

    def test_add_comment_no_auth(self):
        response = self.client.post(reverse('add_comment', kwargs={'username': self.user.username, 'post_id': self.post.id }), follow=True)
        self.assertRedirects(response, '/auth/login/?next=%2Fpupa%2F1%2Fcomment%2F')

    def test_add_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('add_comment', kwargs={'username': self.user.username, 'post_id': self.post.id }), {'text': 'Комментик=)'}, follow=True)
        self.assertContains(response, 'Комментик=)')


class ImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pupa', email='pupa@mail.ru', password='12345')
        self.post = Post.objects.create(text='Картиночка подъехала', author=self.user)
        self.group = Group.objects.create(title='Любители картинок', slug='Love', description='lovelove')
        
    @override_settings(CACHES=TEST_CACHE)
    def test_image_post(self):
        self.client.force_login(self.user)
        with open('media/tests/Test.jpg', 'rb') as fp:
            response = self.client.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id}), {'text': self.post.text, 'image': fp, 'group': self.group.id}, follow=True)
        response_dec = response.content.decode('utf-8')
        self.assertIn('<img', response_dec)
        response = self.client.get('/')
        response_dec = response.content.decode('utf-8')
        self.assertIn('<img', response_dec)
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        response_dec = response.content.decode('utf-8')
        self.assertIn('<img', response_dec)
