/**
 * CareHospital - Hospital Management System
 * Frontend Interactivity Script
 */

document.addEventListener('DOMContentLoaded', function () {

    // 1. Password Visibility Toggle
    // Finds any toggle buttons matching class .toggle-password and toggles target input type
    const toggleButtons = document.querySelectorAll('.toggle-password-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetInputId = this.getAttribute('data-target');
            const targetInput = document.getElementById(targetInputId);
            if (targetInput) {
                if (targetInput.type === 'password') {
                    targetInput.type = 'text';
                    this.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
                } else {
                    targetInput.type = 'password';
                    this.innerHTML = '<i class="bi bi-eye"></i> Show';
                }
            }
        });
    });

    // 2. Appointment Cancellation Confirmation Popup
    const cancelButtons = document.querySelectorAll('.btn-cancel-appointment');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmed = window.confirm("Are you sure you want to cancel this appointment? This action cannot be undone.");
            if (!confirmed) {
                event.preventDefault(); // Stop navigation
            }
        });
    });

    // 3. Client-side Doctor Live Search & Filter (on doctors.html)
    const doctorSearchInput = document.getElementById('doctorSearchInput');
    const doctorDepartmentFilter = document.getElementById('doctorDepartmentFilter');
    const doctorCards = document.querySelectorAll('.doctor-item-card');

    function filterDoctorCards() {
        if (!doctorCards.length) return;

        const searchText = doctorSearchInput ? doctorSearchInput.value.toLowerCase().trim() : '';
        const selectedDepartment = doctorDepartmentFilter ? doctorDepartmentFilter.value.toLowerCase().trim() : '';

        let visibleCount = 0;

        doctorCards.forEach(card => {
            const name = (card.getAttribute('data-name') || '').toLowerCase();
            const department = (card.getAttribute('data-department') || '').toLowerCase();

            const matchesSearch = !searchText || name.includes(searchText) || department.includes(searchText);
            const matchesDept = !selectedDepartment || department === selectedDepartment;

            if (matchesSearch && matchesDept) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        const noResultsMsg = document.getElementById('noDoctorsMessage');
        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (doctorSearchInput) {
        doctorSearchInput.addEventListener('keyup', filterDoctorCards);
    }
    if (doctorDepartmentFilter) {
        doctorDepartmentFilter.addEventListener('change', filterDoctorCards);
    }

    // 4. Basic Form Validation Feedback
    const validatedForms = document.querySelectorAll('.needs-validation');
    validatedForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // 5. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

});

