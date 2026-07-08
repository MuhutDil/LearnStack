from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = [
    path(
        'register/',
        views.LearnerRegistrationView.as_view(),
        name='learner_registration',
    ),
    path(
        'enroll-course/',
        views.LearnerEnrollCourseView.as_view(),
        name='learner_enroll_course',
    ),
    path(
        'unenroll-course/',
        views.LearnerUnenrollCourseView.as_view(),
        name='learner_unenroll_course',
    ),
    path(
        'courses/',
        views.LearnerCourseListView.as_view(),
        name='learner_course_list',
    ),
    path(
        'course/<pk>/',
        # cache_page(60 * 15)(views.LearnerCourseDetailView.as_view()),
        (views.LearnerCourseDetailView.as_view()),
        name='learner_course_detail',
    ),
    path(
        'course/<pk>/<module_id>/',
        cache_page(60 * 15)(views.LearnerCourseDetailView.as_view()),
        name='learner_course_detail_module',
    ),
]