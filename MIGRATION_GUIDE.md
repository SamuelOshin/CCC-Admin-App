# Template Migration Guide

## Overview
This guide shows how to migrate existing app templates to use the new centralized dashboard system.

## Migration Steps

### 1. Dashboard/Overview Pages

**Before (Old template structure):**
```html
<!-- clergy_reg/templates/clergy_reg/dashboard.html -->
{% extends 'clergy_reg/base.html' %}
{% block content %}
    <!-- Dashboard content here -->
{% endblock %}
```

**After (Using centralized system):**
```html
<!-- clergy_reg/templates/clergy_reg/dashboard.html -->
{% extends 'dashboard/layouts/dashboard_layout.html' %}

{% block title %}Clergy Management Dashboard{% endblock %}
{% block dashboard_title %}Clergy Management{% endblock %}
{% block dashboard_subtitle %}Manage clergy members and registrations{% endblock %}

{% block dashboard_stats %}
    <!-- Your stats cards here -->
{% endblock %}

{% block main_content %}
    <!-- Your main dashboard content here -->
{% endblock %}
```

### 2. Form Pages

**Before:**
```html
{% extends 'clergy_reg/base.html' %}
{% block content %}
    <form method="post">
        <!-- Form content -->
    </form>
{% endblock %}
```

**After:**
```html
{% extends 'dashboard/layouts/form_layout.html' %}

{% block form_title %}Register New Clergy{% endblock %}
{% block form_action %}{% url 'register_clergy' %}{% endblock %}
{% block form_method %}post{% endblock %}

{% block form_content %}
    <!-- Your form fields here -->
{% endblock %}
```

### 3. Table/List Pages

**Before:**
```html
{% extends 'clergy_reg/base.html' %}
{% block content %}
    <table class="table">
        <!-- Table content -->
    </table>
{% endblock %}
```

**After:**
```html
{% extends 'dashboard/layouts/table_layout.html' %}

{% block table_title %}All Clergy{% endblock %}
{% block table_actions %}
    <!-- Action buttons -->
{% endblock %}

{% block table_content %}
    <table class="table">
        <!-- Your table content -->
    </table>
{% endblock %}
```

## Template Block Reference

### Dashboard Layout Blocks
- `dashboard_title` - Main page title
- `dashboard_subtitle` - Page description
- `dashboard_stats` - Statistics cards section
- `main_content` - Main content area
- `sidebar_stats` - Right sidebar statistics
- `recent_actions` - Recent activity timeline
- `additional_content` - Extra content below main area

### Form Layout Blocks
- `form_title` - Form page title
- `form_subtitle` - Form description
- `form_action` - Form action URL
- `form_method` - Form method (get/post)
- `form_enctype` - Form encoding type
- `form_tabs` - Tab navigation for multi-step forms
- `form_content` - Main form content
- `form_actions` - Form action buttons
- `form_help` - Help sidebar content

### Table Layout Blocks
- `table_title` - Table page title
- `table_subtitle` - Table description
- `table_actions` - Action buttons (Add, Import, Export)
- `table_filters` - Filter controls
- `bulk_actions` - Bulk action controls
- `table_content` - Main table content
- `pagination_info` - Pagination information
- `table_help` - Help sidebar content
- `modals` - Modal dialogs

## Example Migrations

### Clergy Registration App

1. **Update `clergy_reg/templates/clergy_reg/dashboard.html`:**
   - Replace with `templates/clergy_reg/dashboard_new.html` (created above)

2. **Update `clergy_reg/templates/clergy_reg/register.html`:**
   - Replace with `templates/clergy_reg/register_new.html` (created above)

3. **Update `clergy_reg/templates/clergy_reg/all_clergy.html`:**
   - Replace with `templates/clergy_reg/all_clergy_new.html` (created above)

### Transfer App

1. **Create new dashboard template:**
```html
{% extends 'dashboard/layouts/dashboard_layout.html' %}
{% block dashboard_title %}Transfer Management{% endblock %}
{% block dashboard_subtitle %}Manage clergy transfers and assignments{% endblock %}
```

2. **Create new transfer form template:**
```html
{% extends 'dashboard/layouts/form_layout.html' %}
{% block form_title %}Create Transfer Request{% endblock %}
{% block form_action %}{% url 'create_transfer' %}{% endblock %}
```

### Parish Restructure App

1. **Create new dashboard template:**
```html
{% extends 'dashboard/layouts/dashboard_layout.html' %}
{% block dashboard_title %}Parish Management{% endblock %}
{% block dashboard_subtitle %}Manage parishes and restructuring{% endblock %}
```

## Benefits of Migration

1. **Consistency**: All apps now have the same look and feel
2. **Maintainability**: Single place to update UI components
3. **Responsiveness**: Built-in mobile-friendly design
4. **Features**: Built-in search, filters, bulk actions, etc.
5. **Performance**: Optimized CSS and JavaScript
6. **Accessibility**: WCAG compliant components

## Migration Checklist

- [ ] Backup existing templates
- [ ] Create new templates using centralized layouts
- [ ] Update URL patterns if needed
- [ ] Test all functionality
- [ ] Update any custom CSS/JS
- [ ] Validate responsive design
- [ ] Test accessibility features
- [ ] Update documentation

## Common Patterns

### Adding Custom Styles
```html
{% block extra_css %}
<style>
    .custom-clergy-card {
        /* Your custom styles */
    }
</style>
{% endblock %}
```

### Adding Custom JavaScript
```html
{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Your custom JavaScript
});
</script>
{% endblock %}
```

### Custom Breadcrumbs
```html
{% block breadcrumb_items %}
    <li class="breadcrumb-item"><a href="{% url 'clergy_dashboard' %}">Clergy</a></li>
    <li class="breadcrumb-item active">Register New</li>
{% endblock %}
```

## Next Steps

1. Start with one app (e.g., clergy_registration)
2. Migrate dashboard page first
3. Test thoroughly
4. Move to form pages
5. Finally migrate list/table pages
6. Repeat for other apps
7. Remove old base templates once migration is complete

## Support

If you need help during migration:
1. Check the example templates created above
2. Review the layout templates in `templates/dashboard/layouts/`
3. Look at the component templates in `templates/dashboard/components/`
4. Test each template as you migrate it
