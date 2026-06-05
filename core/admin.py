from django.contrib import admin

from .models import ContactMessage, TestimonialSubmission


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'telegram_sent', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('telegram_sent', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(TestimonialSubmission)
class TestimonialSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'company', 'rating', 'telegram_sent', 'created_at')
    search_fields = ('name', 'designation', 'company', 'feedback')
    list_filter = ('rating', 'telegram_sent', 'created_at')
    readonly_fields = ('created_at',)
