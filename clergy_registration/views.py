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
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get all clergy
    all_clergy_qs = ClergyDetails.objects.all()
    
    # Calculate statistics
    total_clergy = all_clergy_qs.count()
    
    # Get recent registrations (last 30 days) - using id as proxy for recent since no created_at field
    recent_cutoff = all_clergy_qs.order_by('-clergy_id')[:10] if all_clergy_qs.exists() else all_clergy_qs.none()
    recent_registrations = recent_cutoff.count()
    
    # Count by rank (using rank field from AnnointmentGazzette through relationship)
    rank_counts = AnnointmentGazzette.objects.values('rank').annotate(count=Count('rank'))
    
    # Create rank statistics with available ranks
    bishop_count = 0
    pastor_count = 0
    evangelist_count = 0
    deacon_count = 0
    
    for rank_data in rank_counts:
        rank = rank_data['rank'].lower() if rank_data['rank'] else ''
        count = rank_data['count']
        
        if 'bishop' in rank or 'pastor' in rank or 'leader' in rank:
            pastor_count += count
        elif 'evangelist' in rank or 'evang' in rank:
            evangelist_count += count
        elif 'elder' in rank:
            deacon_count += count
    
    # Get recent clergy for table display with their ranks
    recent_clergy = all_clergy_qs.order_by('-clergy_id')[:5]
    
    # Add rank information to each clergy member
    for clergy in recent_clergy:
        # Get the most recent annointment for this clergy
        latest_annointment = AnnointmentGazzette.objects.filter(clergy=clergy).order_by('-year_of_annointment', '-month_of_annointment').first()
        clergy.rank = latest_annointment.rank if latest_annointment else 'Not Set'
    
    # Prepare context data
    context = {
        'total_clergy': total_clergy,
        'active_clergy': total_clergy,  # Since there's no is_active field, assume all are active
        'recent_registrations': recent_registrations,
        'ordained_clergy': total_clergy,  # Since there's no ordination tracking, assume all are ordained
        'recent_clergy': recent_clergy,
        'bishop_count': bishop_count,
        'pastor_count': pastor_count,
        'evangelist_count': evangelist_count,
        'deacon_count': deacon_count,
        'chart_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'chart_data': [5, 10, 8, 12, 15, 18],  # Sample data for chart
        'recent_actions': [
            {
                'title': 'New Clergy Registered',
                'description': 'Latest clergy member added to system',
                'timestamp': datetime.now() - timedelta(hours=2),
                'icon': 'fas fa-user-plus',
                'icon_bg': 'bg-success'
            }
        ] if total_clergy > 0 else []
    }
    
    return render(request, 'clergy_reg/dashboard_new.html', context)

@login_required
@user_passes_test(is_clergy_admin)
def register_clergy(request):
    if request.method == 'POST':
        form = ClergyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # save the form data to the ClergyDetails model
            clergy_data = form.save(commit=False)
            clergy_data.save()
            
            # Add success message
            messages.success(
                request, 
                f'Clergy registration for {clergy_data.first_name} {clergy_data.last_name} completed successfully!'
            )
            
            # redirect user to dashboard
            return redirect('dashboard')
        else:
            # Add error message
            messages.error(
                request, 
                'There were errors in your form. Please check the highlighted fields and try again.'
            )
            print(form.errors)
            return render(request, 'clergy_reg/add_clergy_new.html', {'form': form})
    else:
        form = ClergyRegistrationForm()
        return render(request, 'clergy_reg/add_clergy_new.html', {'form': form})

        

