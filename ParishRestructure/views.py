from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ParishForm, LocationForm, ParishRegForm, ParishDirectoryForm, ParishRegForm1
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import JsonResponse
#api
from rest_framework import viewsets
from .serializers import ParishDirectorySerializer
import datetime

#api
class ParishDirectoryViewSet(viewsets.ModelViewSet):
    queryset = ParishDirectory.objects.all()
    serializer_class = ParishDirectorySerializer
#endapi    
@login_required    
def restructure_parish(request):
    if request.method == 'POST':
        form = ParishForm(request.POST)
        if form.is_valid(): 
            parish_instance = form.save(commit=False)

            # Assuming 'location_id' is the field to save the area ID
            if 'location' in form.cleaned_data:
                parish_instance.location_id = form.cleaned_data['location'].id

            parish_instance.save()

            messages.success(request, 'Parish added successfully.')
            return redirect('parish_dashboard')  # Redirect to success page or any other URL
    else:
        form = ParishForm()
    return render(request, 'ParishRestructure/restructure.html', {'form': form})


@login_required  
def get_regions_and_areas(request):
    if request.method == 'GET':
        diocese_id = request.GET.get('diocese_id')  # Extract diocese ID from query parameters
        region_id = request.GET.get('region_id')    # Extract region ID from query parameters

        # Fetch regions for the selected diocese
        regions = Location.objects.filter(parent_id=diocese_id, level='region')

        # Fetch areas for the selected region
        areas = Location.objects.filter(parent_id=region_id, level='area')

        # Serialize regions and areas data
        serialized_regions = [{'id': region.id, 'name': region.name} for region in regions]
        serialized_areas = [{'id': area.id, 'name': area.name} for area in areas]

        # Return JSON response with regions and areas data
        return JsonResponse({'regions': serialized_regions, 'areas': serialized_areas})

@login_required  
@user_passes_test(lambda u: not u.groups.filter(name='Clergyadmin').exists())
def parish_dashboard(request):
    return render(request, 'ParishRestructure/parish_dashboard.html')

@login_required  
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location added successfully.')
    else:
        form = LocationForm()
    return render(request, 'ParishRestructure/add_location.html', {'form': form})

def get_all_parishes_in_children(location):
    parishes = []
    
    # Recursively traverse the hierarchy of child locations
    for child_location in location.children.all():
        # Retrieve all parishes associated with the current child location
        child_location_parishes = child_location.parishrestructure_set.all()
        
        # Extend the list of parishes with the parishes from the current child location
        parishes.extend(child_location_parishes)
        
        # Recursively collect parishes from the child location's children
        parishes.extend(get_all_parishes_in_children(child_location))
    
    return parishes



@login_required  
def view_parishes(request):
    locations = Location.objects.all()
    if request.method == 'POST':
        location_id = request.POST.get('location')
        selected_location = Location.objects.get(pk=location_id)
        parishes = get_all_parishes_in_children(selected_location)
        
        if parishes:  # Check if parishes are found
            return render(request, 'ParishRestructure/select_parish.html', {'selected_location': selected_location, 'parishes': parishes, 'locations': locations})
        else:
            messages.error(request, 'No Parish Found.') 

    # If no parish is found or if the request method is not 'POST', render the page with an error message
    return render(request, 'ParishRestructure/select_parish.html', {
        'locations': locations, 
        })

@login_required  
def edit_parish_reg(request, pk):
    parish = get_object_or_404(ParishDirectory, pk=pk)
    # parishinfo = get_object_or_404(ParishRegistration, parish=parish)
    
    if request.method == 'POST':
        parish_form = ParishDirectoryForm(request.POST, instance=parish)
        # preg_form = ParishRegForm(request.POST, instance=parish.parishregistration)
        if parish_form.is_valid(): 
            parish = parish_form.save(commit=False) 
            parish.save()

            messages.success(request, 'Parish edited successfully.')
            return redirect('all-parish')  # Redirect to success page or any other URL
        else:
            messages.error(request, 'Something went wrong, Please try again.')
    else:
        parish_form = ParishDirectoryForm(instance=parish)  # Define parish_form for non-POST requests
        
    return render(request, 'ParishRestructure/reg_parish.html', {'parish_form': parish_form})

@login_required  
def edit_parish(request, pk):
    parish = get_object_or_404(ParishRestructure, pk=pk)
    if request.method == 'POST':
        form = ParishForm(request.POST)
        if form.is_valid(): 
            parish_instance = form.save(commit=False)

            # Assuming 'location_id' is the field to save the area ID
            if 'location' in form.cleaned_data:
                parish_instance.location_id = form.cleaned_data['location'].id

            parish_instance.save()

            messages.success(request, 'Parish edited successfully.')
            return redirect('parish_dashboard')  # Redirect to success page or any other URL
        else:
            messages.error(request, 'Something went wrong, Please try again.')
    form = ParishForm(instance=parish)
    return render(request, 'ParishRestructure/edit_parish.html', {'form': form})

