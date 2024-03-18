from django import forms
from .models import Location, ParishRestructure, ParishRegistration, ParishDirectory

class ParishDirectoryForm(forms.ModelForm):
    # name = forms.ModelChoiceField(queryset=ParishDirectory.objects.all(), empty_label=None)


    class Meta:
        model = ParishDirectory
        fields = ['name', 'address']

class ParishForm(forms.ModelForm):
    parish = forms.ModelChoiceField(queryset=ParishDirectory.objects.order_by('name'))
    diocese = forms.ModelChoiceField(queryset=Location.objects.filter(level='diocese'), empty_label="Select Diocese")
    region = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Region", required=False)
    area = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label="Select Area", required=False)

    class Meta:
        model = ParishRestructure
        fields = ['parish', 'address']

    def clean(self):
        cleaned_data = super().clean()
        diocese = cleaned_data.get('diocese')
        region = cleaned_data.get('region')
        area = cleaned_data.get('area')

        if not region and not area and diocese:
            # If diocese is selected and no region or area is selected, set location to diocese
            cleaned_data['location'] = diocese

        elif not area and region:
            # If region is selected but no area is selected, set location to region
            cleaned_data['location'] = region

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
                areas = Location.objects.filter(parent_id=region_id, level='area')
                self.fields['area'].queryset = areas
            except (ValueError, TypeError):
                pass




    

        
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
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs) 

         self.fields['diocese'].queryset = Location.objects.filter(level='diocese')  

class ParishRegForm1(forms.ModelForm):
    parish = forms.ModelChoiceField(queryset=ParishDirectory.objects.order_by('name'), empty_label=None)
    date_of_establishment = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = ParishRegistration
        fields = [ 'parish', 'country', 'state', 'city', 'diocese', 'founding_patron','date_of_establishment', 'name_of_shepherd', 'phone', 'email', 'parish_picture', 'application_for_registration', 'original_receipt_of_land', 'original_survey_plan', 'building_plan', 'sworn_affidavit', 'passport_photograph', 'approval_from_government_diaspora', 'payment_proof_of_auditorium' ]
        widgets = {
            'parish_picture': forms.FileInput(attrs={'accept': 'image/*'})
        }
        enctype = 'multipart/form-data'
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs) 

         self.fields['diocese'].queryset = Location.objects.filter(level='diocese')  


        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['parent'].queryset = Location.objects.filter(level='continent')
    #     self.fields['level'].widget.attrs['readonly'] = True
    #     self.fields['level'].widget.attrs['disabled'] = True
    #     self.fields['level'].widget.attrs['value'] = 'region'
    #     self.fields['level'].initial = 'region'
    #     self.fields['level'].disabled = True
    #     self.fields['level'].required = False
    #     self.fields['level'].widget.attrs['required'] = False
    #     self.fields['level'].widget.attrs['hidden'] = True