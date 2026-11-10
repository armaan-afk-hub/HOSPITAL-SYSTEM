from django.contrib import admin
from .models import Doctor, Appointment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'email', 'phone', 'consultation_fee', 'available')
    list_filter = ('department', 'available')
    search_fields = ('name', 'department', 'email', 'phone')
    list_editable = ('available',)
    actions = ['mark_as_available', 'mark_as_unavailable']

    @admin.action(description="Mark selected doctors as Available")
    def mark_as_available(self, request, queryset):
        queryset.update(available=True)

    @admin.action(description="Mark selected doctors as Unavailable")
    def mark_as_unavailable(self, request, queryset):
        queryset.update(available=False)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor__department')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'doctor__name')
    list_editable = ('status',)
    actions = ['approve_appointments', 'reject_appointments']

    @admin.action(description="Approve selected appointments")
    def approve_appointments(self, request, queryset):
        queryset.update(status='Approved')

    @admin.action(description="Reject selected appointments")
    def reject_appointments(self, request, queryset):
        queryset.update(status='Rejected')
