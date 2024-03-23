from django import forms
from .models import ClergyDetails

class ClergyRegistrationForm(forms.ModelForm):
    additional_data = forms.CharField(widget=forms.Textarea, required=False)
    children_info = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    work_experience_ifyes = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), required=False)
    trg_number = forms.IntegerField(required=False)
    class Meta:
        model = ClergyDetails
        fields = '__all__'


