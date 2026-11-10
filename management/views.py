from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q, Count

from .models import Doctor, Appointment
from .forms import UserRegistrationForm, AppointmentBookingForm, DoctorForm


# ==============================================================================
# PUBLIC VIEWS
# ==============================================================================

def home_view(request):
    """
    Public landing page showing hospital overview, statistics, departments, and doctors.
    """
    doctors = Doctor.objects.filter(available=True)[:6]
    departments = Doctor.objects.values_list('department', flat=True).distinct()
    
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_appointments = Appointment.objects.count()

    context = {
        'doctors': doctors,
        'departments': departments,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    }
    return render(request, 'management/home.html', context)


def register_view(request):
    """
    Patient registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to CareHospital, {user.first_name or user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = UserRegistrationForm()

    return render(request, 'management/register.html', {'form': form})


def login_view(request):
    """
    User/Admin login view using Django's built-in authentication.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Check redirect target or role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'management/login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


def doctors_view(request):
    """
    Public listing of all doctors with search and department filtering.
    """
    query = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('department', '').strip()

    doctors = Doctor.objects.all()

    if query:
        doctors = doctors.filter(Q(name__icontains=query) | Q(department__icontains=query))

    if dept_filter:
        doctors = doctors.filter(department__iexact=dept_filter)

    departments = Doctor.objects.values_list('department', flat=True).distinct()

    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_dept': dept_filter,
        'search_query': query,
    }
    return render(request, 'management/doctors.html', context)


# ==============================================================================
# PATIENT VIEWS (Protected by @login_required)
# ==============================================================================

@login_required
def dashboard_view(request):
    """
    Patient dashboard displaying personalized appointment statistics and upcoming appointments.
    """
    # If a staff member visits the patient dashboard, offer direct link or redirect
    user_appointments = Appointment.objects.filter(patient=request.user)

    total_count = user_appointments.count()
    pending_count = user_appointments.filter(status='Pending').count()
    approved_count = user_appointments.filter(status='Approved').count()
    rejected_count = user_appointments.filter(status='Rejected').count()
    cancelled_count = user_appointments.filter(status='Cancelled').count()

    # Upcoming active appointments (today or future, not rejected or cancelled)
    upcoming_appointments = user_appointments.filter(
        appointment_date__gte=date.today()
    ).exclude(status__in=['Rejected', 'Cancelled']).order_by('appointment_date', 'appointment_time')[:5]

    recent_appointments = user_appointments.order_by('-created_at')[:5]

    context = {
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'management/dashboard.html', context)


@login_required
def book_appointment_view(request):
    """
    View allowing patients to book a new appointment.
    """
    initial_data = {}
    doctor_id = request.GET.get('doctor')
    if doctor_id:
        try:
            initial_data['doctor'] = Doctor.objects.get(id=doctor_id, available=True)
        except Doctor.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            appointment.save()
            messages.success(
                request,
                f"Your appointment with {appointment.doctor.name} on {appointment.appointment_date} at {appointment.appointment_time} has been requested successfully! Status: Pending."
            )
            return redirect('my_appointments')
        else:
            messages.error(request, "Unable to book appointment. Please review the errors below.")
    else:
        form = AppointmentBookingForm(initial=initial_data)

    context = {
        'form': form,
        'min_date': date.today().isoformat(),
    }
    return render(request, 'management/book_appointment.html', context)


@login_required
def my_appointments_view(request):
    """
    View displaying all appointments belonging to the logged-in patient.
    """
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date', '-appointment_time')
    return render(request, 'management/my_appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment_view(request, appointment_id):
    """
    Allows a patient to cancel their own pending appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status == 'Pending':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, f"Appointment with {appointment.doctor.name} has been cancelled.")
    else:
        messages.warning(request, f"Only 'Pending' appointments can be cancelled. Current status is {appointment.status}.")

    return redirect('my_appointments')


# ==============================================================================
# ADMIN / STAFF VIEWS (Protected by @staff_member_required)
# ==============================================================================

@staff_member_required
def admin_dashboard_view(request):
    """
    Custom Admin Dashboard displaying hospital statistics and recent appointments.
    """
    total_doctors = Doctor.objects.count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='Pending').count()
    approved_appointments = Appointment.objects.filter(status='Approved').count()
    rejected_appointments = Appointment.objects.filter(status='Rejected').count()

    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'management/admin_dashboard.html', context)


@staff_member_required
def admin_doctors_view(request):
    """
    Admin management view for doctors (Create, Read, Update availability, Delete).
    """
    query = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('department', '').strip()

    doctors = Doctor.objects.all()
    if query:
        doctors = doctors.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
    if dept_filter:
        doctors = doctors.filter(department__iexact=dept_filter)

    departments = Doctor.objects.values_list('department', flat=True).distinct()
    form = DoctorForm()

    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_dept': dept_filter,
        'search_query': query,
        'form': form,
    }
    return render(request, 'management/admin_doctors.html', context)


@staff_member_required
def admin_add_doctor_view(request):
    """
    View to add a doctor from the custom admin interface.
    """
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Dr. {doctor.name} has been added successfully.")
        else:
            messages.error(request, "Error adding doctor. Please check form values.")
    return redirect('admin_doctors')


@staff_member_required
def admin_delete_doctor_view(request, doctor_id):
    """
    View to delete a doctor.
    """
    doctor = get_object_or_404(Doctor, id=doctor_id)
    name = doctor.name
    doctor.delete()
    messages.success(request, f"Dr. {name} has been removed.")
    return redirect('admin_doctors')


@staff_member_required
def admin_toggle_doctor_availability_view(request, doctor_id):
    """
    Quick toggle for doctor availability status.
    """
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.available = not doctor.available
    doctor.save()
    status_str = "Available" if doctor.available else "Unavailable"
    messages.success(request, f"Dr. {doctor.name} is now marked as {status_str}.")
    return redirect('admin_doctors')


@staff_member_required
def admin_patients_view(request):
    """
    Admin view for listing registered patients.
    """
    query = request.GET.get('q', '').strip()
    patients = User.objects.filter(is_staff=False).annotate(total_appointments=Count('appointments')).order_by('-date_joined')

    if query:
        patients = patients.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'patients': patients,
        'search_query': query,
    }
    return render(request, 'management/admin_patients.html', context)


@staff_member_required
def admin_appointments_view(request):
    """
    Admin view to view, filter, and manage all appointments.
    """
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if query:
        appointments = appointments.filter(
            Q(patient__username__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(doctor__name__icontains=query) |
            Q(doctor__department__icontains=query)
        )

    context = {
        'appointments': appointments,
        'selected_status': status_filter,
        'search_query': query,
    }
    return render(request, 'management/admin_appointments.html', context)


@staff_member_required
def admin_update_appointment_status_view(request, appointment_id, new_status):
    """
    View for admin to Approve or Reject an appointment.
    """
    valid_statuses = ['Approved', 'Rejected', 'Pending']
    if new_status not in valid_statuses:
        messages.error(request, "Invalid status choice.")
        return redirect('admin_appointments')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = new_status
    appointment.save()

    messages.success(request, f"Appointment #{appointment.id} ({appointment.patient.username} with {appointment.doctor.name}) marked as '{new_status}'.")
    return redirect('admin_appointments')
