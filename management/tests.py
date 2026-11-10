from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from management.models import Doctor, Appointment


class HospitalManagementSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test patient
        self.patient = User.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe'
        )

        # Create another patient to test data isolation
        self.other_patient = User.objects.create_user(
            username='otherpatient',
            email='other@example.com',
            password='Password123!',
            first_name='Jane',
            last_name='Smith'
        )

        # Create staff / admin user
        self.admin = User.objects.create_superuser(
            username='testadmin',
            email='admin@hospital.com',
            password='AdminPassword123!'
        )

        # Create test doctors
        self.doctor1 = Doctor.objects.create(
            name='Dr. Arjun Kumar',
            department='Cardiology',
            email='arjun@hospital.com',
            phone='+91 9876543210',
            consultation_fee=800.00,
            available=True
        )

        self.doctor2 = Doctor.objects.create(
            name='Dr. Priya Sharma',
            department='Neurology',
            email='priya@hospital.com',
            phone='+91 9876543211',
            consultation_fee=950.00,
            available=False
        )

        # Create sample appointment
        self.appointment1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            appointment_date=date.today() + timedelta(days=2),
            appointment_time='10:00:00',
            status='Pending'
        )

    # --------------------------------------------------------------------------
    # 1. PUBLIC PAGES TESTS
    # --------------------------------------------------------------------------
    def test_home_page_loads(self):
        """Test home page renders successfully and lists doctors and stats."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CareHospital')
        self.assertContains(response, 'Dr. Arjun Kumar')

    def test_doctors_page_and_filtering(self):
        """Test doctor listing and search filtering."""
        response = self.client.get(reverse('doctors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Arjun Kumar')
        self.assertContains(response, 'Cardiology')

        # Test search query
        response = self.client.get(reverse('doctors'), {'q': 'Arjun'})
        self.assertContains(response, 'Dr. Arjun Kumar')

        # Test department filter
        response = self.client.get(reverse('doctors'), {'department': 'Cardiology'})
        self.assertContains(response, 'Dr. Arjun Kumar')

    # --------------------------------------------------------------------------
    # 2. AUTHENTICATION TESTS
    # --------------------------------------------------------------------------
    def test_patient_registration_success(self):
        """Test registering a new patient."""
        response = self.client.post(reverse('register'), {
            'full_name': 'Ramesh Kumar',
            'username': 'rameshk',
            'email': 'ramesh@example.com',
            'password': 'SafePassword123!',
            'confirm_password': 'SafePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.filter(username='rameshk').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.first_name, 'Ramesh')
        self.assertEqual(new_user.last_name, 'Kumar')

    def test_registration_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        response = self.client.post(reverse('register'), {
            'full_name': 'Ramesh Kumar',
            'username': 'ramesh2',
            'email': 'ramesh2@example.com',
            'password': 'SafePassword123!',
            'confirm_password': 'DifferentPassword456!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='ramesh2').exists())
        self.assertContains(response, 'Passwords do not match')

    def test_patient_login_and_logout(self):
        """Test user login and logout flows."""
        login_response = self.client.post(reverse('login'), {
            'username': 'testpatient',
            'password': 'Password123!'
        })
        self.assertRedirects(login_response, reverse('dashboard'))

        logout_response = self.client.get(reverse('logout'))
        self.assertRedirects(logout_response, reverse('home'))

    # --------------------------------------------------------------------------
    # 3. PATIENT DASHBOARD & APPOINTMENTS TESTS
    # --------------------------------------------------------------------------
    def test_dashboard_access_requires_login(self):
        """Unauthenticated access to dashboard should redirect to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_patient_dashboard_statistics(self):
        """Test patient dashboard calculates correct dynamic stats."""
        self.client.login(username='testpatient', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 1)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertContains(response, 'Welcome back, John Doe!')

    def test_book_appointment_success(self):
        """Test booking an appointment successfully."""
        self.client.login(username='testpatient', password='Password123!')
        target_date = date.today() + timedelta(days=5)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor1.id,
            'appointment_date': target_date.isoformat(),
            'appointment_time': '11:00:00'
        })
        self.assertRedirects(response, reverse('my_appointments'))

        new_appointment = Appointment.objects.filter(
            patient=self.patient,
            doctor=self.doctor1,
            appointment_date=target_date,
            appointment_time='11:00:00'
        ).first()
        self.assertIsNotNone(new_appointment)
        self.assertEqual(new_appointment.status, 'Pending')

    def test_book_appointment_prevents_past_date(self):
        """Booking for past dates should be rejected."""
        self.client.login(username='testpatient', password='Password123!')
        past_date = date.today() - timedelta(days=1)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor1.id,
            'appointment_date': past_date.isoformat(),
            'appointment_time': '11:00:00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appointment date cannot be in the past.')

    def test_book_appointment_prevents_unavailable_doctor(self):
        """Booking for unavailable doctor should be rejected."""
        self.client.login(username='testpatient', password='Password123!')
        target_date = date.today() + timedelta(days=3)

        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor2.id,
            'appointment_date': target_date.isoformat(),
            'appointment_time': '10:00:00'
        })
        self.assertEqual(response.status_code, 200)

    def test_book_appointment_prevents_duplicate_slot(self):
        """Duplicate booking for the same doctor, date, and time should be blocked."""
        self.client.login(username='otherpatient', password='Password123!')

        # self.appointment1 is already booked on date.today() + 2 days at 10:00:00
        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor1.id,
            'appointment_date': self.appointment1.appointment_date.isoformat(),
            'appointment_time': '10:00:00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already has an appointment booked')

    def test_my_appointments_isolation(self):
        """Patients should only see their own appointments."""
        # Create an appointment for other_patient
        Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.doctor1,
            appointment_date=date.today() + timedelta(days=3),
            appointment_time='14:00:00',
            status='Approved'
        )

        self.client.login(username='testpatient', password='Password123!')
        response = self.client.get(reverse('my_appointments'))
        self.assertEqual(response.status_code, 200)
        # Should contain patient's appointment
        self.assertContains(response, f"#{self.appointment1.id}")
        # Should NOT contain other_patient's 14:00 appointment
        self.assertEqual(len(response.context['appointments']), 1)

    def test_cancel_appointment(self):
        """Patients can cancel their pending appointment."""
        self.client.login(username='testpatient', password='Password123!')
        response = self.client.get(reverse('cancel_appointment', args=[self.appointment1.id]))
        self.assertRedirects(response, reverse('my_appointments'))

        self.appointment1.refresh_from_db()
        self.assertEqual(self.appointment1.status, 'Cancelled')

    def test_cannot_cancel_other_patients_appointment(self):
        """Patients cannot cancel an appointment that belongs to another patient."""
        self.client.login(username='otherpatient', password='Password123!')
        response = self.client.get(reverse('cancel_appointment', args=[self.appointment1.id]))
        self.assertEqual(response.status_code, 404)
        self.appointment1.refresh_from_db()
        self.assertEqual(self.appointment1.status, 'Pending')

    # --------------------------------------------------------------------------
    # 4. ADMIN & SECURITY TESTS
    # --------------------------------------------------------------------------
    def test_patient_cannot_access_admin_dashboard(self):
        """Regular patients must be denied access to admin dashboard."""
        self.client.login(username='testpatient', password='Password123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        # Redirected to login with next parameter
        self.assertIn('admin', response.url)

    def test_admin_dashboard_accessible_by_staff(self):
        """Staff user can access custom admin dashboard with correct stats."""
        self.client.login(username='testadmin', password='AdminPassword123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_doctors'], 2)
        self.assertEqual(response.context['total_patients'], 2)
        self.assertEqual(response.context['total_appointments'], 1)
        self.assertEqual(response.context['pending_appointments'], 1)

    def test_admin_approve_and_reject_appointment(self):
        """Admin can approve or reject an appointment."""
        self.client.login(username='testadmin', password='AdminPassword123!')

        # Approve
        response = self.client.get(reverse('admin_update_status', args=[self.appointment1.id, 'Approved']))
        self.assertRedirects(response, reverse('admin_appointments'))
        self.appointment1.refresh_from_db()
        self.assertEqual(self.appointment1.status, 'Approved')

        # Reject
        response = self.client.get(reverse('admin_update_status', args=[self.appointment1.id, 'Rejected']))
        self.assertRedirects(response, reverse('admin_appointments'))
        self.appointment1.refresh_from_db()
        self.assertEqual(self.appointment1.status, 'Rejected')

    def test_admin_toggle_doctor_availability(self):
        """Admin can toggle doctor availability."""
        self.client.login(username='testadmin', password='AdminPassword123!')
        self.assertTrue(self.doctor1.available)

        response = self.client.get(reverse('admin_toggle_doctor', args=[self.doctor1.id]))
        self.assertRedirects(response, reverse('admin_doctors'))
        self.doctor1.refresh_from_db()
        self.assertFalse(self.doctor1.available)

    def test_admin_delete_doctor(self):
        """Admin can delete a doctor."""
        self.client.login(username='testadmin', password='AdminPassword123!')
        response = self.client.get(reverse('admin_delete_doctor', args=[self.doctor2.id]))
        self.assertRedirects(response, reverse('admin_doctors'))
        self.assertFalse(Doctor.objects.filter(id=self.doctor2.id).exists())
