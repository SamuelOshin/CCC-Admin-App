from django import forms
from .models import Location, ParishRestructure, ParishRegistration, ParishDirectory
from django.db.models import Q

class ParishDirectoryForm(forms.ModelForm):
    # name = forms.ModelChoiceField(queryset=ParishDirectory.objects.all(), empty_label=None)


    class Meta:
        model = ParishDirectory
        fields = '__all__'
        labels = {
            'name': 'Parish Name',
            'address': 'Parish Address'
        }

from django import forms
from .models import ParishRestructure, ParishDirectory, Location

class ParishForm(forms.ModelForm):
    parish = forms.ModelChoiceField(queryset=ParishDirectory.objects.order_by('name'))
    diocese = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Diocese")
    region = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Region", required=False)
    state = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select State", required=False)
    division = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Division", required=False)
    area = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Area", required=False)
    district = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select District", required=False)
    zone = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select zone", required=False)

    class Meta:
        model = ParishRestructure
        fields = ['parish', 'address']
        widgets = {
        'parish': forms.Select(attrs={'class': 'form-control parishSelect'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['diocese'].queryset = Location.objects.filter(
            Q(name='Arch Diocese') | Q(level='diocese')
        ).order_by('name')
        self.fields['region'].queryset = Location.objects.none()
        self.fields['state'].queryset = Location.objects.none()
        self.fields['division'].queryset = Location.objects.none()
        self.fields['area'].queryset = Location.objects.none()
         # Modify region field queryset to include special option
        self.fields['district'].queryset = Location.objects.filter(
            Q(name='Special District') | Q(level='district')
        )
        self.fields['zone'].queryset = Location.objects.none()

        if 'diocese' in self.data:
            try:
                diocese_id = int(self.data.get('diocese'))
                regions = Location.objects.filter(parent_id=diocese_id, level='region')
                self.fields['region'].queryset = regions
            except (ValueError, TypeError):
                pass

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                states = Location.objects.filter(parent_id=region_id, level='state')
                self.fields['state'].queryset = states
            except (ValueError, TypeError):
                pass

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                divisions = Location.objects.filter(parent_id=state_id, level='division')
                self.fields['division'].queryset = divisions
            except (ValueError, TypeError):
                pass

        if 'division' in self.data:
            try:
                division_id = int(self.data.get('division'))
                areas = Location.objects.filter(parent_id=division_id, level='area')
                self.fields['area'].queryset = areas
            except (ValueError, TypeError):
                pass

        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                districts = Location.objects.filter(parent_id=area_id, level='district')
                self.fields['district'].queryset = districts
            except (ValueError, TypeError):
                pass

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                zones = Location.objects.filter(parent_id=district_id, level='zone')
                self.fields['zone'].queryset = zones
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        diocese = cleaned_data.get('diocese')
        region = cleaned_data.get('region')
        state = cleaned_data.get('state')
        area = cleaned_data.get('area')
        district = cleaned_data.get('district')
        division = cleaned_data.get('division')
        zone = cleaned_data.get('zone')

        if not region and not state and not division and not area and not district and not zone and diocese:
            cleaned_data['location'] = diocese
        elif not state and not division and not area and not district and not zone and region:
            cleaned_data['location'] = region
        elif not division and not area and not district and not zone and state:
            cleaned_data['location'] = state
        elif not area and not district and not zone and division:
            cleaned_data['location'] = division
        elif not district and not zone and area:
            cleaned_data['location'] = area
        elif not zone and district:
            cleaned_data['location'] = district
        elif zone:
            cleaned_data['location'] = zone
        elif zone:
            cleaned_data['location'] = zone

        return cleaned_data




    

        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'parent', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['parent'].choices = self.get_location_choices()

    def get_location_choices(self):
        choices = []

        # Get unique levels
        levels = Location.objects.values_list('level', flat=True).distinct()

        # Create choices with optgroup structure
        for level in levels:
            locations_by_level = Location.objects.filter(level=level)
            location_choices = [(location.id, location.name) for location in locations_by_level]
            choices.append((level.capitalize(), location_choices))

        return choices

class ParishRegForm(forms.ModelForm):
    """A form to create a new parish registration."""
    date_of_establishment = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = ParishRegistration
        fields = [ 'country', 'state', 'city', 'diocese', 'founding_patron','date_of_establishment', 'name_of_shepherd', 'phone', 'email', 'parish_picture', 'application_for_registration', 'original_receipt_of_land', 'original_survey_plan', 'building_plan', 'sworn_affidavit', 'passport_photograph', 'approval_from_government_diaspora', 'payment_proof_of_auditorium' ]
        widgets = {
            'phone' : forms.NumberInput(attrs={'type':'tel' }),
            'parish': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'state': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'parish_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'country': forms.Select(attrs={'class': 'form-control parishSelect', 'onchange': "print_state('id_state', this.selectedIndex);" })
        }
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs) 

         self.fields['diocese'].queryset = Location.objects.filter(level='diocese')  

class ParishRegForm1(forms.ModelForm):
    # parish = forms.ModelChoiceField(queryset=ParishDirectory.objects.order_by('name'), empty_label=None)
    date_of_establishment = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = ParishRegistration
        fields = [ 'parish', 'country', 'state', 'city', 'diocese', 'founding_patron','date_of_establishment', 'name_of_shepherd', 'phone', 'email', 'parish_picture', 'application_for_registration', 'original_receipt_of_land', 'original_survey_plan', 'building_plan', 'sworn_affidavit', 'passport_photograph', 'approval_from_government_diaspora', 'payment_proof_of_auditorium' ]
        widgets = {
            'parish': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'state': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'parish_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'country': forms.Select(attrs={'class': 'form-control parishSelect', 'onchange': "print_state('id_state', this.selectedIndex);" })
        }
        enctype = 'multipart/form-data'
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs) 

         self.fields['diocese'].queryset = Location.objects.filter(level='diocese')  
         self.fields['parish'].queryset = ParishDirectory.objects.order_by('name')
         
         # Make parish field readonly when editing existing registration
         if self.instance and self.instance.pk:
             self.fields['parish'].widget.attrs['readonly'] = True
             self.fields['parish'].required = False  


        
