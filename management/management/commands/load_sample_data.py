from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from management.models import Doctor, Appointment
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Loads 5 sample doctors and optional test data for the Hospital Management System'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Populating sample hospital data..."))

        doctors_data = [
            {
                'name': 'Dr. Arjun Kumar',
                'department': 'Cardiology',
                'email': 'arjun.kumar@carehospital.com',
                'phone': '+91 9876543210',
                'consultation_fee': 800.00,
                'available': True,
            },
            {
                'name': 'Dr. Priya Sharma',
                'department': 'Neurology',
                'email': 'priya.sharma@carehospital.com',
                'phone': '+91 9876543211',
                'consultation_fee': 950.00,
                'available': True,
            },
            {
                'name': 'Dr. Ahmed Khan',
                'department': 'Orthopedics',
                'email': 'ahmed.khan@carehospital.com',
                'phone': '+91 9876543212',
                'consultation_fee': 700.00,
                'available': True,
            },
            {
                'name': 'Dr. Sneha Reddy',
                'department': 'Dermatology',
                'email': 'sneha.reddy@carehospital.com',
                'phone': '+91 9876543213',
                'consultation_fee': 600.00,
                'available': True,
            },
            {
                'name': 'Dr. Rahul Verma',
                'department': 'General Medicine',
                'email': 'rahul.verma@carehospital.com',
                'phone': '+91 9876543214',
                'consultation_fee': 500.00,
                'available': True,
            },
        ]

        created_count = 0
        for doc_info in doctors_data:
            doc, created = Doctor.objects.get_or_create(
                name=doc_info['name'],
                defaults=doc_info
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created Doctor: {doc.name} ({doc.department})"))
            else:
                self.stdout.write(f"Doctor {doc.name} already exists.")

        # Also create a demo patient for easy review/testing if it doesn't exist
        patient_user, p_created = User.objects.get_or_create(
            username='patient1',
            defaults={
                'email': 'patient1@example.com',
                'first_name': 'Rohan',
                'last_name': 'Gupta',
            }
        )
        if p_created:
            patient_user.set_password('patient123')
            patient_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo patient: username='patient1', password='patient123'"))

            # Create sample appointments for patient1
            doc1 = Doctor.objects.get(name='Dr. Arjun Kumar')
            doc2 = Doctor.objects.get(name='Dr. Sneha Reddy')
            
            Appointment.objects.get_or_create(
                patient=patient_user,
                doctor=doc1,
                appointment_date=date.today() + timedelta(days=2),
                appointment_time='10:00:00',
                defaults={'status': 'Pending'}
            )
            Appointment.objects.get_or_create(
                patient=patient_user,
                doctor=doc2,
                appointment_date=date.today() + timedelta(days=4),
                appointment_time='14:00:00',
                defaults={'status': 'Approved'}
            )
            self.stdout.write(self.style.SUCCESS("Created demo appointments for testing."))

        self.stdout.write(self.style.SUCCESS("Sample data setup completed successfully!"))

