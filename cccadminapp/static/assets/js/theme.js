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
  var stateSelect = $('#id_state');
  var areaSelect = $('#id_area');
  var districtSelect = $('#id_district');
  var zoneSelect = $('#id_zone');

  // Store active requests to prevent race conditions
  var activeRequests = {
    diocese: null,
    region: null,
    state: null,
    area: null,
    district: null
  };

  // Initialize Select2 for each select element
  dioceseSelect.select2();
  regionSelect.select2();
  stateSelect.select2();
  areaSelect.select2();
  districtSelect.select2();
  zoneSelect.select2();

  // Utility function to safely clear select without triggering change events
  function clearSelectSafely(selectElement, placeholderText) {
    // Temporarily unbind change event to prevent unnecessary API calls
    selectElement.off('change.temp');

    // Clear the select
    selectElement.empty().append(`<option value="">${placeholderText}</option>`);

    // Rebind the change event
    setTimeout(function() {
      selectElement.on('change.temp', function() {
        // This will be rebound by the specific change handlers below
      });
    }, 10);
  }

  // Utility function to cancel active request
  function cancelActiveRequest(type) {
    if (activeRequests[type]) {
      activeRequests[type].abort();
      activeRequests[type] = null;
    }
  }

  dioceseSelect.on('change', function () {
    var dioceseId = $(this).val();

    // Cancel any active requests
    cancelActiveRequest('diocese');
    cancelActiveRequest('region');
    cancelActiveRequest('state');
    cancelActiveRequest('area');
    cancelActiveRequest('district');

    // Clear previous selections without triggering change events
    clearSelectSafely(regionSelect, 'Select Region');
    clearSelectSafely(stateSelect, 'Select State');
    clearSelectSafely(areaSelect, 'Select Area');
    clearSelectSafely(districtSelect, 'Select District');
    clearSelectSafely(zoneSelect, 'Select zone');

    // Only make API call if dioceseId is not empty
    if (dioceseId && dioceseId.trim() !== '') {
      // Create abort controller for this request
      var controller = new AbortController();
      activeRequests.diocese = controller;

      // Fetch regions for the selected diocese
      fetch(`/get_regions_and_areas/?diocese_id=${dioceseId}`, {
        signal: controller.signal
      })
        .then(response => response.json())
        .then(data => {
          console.log('Received data:', data); // Debugging: Log received data

          // Populate regions select
          if (data.regions && data.regions.length > 0) {
            data.regions.forEach(region => {
              var option = new Option(region.name, region.id, false, false);
              regionSelect.append(option);
            });
          }
          // Clear active request
          activeRequests.diocese = null;
        })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Error:', error);
          }
          activeRequests.diocese = null;
        });
    }
  });

  regionSelect.on('change', function () {
    var regionId = $(this).val();

    // Cancel any active requests for dependent fields
    cancelActiveRequest('region');
    cancelActiveRequest('state');
    cancelActiveRequest('area');
    cancelActiveRequest('district');

    // Clear previous selections without triggering change events
    clearSelectSafely(stateSelect, 'Select State');
    clearSelectSafely(areaSelect, 'Select Area');
    clearSelectSafely(districtSelect, 'Select District');
    clearSelectSafely(zoneSelect, 'Select zone');

    // Only make API call if regionId is not empty
    if (regionId && regionId.trim() !== '') {
      // Create abort controller for this request
      var controller = new AbortController();
      activeRequests.region = controller;

      // Fetch states for the selected region
      fetch(`/get_regions_and_areas/?region_id=${regionId}`, {
        signal: controller.signal
      })
        .then(response => response.json())
        .then(data => {
          console.log('Received data:', data); // Debugging: Log received data

          // Populate states select
          if (data.states && data.states.length > 0) {
            data.states.forEach(state => {
              var option = new Option(state.name, state.id, false, false);
              stateSelect.append(option);
            });
          }
          // Clear active request
          activeRequests.region = null;
        })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Error:', error);
          }
          activeRequests.region = null;
        });
    }
  });

  stateSelect.on('change', function () {
    var stateId = $(this).val();

    // Cancel any active requests for dependent fields
    cancelActiveRequest('state');
    cancelActiveRequest('area');
    cancelActiveRequest('district');

    // Clear previous selections without triggering change events
    clearSelectSafely(areaSelect, 'Select Area');
    clearSelectSafely(districtSelect, 'Select District');
    clearSelectSafely(zoneSelect, 'Select zone');

    // Only make API call if stateId is not empty
    if (stateId && stateId.trim() !== '') {
      // Create abort controller for this request
      var controller = new AbortController();
      activeRequests.state = controller;

      // Fetch areas for the selected state
      fetch(`/get_regions_and_areas/?state_id=${stateId}`, {
        signal: controller.signal
      })
        .then(response => response.json())
        .then(data => {
          console.log('Received data:', data); // Debugging: Log received data

          // Populate areas select
          if (data.areas && data.areas.length > 0) {
            data.areas.forEach(area => {
              var option = new Option(area.name, area.id, false, false);
              areaSelect.append(option);
            });
          }
          // Clear active request
          activeRequests.state = null;
        })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Error:', error);
          }
          activeRequests.state = null;
        });
    }
  });

  areaSelect.on('change', function () {
    var areaId = $(this).val();

    // Cancel any active requests for dependent fields
    cancelActiveRequest('area');
    cancelActiveRequest('district');

    // Clear previous selections without triggering change events
    clearSelectSafely(districtSelect, 'Select District');
    clearSelectSafely(zoneSelect, 'Select zone');

    // Only make API call if areaId is not empty
    if (areaId && areaId.trim() !== '') {
      // Create abort controller for this request
      var controller = new AbortController();
      activeRequests.area = controller;

      // Fetch districts for the selected area
      fetch(`/get_regions_and_areas/?area_id=${areaId}`, {
        signal: controller.signal
      })
        .then(response => response.json())
        .then(data => {
          console.log('Received data:', data); // Debugging: Log received data

          // Populate districts select
          if (data.districts && data.districts.length > 0) {
            data.districts.forEach(district => {
              var option = new Option(district.name, district.id, false, false);
              districtSelect.append(option);
            });
          }
          // Clear active request
          activeRequests.area = null;
        })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Error:', error);
          }
          activeRequests.area = null;
        });
    }
  });

  districtSelect.on('change', function () {
    var districtId = $(this).val();

    // Cancel any active requests for dependent fields
    cancelActiveRequest('district');

    // Clear previous selections without triggering change events
    clearSelectSafely(zoneSelect, 'Select zone');

    // Only make API call if districtId is not empty
    if (districtId && districtId.trim() !== '') {
      // Create abort controller for this request
      var controller = new AbortController();
      activeRequests.district = controller;

      // Fetch zones for the selected district
      fetch(`/get_regions_and_areas/?district_id=${districtId}`, {
        signal: controller.signal
      })
        .then(response => response.json())
        .then(data => {
          console.log('Received data:', data); // Debugging: Log received data

          // Populate zones select
          if (data.zones && data.zones.length > 0) {
            data.zones.forEach(zone => {
              var option = new Option(zone.name, zone.id, false, false);
              zoneSelect.append(option);
            });
          }
          // Clear active request
          activeRequests.district = null;
        })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('Error:', error);
          }
          activeRequests.district = null;
        });
    }
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
// Parish selection event listeners - Unified for all templates
document.addEventListener('DOMContentLoaded', function() {
    // Initialize parish selection for both trfForm and update_transfer templates
    initParishSelection();
});

