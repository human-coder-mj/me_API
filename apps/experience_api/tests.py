from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from profile_api.models import Profile
from .models import WorkExperience


class WorkExperienceModelTest(TestCase):
    """
    Test cases for WorkExperience model
    """
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="Software Developer"
        )
    
    def test_work_experience_creation(self):
        """Test creating a work experience"""
        experience = WorkExperience.objects.create(
            profile=self.profile,
            company="Tech Corp",
            position="Senior Developer",
            location="San Francisco, CA",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 12, 31),
            is_current=False,
            description="Developed web applications",
            achievements="Led team of 5 developers"
        )
        
        self.assertEqual(experience.company, "Tech Corp")
        self.assertEqual(experience.position, "Senior Developer")
        self.assertEqual(str(experience), "Senior Developer at Tech Corp")
    
    def test_current_position(self):
        """Test current position without end date"""
        experience = WorkExperience.objects.create(
            profile=self.profile,
            company="Current Corp",
            position="Lead Developer",
            start_date=date(2023, 1, 1),
            is_current=True,
            description="Leading development team"
        )
        
        self.assertTrue(experience.is_current)
        self.assertIsNone(experience.end_date)


class WorkExperienceAPITest(APITestCase):
    """
    Test cases for WorkExperience API endpoints
    """
    
    def setUp(self):
        # Create test user and admin
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        
        # Create test profile
        self.profile = Profile.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            bio="Data Scientist"
        )
        
        # Create test work experiences
        self.experience1 = WorkExperience.objects.create(
            profile=self.profile,
            company="Data Corp",
            position="Data Scientist",
            location="New York, NY",
            start_date=date(2021, 1, 1),
            end_date=date(2022, 12, 31),
            is_current=False,
            description="Analyzed large datasets"
        )
        
        self.experience2 = WorkExperience.objects.create(
            profile=self.profile,
            company="AI Startup",
            position="Senior Data Scientist",
            location="Remote",
            start_date=date(2023, 1, 1),
            is_current=True,
            description="Developing ML models"
        )
    
    def test_get_experience_list(self):
        """Test retrieving work experience list"""
        url = reverse('experience-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_experience_detail(self):
        """Test retrieving specific work experience"""
        url = reverse('experience-detail', kwargs={'pk': self.experience1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Data Corp')
        self.assertEqual(response.data['position'], 'Data Scientist')
    
    def test_create_experience_as_admin(self):
        """Test creating work experience as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('experience-list-create')
        data = {
            'profile_name': 'Jane Smith',
            'company': 'New Company',
            'position': 'Lead Scientist',
            'location': 'Boston, MA',
            'start_date': '2024-01-01',
            'is_current': True,
            'description': 'Leading research team'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkExperience.objects.count(), 3)
    
    def test_create_experience_as_regular_user(self):
        """Test creating work experience as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('experience-list-create')
        data = {
            'profile_name': 'Jane Smith',
            'company': 'Unauthorized Company',
            'position': 'Developer',
            'start_date': '2024-01-01',
            'is_current': True,
            'description': 'Should not be created'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_experience_as_admin(self):
        """Test updating work experience as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('experience-detail', kwargs={'pk': self.experience1.pk})
        data = {
            'profile': self.profile.pk,
            'company': 'Updated Company',
            'position': 'Senior Data Scientist',
            'location': 'Updated Location',
            'start_date': '2021-01-01',
            'end_date': '2022-12-31',
            'is_current': False,
            'description': 'Updated description'
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Updated Company')
    
    def test_delete_experience_as_admin(self):
        """Test deleting work experience as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('experience-detail', kwargs={'pk': self.experience1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WorkExperience.objects.count(), 1)
    
    def test_filter_by_profile_name(self):
        """Test filtering experiences by profile name"""
        url = reverse('experience-list-create')
        response = self.client.get(url, {'profile_name': 'Jane Smith'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_by_company(self):
        """Test filtering experiences by company"""
        url = reverse('experience-list-create')
        response = self.client.get(url, {'company': 'Data Corp'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company'], 'Data Corp')
    
    def test_filter_current_only(self):
        """Test filtering current positions only"""
        url = reverse('experience-list-create')
        response = self.client.get(url, {'current_only': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_current'])
    
    def test_search_experiences(self):
        """Test searching across experience fields"""
        url = reverse('experience-list-create')
        response = self.client.get(url, {'search': 'Data'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both have "Data" in company or position
    
    def test_experience_by_profile_name(self):
        """Test getting experiences by profile name"""
        url = reverse('experience-by-profile-name', kwargs={'name': 'Jane Smith'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_experience_by_profile_name_not_found(self):
        """Test getting experiences for non-existent profile"""
        url = reverse('experience-by-profile-name', kwargs={'name': 'Non Existent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_experience_stats(self):
        """Test experience statistics endpoint"""
        url = reverse('experience-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_experiences'], 2)
        self.assertEqual(response.data['current_positions'], 1)
        self.assertEqual(response.data['past_positions'], 1)
    
    def test_validation_current_with_end_date(self):
        """Test validation: current position cannot have end date"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('experience-list-create')
        data = {
            'profile_name': 'Jane Smith',
            'company': 'Test Company',
            'position': 'Test Position',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',  # This should fail
            'is_current': True,
            'description': 'Test description'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validation_non_current_without_end_date(self):
        """Test validation: non-current position must have end date"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('experience-list-create')
        data = {
            'profile_name': 'Jane Smith',
            'company': 'Test Company',
            'position': 'Test Position',
            'start_date': '2024-01-01',
            'is_current': False,  # This should fail without end_date
            'description': 'Test description'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
