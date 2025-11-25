from django.urls import path
from . import views

urlpatterns = [
    # Grad admin dashboard
    path('', views.grad_admin, name='grad_admin'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),

    # Check-in front-end
    path('check-in/', views.check_in_search, name='check_in_search'),
    path('check-in/<int:pk>/', views.check_in_detail, name='check_in_detail'),

    # Gown front-end
    path('gowns/', views.gown_search, name='gown_search'),
    path('gowns/<int:pk>/', views.gown_detail, name='gown_detail'),

    # Stage front-end
    path('stage/control/', views.stage_control, name='stage_control'),
    path('stage/display/', views.stage_display, name='stage_display'),
]
