from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from profile_api.models import Profile
from .models import Education
from datetime import date


class EducationModelTest(TestCase):
    """Test cases for Education model"""
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="Software Developer"
        )
        self.education = Education.objects.create(
            profile=self.profile,
            institution="University of Technology",
            degree="Bachelor of Computer Science",
            field_of_study="Computer Science",
            start_date=date(2018, 9, 1),
            end_date=date(2022, 6, 30),
            grade="First Class",
            description="Focused on software engineering and algorithms"
        )
    
    def test_education_creation(self):
        """Test education record creation"""
        self.assertEqual(self.education.institution, "University of Technology")
        self.assertEqual(self.education.degree, "Bachelor of Computer Science")
        self.assertEqual(str(self.education), "Bachelor of Computer Science at University of Technology")
    
    def test_education_ordering(self):
        """Test education records are ordered by start_date descending"""
        education2 = Education.objects.create(
            profile=self.profile,
            institution="High School",
            degree="High School Diploma",
            start_date=date(2016, 9, 1),
            end_date=date(2018, 6, 30)
        )
        
        education_list = list(Education.objects.all())
        self.assertEqual(education_list[0], self.education)  # Most recent first
        self.assertEqual(education_list[1], education2)


class EducationAPITest(APITestCase):
    """Test cases for Education API endpoints"""
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="Software Developer"
        )
        self.education = Education.objects.create(
            profile=self.profile,
            institution="University of Technology",
            degree="Bachelor of Computer Science",
            field_of_study="Computer Science",
            start_date=date(2018, 9, 1),
            end_date=date(2022, 6, 30),
            grade="First Class"
        )
        
        # Create admin user for write operations
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
    
    def test_get_education_list(self):
        """Test retrieving education list (public access)"""
        url = reverse('education_api:education-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_education_detail(self):
        """Test retrieving education detail (public access)"""
        url = reverse('education_api:education-detail', kwargs={'pk': self.education.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['institution'], 'University of Technology')
    
    def test_create_education_unauthorized(self):
        """Test creating education without admin privileges (should fail)"""
        url = reverse('education_api:education-list-create')
        data = {
            'profile': self.profile.id,
            'institution': 'New University',
            'degree': 'Master of Science',
            'start_date': '2022-09-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_education_authorized(self):
        """Test creating education with admin privileges"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('education_api:education-list-create')
        data = {
            'profile': self.profile.id,
            'institution': 'New University',
            'degree': 'Master of Science',
            'field_of_study': 'Data Science',
            'start_date': '2022-09-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 2)
    
    def test_education_by_profile(self):
        """Test getting education records by profile"""
        url = reverse('education_api:education-by-profile', kwargs={'profile_id': self.profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['education_count'], 1)
    
    def test_education_by_profile_name(self):
        """Test getting education records by profile name"""
        url = reverse('education_api:education-by-profile-name', kwargs={'name': self.profile.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['education_count'], 1)
        self.assertEqual(response.data['profile_name'], 'John Doe')
    
    def test_education_by_profile_name_not_found(self):
        """Test getting education records by non-existent profile name"""
        url = reverse('education_api:education-by-profile-name', kwargs={'name': 'Non Existent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_education_search(self):
        """Test education search functionality"""
        url = reverse('education_api:education-search')
        response = self.client.get(url, {'q': 'Computer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results_count'], 1)
    
    def test_education_institutions(self):
        """Test getting list of institutions"""
        url = reverse('education_api:education-institutions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('University of Technology', response.data['institutions'])
    
    def test_education_degrees(self):
        """Test getting list of degrees"""
        url = reverse('education_api:education-degrees')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Bachelor of Computer Science', response.data['degrees'])
    
    def test_education_stats(self):
        """Test education statistics"""
        url = reverse('education_api:education-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_education_records'], 1)
    
    def test_education_filtering(self):
        """Test education filtering by various parameters"""
        url = reverse('education_api:education-list-create')
        
        # Filter by institution
        response = self.client.get(url, {'institution': 'University'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by degree
        response = self.client.get(url, {'degree': 'Bachelor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by field
        response = self.client.get(url, {'field': 'Computer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_update_education_authorized(self):
        """Test updating education with admin privileges"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('education_api:education-detail', kwargs={'pk': self.education.pk})
        data = {
            'profile': self.profile.id,
            'institution': 'Updated University',
            'degree': 'Bachelor of Computer Science',
            'start_date': '2018-09-01'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, 'Updated University')
    
    def test_delete_education_authorized(self):
        """Test deleting education with admin privileges"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('education_api:education-detail', kwargs={'pk': self.education.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Education.objects.count(), 0)
