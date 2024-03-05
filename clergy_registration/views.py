from django.shortcuts import render, redirect
from .forms import ClergyRegistrationForm
from .models import ClergyDetails
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404


# def handle_clergy_registration(request):
#     if request.method == 'POST':
#         form = ClergyRegistrationForm(request.POST)
#         if form.is_valid():
#             # Save the form data to create the first clergy instance
#             first_clergy_data = form.save(commit=False)
#             first_clergy_data.save()
            
#             # Retrieve the clergy_id of the first clergy instance
#             clergy_id = first_clergy_data.pk
            
#             # Create new clergy instances with the remaining form data and associate them with the first clergy record
#             for data in form.cleaned_data['additional_data']:
#                 new_clergy_data = ClergyDetails(clergy_id=clergy_id, additional_data=data)
#                 new_clergy_data.save()
            
#             # Redirect to a success page or another URL
#             return HttpResponseRedirect('/success/')  # Replace '/success/' with your desired success URL
#         else:
#             print(form.errors)
#     else:
#         form = ClergyRegistrationForm()
    
#     return render(request, 'clergy_reg/profile.html', {'form': form})


# def handle_clergy_registration(request):
#     if request.method == 'POST':
#         form = ClergyRegistrationForm(request.POST)
#         if form.is_valid():
#             # Save the data from the form to the database
#             form.save()

#             # Redirect to a new URL:
#             return HttpResponseRedirect('/thanks/')
#         else:
#             # The form is invalid, redisplay it
#             print(form.errors)
#     else:
#         # Render the form
#         form = ClergyRegistrationForm()
#         return render(request, 'clerg_registration/index.html', {'form': form})
# def register_clergy(request):
#     return render(request, 'clergy_reg/profile.html')

def dashboard(request):
    return render(request, 'clergy_reg/index.html')

class register_clergy(CreateView):
    def get(self, request):
        form = ClergyRegistrationForm()
        return render(request, 'clergy_reg/add_clergy.html', {'form': form})
    
    def post(self, request):
        form = ClergyRegistrationForm(request.POST)
        if form.is_valid():
            # save the form data to the ClergyDetails model
            clergy_data = form.save(commit=False)
            clergy_data.save()
            # redirect user to their profile page
            return redirect('dashboard')
        else:
            print(form.errors)
            return render(request, 'clergy_reg/add_clergy.html', {'form': form})
        
def all_clergy(request):
    all_clergy = ClergyDetails.objects.all()
    return render(request, 'clergy_reg/all_clergy.html', {'all_clergy': all_clergy})


def view_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Pass the retrieved object to the template context
    return render(request, 'clergy_reg/view_clergy.html', {'clergy': clergy})

def edit_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Create a form instance with the retrieved object
    form = ClergyRegistrationForm(instance=clergy)
    
    # Check if the form has been submitted
    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = ClergyRegistrationForm(request.POST, request.FILES, instance=clergy)
        
        # Check if the form is valid
        if form.is_valid():
            # Save the form data to the database
            clergy_data = form.save(commit=False)
            clergy_data.save()
            
            # Redirect to a new URL:
            return redirect('all_clergy')
        else:
            # The form is invalid, redisplay it
            print(form.errors)
    
    # Render the form
    return render(request, 'clergy_reg/edit_clergy.html', {'clergy': clergy, 'form': form})

def delete_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Delete the clergy object
    clergy.delete()
    
    # Redirect to a new URL:
    return redirect('all_clergy')
