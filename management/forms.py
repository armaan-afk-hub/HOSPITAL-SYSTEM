from datetime import date
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Doctor, Appointment


class UserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new patient using Django's User model.
    """
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a secure password',
            'id': 'regPassword'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'regConfirmPassword'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        name_parts = full_name.split(' ', 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user


class AppointmentBookingForm(forms.ModelForm):
    """
    Form for patients to book an appointment with a doctor.
    """
    TIME_SLOT_CHOICES = [
        ('', 'Select a time slot'),
        ('09:00:00', '09:00 AM'),
        ('10:00:00', '10:00 AM'),
        ('11:00:00', '11:00 AM'),
        ('12:00:00', '12:00 PM'),
        ('14:00:00', '02:00 PM'),
        ('15:00:00', '03:00 PM'),
        ('16:00:00', '04:00 PM'),
        ('17:00:00', '05:00 PM'),
    ]

    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(available=True),
        empty_label="Choose a Doctor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    appointment_time = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time']

    def clean_appointment_date(self):
        app_date = self.cleaned_data.get('appointment_date')
        if app_date and app_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return app_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        app_date = cleaned_data.get('appointment_date')
        app_time = cleaned_data.get('appointment_time')

        if doctor and not doctor.available:
            self.add_error('doctor', "This doctor is currently marked as unavailable.")

        if doctor and app_date and app_time:
            # Check for duplicate bookings (excluding cancelled ones)
            duplicate_exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=app_date,
                appointment_time=app_time
            ).exclude(status='Cancelled').exists()

            if duplicate_exists:
                raise ValidationError(
                    f"Dr. {doctor.name} already has an appointment booked on {app_date} at this time. Please choose another time slot."
                )

        return cleaned_data


class DoctorForm(forms.ModelForm):
    """
    Form for administrator to add or edit a doctor.
    """
    DEPARTMENT_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Orthopedics', 'Orthopedics'),
        ('Dermatology', 'Dermatology'),
        ('General Medicine', 'General Medicine'),
        ('Pediatrics', 'Pediatrics'),
        ('Gynecology', 'Gynecology'),
        ('Ophthalmology', 'Ophthalmology'),
    ]

    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Doctor
        fields = ['name', 'department', 'email', 'phone', 'consultation_fee', 'available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dr. Arjun Kumar'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. arjun@hospital.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 9876543210'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500.00', 'step': '0.01'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

