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

document.addEventListener('DOMContentLoaded', function () {
  var dioceseSelect = document.getElementById('id_diocese');
  var regionSelect = document.getElementById('id_region');
  var areaSelect = document.getElementById('id_area');

  dioceseSelect.addEventListener('change', function () {
    var dioceseId = this.value;


    // Fetch regions for the selected diocese
    fetch(`/get_regions_and_areas/?diocese_id=${dioceseId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate regions select
        data.regions.forEach(region => {
          var option = document.createElement('option');
          option.value = region.id;
          option.text = region.name;
          regionSelect.appendChild(option);
        });

        // Populate areas select (optional)
        // You can implement this if needed
      })
      .catch(error => console.error('Error:', error));
  });

  regionSelect.addEventListener('change', function () {
    var regionId = this.value;


    // Fetch areas for the selected region
    fetch(`/get_regions_and_areas/?region_id=${regionId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate areas select
        data.areas.forEach(area => {
          var option = document.createElement('option');
          option.value = area.id;
          option.text = area.name;
          areaSelect.appendChild(option);
        });
      })
      .catch(error => console.error('Error:', error));
  });
});

let autocomplete;

function initAutocomplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
      types: ['establishment'],
      componentRestrictions: { country: ['ng', 'us'] }, // Use an array for multiple country codes
      fields: ['place_id', 'geometry', 'name']
    }
  );

  // When the user selects an address, get the place details and fill in the form
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  let place = autocomplete.getPlace();
  if (!place.geometry) {
    // User did not select a prediction; reset the field
    document.getElementById('id_address').value = ''; // Clear the input field
    return; // Exit the function early
  }

  // Display details about the valid place
  document.getElementById('details').innerHTML = place.name;
}

// Fetch address of the selected parish id
document.getElementById("id_parish").addEventListener("change", function () {
  var selectedParishId = this.value;
  fetchParishAddress(selectedParishId);
});

function fetchParishAddress(parishId) {
  fetch(`/api/parish/${parishId}/`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address").value = data.address;
    })
    .catch(error => console.error('Error:', error));
  console.log('Error:', error);
}
