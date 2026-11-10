from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('doctors/', views.doctors_view, name='doctors'),

    # Patient URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('appointments/book/', views.book_appointment_view, name='book_appointment'),
    path('appointments/my/', views.my_appointments_view, name='my_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment_view, name='cancel_appointment'),

    # Custom Admin URLs
    path('custom-admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('custom-admin/doctors/', views.admin_doctors_view, name='admin_doctors'),
    path('custom-admin/doctors/add/', views.admin_add_doctor_view, name='admin_add_doctor'),
    path('custom-admin/doctors/delete/<int:doctor_id>/', views.admin_delete_doctor_view, name='admin_delete_doctor'),
    path('custom-admin/doctors/toggle/<int:doctor_id>/', views.admin_toggle_doctor_availability_view, name='admin_toggle_doctor'),
    path('custom-admin/patients/', views.admin_patients_view, name='admin_patients'),
    path('custom-admin/appointments/', views.admin_appointments_view, name='admin_appointments'),
    path('custom-admin/appointments/status/<int:appointment_id>/<str:new_status>/', views.admin_update_appointment_status_view, name='admin_update_status'),
]

