from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    """
    Model representing a Doctor in the hospital.
    """
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.department}"

    class Meta:
        ordering = ['name']


class Appointment(models.Model):
    """
    Model representing an Appointment booked by a Patient with a Doctor.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.name} ({self.appointment_date} at {self.appointment_time})"

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'appointment_time')
        ordering = ['-appointment_date', '-appointment_time']
