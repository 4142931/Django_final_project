# survey/admin.py

from django.contrib import admin
from .models import Question, Choice
from .models import InvestmentResult

class ChoiceInline(admin.TabularInline):
    model = Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)


@admin.register(InvestmentResult)
class InvestmentResultAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'total_score', 'result_type', 'created_at')
