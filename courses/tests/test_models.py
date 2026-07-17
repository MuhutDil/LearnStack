from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
 
from courses.models import (
    Subject, Course, Module, Content,
    Text, Video, Image, File
)
 
 
class SubjectModelTest(TestCase):
    """Tests for the Subject model."""
    
    @classmethod
    def setUpTestData(cls):
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
    
    def test_subject_creation(self):
        """Test that a subject can be created with correct attributes."""
        self.assertEqual(self.subject.title, "Programming")
        self.assertEqual(self.subject.slug, "programming")
    
    def test_subject_str_method(self):
        """Test the string representation of a subject."""
        self.assertEqual(str(self.subject), "Programming")
    
    def test_subject_unique_slug(self):
        """Test that duplicate slugs are not allowed."""
        with self.assertRaises(Exception):
            Subject.objects.create(
                title="Programming 2",
                slug="programming"  # Duplicate slug
            )
    
    def test_subject_ordering(self):
        """Test that subjects are ordered by title."""
        subject2 = Subject.objects.create(
            title="Algorithms",
            slug="algorithms"
        )
        subject3 = Subject.objects.create(
            title="Data Science",
            slug="data-science"
        )
        subjects = Subject.objects.all()
        self.assertEqual(list(subjects), [subject2, subject3, self.subject])
 
 
class CourseModelTest(TestCase):
    """Tests for the Course model."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title="Python 101",
            slug="python-101",
            overview="Learn Python from scratch"
        )
    
    def test_course_creation(self):
        """Test that a course can be created with correct attributes."""
        self.assertEqual(self.course.owner, self.user)
        self.assertEqual(self.course.subject, self.subject)
        self.assertEqual(self.course.title, "Python 101")
        self.assertEqual(self.course.slug, "python-101")
        self.assertEqual(self.course.overview, "Learn Python from scratch")
        self.assertIsNotNone(self.course.created)
    
    def test_course_str_method(self):
        """Test the string representation of a course."""
        self.assertEqual(str(self.course), "Python 101")
    
    def test_course_ordering(self):
        """Test that courses are ordered by creation date (newest first)."""
        course2 = Course.objects.create(
            owner=self.user,
            subject=self.subject,
            title="Python 102",
            slug="python-102",
            overview="Advanced Python"
        )
        courses = Course.objects.all()
        # Newest first
        self.assertEqual(list(courses), [course2, self.course])
    
    def test_course_related_names(self):
        """Test the related_name for foreign keys."""
        # Test reverse relation from user to courses
        self.assertEqual(self.user.courses_created.count(), 1)
        self.assertEqual(self.user.courses_created.first(), self.course)
        
        # Test reverse relation from subject to courses
        self.assertEqual(self.subject.courses.count(), 1)
        self.assertEqual(self.subject.courses.first(), self.course)
 
 
class ModuleModelTest(TestCase):
    """Tests for the Module model."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title="Python 101",
            slug="python-101",
            overview="Learn Python from scratch"
        )
    
    def test_module_creation_with_auto_order(self):
        """Test that modules automatically get order numbers."""
        module1 = Module.objects.create(
            course=self.course,
            title="Introduction",
            description="Getting started"
        )
        module2 = Module.objects.create(
            course=self.course,
            title="Basics",
            description="Basic concepts"
        )
        module3 = Module.objects.create(
            course=self.course,
            title="Advanced",
            description="Advanced topics"
        )
        
        # Orders should be assigned sequentially
        module1.refresh_from_db()
        module2.refresh_from_db()
        module3.refresh_from_db()
        
        self.assertEqual(module1.order, 0)
        self.assertEqual(module2.order, 1)
        self.assertEqual(module3.order, 2)
    
    def test_module_ordering_per_course(self):
        """Test that module ordering is scoped to each course."""
        # Create another course
        course2 = Course.objects.create(
            owner=self.user,
            subject=self.subject,
            title="JavaScript 101",
            slug="js-101",
            overview="Learn JavaScript"
        )
        
        # Create modules for both courses
        module1_course1 = Module.objects.create(
            course=self.course,
            title="Module 1"
        )
        module1_course2 = Module.objects.create(
            course=course2,
            title="Module 1"
        )
        
        module1_course1.refresh_from_db()
        module1_course2.refresh_from_db()
        
        # Both should have order 0 (scoped to their respective courses)
        self.assertEqual(module1_course1.order, 0)
        self.assertEqual(module1_course2.order, 0)
        
        # Add another module to course 1
        module2_course1 = Module.objects.create(
            course=self.course,
            title="Module 2"
        )
        module2_course1.refresh_from_db()
        self.assertEqual(module2_course1.order, 1)
        
        # Course 2 should still have only one module with order 0
        self.assertEqual(module1_course2.order, 0)
    
    def test_module_str_method(self):
        """Test the string representation of a module."""
        module = Module.objects.create(
            course=self.course,
            title="Introduction"
        )
        module.refresh_from_db()
        self.assertEqual(str(module), "0. Introduction")
    
    def test_module_ordering_meta(self):
        """Test that modules are ordered by the 'order' field."""
        module1 = Module.objects.create(course=self.course, title="Module 1")
        module2 = Module.objects.create(course=self.course, title="Module 2")
        module3 = Module.objects.create(course=self.course, title="Module 3")
        
        # Manually reorder to test ordering
        module1.order = 2
        module2.order = 0
        module3.order = 1
        module1.save()
        module2.save()
        module3.save()
        
        modules = Module.objects.all()
        self.assertEqual(list(modules), [module2, module3, module1])
 
 
