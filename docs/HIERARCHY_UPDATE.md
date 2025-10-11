# Location Hierarchy Update - Sub Division Added

## Summary

Updated the location hierarchy to include "Sub Division" between "Division" and "Area" as requested.

## Correct Hierarchy

**Diocese → Region → State → Division → Sub Division → Area → District → Zone**

## Changes Made

### 1. JavaScript Utilities

#### cascading-dropdown-utils.js
- Updated `initLocationHierarchy()` function to include Sub Division in the cascading chain
- Added new cascade: Division → Sub Division
- Updated existing cascade: Sub Division → Area (moved from Division → Area)
- Updated dependent selects arrays to include '#id_subdivision'

**New cascading flow:**
```javascript
Diocese → Regions
State → Divisions  
Division → Sub Divisions (NEW)
Sub Division → Areas (UPDATED)
Area → Districts
District → Zones
```

#### theme.js
- Updated Select2 initialization array to include 'id_subdivision'
- Order: `'id_diocese', 'id_region', 'id_state', 'id_division', 'id_subdivision', 'id_area', 'id_district', 'id_zone'`

### 2. Templates

#### restructure.html
- Updated `regularSelects` array to include '#id_subdivision' in correct position
- Updated `dependentSelects` array to include '#id_subdivision'

#### edit_parish.html
- Added 'subdivision' to FORM_FIELD_IDS with default fallback
- Updated hierarchy array to: `['diocese', 'region', 'state', 'division', 'subdivision', 'area', 'district', 'zone']`
- Added subdivisionSelect mapping in CascadingDropdownUtils integration
- Updated resetForm() to include subdivision field

### 3. Documentation

#### DRY_REFACTORING.md
- Updated hierarchy description to include "Sub Division"
- New: Diocese → Region → State → Division → **Sub Division** → Area → District → Zone

#### REFACTORING_SUMMARY.md
- Updated hierarchy description in cascading-dropdown-utils.js section

## Backend Integration Notes

**Important:** The JavaScript utilities have been updated to support the subdivision field, but the following backend changes are still needed:

### Required Backend Updates:

1. **models.py** - Add 'subdivision' to Location.LEVEL_CHOICES:
```python
LEVEL_CHOICES = [
    # ... existing choices ...
    ('division', 'Division'),
    ('subdivision', 'Sub Division'),  # ADD THIS
    ('area', 'Area'),
    # ... rest of choices ...
]
```

2. **forms.py (ParishForm)** - Add subdivision field:
```python
subdivision = forms.ModelChoiceField(
    queryset=Location.objects.none(), 
    empty_label="Select Sub Division", 
    required=False
)
```

3. **forms.py (ParishForm.__init__)** - Add subdivision queryset logic:
```python
if 'division' in self.data:
    try:
        division_id = int(self.data.get('division'))
        subdivisions = Location.objects.filter(parent_id=division_id, level='subdivision')
        self.fields['subdivision'].queryset = subdivisions
    except (ValueError, TypeError):
        pass

if 'subdivision' in self.data:
    try:
        subdivision_id = int(self.data.get('subdivision'))
        areas = Location.objects.filter(parent_id=subdivision_id, level='area')
        self.fields['area'].queryset = areas
    except (ValueError, TypeError):
        pass
```

4. **views.py (get_regions_and_areas)** - Add subdivision handling:
```python
# Add subdivision query parameter handling
subdivision_id = request.GET.get('subdivision_id')
if subdivision_id:
    areas = Location.objects.filter(parent_id=subdivision_id, level='area')
    return JsonResponse({'areas': list(areas.values('id', 'name'))})

# Add division handling for subdivisions
division_id = request.GET.get('division_id')
if division_id:
    subdivisions = Location.objects.filter(parent_id=division_id, level='subdivision')
    return JsonResponse({'subdivisions': list(subdivisions.values('id', 'name'))})
```

5. **templates/ParishRestructure/restructure.html** - Add subdivision HTML field:
```html
<!-- After Division Selection, before Area Selection -->
<div class="col-12">
    <div class="form-floating position-relative">
        {{ form.subdivision|add_class:"form-select"|attr:"id:id_subdivision" }}
        <label for="id_subdivision">
            <i class="bi bi-diagram-2 me-1"></i>{{ form.subdivision.label }}
        </label>
        {% if form.subdivision.errors %}
            <div class="invalid-feedback d-block">
                {% for error in form.subdivision.errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
    </div>
</div>
```

6. **forms.py (ParishForm.clean)** - Update clean method to include subdivision:
```python
def clean(self):
    cleaned_data = super().clean()
    # ... existing code ...
    subdivision = cleaned_data.get('subdivision')
    
    # Update the location selection logic to include subdivision
    if not subdivision and not area and not district and not zone and division:
        cleaned_data['location'] = division
    elif not area and not district and not zone and subdivision:
        cleaned_data['location'] = subdivision
    # ... rest of logic ...
```

## Testing After Backend Updates

Once backend is updated:

1. Navigate to Parish Restructure form
2. Select Diocese → verify Regions load
3. Select State → verify Divisions load
4. Select Division → verify **Sub Divisions** load (NEW)
5. Select Sub Division → verify Areas load
6. Continue through Area → District → Zone
7. Verify form submission works correctly
8. Check that location is saved to the correct level

## Benefits

✅ **Correct Hierarchy**: Now matches the organizational structure  
✅ **Future-Proof**: JavaScript ready for backend implementation  
✅ **Backward Compatible**: Works with or without subdivision field  
✅ **Consistent**: All templates and utilities updated uniformly

## Files Modified

1. `cccadminapp/static/assets/js/cascading-dropdown-utils.js`
2. `cccadminapp/static/assets/js/theme.js`
3. `templates/ParishRestructure/restructure.html`
4. `templates/ParishRestructure/edit_parish.html`
5. `docs/DRY_REFACTORING.md`
6. `docs/REFACTORING_SUMMARY.md`
7. `docs/HIERARCHY_UPDATE.md` (this file)

## Commit Information

All JavaScript utilities and templates have been updated to support the correct location hierarchy with Sub Division included between Division and Area.
