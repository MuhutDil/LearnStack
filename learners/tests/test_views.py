from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from courses.models import Course, Module, Subject
 
User = get_user_model()
 

FAST_PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
 

@override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
class LearnerRegistrationViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('learner_registration')
 
    def test_registration_get(self):
        """Test that the registration page renders correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learners/registration.html')
 
    def test_registration_post_valid(self):
        """Test successful registration logs the user in and redirects."""
        data = {
            'username': 'newlearner',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        response = self.client.post(self.url, data)
        
        # Should redirect to course list on success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('learner_course_list'))
        
        # Verify user is created and authenticated in the session
        self.assertTrue(User.objects.filter(username='newlearner').exists())
        self.assertIn('_auth_user_id', self.client.session)
 
    def test_registration_post_invalid(self):
        """Test that invalid data re-renders the form with errors."""
        data = {
            'username': '',
            'password1': 'pwd',
            'password2': 'pwd',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
 
 
@override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
class LearnerEnrollCourseViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='learner', password='password')
        cls.subject = Subject.objects.create(title='Unit Test', slug='unit_test')
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.url = reverse('learner_enroll_course')
 
    def test_enroll_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.post(self.url, {'course': self.course.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
 
    def test_enroll_authenticated(self):
        """Test that authenticated users can enroll and are redirected correctly."""
        self.client.login(username='learner', password='password')
        data = {'course': self.course.id}
        self.client.post(self.url, data)
        
        self.assertTrue(self.course.learners.filter(pk=self.user.pk).exists())
 
 
@override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
class LearnerCourseListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='learner', password='password')
        cls.subject = Subject.objects.create(title='Unit Test', slug='unit_test')
        
        cls.course_enrolled = Course.objects.create(
            owner=cls.user, subject=cls.subject, title='Enrolled Course',
            slug='enrolled_course', overview='Test overview'
        )
        cls.course_enrolled.learners.add(cls.user)
        
        cls.course_not_enrolled = Course.objects.create(
            owner=cls.user, subject=cls.subject, title='Not Enrolled Course',
            slug='not_enrolled_course', overview='Test overview'
        )
        cls.url = reverse('learner_course_list')
 
    def test_list_unauthenticated(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
 
    def test_list_authenticated_filters_queryset(self):
        """Test that the list only shows courses the user is enrolled in."""
        self.client.login(username='learner', password='password')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learners/list.html')
        
        courses_in_context = list(response.context['object_list'])
        self.assertIn(self.course_enrolled, courses_in_context)
        self.assertNotIn(self.course_not_enrolled, courses_in_context)
 
 
@override_settings(
    PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class LearnerCourseDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='learner', password='password')
        cls.other_user = User.objects.create_user(username='other', password='password')
        
        cls.subject = Subject.objects.create(title='Unit Test', slug='unit_test')
        cls.course = Course.objects.create(
            owner=cls.user, subject=cls.subject, title='Detail Course',
            slug='detail_course', overview='Test overview'
        )
        cls.course.learners.add(cls.user)
        cls.module = Module.objects.create(
            course=cls.course, title="Basics", description="Basic concepts"
        )
        cls.url = reverse('learner_course_detail', args=[cls.course.id])
    
    def test_detail_unauthenticated(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
 
    def test_detail_unenrolled_user_returns_404(self):
        """Test that an authenticated but unenrolled user gets a 404."""
        self.client.login(username='other', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
 
    def test_detail_enrolled_user_no_module_id(self):
        """Test default module context when no module_id is provided in URL."""
        self.client.login(username='learner', password='password')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learners/detail.html')
        
        self.assertEqual(response.context['module'], self.module)
 