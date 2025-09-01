from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import IntegrityError
from profile_api.models import Profile
from .models import SocialLink


class SocialLinkModelTest(TestCase):
    """
    Test cases for SocialLink model
    """
    
    def setUp(self):
        self.profile = Profile.objects.create(
            name="Social Media Pro",
            email="social@example.com",
            bio="Digital Marketing Expert"
        )
    
    def test_social_link_creation(self):
        """Test creating a social link"""
        link = SocialLink.objects.create(
            profile=self.profile,
            link_type="github",
            url="https://github.com/socialpro",
            display_name="My GitHub"
        )
        
        self.assertEqual(link.link_type, "github")
        self.assertEqual(link.url, "https://github.com/socialpro")
        self.assertEqual(link.display_name, "My GitHub")
        self.assertEqual(str(link), "GitHub: https://github.com/socialpro")
    
    def test_link_type_choices(self):
        """Test link type choices"""
        link = SocialLink.objects.create(
            profile=self.profile,
            link_type="linkedin",
            url="https://linkedin.com/in/socialpro"
        )
        
        self.assertEqual(link.get_link_type_display(), "LinkedIn")
    
    def test_unique_together_constraint(self):
        """Test that profile + link_type combination must be unique"""
        SocialLink.objects.create(
            profile=self.profile,
            link_type="github",
            url="https://github.com/socialpro1"
        )
        
        # This should raise an IntegrityError
        with self.assertRaises(IntegrityError):
            SocialLink.objects.create(
                profile=self.profile,
                link_type="github",  # Same type, same profile
                url="https://github.com/socialpro2"
            )
    
    def test_social_link_without_display_name(self):
        """Test social link creation without display name"""
        link = SocialLink.objects.create(
            profile=self.profile,
            link_type="twitter",
            url="https://twitter.com/socialpro"
        )
        
        self.assertEqual(link.display_name, "")
        self.assertEqual(str(link), "Twitter: https://twitter.com/socialpro")