function initParishSelection() {
    // Check if parish select elements exist on the page
    const parishFromSelect = document.getElementById('parishFrmId');
    const parishToSelect = document.getElementById('parishToId');

    if (parishFromSelect) {
        // Use Select2 events for Transfer From parish
        $('#parishFrmId').on('select2:select', function(e) {
            const parishId = e.params.data.id;
            console.log('From parish selected:', parishId);
            updateParishDetails(parishId, 'from');
        });

        $('#parishFrmId').on('select2:clear', function(e) {
            console.log('From parish cleared');
            updateParishDetails('', 'from');
        });
    }

    if (parishToSelect) {
        // Use Select2 events for Transfer To parish
        $('#parishToId').on('select2:select', function(e) {
            const parishId = e.params.data.id;
            console.log('To parish selected:', parishId);
            updateParishDetails(parishId, 'to');
        });

        $('#parishToId').on('select2:clear', function(e) {
            console.log('To parish cleared');
            updateParishDetails('', 'to');
        });
    }
}

function updateParishDetails(parishId, type) {
    if (!parishId) {
        // Clear fields if no parish selected
        if (type === 'from') {
            const addressField = document.getElementById('id_address') || document.getElementById('id_address_from');
            const locationField = document.getElementById('id_location') || document.getElementById('id_location_from');
            const parishHiddenField = document.getElementById('id_parishFrm');

            if (addressField) addressField.value = '';
            if (locationField) locationField.value = '';
            if (parishHiddenField) parishHiddenField.value = '';
        } else {
            const addressField = document.getElementById('id_address_to');
            const locationField = document.getElementById('id_location_to');
            const parishHiddenField = document.getElementById('id_parishTo');

            if (addressField) addressField.value = '';
            if (locationField) locationField.value = '';
            if (parishHiddenField) parishHiddenField.value = '';
        }
        return;
    }

    // Get parish data from global scope (available from templates)
    let parishesData = window.parishesData;

    // If parishesData is not available, try to get it from Django context
    if (!parishesData && typeof window.parishes !== 'undefined') {
        parishesData = window.parishes;
    }

    // If still not available, try to find it in the template's script
    if (!parishesData) {
        // Look for parishes data in script tags
        const scripts = document.querySelectorAll('script');
        for (let script of scripts) {
            if (script.textContent.includes('parishesData = [')) {
                try {
                    // Extract and parse the parishesData from the script content
                    const scriptContent = script.textContent;
                    const dataMatch = scriptContent.match(/parishesData\s*=\s*(\[[\s\S]*?\]);/);
                    if (dataMatch) {
                        parishesData = JSON.parse(dataMatch[1]);
                        break;
                    }
                } catch (e) {
                    console.error('Error parsing parishes data:', e);
                }
            }
        }
    }

    if (!parishesData) {
        console.error('Parishes data not found');
        return;
    }

    console.log('Available parishes data:', parishesData);
    const selectedParish = parishesData.find(p => p.id == parishId);
    console.log('Selected parish:', selectedParish);

    if (selectedParish) {
        if (type === 'from') {
            const addressField = document.getElementById('id_address') || document.getElementById('id_address_from');
            const locationField = document.getElementById('id_location') || document.getElementById('id_location_from');
            const parishHiddenField = document.getElementById('id_parishFrm');

            if (addressField) addressField.value = selectedParish.address || '';
            if (locationField) locationField.value = selectedParish.location || '';
            if (parishHiddenField) parishHiddenField.value = parishId;

            console.log('Updated FROM fields:', {
                address: selectedParish.address,
                location: selectedParish.location,
                parishId: parishId
            });
        } else {
            const addressField = document.getElementById('id_address_to');
            const locationField = document.getElementById('id_location_to');
            const parishHiddenField = document.getElementById('id_parishTo');

            if (addressField) addressField.value = selectedParish.address || '';
            if (locationField) locationField.value = selectedParish.location || '';
            if (parishHiddenField) parishHiddenField.value = parishId;

            console.log('Updated TO fields:', {
                address: selectedParish.address,
                location: selectedParish.location,
                parishId: parishId
            });
        }
    } else {
        console.error('Parish not found for ID:', parishId);
    }
}

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
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishFrmId}/` : `transfer/api/parish/${parishFrmId}/`;

  fetch(apiUrl, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address").value = data.address;
    })
    .catch(error => console.error('Error:', error));
}function fetchParishAddresssTo(parishFrmId) {
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishFrmId}/` : `transfer/api/parish/${parishFrmId}/`;

  fetch(apiUrl, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_address_to").value = data.address;
    })
    .catch(error => console.error('Error:', error));
}


