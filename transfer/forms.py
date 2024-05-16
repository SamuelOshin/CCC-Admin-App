# # Create a form to handle data entry for new transfers


from dal import autocomplete
from django import forms
from .models import PostingHistory, ClergyTrfbio, TransferData, ParishRestructure, ParishDirectory

class TransferDataForm(forms.ModelForm):
   

    class Meta:
        model = TransferData
        fields = ['parishFrm', 'parishTo',  'trf_begin', 'trf_end', 'trf_status', 'trf_extended', 'remarks', 'extended_date', 'designation_frm', 'designation_to']
        widgets = {
            'parishFrm': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'parishTo': forms.Select(attrs={'class': 'form-control parishSelect'}),
            'designation_frm': forms.Select(attrs={'class': 'form-control'}),
            'designation_to': forms.Select(attrs={'class': 'form-control'}),
            'trf_begin': forms.DateInput(attrs={'class': 'form-control'}),
            'trf_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'trf_status': forms.Select(attrs={'class': 'form-control'}),
            'trf_extended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'extended_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter note here...'}),
        }

class ClergyTrfbioForm(forms.ModelForm):
    class Meta:
        model = ClergyTrfbio
        fields = ['floating']
        widgets = {
        }
        labels = {
            'note': 'Notes',
        }

class PostinghistoryForm(forms.ModelForm):
    class Meta:
        model = PostingHistory
        fields = '__all__'
        exclude = ['clergy']
        widgets = {
            'date_of_entry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_exit': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter note here...'}),
            'designation': forms.Select(attrs={'class': 'form-select'}),
            'clergy': forms.TextInput(attrs={'class': 'form-control'}),
            'parish': forms.Select(attrs={'class': 'form-control parishSelect'}),
        }
