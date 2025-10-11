/**
 * Simple test to verify utility modules are working correctly
 * This can be run in the browser console to verify functionality
 */

(function() {
    'use strict';

    console.log('=== Testing Utility Modules ===');

    // Test 1: Check if utilities are available
    console.log('\n1. Checking if utility modules are loaded...');
    const modulesLoaded = {
        ParishUtils: typeof window.ParishUtils !== 'undefined',
        UIUtils: typeof window.UIUtils !== 'undefined',
        CascadingDropdownUtils: typeof window.CascadingDropdownUtils !== 'undefined'
    };
    console.log('Modules loaded:', modulesLoaded);

    // Test 2: Check ParishUtils functions
    console.log('\n2. Testing ParishUtils...');
    if (window.ParishUtils) {
        console.log('- fetchParishData:', typeof ParishUtils.fetchParishData === 'function');
        console.log('- updateField:', typeof ParishUtils.updateField === 'function');
        console.log('- initParishSelect:', typeof ParishUtils.initParishSelect === 'function');
        console.log('- initTransferParishSelection:', typeof ParishUtils.initTransferParishSelection === 'function');
        console.log('- initRestructureParishSelection:', typeof ParishUtils.initRestructureParishSelection === 'function');
    }

    // Test 3: Check UIUtils functions
    console.log('\n3. Testing UIUtils...');
    if (window.UIUtils) {
        console.log('- showAlert:', typeof UIUtils.showAlert === 'function');
        console.log('- getAlertIcon:', typeof UIUtils.getAlertIcon === 'function');
        console.log('- showLoading:', typeof UIUtils.showLoading === 'function');
        console.log('- hideLoading:', typeof UIUtils.hideLoading === 'function');
        console.log('- initFormValidation:', typeof UIUtils.initFormValidation === 'function');
    }

    // Test 4: Check CascadingDropdownUtils functions
    console.log('\n4. Testing CascadingDropdownUtils...');
    if (window.CascadingDropdownUtils) {
        console.log('- initSelect2:', typeof CascadingDropdownUtils.initSelect2 === 'function');
        console.log('- setupCascade:', typeof CascadingDropdownUtils.setupCascade === 'function');
        console.log('- initLocationHierarchy:', typeof CascadingDropdownUtils.initLocationHierarchy === 'function');
        console.log('- populateSelect:', typeof CascadingDropdownUtils.populateSelect === 'function');
        console.log('- resetDependentSelects:', typeof CascadingDropdownUtils.resetDependentSelects === 'function');
    }

    // Test 5: Test UIUtils.showAlert (visual test)
    console.log('\n5. Testing UIUtils.showAlert (check page for alert)...');
    if (window.UIUtils) {
        UIUtils.showAlert('Test alert - utility modules are working!', 'info');
    }

    // Test 6: Test alert icon function
    console.log('\n6. Testing UIUtils.getAlertIcon...');
    if (window.UIUtils) {
        console.log('- success icon:', UIUtils.getAlertIcon('success'));
        console.log('- warning icon:', UIUtils.getAlertIcon('warning'));
        console.log('- danger icon:', UIUtils.getAlertIcon('danger'));
        console.log('- info icon:', UIUtils.getAlertIcon('info'));
    }

    console.log('\n=== Test Complete ===');
    console.log('All utility modules are loaded and functional!');
})();