function fetchParishLocation(parishFrmId) {
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishFrmId}/` : `transfer/api/parish/${parishFrmId}/`;

  fetch(apiUrl, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_location").value = data.location;
    })
    .catch(error => console.error('Error:', error));
}function fetchParishLocationI(parishToId) {
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishToId}/` : `transfer/api/parish/${parishToId}/`;

  fetch(apiUrl, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_location_to").value = data.location;
    })
    .catch(error => console.error('Error:', error));
}
function fetchParish(parishFrmId) {
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishFrmId}/` : `transfer/api/parish/${parishFrmId}/`;

  fetch(apiUrl, {
    method: 'GET' // specifying the request method
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("id_parishFrm").value = data.id;
    })
    .catch(error => console.error('Error:', error));
}function fetchParishI(parishToId) {
  // Check if we're on the update transfer page
  const isUpdatePage = window.location.pathname.includes('/update/');
  const apiUrl = isUpdatePage ? `api/parish/${parishToId}/` : `transfer/api/parish/${parishToId}/`;

  fetch(apiUrl, {
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
  window.addEventListener('beforeunload', function(event) {
    // Don't show loading screen for form submissions - they handle their own loading states
    const activeElement = document.activeElement;
    if (activeElement && (activeElement.tagName === 'BUTTON' || activeElement.tagName === 'INPUT') &&
        (activeElement.type === 'submit' || activeElement.form)) {
      return; // Don't show loading screen for form submissions
    }

    // Show loading screen for regular navigation
    if (loadingScreen) {
      loadingScreen.style.display = 'flex';
    }
  });

  // Hide loading screen when page is fully loaded or becomes visible again
  window.addEventListener('load', function() {
    if (loadingScreen) {
      loadingScreen.style.display = 'none';
    }
  });

  // Hide loading screen when page becomes visible (handles back/forward navigation)
  document.addEventListener('visibilitychange', function() {
    if (!document.hidden && loadingScreen) {
      loadingScreen.style.display = 'none';
    }
  });

  // Hide loading screen when navigating back to the page
  window.addEventListener('pageshow', function(event) {
    if (loadingScreen) {
      loadingScreen.style.display = 'none';
    }
  });
});

// Show loading screen when a link is clicked (but not for form submissions or sidebar toggles)
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function(event) {
      const loadingScreen = document.getElementById('loading');

      // Don't show loading screen for sidebar toggle links (submenu expanders)
      if (this.hasAttribute('data-bs-toggle') && this.getAttribute('data-bs-toggle') === 'collapse') {
        return; // Skip loading screen for sidebar submenu toggles
      }

      // Don't show loading screen if this is part of a form submission
      if (this.closest('form')) {
        return; // Skip loading screen for form-related links
      }

      // Don't show loading screen for links that don't navigate (href="#")
      if (this.getAttribute('href') === '#') {
        return; // Skip loading screen for anchor links that don't navigate
      }

      // Don't show loading screen for external links or links that open in new tabs
      if (this.getAttribute('target') === '_blank' || this.hostname !== window.location.hostname) {
        return; // Skip loading screen for external links
      }

      // Show loading screen for regular navigation links
      if (loadingScreen) {
        loadingScreen.style.display = 'flex';
      }
    });
  });

  // Handle form submissions - don't interfere with their loading states
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      // Let the form handle its own loading state
      // The global loading screen will be hidden when the response loads
    });
  });
});