@login_required
def all_clergy(request):
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get all clergy with optimized query
    all_clergy_qs = ClergyDetails.objects.select_related().all()
    
    # Apply search filter if provided
    search_query = request.GET.get('search', '').strip()
    if search_query:
        all_clergy_qs = all_clergy_qs.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(reg_number__icontains=search_query) |
            Q(email_address__icontains=search_query) |
            Q(telephone__icontains=search_query)
        )
    
    # Apply status filter if provided
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        # Assuming we might add an is_active field later, for now show all
        pass
    
    # Get statistics
    total_clergy = all_clergy_qs.count()
    
    # Get recent registrations (last 30 days) - using id as proxy for recent since no created_at field
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_clergy = all_clergy_qs.order_by('-clergy_id')[:10]
    recent_count = recent_clergy.count()
    
    # Get active clergy count (assuming all are active for now)
    active_count = total_clergy
    
    # Get clergy by gender statistics
    gender_stats = all_clergy_qs.values('gender').annotate(count=Count('gender'))
    male_count = 0
    female_count = 0
    for stat in gender_stats:
        if stat['gender'] == 'Male':
            male_count = stat['count']
        elif stat['gender'] == 'Female':
            female_count = stat['count']
    
    # Get top nationalities
    nationality_stats = all_clergy_qs.values('nationality').annotate(count=Count('nationality')).order_by('-count')[:5]
    
    # Prepare context data
    context = {
        'all_clergy': all_clergy_qs,
        'total_count': total_clergy,
        'active_count': active_count,
        'recent_count': recent_count,
        'male_count': male_count,
        'female_count': female_count,
        'nationality_stats': nationality_stats,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Clergy Directory',
        'page_subtitle': 'Comprehensive list of all registered clergy members',
        'add_new_url': reverse('register_clergy'),
        'add_new_text': 'Register New Clergy',
        'table_icon': 'fas fa-users',
        'table_card_title': 'Clergy Members',
    }
    
    return render(request, 'clergy_reg/all_clergy_new.html', context)


@login_required
def view_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Calculate age from date of birth
    from datetime import date
    today = date.today()
    age = today.year - clergy.dob.year - ((today.month, today.day) < (clergy.dob.month, clergy.dob.day))
    
    # Get related annointments
    annointments = AnnointmentGazzette.objects.filter(clergy=clergy).order_by('-year_of_annointment', '-month_of_annointment')
    
    # Prepare context data with organized sections
    context = {
        'clergy': clergy,
        'age': age,
        'annointments': annointments,
        
        # Page metadata
        'page_title': f'Clergy Details - {clergy.first_name} {clergy.last_name}',
        'page_subtitle': f'Comprehensive profile information for {clergy.get_full_name()}',
        
        # Personal Information Section
        'personal_info': {
            'Full Name': f"{clergy.first_name} {clergy.middle_name} {clergy.last_name}",
            'Alias': clergy.alias or 'N/A',
            'Gender': clergy.get_gender_display(),
            'Date of Birth': clergy.dob.strftime('%B %d, %Y'),
            'Age': f"{age} years old",
            'Marital Status': clergy.get_marital_status_display(),
            'Nationality': clergy.get_nationality_display(),
            'State of Origin': clergy.state_of_origin,
            'LGA (if Nigerian)': clergy.lga_if_nigerian or 'N/A',
        },
        
        # Contact Information Section
        'contact_info': {
            'Telephone': str(clergy.telephone) if clergy.telephone else 'N/A',
            'Email Address': clergy.email_address,
            'Permanent Address': clergy.permanent_address,
            'Resident Address': clergy.resident_address,
        },
        
        # Parish Information Section
        'parish_info': {
            'Current Parish': clergy.parish,
            'Parish Address': clergy.parish_address,
        },
        
        # Health Information Section
        'health_info': {
            'Blood Group': clergy.get_blood_group_display() or 'N/A',
            'Genotype': clergy.get_genotype_display() or 'N/A',
            'Any Ailment': clergy.get_any_ailment_display() or 'N/A',
            'Ailment Details': clergy.ailment or 'N/A',
            'Any Disabilities': clergy.get_any_disabilities_display() or 'N/A',
            'Disability Details': clergy.disability or 'N/A',
        },
        
        # Religious Information Section
        'religious_info': {
            'Registration Number': clergy.reg_number,
            'Training Number': clergy.trg_number,
            'Entry Date in CCC': clergy.entry_date_in_ccc.strftime('%B %d, %Y'),
            'First Parish': clergy.first_parish,
            'Former Religion': clergy.former_religion or 'N/A',
            'Denomination': clergy.denomination or 'N/A',
            'Status in Former Religion': clergy.status_former_religion or 'N/A',
        },
        
        # Baptism Information Section
        'baptism_info': {
            'Date When Baptized': clergy.date_when_baptized.strftime('%B %d, %Y'),
            'Parish Where Baptized': clergy.parish_where_baptized,
            'Shepherd Who Baptized': clergy.shepherd_who_baptized_you,
            'Shepherd Who Sanctified': clergy.shepherd_who_sanctified_you,
        },
        
        # Appointment Information Section
        'appointment_info': {
            'First Appointment': clergy.get_first_annointment_display(),
            'Date of First Appointment': clergy.date_of_first_annointment.strftime('%B %d, %Y'),
            'Present Appointment': clergy.get_present_annointment_display() or 'N/A',
            'Date of Present Appointment': clergy.date_of_present_annointment.strftime('%B %d, %Y') if clergy.date_of_present_annointment else 'N/A',
        },
        
        # Education Information Section
        'education_info': {
            'Education Level': ', '.join(clergy.edu_level) if clergy.edu_level else 'N/A',
            'Education Qualification': ', '.join(clergy.edu_qualification) if clergy.edu_qualification else 'N/A',
            'Apprenticeship': clergy.apprenticeship,
        },
        
        # Other Information Section
        'other_info': {
            'Spoken Languages': ', '.join(clergy.spoken_languages) if clergy.spoken_languages else 'N/A',
            'Hobbies': clergy.hobbies,
            'Area of Calling': ', '.join(clergy.area_of_calling) if clergy.area_of_calling else 'N/A',
            'Working Experience': clergy.get_working_experience_option_display(),
            'Work Experience Details': clergy.work_experience_ifyes or 'N/A',
        },
        
        # Family Information Section
        'family_info': {
            'Spouse': clergy.spouse,
            'Father': clergy.father,
            'Mother': clergy.mother,
            'Next of Kin': clergy.next_of_kin,
            'Relation in CCC': clergy.relation_in_ccc,
            'Children Information': clergy.children_info,
        },
        
        # Action URLs
        'edit_url': reverse('edit_clergy_new', kwargs={'id': clergy.clergy_id}),
        'delete_url': reverse('delete_clergy', kwargs={'id': clergy.clergy_id}),
        'pdf_url': reverse('generate_clergy_pdf', kwargs={'id': clergy.clergy_id}),
        'annointments_url': reverse('view-and-add-annointment', kwargs={'id': clergy.clergy_id}),
        'back_url': reverse('all_clergy'),
    }
    
    return render(request, 'clergy_reg/view_clergy_new.html', context)

