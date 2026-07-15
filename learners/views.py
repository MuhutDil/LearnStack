from courses.models import Course
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from .forms import CourseEnrollForm, LearnerCreationForm
from .redis_utils import save_last_accessed_module, get_last_accessed_module


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


class LearnerUnenrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.learners.remove(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'learner_course_list'
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
        # form to unenroll
        context['unenroll_form'] = CourseEnrollForm(
            initial={'course': self.object}
        )
        # get course object
        course = self.get_object()
        user = self.request.user
        
        if 'module_id' in self.kwargs:
            # Get specified module
            module = get_object_or_404(course.modules, id=self.kwargs['module_id'])
            
            # Save current module as last accessed
            save_last_accessed_module(user.id, course.id, module.id)
            context['module'] = module
        else:
            # Try to get last accessed module from Redis
            last_module_id = get_last_accessed_module(user.id, course.id)
            
            if last_module_id:
                # Resume from where learner left off
                try:
                    module = course.modules.get(id=last_module_id)
                except course.modules.model.DoesNotExist:
                    # Fallback to first module if saved module no longer exists
                    module = course.modules.first()
            else:
                # No history found, start from first module
                module = course.modules.first()
            
            if module:
                # Save current module as last accessed
                save_last_accessed_module(user.id, course.id, module.id)
            
            context['module'] = module
        
        return context
 