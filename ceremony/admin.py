from django.contrib import admin
from .models import Graduate, StageState


@admin.register(Graduate)
class GraduateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'student_id',
        'payment_status',
        'attended',
        'gown_collected',
        'gown_returned',
        'presentation_order',
    )
    list_filter = ('attended', 'gown_collected', 'gown_returned', 'payment_status')
    search_fields = ('name', 'student_id', 'email', 'unique_id', 'submission_id')


@admin.register(StageState)
class StageStateAdmin(admin.ModelAdmin):
    list_display = ('current_graduate',)
