from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from courses.models import Course
from .models import Learner


class LearnerCreationForm(UserCreationForm):
    class Meta:
        model = Learner
        fields = UserCreationForm.Meta.fields


class LearnerChangeForm(UserChangeForm):
    class Meta:
        model = Learner
        fields = UserChangeForm.Meta.fields


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super(CourseEnrollForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()