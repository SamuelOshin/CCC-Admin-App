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

// For Parish Restructure
document.addEventListener('DOMContentLoaded', function () {
  var dioceseSelect = $('#id_diocese');
  var regionSelect = $('#id_region');
  var areaSelect = $('#id_area');
  var districtSelect = $('#id_district');
  var circuitSelect = $('#id_circuit');

  // Initialize Select2 for each select element
  dioceseSelect.select2();
  regionSelect.select2();
  areaSelect.select2();
  districtSelect.select2();
  circuitSelect.select2();

  dioceseSelect.on('change', function () {
    var dioceseId = $(this).val();

    // Clear previous selections
    regionSelect.empty().append('<option value="">Select Region</option>').trigger('change');
    areaSelect.empty().append('<option value="">Select Area</option>').trigger('change');
    
    circuitSelect.empty().append('<option value="">Select Circuit</option>').trigger('change');

    // Fetch regions for the selected diocese
    fetch(`/get_regions_and_areas/?diocese_id=${dioceseId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate regions select
        data.regions.forEach(region => {
          var option = new Option(region.name, region.id, false, false);
          regionSelect.append(option);
        });
        regionSelect.trigger('change'); // Update Select2
      })
      .catch(error => console.error('Error:', error));
  });

  regionSelect.on('change', function () {
    var regionId = $(this).val();

    // Clear previous selections
    areaSelect.empty().append('<option value="">Select Area</option>').trigger('change');
    
    circuitSelect.empty().append('<option value="">Select Circuit</option>').trigger('change');

    // Fetch areas for the selected region
    fetch(`/get_regions_and_areas/?region_id=${regionId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate areas select
        data.areas.forEach(area => {
          var option = new Option(area.name, area.id, false, false);
          areaSelect.append(option);
        });
        areaSelect.trigger('change'); // Update Select2
      })
      .catch(error => console.error('Error:', error));
  });

  areaSelect.on('change', function () {
    var areaId = $(this).val();

    // Clear previous selections
    
    circuitSelect.empty().append('<option value="">Select Circuit</option>').trigger('change');

    // Fetch districts for the selected area
    fetch(`/get_regions_and_areas/?area_id=${areaId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate districts select
        data.districts.forEach(district => {
          var option = new Option(district.name, district.id, false, false);
          districtSelect.append(option);
        });
        districtSelect.trigger('change'); // Update Select2
      })
      .catch(error => console.error('Error:', error));
  });

  districtSelect.on('change', function () {
    var districtId = $(this).val();

    // Clear previous selections
    circuitSelect.empty().append('<option value="">Select Circuit</option>').trigger('change');

    // Fetch circuits for the selected district
    fetch(`/get_regions_and_areas/?district_id=${districtId}`)
      .then(response => response.json())
      .then(data => {
        console.log('Received data:', data); // Debugging: Log received data

        // Populate circuits select
        data.circuits.forEach(circuit => {
          var option = new Option(circuit.name, circuit.id, false, false);
          circuitSelect.append(option);
        });
        circuitSelect.trigger('change'); // Update Select2
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
$('#parishFrmId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishAddresss(selectedParishId); // Fetch parish address
});
$('#parishToId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishAddresssTo(selectedParishId); // Fetch parish address
});

$('#parishFrmId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishLocation(selectedParishId); // Fetch parish address
});
$('#parishToId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishLocationI(selectedParishId); // Fetch parish address
});
$('#parishFrmId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParish(selectedParishId); // Fetch parish address
});
$('#parishToId').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishI(selectedParishId); // Fetch parish address
});

$('#id_parish').on('select2:select', function (e) {
  var selectedParishId = e.params.data.id; // Get the selected value from Select2 data
  fetchParishAddress(selectedParishId); // Fetch parish address
});

function fetchParishAddress(parishId) {
  fetch(`/api/parish/${parishId}/`)
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address").value = data.address;
    })
    .catch(error => console.error('Error:', error));
}

function fetchParishAddresss(parishFrmId) {
  fetch(`transfer/api/parish/${parishFrmId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address").value = data.address;
    })
    .catch(error => console.error('Error:', error)); 
}

function fetchParishAddresssTo(parishFrmId) {
  fetch(`transfer/api/parish/${parishFrmId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address_to").value = data.address;
    })
    .catch(error => console.error('Error:', error)); 
}


function fetchParishLocation(parishFrmId) {
  fetch(`transfer/api/parish/${parishFrmId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_location").value = data.location;
    })
    .catch(error => console.error('Error:', error)); 
}

function fetchParishLocationI(parishToId) {
  fetch(`transfer/api/parish/${parishToId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_location_to").value = data.location;
    })
    .catch(error => console.error('Error:', error)); 
}
function fetchParish(parishFrmId) {
  fetch(`transfer/api/parish/${parishFrmId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_parishFrm").value = data.id;
    })
    .catch(error => console.error('Error:', error)); 
}

function fetchParishI(parishToId) {
  fetch(`transfer/api/parish/${parishToId}/`, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_parishTo").value = data.id;
    })
    .catch(error => console.error('Error:', error)); 
}

document.addEventListener("DOMContentLoaded", function() {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function(alert) {
      setTimeout(function() {
          alert.style.display = 'none';
      }, 5000);
  });
});

// Page reload icon
document.addEventListener('DOMContentLoaded', function() {
  const loadingScreen = document.getElementById('loading');

  // Show loading screen on page load
  window.addEventListener('beforeunload', () => {
    loadingScreen.style.display = 'flex';
  });

  // Optional: Hide loading screen when page is fully loaded
  window.addEventListener('load', () => {
    loadingScreen.style.display = 'none';
  });
});

// Show loading screen when a link is clicked
document.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', function() {
    loadingScreen.style.display = 'flex';
  });
});