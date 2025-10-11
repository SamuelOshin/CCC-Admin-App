(function () {
  "use strict"; // Start of use strict

  var sidebar = document.querySelector('.sidebar');
  var sidebarToggles = document.querySelectorAll('#sidebarToggle, #sidebarToggleTop');

  if (sidebar) {

    var collapseElementList = [].slice.call(document.querySelectorAll('.sidebar .collapse'))
    var sidebarCollapseList = collapseElementList.map(function (collapseEl) {
      return new bootstrap.Collapse(collapseEl, { toggle: false });
    });

    for (var toggle of sidebarToggles) {

      // Toggle the side navigation
      toggle.addEventListener('click', function (e) {
        e.preventDefault();
        document.body.classList.toggle('sidebar-toggled');
        sidebar.classList.toggle('toggled');

        if (sidebar.classList.contains('toggled')) {
          for (var bsCollapse of sidebarCollapseList) {
            bsCollapse.hide();
          }
        };
      });
    }

    // Close any open menu accordions when window is resized below 768px
    window.addEventListener('resize', function () {
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);

      if (vw < 768) {
        for (var bsCollapse of sidebarCollapseList) {
          bsCollapse.hide();
        }
      };
    });

    // Hide sidebar on devices with a maximum width of 996px
    var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    if (vw <= 996) {
      document.body.classList.add('sidebar-toggled');
      sidebar.classList.add('toggled');
    }
  }

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over

  var fixedNaigation = document.querySelector('body.fixed-nav .sidebar');

  if (fixedNaigation) {
    fixedNaigation.on('mousewheel DOMMouseScroll wheel', function (e) {
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);

      if (vw > 768) {
        var e0 = e.originalEvent,
          delta = e0.wheelDelta || -e0.detail;
        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
      }
    });
  }

  var scrollToTop = document.querySelector('.scroll-to-top');

  if (scrollToTop) {

    // Scroll to top button appear
    window.addEventListener('scroll', function () {
      var scrollDistance = window.scrollY;

      //check if user is scrolling up
      if (scrollDistance > 100) {
        scrollToTop.style.display = 'block';
      } else {
        scrollToTop.style.display = 'none';
      }
    });
  }

})(); // End of use strict

// Initialize location hierarchy cascading dropdowns using CascadingDropdownUtils
document.addEventListener('DOMContentLoaded', function () {
  // Check if the location hierarchy selects exist on this page
  if (document.getElementById('id_diocese')) {
    // Initialize Select2 for location hierarchy selects
    if (window.CascadingDropdownUtils) {
      CascadingDropdownUtils.initSelect2([
        'id_diocese', 'id_region', 'id_state', 'id_area', 
        'id_district', 'id_division', 'id_zone'
      ]);

      // Initialize cascading dropdown relationships
      CascadingDropdownUtils.initLocationHierarchy('/parish/get_regions_and_areas/');
    }
  }
});


// Google Maps Autocomplete initialization
let autocomplete;

function initAutocomplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
      types: ['establishment'],
      componentRestrictions: { country: ['ng', 'us'] },
      fields: ['place_id', 'geometry', 'name']
    }
  );

  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  let place = autocomplete.getPlace();
  if (!place.geometry) {
    document.getElementById('id_address').value = '';
    return;
  }
  document.getElementById('details').innerHTML = place.name;
}

// Initialize parish selection for transfer forms using ParishUtils
document.addEventListener('DOMContentLoaded', function() {
  // Initialize transfer parish selection if elements exist
  if (document.getElementById('parishFrmId') || document.getElementById('parishToId')) {
    if (window.ParishUtils) {
      ParishUtils.initTransferParishSelection();
    }
  }
});