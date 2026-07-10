from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.urls import reverse
 
from courses.models import Course, Module, Content, Subject, Text, Video, Image, File
from courses.views import ManageCourseListView
 
User = get_user_model()
 
 
class OwnerMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com'
            )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@email.com'
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.other_course = Course.objects.create(
            owner=cls.other_user,
            subject=cls.subject,
            title='Other Course',
            slug='other-course',
            overview='Other overview'
        )
 
    def test_owner_mixin_filters_by_owner(self):
        """Test that OwnerMixin filters queryset by the current user"""
        factory = RequestFactory()
        request = factory.get(reverse('manage_course_list'))
        request.user = self.user
        
        view = ManageCourseListView()
        view.request = request
        
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.course)
 
 
class ManageCourseListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='view_course')
        )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_manage_course_list_view(self):
        """Test that the course list view displays user's courses"""
        response = self.client.get(reverse('manage_course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/course/list.html')
        self.assertContains(response, 'Test Course')
 
    def test_manage_course_list_requires_permission(self):
        """Test that the view requires view_course permission"""
        otheruser = User.objects.create_user(
            username='nopermission',
            email='otheruser@email.com',
            )
        self.client.force_login(otheruser)
        response = self.client.get(reverse('manage_course_list'))
        self.assertEqual(response.status_code, 403)
 
 
class CourseCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='add_course')
        )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_course_create_view_get(self):
        """Test GET request to create a course"""
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/course/form.html')
 
    def test_course_create_view_post_valid(self):
        """Test POST request with valid data to create a course"""
        response = self.client.post(reverse('course_create'), {
            'subject': self.subject.id,
            'title': 'New Course',
            'slug': 'new-course',
            'overview': 'New course overview'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage_course_list'))
        
        course = Course.objects.get(title='New Course')
        self.assertEqual(course.owner, self.user)
 
    def test_course_create_requires_permission(self):
        """Test that the view requires add_course permission"""
        user = User.objects.create_user(username='nopermission')
        self.client.force_login(user)
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 403)
 
 
class CourseUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='change_course')
        )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_course_update_view_get(self):
        """Test GET request to update a course"""
        response = self.client.get(
            reverse('course_edit', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/course/form.html')
        self.assertContains(response, 'Test Course')
 
    def test_course_update_view_post_valid(self):
        """Test POST request with valid data to update a course"""
        response = self.client.post(
            reverse('course_edit', kwargs={'pk': self.course.id}),
            {
                'subject': self.subject.id,
                'title': 'Updated Course',
                'slug': 'updated-course',
                'overview': 'Updated overview'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage_course_list'))
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')
 
    def test_course_update_requires_permission(self):
        """Test that the view requires change_course permission"""
        user = User.objects.create_user(username='nopermission')
        self.client.force_login(user)
        response = self.client.get(
            reverse('course_edit', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 403)
 
 
class CourseDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='delete_course')
        )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_course_delete_view_get(self):
        """Test GET request to delete a course"""
        response = self.client.get(
            reverse('course_delete', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/course/delete.html')
 
    def test_course_delete_view_post(self):
        """Test POST request to delete a course"""
        response = self.client.post(
            reverse('course_delete', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('manage_course_list'))
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())
 
    def test_course_delete_requires_permission(self):
        """Test that the view requires delete_course permission"""
        user = User.objects.create_user(username='nopermission')
        self.client.force_login(user)
        response = self.client.get(
            reverse('course_delete', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 403)
 
 
class CourseModuleUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module1 = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        cls.module2 = Module.objects.create(
            course=cls.course,
            title='Module 2',
            description='Description 2',
            order=2
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_course_module_update_view_get(self):
        """Test GET request to update course modules"""
        response = self.client.get(
            reverse('course_module_update', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/module/formset.html')
        self.assertContains(response, 'Module 1')
        self.assertContains(response, 'Module 2')
 
    def test_course_module_update_requires_ownership(self):
        """Test that only the course owner can update modules"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.get(
            reverse('course_module_update', kwargs={'pk': self.course.id})
        )
        self.assertEqual(response.status_code, 404)
 
 
class ContentCreateUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com')
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_content_create_view_get_text(self):
        """Test GET request to create text content"""
        response = self.client.get(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'text'
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/content/form.html')
 
    def test_content_create_view_post_text(self):
        """Test POST request to create text content"""
        response = self.client.post(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'text'
            }),
            {
                'title': 'Text Content',
                'content': 'This is some text content'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('module_content_list', kwargs={'module_id': self.module.id})
        )
        text = Text.objects.get(title='Text Content')
        self.assertEqual(text.owner, self.user)
        self.assertTrue(
            Content.objects.filter(module=self.module, object_id=text.id).exists()
        )
 
    def test_content_create_view_post_video(self):
        """Test POST request to create video content"""
        response = self.client.post(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'video'
            }),
            {
                'title': 'Video Content',
                'url': 'https://www.youtube.com/watch?v=test'
            }
        )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(title='Video Content')
        self.assertEqual(video.owner, self.user)
        self.assertTrue(
            Content.objects.filter(module=self.module, object_id=video.id).exists()
        )
 
    def test_content_create_view_post_image(self):
        """Test POST request to create image content"""
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            b'file_content',
            content_type='image/jpeg'
        )
        response = self.client.post(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'image'
            }),
            {
                'title': 'Image Content',
                'file': image_file
            }
        )
        self.assertEqual(response.status_code, 302)
        image = Image.objects.get(title='Image Content')
        self.assertEqual(image.owner, self.user)
        self.assertTrue(
            Content.objects.filter(module=self.module, object_id=image.id).exists()
        )
 
    def test_content_create_view_post_file(self):
        """Test POST request to create file content"""
        file_obj = SimpleUploadedFile(
            'test_file.txt',
            b'file_content',
            content_type='text/plain'
        )
        response = self.client.post(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'file'
            }),
            {
                'title': 'File Content',
                'file': file_obj
            }
        )
        self.assertEqual(response.status_code, 302)
        file_content = File.objects.get(title='File Content')
        self.assertEqual(file_content.owner, self.user)  
        self.assertTrue(
            Content.objects.filter(module=self.module, object_id=file_content.id).exists()
        )
 
    def test_content_update_view_get(self):
        """Test GET request to update existing content"""
        text = Text.objects.create(
            owner=self.user,
            title='Existing Text',
            content='Existing content'
        )
        content = Content.objects.create(
            module=self.module,
            item=text
        )
        response = self.client.get(
            reverse('module_content_update', kwargs={
                'module_id': self.module.id,
                'model_name': 'text',
                'id': content.id
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing Text')
 
    def test_content_update_view_post(self):
        """Test POST request to update existing content"""
        text = Text.objects.create(
            owner=self.user,
            title='Existing Text',
            content='Existing content'
        )
        content = Content.objects.create(
            module=self.module,
            item=text
        )
        response = self.client.post(
            reverse('module_content_update', kwargs={
                'module_id': self.module.id,
                'model_name': 'text',
                'id': content.id
            }),
            {
                'title': 'Updated Text',
                'content': 'Updated content'
            }
        )
        self.assertEqual(response.status_code, 302)
        text.refresh_from_db()
        self.assertEqual(text.title, 'Updated Text')
 
    def test_content_create_requires_ownership(self):
        """Test that only the course owner can create content"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.get(
            reverse('module_content_create', kwargs={
                'module_id': self.module.id,
                'model_name': 'text'
            })
        )
        self.assertEqual(response.status_code, 404)
 
 
class ContentDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        cls.text = Text.objects.create(
            owner=cls.user,
            title='Text Content',
            content='Some content'
        )
        cls.content = Content.objects.create(
            module=cls.module,
            item=cls.text
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_content_delete_view_post(self):
        """Test POST request to delete content"""
        response = self.client.post(
            reverse('module_content_delete', kwargs={'id': self.content.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('module_content_list', kwargs={'module_id': self.module.id})
        )
        self.assertFalse(Content.objects.filter(id=self.content.id).exists())
        self.assertFalse(Text.objects.filter(id=self.text.id).exists())
 
    def test_content_delete_requires_ownership(self):
        """Test that only the course owner can delete content"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.post(
            reverse('module_content_delete', kwargs={'id': self.content.id})
        )
        self.assertEqual(response.status_code, 404)
 
 
class ModuleContentListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        cls.text = Text.objects.create(
            owner=cls.user,
            title='Text Content',
            content='Some content'
        )
        Content.objects.create(module=cls.module, item=cls.text)
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_module_content_list_view(self):
        """Test that the module content list view displays content"""
        response = self.client.get(
            reverse('module_content_list', kwargs={'module_id': self.module.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/manage/module/content_list.html')
        self.assertContains(response, 'Text Content')
 
    def test_module_content_list_requires_ownership(self):
        """Test that only the course owner can view module contents"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.get(
            reverse('module_content_list', kwargs={'module_id': self.module.id})
        )
        self.assertEqual(response.status_code, 404)
 
 
class ModuleOrderViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module1 = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        cls.module2 = Module.objects.create(
            course=cls.course,
            title='Module 2',
            description='Description 2',
            order=2
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_module_order_view_post(self):
        """Test POST request to reorder modules"""
        response = self.client.post(
            reverse('module_order'),
            data={
                str(self.module1.id): 2,
                str(self.module2.id): 1
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.assertEqual(self.module1.order, 2)
        self.assertEqual(self.module2.order, 1)
 
    def test_module_order_requires_ownership(self):
        """Test that only the course owner can reorder modules"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.post(
            reverse('module_order'),
            data={
                str(self.module1.id): 2,
                str(self.module2.id): 1
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()

        self.assertEqual(self.module1.order, 1)
        self.assertEqual(self.module2.order, 2)
 
 
class ContentOrderViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@email.com',
            )
        cls.subject = Subject.objects.create(
            title='Mathematics',
            slug='mathematics'
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title='Test Course',
            slug='test-course',
            overview='Test overview'
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title='Module 1',
            description='Description 1',
            order=1
        )
        cls.text1 = Text.objects.create(
            owner=cls.user,
            title='Text 1',
            content='Content 1'
        )
        cls.text2 = Text.objects.create(
            owner=cls.user,
            title='Text 2',
            content='Content 2'
        )
        cls.content1 = Content.objects.create(
            module=cls.module,
            item=cls.text1,
            order=1
        )
        cls.content2 = Content.objects.create(
            module=cls.module,
            item=cls.text2,
            order=2
        )
        
    def setUp(self):
        self.client.force_login(self.user)
 
    def test_content_order_view_post(self):
        """Test POST request to reorder contents"""
        response = self.client.post(
            reverse('content_order'),
            data={
                str(self.content1.id): 2,
                str(self.content2.id): 1
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.content1.refresh_from_db()
        self.content2.refresh_from_db()
        self.assertEqual(self.content1.order, 2)
        self.assertEqual(self.content2.order, 1)
 
    def test_content_order_requires_ownership(self):
        """Test that only the course owner can reorder contents"""
        other_user = User.objects.create_user(username='otheruser')
        self.client.force_login(other_user)
        response = self.client.post(
            reverse('content_order'),
            data={
                str(self.content1.id): 2,
                str(self.content2.id): 1
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.content1.refresh_from_db()
        self.content2.refresh_from_db()
        self.assertEqual(self.content1.order, 1)
        self.assertEqual(self.content2.order, 2)