class SocialLinkAPITest(APITestCase):
    """
    Test cases for SocialLink API endpoints
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
            name="Link Master",
            email="links@example.com",
            bio="Portfolio Showcase Expert"
        )
        
        # Create test social links
        self.link1 = SocialLink.objects.create(
            profile=self.profile,
            link_type="github",
            url="https://github.com/linkmaster",
            display_name="My Code Repository"
        )
        
        self.link2 = SocialLink.objects.create(
            profile=self.profile,
            link_type="linkedin",
            url="https://linkedin.com/in/linkmaster"
        )
        
        self.link3 = SocialLink.objects.create(
            profile=self.profile,
            link_type="portfolio",
            url="https://linkmaster.dev",
            display_name="Personal Portfolio"
        )
    
    def test_get_social_link_list(self):
        """Test retrieving social link list"""
        url = reverse('social-link-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_social_link_detail(self):
        """Test retrieving specific social link"""
        url = reverse('social-link-detail', kwargs={'pk': self.link1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['link_type'], 'github')
        self.assertEqual(response.data['display_name'], 'My Code Repository')
    
    def test_create_social_link_as_admin(self):
        """Test creating social link as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('social-link-list-create')
        data = {
            'profile_name': 'Link Master',
            'link_type': 'twitter',
            'url': 'https://twitter.com/linkmaster',
            'display_name': 'Follow me on Twitter'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SocialLink.objects.count(), 4)
    
    def test_create_social_link_as_regular_user(self):
        """Test creating social link as regular user (should fail)"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('social-link-list-create')
        data = {
            'profile_name': 'Link Master',
            'link_type': 'website',
            'url': 'https://unauthorized.com'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_duplicate_link_type(self):
        """Test creating duplicate link type (should fail)"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('social-link-list-create')
        data = {
            'profile_name': 'Link Master',
            'link_type': 'github',  # Already exists
            'url': 'https://github.com/linkmaster2'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_social_link_as_admin(self):
        """Test updating social link as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('social-link-detail', kwargs={'pk': self.link2.pk})
        data = {
            'profile': self.profile.pk,
            'link_type': 'linkedin',
            'url': 'https://linkedin.com/in/updated-linkmaster',
            'display_name': 'Professional Profile'  # Added display name
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['url'], 'https://linkedin.com/in/updated-linkmaster')
        self.assertEqual(response.data['display_name'], 'Professional Profile')
    
    def test_delete_social_link_as_admin(self):
        """Test deleting social link as admin"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('social-link-detail', kwargs={'pk': self.link1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SocialLink.objects.count(), 2)
    
    def test_filter_by_profile_name(self):
        """Test filtering social links by profile name"""
        url = reverse('social-link-list-create')
        response = self.client.get(url, {'profile_name': 'Link Master'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_filter_by_link_type(self):
        """Test filtering social links by link type"""
        url = reverse('social-link-list-create')
        response = self.client.get(url, {'link_type': 'github'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['link_type'], 'github')
    
    def test_filter_by_platform(self):
        """Test filtering social links by platform (case-insensitive)"""
        url = reverse('social-link-list-create')
        response = self.client.get(url, {'platform': 'linked'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['link_type'], 'linkedin')
    
    def test_search_social_links(self):
        """Test searching across social link fields"""
        url = reverse('social-link-list-create')
        response = self.client.get(url, {'search': 'github'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_summary_view(self):
        """Test getting social links with summary serializer"""
        url = reverse('social-link-list-create')
        response = self.client.get(url, {'summary': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Summary view should have link_type_display
        self.assertIn('link_type_display', response.data[0])
    
    def test_social_links_by_profile_name(self):
        """Test getting social links by profile name"""
        url = reverse('social-links-by-profile-name', kwargs={'name': 'Link Master'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_social_links_by_profile_name_not_found(self):
        """Test getting social links for non-existent profile"""
        url = reverse('social-links-by-profile-name', kwargs={'name': 'Non Existent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_social_links_by_type(self):
        """Test social links by type endpoint"""
        url = reverse('social-links-by-type', kwargs={'link_type': 'github'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['link_type'], 'github')
    
    def test_social_links_grouped_by_type(self):
        """Test social links grouped by type endpoint"""
        url = reverse('social-links-grouped-by-type')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # github, linkedin, portfolio
        
        # Check structure
        for group in response.data:
            self.assertIn('link_type', group)
            self.assertIn('link_type_display', group)
            self.assertIn('links', group)
            self.assertIn('link_count', group)
    
    def test_professional_links(self):
        """Test professional links endpoint"""
        url = reverse('professional-links')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # github, linkedin, portfolio are professional
    
    def test_social_media_links(self):
        """Test social media links endpoint"""
        # Create a Twitter link for testing
        SocialLink.objects.create(
            profile=self.profile,
            link_type="twitter",
            url="https://twitter.com/linkmaster"
        )
        
        url = reverse('social-media-links')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only twitter
        self.assertEqual(response.data[0]['link_type'], 'twitter')
    
    def test_social_stats(self):
        """Test social link statistics endpoint"""
        url = reverse('social-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_links'], 3)
        self.assertEqual(response.data['unique_link_types'], 3)
        self.assertEqual(response.data['profiles_with_links'], 1)
        self.assertIn('link_type_distribution', response.data)
        self.assertIn('most_popular_platforms', response.data)
        self.assertIn('profiles_by_platform', response.data)
        self.assertIn('platform_coverage', response.data)
        self.assertIn('available_link_types', response.data)
    
    def test_link_type_display(self):
        """Test that link_type_display shows human-readable type"""
        url = reverse('social-link-detail', kwargs={'pk': self.link1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['link_type'], 'github')
        self.assertEqual(response.data['link_type_display'], 'GitHub')
    
    def test_create_social_link_with_invalid_profile(self):
        """Test creating social link with non-existent profile"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('social-link-list-create')
        data = {
            'profile_name': 'Non Existent Profile',
            'link_type': 'website',
            'url': 'https://test.com'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
