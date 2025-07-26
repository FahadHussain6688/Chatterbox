from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import Status
from chat.models import Chat, Message

class StatusAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_create_status(self):
        url = reverse('api_statuses')
        with open('media/status_images/myself.jpg', 'rb') as img:
            response = self.client.post(url, {'image': img}, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_list_statuses(self):
        url = reverse('api_statuses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class ChatAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.client.login(username='user1', password='pass1')
        self.chat = Chat.objects.create()
        self.chat.participants.set([self.user1, self.user2])

    def test_list_chats(self):
        url = reverse('api_chats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_message(self):
        url = reverse('api_chat_messages', args=[self.chat.id])
        response = self.client.post(url, {'content': 'Hello!'}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_list_messages(self):
        url = reverse('api_chat_messages', args=[self.chat.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