class ContentModelTest(TestCase):
    """Tests for the Content model."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title="Python 101",
            slug="python-101",
            overview="Learn Python from scratch"
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title="Introduction"
        )
        # Get content types for each model
        cls.text_type = ContentType.objects.get_for_model(Text)
        cls.video_type = ContentType.objects.get_for_model(Video)
        cls.image_type = ContentType.objects.get_for_model(Image)
        cls.file_type = ContentType.objects.get_for_model(File)
    
    def test_content_creation_with_auto_order(self):
        """Test that content items automatically get order numbers."""
        text = Text.objects.create(
            owner=self.user,
            title="Welcome",
            content="Welcome to the course!"
        )
        content1 = Content.objects.create(
            module=self.module,
            content_type=self.text_type,
            object_id=text.id
        )
        
        video = Video.objects.create(
            owner=self.user,
            title="Introduction Video",
            url="https://example.com/video.mp4"
        )
        content2 = Content.objects.create(
            module=self.module,
            content_type=self.video_type,
            object_id=video.id
        )
        
        content1.refresh_from_db()
        content2.refresh_from_db()
        
        self.assertEqual(content1.order, 0)
        self.assertEqual(content2.order, 1)
    
    def test_content_ordering_per_module(self):
        """Test that content ordering is scoped to each module."""
        # Create another module
        module2 = Module.objects.create(
            course=self.course,
            title="Module 2"
        )
        
        # Create content for both modules
        text = Text.objects.create(
            owner=self.user,
            title="Text",
            content="Content"
        )
        content1_module1 = Content.objects.create(
            module=self.module,
            content_type=self.text_type,
            object_id=text.id
        )
        content1_module2 = Content.objects.create(
            module=module2,
            content_type=self.text_type,
            object_id=text.id
        )
        
        content1_module1.refresh_from_db()
        content1_module2.refresh_from_db()
        
        self.assertEqual(content1_module1.order, 0)
        self.assertEqual(content1_module2.order, 0)
    
    def test_content_generic_relationship(self):
        """Test the generic foreign key relationship."""
        text = Text.objects.create(
            owner=self.user,
            title="Lesson 1",
            content="This is the lesson content"
        )
        content = Content.objects.create(
            module=self.module,
            content_type=self.text_type,
            object_id=text.id
        )
        
        # Access the related object through the generic relationship
        self.assertEqual(content.item, text)
        self.assertEqual(content.item.title, "Lesson 1")
        self.assertEqual(content.item.content, "This is the lesson content")
    
    def test_content_str_method(self):
        """Test the string representation of content."""
        # Content doesn't have a custom __str__ method,
        # so it will use the default from Model
        text = Text.objects.create(
            owner=self.user,
            title="Test",
            content="Content"
        )
        content = Content.objects.create(
            module=self.module,
            content_type=self.text_type,
            object_id=text.id
        )
        self.assertIsNotNone(str(content))
 
 
class ItemBaseModelTest(TestCase):
    """Tests for the abstract ItemBase model and its subclasses."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
    
    def test_text_creation(self):
        """Test creating a Text item."""
        text = Text.objects.create(
            owner=self.user,
            title="Lesson Notes",
            content="These are the lesson notes"
        )
        self.assertEqual(text.owner, self.user)
        self.assertEqual(text.title, "Lesson Notes")
        self.assertEqual(text.content, "These are the lesson notes")
        self.assertIsNotNone(text.created)
        self.assertIsNotNone(text.updated)
    
    def test_text_str_method(self):
        """Test the string representation of Text."""
        text = Text.objects.create(
            owner=self.user,
            title="Lesson Notes",
            content="Content"
        )
        self.assertEqual(str(text), "Lesson Notes")
    
    def test_video_creation(self):
        """Test creating a Video item."""
        video = Video.objects.create(
            owner=self.user,
            title="Tutorial Video",
            url="https://youtube.com/watch?v=123"
        )
        self.assertEqual(video.owner, self.user)
        self.assertEqual(video.title, "Tutorial Video")
        self.assertEqual(video.url, "https://youtube.com/watch?v=123")
    
    def test_image_creation(self):
        """Test creating an Image item."""
        image = Image.objects.create(
            owner=self.user,
            title="Course Image",
            file="images/course.jpg"
        )
        self.assertEqual(image.owner, self.user)
        self.assertEqual(image.title, "Course Image")
        self.assertEqual(image.file, "images/course.jpg")
    
    def test_file_creation(self):
        """Test creating a File item."""
        file = File.objects.create(
            owner=self.user,
            title="Course PDF",
            file="files/course.pdf"
        )
        self.assertEqual(file.owner, self.user)
        self.assertEqual(file.title, "Course PDF")
        self.assertEqual(file.file, "files/course.pdf")
    
    def test_related_name_for_subclasses(self):
        """Test the related_name template for subclasses."""
        text = Text.objects.create(
            owner=self.user,
            title="Test",
            content="Content"
        )
        # The related_name should be 'text_related'
        self.assertEqual(self.user.text_related.count(), 1)
        self.assertEqual(self.user.text_related.first(), text)
        
        video = Video.objects.create(
            owner=self.user,
            title="Video",
            url="http://example.com"
        )
        self.assertEqual(self.user.video_related.count(), 1)
        self.assertEqual(self.user.video_related.first(), video)
 
 
