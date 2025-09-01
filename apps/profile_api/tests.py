from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Profile
from django.urls import reverse


class ProfileModelTest(TestCase):
    """Test cases for Profile model"""
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="Software Developer"
        )
    
    def test_profile_creation(self):
        """Test profile creation"""
        self.assertEqual(self.profile.name, "John Doe")
        self.assertEqual(self.profile.email, "john@example.com")
        self.assertEqual(str(self.profile), "John Doe")
    
    def test_email_uniqueness(self):
        """Test email uniqueness constraint"""
        with self.assertRaises(Exception):
            Profile.objects.create(
                name="Jane Doe",
                email="john@example.com",  # Same email
                bio="Designer"
            )


class ProfileAPITest(APITestCase):
    """Test cases for Profile API endpoints"""
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="Software Developer"
        )
    
    def test_get_profile_list(self):
        """Test retrieving profile list"""
        url = reverse('profile_api:profile-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_profile(self):
        """Test creating a new profile"""
        url = reverse('profile_api:profile-list-create')
        data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'bio': 'UI/UX Designer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 2)
    
    def test_get_profile_detail(self):
        """Test retrieving profile detail"""
        url = reverse('profile_api:profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
    
    def test_update_profile(self):
        """Test updating a profile"""
        url = reverse('profile_api:profile-detail', kwargs={'pk': self.profile.pk})
        data = {
            'name': 'John Updated',
            'email': 'john@example.com',
            'bio': 'Senior Software Developer'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'John Updated')
    
    def test_delete_profile(self):
        """Test deleting a profile"""
        url = reverse('profile_api:profile-detail', kwargs={'pk': self.profile.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profile.objects.count(), 0)
