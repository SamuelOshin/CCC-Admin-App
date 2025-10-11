/**
 * Parish Utilities Module
 * Consolidates all parish-related functions to follow DRY principle
 */

(function(window) {
    'use strict';

    const ParishUtils = {
        /**
         * Fetch parish data from API
         * @param {string} parishId - The parish ID
         * @param {string} apiEndpoint - The API endpoint (default: '/parish/api/parish/')
         * @returns {Promise} - Promise resolving to parish data
         */
        fetchParishData: function(parishId, apiEndpoint = '/parish/api/parish/') {
            if (!parishId) {
                return Promise.reject(new Error('Parish ID is required'));
            }

            return fetch(`${apiEndpoint}${parishId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('Error fetching parish data:', error);
                    throw error;
                });
        },

        /**
         * Update field with parish data
         * @param {string} fieldId - The field ID to update
         * @param {*} value - The value to set
         */
        updateField: function(fieldId, value) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = value || '';
                // Trigger input event for any listeners
                field.dispatchEvent(new Event('input', { bubbles: true }));
            }
        },

        /**
         * Clear field value
         * @param {string} fieldId - The field ID to clear
         */
        clearField: function(fieldId) {
            this.updateField(fieldId, '');
        },

        /**
         * Update multiple parish fields from parish data
         * @param {Object} parishData - Parish data object
         * @param {Object} fieldMapping - Mapping of data keys to field IDs
         */
        updateParishFields: function(parishData, fieldMapping) {
            if (!parishData) return;

            for (const [dataKey, fieldId] of Object.entries(fieldMapping)) {
                if (parishData[dataKey] !== undefined) {
                    this.updateField(fieldId, parishData[dataKey]);
                }
            }
        },

        /**
         * Initialize parish selection with Select2 events
         * @param {string} selectId - The select element ID
         * @param {Function} onSelect - Callback when parish is selected
         * @param {Function} onClear - Callback when parish is cleared
         */
        initParishSelect: function(selectId, onSelect, onClear) {
            const $select = $(`#${selectId}`);
            
            if ($select.length === 0) {
                return;
            }

            // Remove existing event handlers to prevent duplicates
            $select.off('select2:select select2:clear');

            // Attach select event
            if (onSelect && typeof onSelect === 'function') {
                $select.on('select2:select', function(e) {
                    const parishId = e.params.data.id;
                    onSelect(parishId);
                });
            }

            // Attach clear event
            if (onClear && typeof onClear === 'function') {
                $select.on('select2:clear', function() {
                    onClear();
                });
            }
        },

        /**
         * Populate parish details for transfer forms
         * @param {string} parishId - The parish ID
         * @param {string} type - 'from' or 'to'
         * @param {string} apiEndpoint - Optional custom API endpoint
         */
        populateTransferParishDetails: function(parishId, type, apiEndpoint = '/transfer/api/parish/') {
            if (!parishId) {
                // Clear fields if no parish selected
                this.clearTransferFields(type);
                return Promise.resolve();
            }

            return this.fetchParishData(parishId, apiEndpoint)
                .then(data => {
                    const fieldMapping = this.getTransferFieldMapping(type);
                    this.updateParishFields(data, fieldMapping);
                    
                    // Update hidden parish ID field
                    const parishIdField = type === 'from' ? 'id_parishFrm' : 'id_parishTo';
                    this.updateField(parishIdField, parishId);
                    
                    return data;
                });
        },

        /**
         * Get field mapping for transfer forms
         * @param {string} type - 'from' or 'to'
         * @returns {Object} - Field mapping object
         */
        getTransferFieldMapping: function(type) {
            if (type === 'from') {
                return {
                    address: 'id_address',
                    location: 'id_location'
                };
            } else {
                return {
                    address: 'id_address_to',
                    location: 'id_location_to'
                };
            }
        },

        /**
         * Clear transfer form fields
         * @param {string} type - 'from' or 'to'
         */
        clearTransferFields: function(type) {
            const fieldMapping = this.getTransferFieldMapping(type);
            for (const fieldId of Object.values(fieldMapping)) {
                this.clearField(fieldId);
            }
            
            // Clear hidden parish ID field
            const parishIdField = type === 'from' ? 'id_parishFrm' : 'id_parishTo';
            this.clearField(parishIdField);
        },

        /**
         * Initialize parish selection for transfer forms
         */
        initTransferParishSelection: function() {
            // Initialize "From" parish
            this.initParishSelect(
                'parishFrmId',
                (parishId) => {
                    console.log('From parish selected:', parishId);
                    this.populateTransferParishDetails(parishId, 'from')
                        .catch(error => console.error('Error loading from parish:', error));
                },
                () => {
                    console.log('From parish cleared');
                    this.clearTransferFields('from');
                }
            );

            // Initialize "To" parish
            this.initParishSelect(
                'parishToId',
                (parishId) => {
                    console.log('To parish selected:', parishId);
                    this.populateTransferParishDetails(parishId, 'to')
                        .catch(error => console.error('Error loading to parish:', error));
                },
                () => {
                    console.log('To parish cleared');
                    this.clearTransferFields('to');
                }
            );
        },

        /**
         * Initialize parish selection for restructure forms
         * @param {Function} onSuccess - Optional success callback
         * @param {Function} onError - Optional error callback
         */
        initRestructureParishSelection: function(onSuccess, onError) {
            this.initParishSelect(
                'id_parish',
                (parishId) => {
                    this.fetchParishData(parishId, '/parish/api/parish/')
                        .then(data => {
                            this.updateField('id_address', data.address);
                            if (onSuccess) onSuccess(data);
                        })
                        .catch(error => {
                            if (onError) onError(error);
                        });
                },
                () => {
                    this.clearField('id_address');
                }
            );
        }
    };

    // Expose to global scope
    window.ParishUtils = ParishUtils;

})(window);