class OrderFieldTest(TestCase):
    """Tests for the custom OrderField."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title="Python 101",
            slug="python-101",
            overview="Learn Python"
        )
    
    def test_order_field_initializes_with_none(self):
        """Test that order field starts as None."""
        module = Module.objects.create(
            course=self.course,
            title="Module 1"
        )
        # Before refresh, order might be None
        # After pre_save, it should have a value
        module.refresh_from_db()
        self.assertIsNotNone(module.order)
    
    def test_order_field_auto_increment(self):
        """Test that order field auto-increments."""
        module1 = Module.objects.create(course=self.course, title="Module 1")
        module2 = Module.objects.create(course=self.course, title="Module 2")
        module3 = Module.objects.create(course=self.course, title="Module 3")
        
        module1.refresh_from_db()
        module2.refresh_from_db()
        module3.refresh_from_db()
        
        self.assertEqual(module1.order, 0)
        self.assertEqual(module2.order, 1)
        self.assertEqual(module3.order, 2)
    
    def test_order_field_handles_explicit_values(self):
        """Test that explicit order values are respected."""
        module = Module.objects.create(
            course=self.course,
            title="Module",
            order=5
        )
        module.refresh_from_db()
        self.assertEqual(module.order, 5)
        
        # Next module should start from 6
        module2 = Module.objects.create(
            course=self.course,
            title="Module 2"
        )
        module2.refresh_from_db()
        self.assertEqual(module2.order, 6)
    
    def test_order_field_for_fields_filtering(self):
        """Test that for_fields properly filters the query."""
        course2 = Course.objects.create(
            owner=self.user,
            subject=self.subject,
            title="JavaScript 101",
            slug="js-101",
            overview="Learn JavaScript"
        )
        
        module1_course1 = Module.objects.create(course=self.course, title="Module 1")
        module1_course2 = Module.objects.create(course=course2, title="Module 1")
        
        module1_course1.refresh_from_db()
        module1_course2.refresh_from_db()
        
        # Both should start at 0 since they're in different courses
        self.assertEqual(module1_course1.order, 0)
        self.assertEqual(module1_course2.order, 0)
        
        # Add another module to course2
        module2_course2 = Module.objects.create(course=course2, title="Module 2")
        module2_course2.refresh_from_db()
        self.assertEqual(module2_course2.order, 1)
        
        # Course1 should still only have one module at order 0
        module1_course1.refresh_from_db()
        self.assertEqual(module1_course1.order, 0)
    
    def test_order_field_handles_deletions(self):
        """Test that order field doesn't automatically reorder on deletion."""
        module1 = Module.objects.create(course=self.course, title="Module 1")
        module2 = Module.objects.create(course=self.course, title="Module 2")
        module3 = Module.objects.create(course=self.course, title="Module 3")
        
        module1.refresh_from_db()
        module2.refresh_from_db()
        module3.refresh_from_db()
        
        self.assertEqual(module1.order, 0)
        self.assertEqual(module2.order, 1)
        self.assertEqual(module3.order, 2)
        
        # Delete middle module
        module2.delete()
        
        # Remaining modules keep their original orders
        module1.refresh_from_db()
        module3.refresh_from_db()
        self.assertEqual(module1.order, 0)
        self.assertEqual(module3.order, 2)  # Order doesn't shift
        
        # New module should get highest order + 1
        module4 = Module.objects.create(course=self.course, title="Module 4")
        module4.refresh_from_db()
        self.assertEqual(module4.order, 3)
    
    def test_order_field_handles_no_existing_objects(self):
        """Test that order field starts at 0 when no objects exist."""
        module = Module.objects.create(course=self.course, title="Module 1")
        module.refresh_from_db()
        self.assertEqual(module.order, 0)
 
 
