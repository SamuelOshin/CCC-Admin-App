/**
 * Cascading Dropdown Utilities Module
 * Consolidates location hierarchy dropdown logic to follow DRY principle
 */

(function(window) {
    'use strict';

    const CascadingDropdownUtils = {
        // Store active requests to prevent race conditions
        activeRequests: {},

        /**
         * Initialize Select2 for multiple select elements
         * @param {Array} selectIds - Array of select element IDs
         * @param {Object} config - Optional Select2 configuration
         */
        initSelect2: function(selectIds, config = {}) {
            const defaultConfig = {
                width: '100%',
                placeholder: 'Select an option',
                allowClear: true
            };

            const mergedConfig = { ...defaultConfig, ...config };

            selectIds.forEach(id => {
                const $select = $(`#${id}`);
                if ($select.length > 0 && !$select.hasClass('select2-hidden-accessible')) {
                    $select.select2(mergedConfig);
                }
            });
        },

        /**
         * Safely clear a select element without triggering change events
         * @param {jQuery} $selectElement - jQuery select element
         * @param {string} placeholderText - Placeholder text
         */
        clearSelectSafely: function($selectElement, placeholderText) {
            if (!$selectElement || $selectElement.length === 0) return;

            // Temporarily unbind change event to prevent unnecessary API calls
            $selectElement.off('change.temp');

            // Clear the select
            $selectElement.empty().append(`<option value="">${placeholderText}</option>`);

            // Rebind the change event
            setTimeout(function() {
                $selectElement.on('change.temp', function() {
                    // This will be rebound by the specific change handlers
                });
            }, 10);
        },

        /**
         * Cancel an active request
         * @param {string} requestType - Type of request to cancel
         */
        cancelActiveRequest: function(requestType) {
            if (this.activeRequests[requestType]) {
                this.activeRequests[requestType].abort();
                this.activeRequests[requestType] = null;
            }
        },

        /**
         * Fetch dependent options from API
         * @param {string} apiUrl - API endpoint URL
         * @param {string} requestType - Type of request (for cancellation tracking)
         * @returns {Promise} - Promise resolving to data
         */
        fetchDependentOptions: function(apiUrl, requestType) {
            // Cancel any existing request of this type
            this.cancelActiveRequest(requestType);

            // Create abort controller for this request
            const controller = new AbortController();
            this.activeRequests[requestType] = controller;

            return fetch(apiUrl, { signal: controller.signal })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Clear active request
                    this.activeRequests[requestType] = null;
                    return data;
                })
                .catch(error => {
                    if (error.name !== 'AbortError') {
                        console.error('Error fetching options:', error);
                    }
                    this.activeRequests[requestType] = null;
                    throw error;
                });
        },

        /**
         * Populate select element with options
         * @param {jQuery|HTMLElement} selectElement - Select element to populate
         * @param {Array} options - Array of option objects with {id, name}
         * @param {string} placeholderText - Placeholder text
         */
        populateSelect: function(selectElement, options, placeholderText) {
            const $select = selectElement instanceof $ ? selectElement : $(selectElement);
            
            if ($select.length === 0) return;

            // Clear existing options
            $select.empty();

            // Add placeholder
            $select.append(`<option value="" disabled selected>${placeholderText}</option>`);

            // Add options
            if (options && options.length > 0) {
                options.forEach(option => {
                    $select.append(new Option(option.name, option.id, false, false));
                });
            }
        },

        /**
         * Reset dependent select elements
         * @param {Array} selectElements - Array of select elements or selectors
         */
        resetDependentSelects: function(selectElements) {
            selectElements.forEach(element => {
                const $select = element instanceof $ ? element : $(element);
                
                if ($select.length === 0) return;

                // Get field name from ID for placeholder
                const fieldId = $select.attr('id') || '';
                const fieldName = fieldId.replace('id_', '').charAt(0).toUpperCase() + 
                                fieldId.replace('id_', '').slice(1);
                
                // Clear the select
                $select.empty();
                $select.append(`<option value="" disabled selected>Select ${fieldName}</option>`);
            });
        },

        /**
         * Setup cascading relationship between dropdowns
         * @param {Object} config - Configuration object
         * @param {string} config.parentSelectId - Parent select element ID
         * @param {string} config.childSelectId - Child select element ID
         * @param {string} config.apiBaseUrl - Base API URL
         * @param {string} config.apiParamName - Parameter name for API (e.g., 'diocese_id')
         * @param {string} config.dataKey - Key in response data (e.g., 'regions')
         * @param {string} config.childPlaceholder - Placeholder for child select
         * @param {Array} config.dependentSelects - Array of selects to reset when parent changes
         */
        setupCascade: function(config) {
            const {
                parentSelectId,
                childSelectId,
                apiBaseUrl,
                apiParamName,
                dataKey,
                childPlaceholder,
                dependentSelects = []
            } = config;

            const $parent = $(`#${parentSelectId}`);
            const $child = $(`#${childSelectId}`);

            if ($parent.length === 0) return;

            $parent.on('change', () => {
                const parentValue = $parent.val();

                // Cancel related active requests
                this.cancelActiveRequest(apiParamName);
                
                // Cancel requests for dependent fields
                dependentSelects.forEach(depSelect => {
                    const depId = depSelect.replace('#', '').replace('id_', '');
                    this.cancelActiveRequest(depId);
                });

                // Reset child and dependent selects
                const selectsToReset = [$child, ...dependentSelects.map(s => $(s))];
                this.resetDependentSelects(selectsToReset);

                // Only fetch if parent has a value
                if (!parentValue || parentValue.trim() === '') {
                    return;
                }

                // Fetch options for child select
                const apiUrl = `${apiBaseUrl}?${apiParamName}=${parentValue}`;
                
                this.fetchDependentOptions(apiUrl, apiParamName)
                    .then(data => {
                        if (data[dataKey]) {
                            this.populateSelect($child, data[dataKey], childPlaceholder);
                        }
                    })
                    .catch(error => {
                        console.error(`Error loading ${dataKey}:`, error);
                        if (window.UIUtils) {
                            window.UIUtils.showAlert(`Unable to load ${dataKey}. Please try again.`, 'warning');
                        }
                    });
            });
        },

        /**
         * Initialize location hierarchy cascading dropdowns
         * @param {string} apiBaseUrl - Base API URL (e.g., '/parish/get_regions_and_areas/')
         */
        initLocationHierarchy: function(apiBaseUrl = '/parish/get_regions_and_areas/') {
            // Diocese -> Regions
            this.setupCascade({
                parentSelectId: 'id_diocese',
                childSelectId: 'id_region',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'diocese_id',
                dataKey: 'regions',
                childPlaceholder: 'Select Region',
                dependentSelects: ['#id_state', '#id_area', '#id_district', '#id_division', '#id_zone']
            });

            // Region -> (Areas - handled via API)
            this.setupCascade({
                parentSelectId: 'id_region',
                childSelectId: 'id_area',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'region_id',
                dataKey: 'areas',
                childPlaceholder: 'Select Area',
                dependentSelects: ['#id_district', '#id_zone']
            });

            // State -> Divisions
            this.setupCascade({
                parentSelectId: 'id_state',
                childSelectId: 'id_division',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'state_id',
                dataKey: 'divisions',
                childPlaceholder: 'Select Division',
                dependentSelects: ['#id_area', '#id_district', '#id_zone']
            });

            // Division -> Areas
            this.setupCascade({
                parentSelectId: 'id_division',
                childSelectId: 'id_area',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'division_id',
                dataKey: 'areas',
                childPlaceholder: 'Select Area',
                dependentSelects: ['#id_district', '#id_zone']
            });

            // Area -> Districts
            this.setupCascade({
                parentSelectId: 'id_area',
                childSelectId: 'id_district',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'area_id',
                dataKey: 'districts',
                childPlaceholder: 'Select District',
                dependentSelects: ['#id_zone']
            });

            // District -> Zones
            this.setupCascade({
                parentSelectId: 'id_district',
                childSelectId: 'id_zone',
                apiBaseUrl: apiBaseUrl,
                apiParamName: 'district_id',
                dataKey: 'zones',
                childPlaceholder: 'Select Zone',
                dependentSelects: []
            });
        }
    };

    // Expose to global scope
    window.CascadingDropdownUtils = CascadingDropdownUtils;

})(window);
