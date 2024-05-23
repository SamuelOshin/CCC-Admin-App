from django.shortcuts import render, redirect, get_object_or_404, redirect
from .forms import TransferDataForm, ClergyTrfbioForm, PostinghistoryForm
from .models import ClergyDetails, ClergyTrfbio, TransferData, ParishRestructure, PostingHistory
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dal import autocomplete
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import ParishRestructureSerializer
import datetime

#api
class ParishRestructureViewSet(viewsets.ModelViewSet):
    queryset = ParishRestructure.objects.all()
    serializer_class = ParishRestructureSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            # Fetch the location string from the related model
            location_string = instance.location.name  # Assuming location is a ForeignKey
            data['location'] = location_string
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def is_transfer_admin(user):
    return user.groups.filter(name='TransferAdmin').exists() or user.is_superuser

@login_required
@user_passes_test(is_transfer_admin)
def new_transfer(request, id):
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    parishes = ParishRestructure.objects.all()

    if request.method == 'POST':
        transfer_form = TransferDataForm(request.POST)
        if transfer_form.is_valid():
            transfer_instance = transfer_form.save(commit=False)
            transfer_instance.clergy = clergy  # Associate the transfer with the clergy
            transfer_instance.save()
            
            # After saving the transfer, call the method to update floating status
            clergy.clergytrfbio.update_floating_status()
            messages.success(request, 'Transfer Successfully Done.')
            return render(request, 'transfer/trfForm.html', {'transfer_form': transfer_form, 'clergy': clergy,'parishes': parishes})
        else:
            messages.error(request, 'Something went wrong, Check Form Fields.')
    else:
        transfer_form = TransferDataForm(initial={'clergy': clergy})
    
    context = {
        'transfer_form': transfer_form, 
        'clergy': clergy,
        'parishes': parishes,
    }    

    return render(request, 'transfer/trfForm.html', context)

@login_required
def new_trf_table(request):
    # Fetch all transfer data with associated clergy details
    trf_data_with_clergy = TransferData.objects.select_related('clergy').order_by('-date_transfered')
    
    # Pass the data to the template
    return render(request, 'transfer/trfTable.html', {'trf_data_with_clergy': trf_data_with_clergy})
@login_required
def update_transfer(request, transfer_id):
    parishes = ParishRestructure.objects.all()
    # Retrieve transfer instance based on the provided ID
    transfer_instance = get_object_or_404(TransferData, pk=transfer_id)
    # Retrieve clergy instance associated with the transfer
    clergy = transfer_instance.clergy
    
    if request.method == 'POST':
        # If the request method is POST, process the form data
        transfer_form = TransferDataForm(request.POST, instance=transfer_instance)
        
        # Remove the fields 'parishFrm' and 'parishTo' from the form's data
        transfer_form.fields.pop('parishFrm', None)
        transfer_form.fields.pop('parishTo', None)
        transfer_form.fields.pop('date_transffered', None)

        if transfer_form.is_valid():
            # If the form is valid, save the instance without saving the excluded fields
            transfer_instance = transfer_form.save(commit=False)
            transfer_instance.save()  # List fields to update
            clergy.clergytrfbio.update_floating_status()
            messages.success(request, 'Transfer Successfully Updated.')
            # Redirect to a view page or any other appropriate URL
            return redirect('update_transfer', transfer_id=transfer_instance.pk)
        else:
            # If form is not valid, show error message
            messages.error(request, 'Something went wrong, Check Form Fields.')
    else:
        # If the request method is GET, populate the form with instance data
        transfer_form = TransferDataForm(instance=transfer_instance)
    
    # Remove the fields 'parishFrm' and 'parishTo' from the form's fields
    transfer_form.fields.pop('parishFrm', None)
    transfer_form.fields.pop('parishTo', None)
    
    # Prepare context with form, transfer_instance, and clergy
    context = {
        'transfer_form': transfer_form, 
        'clergy': clergy,
        'parishes': parishes,
    }    

    return render(request, 'transfer/update_transfer.html', context)

def view_transfer(request, transfer_id):
    # Retrieve all transfer instances
    transfer_instance = get_object_or_404(TransferData, pk=transfer_id)
    clergy = transfer_instance.clergy
    transfer_form = TransferDataForm(instance=transfer_instance)
    context = {
        'transfer_form': transfer_form,
        'clergy': clergy,
        'transfer_id': transfer_instance.id,
    }
    return render(request, 'transfer/view_transfer.html', context)
@login_required
def clergy_details(request):
    clergy = ClergyTrfbio.objects.all()

    return render(request, 'transfer/clergyt.html', {'clergy':clergy})

@login_required
@user_passes_test(is_transfer_admin)
def transfer_dashboard(request):
    return render(request, 'transfer/dashboard.html')

@login_required
def view_add_posting(request, id):
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    if request.method == 'POST':
        posting_form = PostinghistoryForm(request.POST)
        if posting_form.is_valid():
            posting_instance = posting_form.save(commit=False)
            posting_instance.clergy = clergy
            posting_instance.save()
            messages.success(request, 'Posting Successfully Added.')
            context = {
            'posting_form': posting_form, 
            'clergy': clergy,
        } 
            return render(request, 'transfer/postingH_form.html', context)
        else:
            messages.error(request, 'Something went wrong, Check Form Fields.')
    else:
        posting_form = PostinghistoryForm(initial={'clergy': clergy})
   
    posts = PostingHistory.objects.filter(clergy=clergy).order_by('-date_of_entry')
    context = {
        'posting_form': posting_form, 
        'clergy': clergy,
        'posts': posts,
    }    

    return render(request, 'transfer/postingH_form.html', context)


