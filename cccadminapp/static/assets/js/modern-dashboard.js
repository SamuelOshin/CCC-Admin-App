document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const toggleBtn = document.querySelector('.toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('sidebar-collapse');
            document.querySelector('.main-content').classList.toggle('expanded');
            
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-chevron-left')) {
                icon.classList.remove('bi-chevron-left');
                icon.classList.add('bi-chevron-right');
            } else {
                icon.classList.remove('bi-chevron-right');
                icon.classList.add('bi-chevron-left');
            }
        });
    }

    // Initialize DataTables with modern styling
    const tables = document.querySelectorAll('.modern-table');
    tables.forEach(table => {
        if ($.fn.DataTable) {
            $(table).DataTable({
                responsive: true,
                dom: '<"dt-header"Bfr>t<"dt-footer"lip>',
                lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
                buttons: [
                    'copy', 'excel', 'pdf', 'print'
                ]
            });
        }
    });


});