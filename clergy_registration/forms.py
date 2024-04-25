from django import forms
from .models import ClergyDetails, AnnointmentGazzette
from datetime import datetime

class ClergyRegistrationForm(forms.ModelForm):
    additional_data = forms.CharField(widget=forms.Textarea, required=False)
    children_info = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    work_experience_ifyes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False)
    trg_number = forms.IntegerField(required=False)
    edu_qualification = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    class Meta:
        model = ClergyDetails
        fields = '__all__'


class AnnointmentForm(forms.ModelForm):
    # Define choices for the year field
    year_choices = [(str(year), str(year)) for year in range(1947, datetime.now().year + 1)]
    
    # Override year_of_annointment field to use ChoiceField
    year_of_annointment = forms.ChoiceField(
        label='Year of Annointment',
        choices=year_choices,
        required=True,
    )

    class Meta:
        model = AnnointmentGazzette
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        year = int(self.cleaned_data['year_of_annointment'])
        instance.year_of_annointment = year
        if commit:
            instance.save()
        return instance