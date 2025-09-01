from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from profile_api.models import Profile
from .models import Project


class ProjectModelTest(TestCase):
    """
    Test cases for Project model
    """
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="Jane Developer",
            email="jane@example.com",
            bio="Full Stack Developer"
        )
    
    def test_project_creation(self):
        """Test creating a project"""
        project = Project.objects.create(
            profile=self.profile,
            title="Portfolio Website",
            description="Personal portfolio built with Django and React",
            technologies="Django, React, PostgreSQL",
            github_link="https://github.com/jane/portfolio",
            live_link="https://jane-portfolio.com",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 1),
            is_featured=True
        )
        
        self.assertEqual(project.title, "Portfolio Website")
        self.assertTrue(project.is_featured)
        self.assertEqual(str(project), "Portfolio Website")
    
    def test_project_ordering(self):
        """Test project ordering (featured first, then by start date)"""
        project1 = Project.objects.create(
            profile=self.profile,
            title="Old Project",
            description="An older project",
            technologies="Python",
            start_date=date(2022, 1, 1),
            is_featured=False
        )
        
        project2 = Project.objects.create(
            profile=self.profile,
            title="Featured Project",
            description="A featured project",
            technologies="Django",
            start_date=date(2023, 1, 1),
            is_featured=True
        )
        
        project3 = Project.objects.create(
            profile=self.profile,
            title="Recent Project",
            description="A recent project",
            technologies="React",
            start_date=date(2024, 1, 1),
            is_featured=False
        )
        
        projects = list(Project.objects.all())
        # Should be ordered: featured first, then by start_date descending
        self.assertEqual(projects[0], project2)  # Featured
        self.assertEqual(projects[1], project3)  # Recent non-featured
        self.assertEqual(projects[2], project1)  # Old non-featured


class ProjectAPITest(APITestCase):
    """
    Test cases for Project API endpoints
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
            name="Alex Coder",
            email="alex@example.com",
            bio="Software Engineer"
        )
        
        # Create test projects
        self.project1 = Project.objects.create(
            profile=self.profile,
            title="E-commerce Platform",
            description="Full-featured e-commerce platform",
            technologies="Django, React, PostgreSQL, Redis",
            github_link="https://github.com/alex/ecommerce",
            live_link="https://shop.example.com",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 1),
            is_featured=True
        )
        
        self.project2 = Project.objects.create(
            profile=self.profile,
            title="Task Manager",
            description="Simple task management application",
            technologies="Flask, SQLite, JavaScript",
            github_link="https://github.com/alex/tasks",
            start_date=date(2023, 7, 1),
            is_featured=False
        )
    
    def test_get_project_list(self):
        """Test retrieving project list"""
        url = reverse('project-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_project_detail(self):
        """Test retrieving specific project"""
        url = reverse('project-detail', kwargs={'pk': self.project1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'E-commerce Platform')
        self.assertTrue(response.data['is_featured'])
    
    def test_create_project_as_admin(self):
        """Test creating project as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('project-list-create')
        data = {
            'profile_name': 'Alex Coder',
            'title': 'New Project',
            'description': 'A brand new project',
            'technologies_list': ['Python', 'Django', 'React'],
            'github_link': 'https://github.com/alex/new-project',
            'start_date': '2024-01-01',
            'is_featured': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 3)
    
    def test_create_project_as_regular_user(self):
        """Test creating project as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('project-list-create')
        data = {
            'profile_name': 'Alex Coder',
            'title': 'Unauthorized Project',
            'description': 'Should not be created',
            'technologies': 'Python',
            'start_date': '2024-01-01',
            'is_featured': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_project_as_admin(self):
        """Test updating project as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('project-detail', kwargs={'pk': self.project1.pk})
        data = {
            'profile': self.profile.pk,
            'title': 'Updated E-commerce Platform',
            'description': 'Updated description',
            'technologies': 'Django, React, PostgreSQL, Redis, Docker',
            'github_link': 'https://github.com/alex/ecommerce-v2',
            'live_link': 'https://shop-v2.example.com',
            'start_date': '2023-01-01',
            'end_date': '2023-06-01',
            'is_featured': True
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated E-commerce Platform')
    
    def test_delete_project_as_admin(self):
        """Test deleting project as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('project-detail', kwargs={'pk': self.project1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 1)
    
    def test_filter_by_profile_name(self):
        """Test filtering projects by profile name"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'profile_name': 'Alex Coder'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_by_technology(self):
        """Test filtering projects by technology"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'technology': 'Django'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'E-commerce Platform')
    
    def test_filter_featured_only(self):
        """Test filtering featured projects only"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'featured_only': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_featured'])
    
    def test_filter_has_live_link(self):
        """Test filtering projects with live links"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'has_live_link': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIsNotNone(response.data[0]['live_link'])
    
    def test_search_projects(self):
        """Test searching across project fields"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'search': 'e-commerce'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('E-commerce', response.data[0]['title'])
    
    def test_summary_view(self):
        """Test getting projects with summary serializer"""
        url = reverse('project-list-create')
        response = self.client.get(url, {'summary': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Summary view should have fewer fields
        self.assertNotIn('description', response.data[0])
        self.assertIn('technology_count', response.data[0])
    
    def test_projects_by_profile_name(self):
        """Test getting projects by profile name"""
        url = reverse('projects-by-profile-name', kwargs={'name': 'Alex Coder'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_projects_by_profile_name_not_found(self):
        """Test getting projects for non-existent profile"""
        url = reverse('projects-by-profile-name', kwargs={'name': 'Non Existent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_featured_projects(self):
        """Test featured projects endpoint"""
        url = reverse('featured-projects')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_featured'])
    
    def test_projects_by_technology(self):
        """Test projects by technology endpoint"""
        url = reverse('projects-by-technology', kwargs={'technology': 'Django'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Django', response.data[0]['technologies'])
    
    def test_project_stats(self):
        """Test project statistics endpoint"""
        url = reverse('project-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_projects'], 2)
        self.assertEqual(response.data['featured_projects'], 1)
        self.assertIn('top_technologies', response.data)
        self.assertIn('top_profiles', response.data)
    
    def test_validation_start_date_before_end_date(self):
        """Test validation: start date must be before end date"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('project-list-create')
        data = {
            'profile_name': 'Alex Coder',
            'title': 'Invalid Date Project',
            'description': 'This should fail validation',
            'technologies': 'Python',
            'start_date': '2024-12-31',
            'end_date': '2024-01-01',  # This should fail
            'is_featured': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_technologies_list_processing(self):
        """Test that technologies_list is properly converted to comma-separated string"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('project-list-create')
        data = {
            'profile_name': 'Alex Coder',
            'title': 'Tech List Test',
            'description': 'Testing technologies list processing',
            'technologies_list': ['Python', 'Django', 'React', 'PostgreSQL'],
            'start_date': '2024-01-01',
            'is_featured': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the project was created with proper technologies string
        project = Project.objects.get(title='Tech List Test')
        self.assertIn('Python', project.technologies)
        self.assertIn('Django', project.technologies)
        self.assertIn('React', project.technologies)
        self.assertIn('PostgreSQL', project.technologies)