class IntegrationTest(TestCase):
    """Integration tests for the complete model hierarchy."""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass123"
        )
        cls.subject = Subject.objects.create(
            title="Programming",
            slug="programming"
        )
        cls.course = Course.objects.create(
            owner=cls.user,
            subject=cls.subject,
            title="Python 101",
            slug="python-101",
            overview="Learn Python from scratch"
        )
        cls.text_type = ContentType.objects.get_for_model(Text)
        cls.video_type = ContentType.objects.get_for_model(Video)
    
    def test_complete_course_creation_flow(self):
        """Test creating a complete course with modules and content."""
        # Create modules
        module1 = Module.objects.create(course=self.course, title="Introduction")
        module2 = Module.objects.create(course=self.course, title="Basics")
        
        module1.refresh_from_db()
        module2.refresh_from_db()
        self.assertEqual(module1.order, 0)
        self.assertEqual(module2.order, 1)
        
        # Create content for module 1
        text = Text.objects.create(
            owner=self.user,
            title="Welcome",
            content="Welcome to the course!"
        )
        content1 = Content.objects.create(
            module=module1,
            content_type=self.text_type,
            object_id=text.id
        )
        content1.refresh_from_db()
        self.assertEqual(content1.order, 0)
        
        # Create video for module 1
        video = Video.objects.create(
            owner=self.user,
            title="Intro Video",
            url="https://example.com/video.mp4"
        )
        content2 = Content.objects.create(
            module=module1,
            content_type=self.video_type,
            object_id=video.id
        )
        content2.refresh_from_db()
        self.assertEqual(content2.order, 1)
        
        # Create content for module 2
        text2 = Text.objects.create(
            owner=self.user,
            title="Lesson 1",
            content="Lesson content"
        )
        content3 = Content.objects.create(
            module=module2,
            content_type=self.text_type,
            object_id=text2.id
        )
        content3.refresh_from_db()
        self.assertEqual(content3.order, 0)
        
        # Test relationships
        self.assertEqual(self.course.modules.count(), 2)
        self.assertEqual(module1.contents.count(), 2)
        self.assertEqual(module2.contents.count(), 1)
        
        # Test generic relationship
        self.assertEqual(content1.item.content, "Welcome to the course!")
        self.assertEqual(content2.item.url, "https://example.com/video.mp4")
    
    def test_course_modules_ordered_correctly(self):
        """Test that modules are returned in the correct order."""
        module1 = Module.objects.create(course=self.course, title="First")
        module2 = Module.objects.create(course=self.course, title="Second")
        module3 = Module.objects.create(course=self.course, title="Third")
        
        # Manually reorder
        module1.order = 2
        module2.order = 0
        module3.order = 1
        module1.save()
        module2.save()
        module3.save()
        
        modules = self.course.modules.all()
        self.assertEqual(list(modules), [module2, module3, module1])
    
    def test_course_content_ordered_correctly(self):
        """Test that content items are returned in the correct order."""
        module = Module.objects.create(course=self.course, title="Module")
        
        text1 = Text.objects.create(owner=self.user, title="Text 1", content="Content 1")
        text2 = Text.objects.create(owner=self.user, title="Text 2", content="Content 2")
        text3 = Text.objects.create(owner=self.user, title="Text 3", content="Content 3")
        
        content1 = Content.objects.create(
            module=module,
            content_type=self.text_type,
            object_id=text1.id
        )
        content2 = Content.objects.create(
            module=module,
            content_type=self.text_type,
            object_id=text2.id
        )
        content3 = Content.objects.create(
            module=module,
            content_type=self.text_type,
            object_id=text3.id
        )
        
        content1.refresh_from_db()
        content2.refresh_from_db()
        content3.refresh_from_db()
        
        self.assertEqual(content1.order, 0)
        self.assertEqual(content2.order, 1)
        self.assertEqual(content3.order, 2)