@login_required
@user_passes_test(is_clergy_admin)
def edit_clergy(request, id):
    """
    Edit clergy details with comprehensive error handling and validation.
    
    Args:
        request: HTTP request object
        id: Clergy ID to edit
        
    Returns:
        Rendered template with form or redirect on success
    """
    try:
        # Retrieve the ClergyDetails object
        clergy = get_object_or_404(ClergyDetails, clergy_id=id)
        
        # Check if user has permission to edit this clergy
        if not request.user.is_superuser and not request.user.groups.filter(name='Clergyadmin').exists():
            messages.error(request, 'You do not have permission to edit clergy details.')
            return redirect('dashboard')
        
        # Create form instance
        if request.method == 'POST':
            form = ClergyRegistrationForm(request.POST, request.FILES, instance=clergy)
            
            if form.is_valid():
                try:
                    # Save the form data
                    clergy_data = form.save(commit=False)
                    clergy_data.save()
                    
                    # Log the successful update
                    messages.success(request, f'Clergy details for {clergy.get_full_name()} have been updated successfully.')
                    
                    # Redirect to view page or all clergy list
                    return redirect('view_clergy', id=clergy.clergy_id)
                    
                except Exception as e:
                    # Handle database save errors
                    messages.error(request, f'Error saving clergy details: {str(e)}')
            else:
                # Form validation errors
                messages.error(request, 'Please correct the errors below.')
        else:
            # GET request - create form with existing data
            form = ClergyRegistrationForm(instance=clergy)
        
        # Context data
        context = {
            'clergy': clergy,
            'form': form,
            'page_title': f'Edit Clergy - {clergy.get_full_name()}',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'dashboard'},
                {'title': 'All Clergy', 'url': 'all_clergy'},
                {'title': f'Edit {clergy.get_full_name()}', 'url': None}
            ]
        }
        
        return render(request, 'clergy_reg/edit_clergy_new.html', context)
        
    except ClergyDetails.DoesNotExist:
        messages.error(request, 'Clergy member not found.')
        return redirect('all_clergy')
        
    except Exception as e:
        # General exception handling
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return redirect('all_clergy')

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


