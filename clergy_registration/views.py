from django.shortcuts import render, redirect
from .forms import ClergyRegistrationForm
from .models import ClergyDetails
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required




@user_passes_test(lambda u: u.groups.filter(name='Clergyadmin').exists())
@login_required
def dashboard(request):
    return render(request, 'clergy_reg/index.html')

@login_required
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
        

@login_required
def all_clergy(request):
    all_clergy = ClergyDetails.objects.all()
    return render(request, 'clergy_reg/all_clergy.html', {'all_clergy': all_clergy})


@login_required
def view_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Pass the retrieved object to the template context
    return render(request, 'clergy_reg/view_clergy.html', {'clergy': clergy})

@login_required
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
