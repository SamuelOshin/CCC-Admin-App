// Country data with flag information
const COUNTRIES = [
    { code: 'NG', name: 'Nigeria', dialCode: '234', flag: '🇳🇬' },
    { code: 'GH', name: 'Ghana', dialCode: '233', flag: '🇬🇭' },
    { code: 'BJ', name: 'Benin', dialCode: '229', flag: '🇧🇯' },
    { code: 'TG', name: 'Togo', dialCode: '228', flag: '🇹🇬' },
    { code: 'CM', name: 'Cameroon', dialCode: '237', flag: '🇨🇲' },
    { code: 'CI', name: 'Ivory Coast', dialCode: '225', flag: '🇨🇮' },
    { code: 'LR', name: 'Liberia', dialCode: '231', flag: '🇱🇷' },
    { code: 'SL', name: 'Sierra Leone', dialCode: '232', flag: '🇸🇱' },
    { code: 'GN', name: 'Guinea', dialCode: '224', flag: '🇬🇳' },
    { code: 'SN', name: 'Senegal', dialCode: '221', flag: '🇸🇳' },
    { code: 'US', name: 'United States', dialCode: '1', flag: '🇺🇸' },
    { code: 'GB', name: 'United Kingdom', dialCode: '44', flag: '🇬🇧' },
    { code: 'CA', name: 'Canada', dialCode: '1', flag: '🇨🇦' },
    { code: 'FR', name: 'France', dialCode: '33', flag: '🇫🇷' },
    { code: 'DE', name: 'Germany', dialCode: '49', flag: '🇩🇪' },
    { code: 'AU', name: 'Australia', dialCode: '61', flag: '🇦🇺' },
    { code: 'BR', name: 'Brazil', dialCode: '55', flag: '🇧🇷' },
    { code: 'IN', name: 'India', dialCode: '91', flag: '🇮🇳' },
    { code: 'CN', name: 'China', dialCode: '86', flag: '🇨🇳' },
    { code: 'JP', name: 'Japan', dialCode: '81', flag: '🇯🇵' },
    { code: 'KR', name: 'South Korea', dialCode: '82', flag: '🇰🇷' },
    { code: 'ZA', name: 'South Africa', dialCode: '27', flag: '🇿🇦' },
    { code: 'EG', name: 'Egypt', dialCode: '20', flag: '🇪🇬' },
    { code: 'KE', name: 'Kenya', dialCode: '254', flag: '🇰🇪' },
    { code: 'TZ', name: 'Tanzania', dialCode: '255', flag: '🇹🇿' }
];

// Country selector class for managing flag dropdown
class CountrySelector {
    constructor(selectElement, phoneInput, options = {}) {
        this.selectElement = selectElement;
        this.phoneInput = phoneInput;
        this.options = {
            defaultCountry: 'NG',
            showFlags: true,
            flagType: 'emoji', // 'emoji', 'svg', 'png'
            ...options
        };
        this.init();
    }

    init() {
        this.renderCountryOptions();
        this.bindEvents();
        this.setDefaultCountry();
    }

    renderCountryOptions() {
        const fragment = document.createDocumentFragment();

        COUNTRIES.forEach(country => {
            const option = document.createElement('option');
            option.value = country.code;
            option.dataset.dialCode = country.dialCode;
            option.dataset.flag = country.flag;

            // Create display text with emoji flag
            const flagHtml = `<span class="flag-emoji">${country.flag}</span>`;
            option.innerHTML = `${flagHtml} ${country.name} (+${country.dialCode})`;

            // Fallback text content for accessibility
            option.textContent = `${country.flag} ${country.name} (+${country.dialCode})`;

            fragment.appendChild(option);
        });

        this.selectElement.appendChild(fragment);
    }

    bindEvents() {
        this.selectElement.addEventListener('change', (e) => {
            this.handleCountryChange(e.target.value);
        });

        // Update placeholder when country changes
        this.selectElement.addEventListener('change', () => {
            this.updatePhonePlaceholder();
        });
    }

    handleCountryChange(countryCode) {
        const country = COUNTRIES.find(c => c.code === countryCode);
        if (country) {
            // Update phone input placeholder based on country
            this.updatePhonePlaceholder(country);

            // Trigger custom event for external listeners
            const event = new CustomEvent('countryChanged', {
                detail: { country, countryCode }
            });
            this.selectElement.dispatchEvent(event);
        }
    }

    updatePhonePlaceholder(country = null) {
        if (!country) {
            const selectedValue = this.selectElement.value;
            country = COUNTRIES.find(c => c.code === selectedValue);
        }

        if (country && this.phoneInput) {
            // Set appropriate placeholder based on country
            const placeholders = {
                'NG': 'e.g., 8012345678',
                'US': 'e.g., 5551234567',
                'GB': 'e.g., 7911123456',
                'CA': 'e.g., 4161234567',
                'FR': 'e.g., 612345678',
                'DE': 'e.g., 15123456789'
            };

            this.phoneInput.placeholder = placeholders[country.code] || `Enter phone number`;
        }
    }

    setDefaultCountry() {
        const defaultOption = this.selectElement.querySelector(`option[value="${this.options.defaultCountry}"]`);
        if (defaultOption) {
            defaultOption.selected = true;
            this.handleCountryChange(this.options.defaultCountry);
        }
    }

    getSelectedCountry() {
        const selectedValue = this.selectElement.value;
        return COUNTRIES.find(c => c.code === selectedValue);
    }

    getSelectedCountryCode() {
        return this.selectElement.value;
    }

    getSelectedDialCode() {
        const country = this.getSelectedCountry();
        return country ? country.dialCode : '';
    }
}

// Utility function to initialize country selectors
function initializeCountrySelectors() {
    const countrySelects = document.querySelectorAll('[data-country-selector]');

    countrySelects.forEach(select => {
        const phoneInputId = select.dataset.phoneInput;
        const phoneInput = phoneInputId ? document.getElementById(phoneInputId) : null;

        if (!select.countrySelector) {
            select.countrySelector = new CountrySelector(select, phoneInput);
        }
    });
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeCountrySelectors);

// Export for global use
window.CountrySelector = CountrySelector;
window.COUNTRIES = COUNTRIES;
