from courses.models import Course
from django.contrib.auth import authenticate, login
from .forms import LearnerCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from .forms import CourseEnrollForm


class LearnerRegistrationView(CreateView):
    template_name = 'learners/registration.html'
    form_class = LearnerCreationForm
    success_url = reverse_lazy('learner_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'], password=cd['password1']
        )
        login(self.request, user)
        return result


class LearnerEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.learners.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'learner_course_detail', args=[self.course.id]
        )



class LearnerCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'learners/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(learners__in=[self.request.user])


class LearnerCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'learners/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(learners__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id']
            )
        else:
            # get first module
            try:
                context['module'] = course.modules.all()[0]
            # if mo module
            except IndexError:
                pass
        return context
