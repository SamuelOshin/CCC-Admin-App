from django import forms
from .models import ClergyDetails, AnnointmentGazzette
from datetime import datetime
from phonenumber_field.formfields import PhoneNumberField

class ClergyRegistrationForm(forms.ModelForm):
    additional_data = forms.CharField(widget=forms.Textarea, required=False)
    children_info = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    work_experience_ifyes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False)
    trg_number = forms.IntegerField(required=False)
    
    # Use PhoneNumberField with custom widget for country flags
    telephone = PhoneNumberField(
        required=True,
        region='NG',  # Default to Nigeria
        error_messages={'required': 'Please enter the telephone number.'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )
    
    class Meta:
        model = ClergyDetails
        fields = '__all__'


class AnnointmentForm(forms.ModelForm):
# Get the current year
    current_year = datetime.now().year

# Generate the list of year choices
    year_choices = [(str(year), str(year)) for year in range(current_year, 1946, -1)]

    
    # Override year_of_annointment field to use ChoiceField
    year_of_annointment = forms.ChoiceField(
        label='Year of Annointment',
        choices=year_choices,
        required=True,
    )

    class Meta:
        model = AnnointmentGazzette
        fields = '__all__'
        exclude = ['clergy']

    def save(self, commit=True):
        instance = super().save(commit=False)
        year = int(self.cleaned_data['year_of_annointment'])
        instance.year_of_annointment = year
        if commit:
            instance.save()
        return instance