# Delete Parish fo all parish data table
@login_required  
def delete_parish(request, pk):
    parish = get_object_or_404(ParishDirectory, pk=pk)
    parish.delete()
    messages.success(request, 'Parish deleted successfully.')
    return redirect('parish_dashboard')

# View Parish fo all parish data table
@login_required  
def view_parish(request, pk):
    """View a single parish."""
    parish = get_object_or_404(ParishDirectory, pk=pk)
    
    return render(request, 'ParishRestructure/view_parish.html', {'parish': parish})

@login_required  
def view_parishh(request, pk):
    """View a single parish."""
    parish = get_object_or_404(ParishRestructure, pk=pk)
    
    return render(request, 'ParishRestructure/view_parish copy.html', {'parish': parish})

@login_required  
def reg_parish(request):
    parish = ParishDirectory.objects.all()
    if  request.method=='POST':
        parish_form = ParishDirectoryForm(request.POST)
        preg_form = ParishRegForm(request.POST)
        if parish_form.is_valid() and preg_form.is_valid(): 
            parish = parish_form.save()
            parish_details = preg_form.save(commit=False)
            parish_details.parish = parish
            parish_details.save()
            messages.success(request, 'Parish details has be submitted succesfully for approval.')
            return redirect('parish_dashboard')
    else:
        preg_form = ParishRegForm()
        parish_form = ParishDirectoryForm()
        
    return render(request,'ParishRestructure/reg_parish.html', {'parish_form': parish_form, 'preg_form': preg_form})

@login_required  
def edit_reg_parish(request, pk):
    
    parish = get_object_or_404(ParishRegistration, pk=pk)
    
    if request.method == 'POST':
        form = ParishRegForm1(request.POST, instance=parish)
        if form.is_valid(): 
            parish = form.save(commit=False) 
            parish.save()
            
            messages.success(request, 'Parish updated successfully.')
            return redirect('approved')  # Redirect to success page or any other URL
        else:
            messages.error(request, 'Something went wrong, Please try again.')
    else:
        form = ParishRegForm1(instance=parish)  # Define parish_form for non-POST requests
        
        
    return render(request, 'ParishRestructure/edit_regparish.html', {'form': form})


@login_required  
def regparish(request):
    if request.method == 'POST':
        preg_form = ParishRegForm1(request.POST)
        if preg_form.is_valid(): 
            parishinfo = preg_form.save(commit=False)
            parishinfo.save()
            messages.success(request, 'Parish dtails has been submitted successfully for approval.')
            return redirect('all-parish')  # Redirect to success page or any other URL
        else:
            messages.error(request, 'Something went wrong, Please try again.')
    else:
          # Define parish_form for non-POST requests
        preg_form = ParishRegForm1()  # Define parish_form for non-POST requests
        
    return render(request, 'ParishRestructure/regparish.html', {'preg_form': preg_form})


@login_required  
def all_parish(request):
    parishes = ParishDirectory.objects.all()
    return render(request, 'ParishRestructure/view_allparish.html', {'parishes': parishes})



@login_required  
def accept_parish_registration(request, pk):
    parish_registration = get_object_or_404(ParishRegistration, pk=pk)
    parish_directory = parish_registration.parish

    # Update the register_status of the related ParishDirectory object
    parish_directory.register_status = True
    parish_directory.save()

    # Update the date_approved of the ParishRegistration object
    parish_registration.date_approved = datetime.datetime.now()
    parish_registration.save()

    messages.info(request, 'Parish has been successfully registered!')
    return redirect('approved')


@login_required  
def reject_parish_registration(request, pk):
    parishinfo = get_object_or_404(ParishRegistration, pk=pk)
    parishinfo.parish.register_status = False
    parishinfo.save()
    messages.info(request, 'Parish has been sucessfully declined!')
    return redirect('parish_dashboard')


@login_required  
def approval_queue(request):
    parishes = ParishRegistration.objects.filter(date_approved=None)
    return render(request, 'ParishRestructure/approval_queue.html', {'parishes': parishes})
    

@login_required      
def approved(request):
    parishes = ParishRegistration.objects.filter(date_approved__isnull=False)
    return render(request, 'ParishRestructure/approved.html', {'parishes': parishes})


@login_required  
def view_regparish(request, pk):
    """View a single parish."""
    parish = get_object_or_404(ParishRegistration, pk=pk)
    
    return render(request, 'ParishRestructure/view_regparish.html', {'parish': parish})