@login_required
def view_and_add_annointment(request, id):
    """
    View and manage annointment records for a clergy member.

    This view handles both displaying existing annointment records and
    adding new annointment details for a specific clergy member.

    Args:
        request: HTTP request object
        id: Clergy ID (clergy_id field)

    Returns:
        Rendered template with clergy details, annointment history, and form

    Raises:
        Http404: If clergy member is not found
        Exception: For database or form processing errors
    """
    try:
        # Get clergy details with error handling
        try:
            clergy = get_object_or_404(ClergyDetails, clergy_id=id)
        except Exception as e:
            messages.error(request, f'Error retrieving clergy details: {str(e)}')
            return redirect('all_clergy')

        if request.method == 'POST':
            try:
                # Process the annointment form
                annform = AnnointmentForm(request.POST, request.FILES)

                if annform.is_valid():
                    try:
                        # Save the annointment details
                        anninfo = annform.save(commit=False)
                        anninfo.clergy = clergy  # Associate with clergy
                        anninfo.save()

                        # Log successful addition
                        messages.success(
                            request,
                            f'Annointment record for {clergy.first_name} {clergy.last_name} '
                            f'added successfully as {anninfo.rank}.'
                        )

                        # Redirect to the same page to show updated list
                        return redirect('view-and-add-annointment', id=id)

                    except Exception as e:
                        # Database save error
                        messages.error(
                            request,
                            f'Failed to save annointment record: {str(e)}. Please try again.'
                        )
                else:
                    # Form validation errors
                    error_messages = []
                    for field, errors in annform.errors.items():
                        for error in errors:
                            error_messages.append(f"{field.replace('_', ' ').title()}: {error}")

                    if error_messages:
                        messages.error(
                            request,
                            f'Please correct the following errors: {" ".join(error_messages)}'
                        )
                    else:
                        messages.error(request, 'Please check all required fields and try again.')

            except Exception as e:
                # General form processing error
                messages.error(request, f'An error occurred while processing the form: {str(e)}')

        else:
            # GET request - initialize empty form
            try:
                annform = AnnointmentForm(initial={'clergy': clergy})
            except Exception as e:
                messages.warning(request, f'Warning: Could not initialize form properly: {str(e)}')
                annform = AnnointmentForm()

        # Retrieve annointment history with error handling
        try:
            annointments = AnnointmentGazzette.objects.filter(
                clergy=clergy
            ).order_by('-year_of_annointment', '-month_of_annointment')
        except Exception as e:
            messages.warning(request, f'Could not retrieve annointment history: {str(e)}')
            annointments = []

        # Prepare context data
        context = {
            'clergy': clergy,
            'annointments': annointments,
            'annform': annform,
            'page_title': f'Annointment Gazette - {clergy.first_name} {clergy.last_name}',
            'total_annointments': len(annointments),
            'current_rank': annointments.first().rank if annointments.exists() else 'No annointments',
            'last_annointment_year': annointments.first().year_of_annointment if annointments.exists() else None,
        }

        # Render the template
        return render(request, 'clergy_reg/view_annointment_new.html', context)

    except Exception as e:
        # Catch-all exception handler
        messages.error(
            request,
            f'An unexpected error occurred: {str(e)}. Please contact support if this persists.'
        )
        return redirect('all_clergy')


def generate_clergy_pdf(request, id):
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    profile_picture_url = request.build_absolute_uri(clergy.profile_picture.url)
    html_content = render_to_string('clergy_reg/clergy_report.html', {'clergy': clergy, 'profile_picture': profile_picture_url})
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{clergy.first_name}_{clergy.last_name}_profile.pdf"'
    return response


@login_required
@user_passes_test(is_clergy_admin)
@login_required
def clergy_report(request):
    """Generate comprehensive clergy reports"""
    from django.db.models import Count
    
    # Get all clergy
    all_clergy = ClergyDetails.objects.all()
    
    # Add rank information to each clergy member
    for clergy in all_clergy:
        # Get the most recent annointment for this clergy
        latest_annointment = AnnointmentGazzette.objects.filter(clergy=clergy).order_by('-year_of_annointment', '-month_of_annointment').first()
        clergy.rank = latest_annointment.rank if latest_annointment else None
    
    # Statistics for report
    total_clergy = all_clergy.count()
    
    # Group by gender
    gender_stats = all_clergy.values('gender').annotate(count=Count('gender'))
    
    # Group by nationality  
    nationality_stats = all_clergy.values('nationality').annotate(count=Count('nationality')).order_by('-count')[:10]
    
    # Group by rank (using rank field from AnnointmentGazzette through relationship)
    rank_stats = AnnointmentGazzette.objects.values('rank').annotate(count=Count('rank')).order_by('-count')
    
    context = {
        'total_clergy': total_clergy,
        'all_clergy': all_clergy,
        'gender_stats': gender_stats,
        'nationality_stats': nationality_stats,
        'rank_stats': rank_stats,
    }
    
    return render(request, 'clergy_reg/reports.html', context)