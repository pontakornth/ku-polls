"""Admin site configuration for poll application."""
from django.contrib import admin
from .models import Question, Choice


# Register your models here.

class ChoiceInline(admin.TabularInline):
    """Inline choice for question admin panel."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Question admin site configuration."""

    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    fieldsets = (
        (None,   {'fields': ['question_text']}),
        ('Date Information', {'fields': ['pub_date', 'end_date']})
    )
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
