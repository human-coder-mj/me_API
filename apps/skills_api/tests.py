from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import IntegrityError
from profile_api.models import Profile
from .models import Skill


class SkillModelTest(TestCase):
    """
    Test cases for Skill model
    """
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="Tech Expert",
            email="expert@example.com",
            bio="Senior Software Engineer"
        )
    
    def test_skill_creation(self):
        """Test creating a skill"""
        skill = Skill.objects.create(
            profile=self.profile,
            name="Python",
            level="advanced",
            category="Programming"
        )
        
        self.assertEqual(skill.name, "Python")
        self.assertEqual(skill.level, "advanced")
        self.assertEqual(skill.category, "Programming")
        self.assertEqual(str(skill), "Python (advanced)")
    
    def test_skill_level_choices(self):
        """Test skill level choices"""
        skill = Skill.objects.create(
            profile=self.profile,
            name="JavaScript",
            level="expert",
            category="Programming"
        )
        
        self.assertEqual(skill.get_level_display(), "Expert")
    
    def test_unique_together_constraint(self):
        """Test that profile + name combination must be unique"""
        Skill.objects.create(
            profile=self.profile,
            name="Django",
            level="advanced",
            category="Programming"
        )
        
        # This should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            Skill.objects.create(
                profile=self.profile,
                name="Django",  # Same name, same profile
                level="expert",
                category="Framework"
            )
    
    def test_skill_ordering(self):
        """Test default skill ordering"""
        skill1 = Skill.objects.create(
            profile=self.profile,
            name="React",
            level="intermediate",
            category="Programming"
        )
        
        skill2 = Skill.objects.create(
            profile=self.profile,
            name="Angular",
            level="beginner",
            category="Programming"
        )
        
        skill3 = Skill.objects.create(
            profile=self.profile,
            name="Photoshop",
            level="advanced",
            category="Design"
        )
        
        skills = list(Skill.objects.all())
        # Should be ordered by category, then name
        categories = [skill.category for skill in skills]
        self.assertEqual(categories, ['Design', 'Programming', 'Programming'])


class SkillAPITest(APITestCase):
    """
    Test cases for Skill API endpoints
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
            name="Developer Pro",
            email="dev@example.com",
            bio="Full Stack Developer"
        )
        
        # Create test skills
        self.skill1 = Skill.objects.create(
            profile=self.profile,
            name="Python",
            level="expert",
            category="Programming"
        )
        
        self.skill2 = Skill.objects.create(
            profile=self.profile,
            name="React",
            level="advanced",
            category="Programming"
        )
        
        self.skill3 = Skill.objects.create(
            profile=self.profile,
            name="UI/UX Design",
            level="intermediate",
            category="Design"
        )
    
    def test_get_skill_list(self):
        """Test retrieving skill list"""
        url = reverse('skill-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_skill_detail(self):
        """Test retrieving specific skill"""
        url = reverse('skill-detail', kwargs={'pk': self.skill1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Python')
        self.assertEqual(response.data['level'], 'expert')
    
    def test_create_skill_as_admin(self):
        """Test creating skill as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('skill-list-create')
        data = {
            'profile_name': 'Developer Pro',
            'name': 'Docker',
            'level': 'advanced',
            'category': 'DevOps'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Skill.objects.count(), 4)
    
    def test_create_skill_as_regular_user(self):
        """Test creating skill as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('skill-list-create')
        data = {
            'profile_name': 'Developer Pro',
            'name': 'Unauthorized Skill',
            'level': 'beginner',
            'category': 'Test'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_duplicate_skill(self):
        """Test creating duplicate skill (should fail)"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('skill-list-create')
        data = {
            'profile_name': 'Developer Pro',
            'name': 'Python',  # Already exists
            'level': 'beginner',
            'category': 'Programming'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_skill_as_admin(self):
        """Test updating skill as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('skill-detail', kwargs={'pk': self.skill2.pk})
        data = {
            'profile': self.profile.pk,
            'name': 'React',
            'level': 'expert',  # Updated from advanced
            'category': 'Frontend'  # Updated category
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['level'], 'expert')
        self.assertEqual(response.data['category'], 'Frontend')
    
    def test_delete_skill_as_admin(self):
        """Test deleting skill as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('skill-detail', kwargs={'pk': self.skill1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Skill.objects.count(), 2)
    
    def test_filter_by_profile_name(self):
        """Test filtering skills by profile name"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'profile_name': 'Developer Pro'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_filter_by_level(self):
        """Test filtering skills by level"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'level': 'expert'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Python')
    
    def test_filter_by_category(self):
        """Test filtering skills by category"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'category': 'Programming'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_by_skill_name(self):
        """Test filtering skills by skill name"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'skill_name': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Python')
    
    def test_search_skills(self):
        """Test searching across skill fields"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'search': 'Design'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Design', response.data[0]['category'])
    
    def test_summary_view(self):
        """Test getting skills with summary serializer"""
        url = reverse('skill-list-create')
        response = self.client.get(url, {'summary': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Summary view should have level_display
        self.assertIn('level_display', response.data[0])
    
    def test_skills_by_profile_name(self):
        """Test getting skills by profile name"""
        url = reverse('skills-by-profile-name', kwargs={'name': 'Developer Pro'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_skills_by_profile_name_not_found(self):
        """Test getting skills for non-existent profile"""
        url = reverse('skills-by-profile-name', kwargs={'name': 'Non Existent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_skills_by_category(self):
        """Test skills by category endpoint"""
        url = reverse('skills-by-category', kwargs={'category': 'Programming'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_skills_by_level(self):
        """Test skills by level endpoint"""
        url = reverse('skills-by-level', kwargs={'level': 'advanced'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'React')
    
    def test_skills_grouped_by_category(self):
        """Test skills grouped by category endpoint"""
        url = reverse('skills-grouped-by-category')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Programming and Design categories
        
        # Check structure
        for group in response.data:
            self.assertIn('category', group)
            self.assertIn('skills', group)
            self.assertIn('skill_count', group)
            self.assertIn('level_breakdown', group)
    
    def test_skill_stats(self):
        """Test skill statistics endpoint"""
        url = reverse('skill-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_skills'], 3)
        self.assertEqual(response.data['unique_skills'], 3)
        self.assertEqual(response.data['categories_count'], 2)
        self.assertIn('level_distribution', response.data)
        self.assertIn('top_categories', response.data)
        self.assertIn('top_skills', response.data)
        self.assertIn('available_levels', response.data)
    
    def test_skill_level_display(self):
        """Test that level_display shows human-readable level"""
        url = reverse('skill-detail', kwargs={'pk': self.skill1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['level'], 'expert')
        self.assertEqual(response.data['level_display'], 'Expert')
    
    def test_create_skill_with_invalid_profile(self):
        """Test creating skill with non-existent profile"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('skill-list-create')
        data = {
            'profile_name': 'Non Existent Profile',
            'name': 'Test Skill',
            'level': 'beginner',
            'category': 'Test'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
