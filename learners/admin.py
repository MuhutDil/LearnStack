from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Learner

# admin.site.register(Learner, UserAdmin)


class LearnerAdmin(UserAdmin):
    model = Learner
    # Display custom fields in the admin list view
    list_display = ['username', 'email', 'is_editor']
    
    # Add custom fields to the admin editing fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('is_editor',)}),
    )

admin.site.register(Learner, LearnerAdmin)