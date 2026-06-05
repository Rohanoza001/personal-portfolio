from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
]
