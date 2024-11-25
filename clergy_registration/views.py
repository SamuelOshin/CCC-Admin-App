from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClergyRegistrationForm, AnnointmentForm
from .models import ClergyDetails, AnnointmentGazzette
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
# from xhtml2pdf import pisa
from .models import ClergyDetails




def is_clergy_admin(user):
    return user.groups.filter(name='Clergyadmin').exists() or user.is_superuser

@user_passes_test(is_clergy_admin)
@login_required
def dashboard(request):
    return render(request, 'clergy_reg/index.html')

@login_required
def register_clergy(request):
    if request.method == 'POST':
        form = ClergyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # save the form data to the ClergyDetails model
            clergy_data = form.save(commit=False)
            clergy_data.save()
            # redirect user to their profile page
            return redirect('dashboard')
        else:
            print(form.errors)
            return render(request, 'clergy_reg/add_clergy.html', {'form': form})
    else:
        form = ClergyRegistrationForm()
        return render(request, 'clergy_reg/add_clergy.html', {'form': form})

        

@login_required
def all_clergy(request):
    all_clergy = ClergyDetails.objects.all()
    return render(request, 'clergy_reg/all_clergy.html', {'all_clergy': all_clergy})


@login_required
def view_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    form = ClergyRegistrationForm(instance=clergy)
    
    # Pass the retrieved object to the template context
    return render(request, 'clergy_reg/view_clergy.html', {'clergy': clergy, 'form': form})

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


def view_profile(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    form = ClergyRegistrationForm(instance=clergy)
    
    # Pass the retrieved object to the template context
    return render(request, 'clergy_reg/profile.html', {'clergy': clergy, 'form': form})


def view_and_add_annointment(request, id):
    # Get clergy details
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    if request.method == 'POST':
        # If it's a POST request, handle the form submission
        annform = AnnointmentForm(request.POST, request.FILES)
        if annform.is_valid():
            # Save the annointment details
            anninfo = annform.save(commit=False)
            anninfo.clergy = clergy  # Associate the annointment with the clergy
            anninfo.save()
            messages.success(request, 'Annointment Detail added Successfully.')
            return redirect('view-and-add-annointment', id=id)  # Redirect to the same page after successful submission
        else:
            # If form is not valid, show error messages
            messages.error(request, 'Something went wrong, Please try again.')
    else:
        # If it's a GET request, display the annointment details and form
        annform = AnnointmentForm(initial={'clergy': clergy})
    
    # Get all the annointments associated with the clergy
    annointments = AnnointmentGazzette.objects.filter(clergy=clergy)
    

    context = {
        'clergy': clergy,
        'annointments': annointments,
        'annform': annform,
    }
    
    return render(request, 'AnnointmentGazzette/view_ann.html', context)


def generate_clergy_pdf(request, id):
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    profile_picture_url = request.build_absolute_uri(clergy.profile_picture.url)
    html_content = render_to_string('clergy_reg/clergy_report.html', {'clergy': clergy, 'profile_picture': profile_picture_url})
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{clergy.first_name}_{clergy.last_name}_profile.pdf"'
    return response