# JavaScript Utility Modules - DRY Refactoring

This document describes the utility modules created to eliminate code duplication and follow the DRY (Don't Repeat Yourself) principle.

## Overview

Three utility modules have been created to consolidate duplicate code across `theme.js` and `restructure.html`:

1. **parish-utils.js** - Parish-related functions
2. **ui-utils.js** - UI utilities (alerts, loading screens, form validation)
3. **cascading-dropdown-utils.js** - Cascading dropdown logic

## Modules

### 1. parish-utils.js

Handles all parish-related functionality including fetching parish data, updating form fields, and managing parish selection events.

#### Key Functions:

- `ParishUtils.fetchParishData(parishId, apiEndpoint)` - Fetch parish data from API
- `ParishUtils.updateField(fieldId, value)` - Update a form field
- `ParishUtils.initParishSelect(selectId, onSelect, onClear)` - Initialize parish selection with Select2
- `ParishUtils.initTransferParishSelection()` - Initialize parish selection for transfer forms
- `ParishUtils.initRestructureParishSelection(onSuccess, onError)` - Initialize parish selection for restructure forms

#### Usage Example:

```javascript
// In transfer forms
ParishUtils.initTransferParishSelection();

// In restructure forms
ParishUtils.initRestructureParishSelection(
    function(data) {
        console.log('Parish loaded:', data);
    },
    function(error) {
        console.error('Error:', error);
    }
);
```

### 2. ui-utils.js

Provides UI-related utilities for alerts, loading screens, and form validation.

#### Key Functions:

- `UIUtils.showAlert(message, type, container, autoHideDuration)` - Show an alert message
- `UIUtils.getAlertIcon(type)` - Get Bootstrap icon for alert type
- `UIUtils.autoHideAlerts(duration)` - Auto-hide alerts after duration
- `UIUtils.showLoading()` - Show loading screen
- `UIUtils.hideLoading()` - Hide loading screen
- `UIUtils.initLoadingScreen()` - Initialize loading screen (auto-initialized)
- `UIUtils.initFormValidation()` - Initialize Bootstrap form validation

#### Usage Example:

```javascript
// Show a success alert
UIUtils.showAlert('Operation completed successfully!', 'success');

// Show loading screen
UIUtils.showLoading();

// Initialize form validation
UIUtils.initFormValidation();
```

### 3. cascading-dropdown-utils.js

Handles cascading dropdown relationships for location hierarchy (Diocese → Region → State → Division → Sub Division → Area → District → Zone).

#### Key Functions:

- `CascadingDropdownUtils.initSelect2(selectIds, config)` - Initialize Select2 for multiple selects
- `CascadingDropdownUtils.setupCascade(config)` - Setup a cascading relationship
- `CascadingDropdownUtils.initLocationHierarchy(apiBaseUrl)` - Initialize complete location hierarchy
- `CascadingDropdownUtils.populateSelect(selectElement, options, placeholderText)` - Populate select with options
- `CascadingDropdownUtils.resetDependentSelects(selectElements)` - Reset dependent selects

#### Usage Example:

```javascript
// Initialize location hierarchy cascading
CascadingDropdownUtils.initLocationHierarchy('/parish/get_regions_and_areas/');

// Or setup a custom cascade
CascadingDropdownUtils.setupCascade({
    parentSelectId: 'id_diocese',
    childSelectId: 'id_region',
    apiBaseUrl: '/api/locations/',
    apiParamName: 'diocese_id',
    dataKey: 'regions',
    childPlaceholder: 'Select Region',
    dependentSelects: ['#id_area', '#id_district']
});
```

## Integration

The utility modules are automatically loaded in the base template (`templates/dashboard/base.html`) before `theme.js`:

```html
<!-- DRY Utility Modules -->
<script src="{% static 'assets/js/ui-utils.js' %}"></script>
<script src="{% static 'assets/js/parish-utils.js' %}"></script>
<script src="{% static 'assets/js/cascading-dropdown-utils.js' %}"></script>
<script src="{% static 'assets/js/theme.js' %}"></script>
```

## Auto-Initialization

Some utilities are auto-initialized on DOM ready:

- **UIUtils**: Loading screen and alert auto-hide are initialized automatically
- **theme.js**: Location hierarchy cascading is initialized if the relevant elements exist

## Migration Guide

### Before (Duplicate Code):

```javascript
// In restructure.html
function fetchParishDetails(parishId) {
    fetch(`/parish/api/parish/${parishId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_address').value = data.address;
        });
}

// In theme.js
function fetchParishAddress(parishId) {
    fetch(`/parish/api/parish/${parishId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_address').value = data.address;
        });
}
```

### After (Using Utilities):

```javascript
// Both can use ParishUtils
ParishUtils.initRestructureParishSelection(
    function(data) {
        UIUtils.showAlert('Parish loaded!', 'success');
    },
    function(error) {
        UIUtils.showAlert('Error loading parish', 'error');
    }
);
```

## Benefits

1. **Code Reusability**: Common functionality is centralized and reusable
2. **Maintainability**: Changes need to be made in one place
3. **Consistency**: UI behaviors are consistent across the application
4. **Reduced File Size**: Eliminated ~300+ lines of duplicate code
5. **Better Organization**: Code is organized by functionality
6. **Easier Testing**: Utilities can be tested independently

## Files Modified

1. `cccadminapp/static/assets/js/parish-utils.js` (NEW)
2. `cccadminapp/static/assets/js/ui-utils.js` (NEW)
3. `cccadminapp/static/assets/js/cascading-dropdown-utils.js` (NEW)
4. `cccadminapp/static/assets/js/theme.js` (REFACTORED)
5. `templates/ParishRestructure/restructure.html` (REFACTORED)
6. `templates/dashboard/base.html` (UPDATED - includes new scripts)

## Future Enhancements

Consider extending these utilities for:
- Additional form validation rules
- More complex cascading relationships
- Enhanced error handling and retry logic
- Loading state indicators for individual fields
- Caching mechanisms for API responses
