from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClergyRegistrationForm, AnnointmentForm
from .models import ClergyDetails, AnnointmentGazzette
from django.http import HttpResponseRedirect, JsonResponse
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
    result = user.groups.filter(name='clergyadmin').exists() or user.is_superuser
    print(f"DEBUG: is_clergy_admin for user {user.username if user.is_authenticated else 'Anonymous'}: {result}")
    return result

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
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.core.cache import cache
    import time
    import json

    start_time = time.time()  # Performance monitoring

    # Check if this is a DataTables AJAX request
    if request.GET.get('draw'):
        return all_clergy_datatables(request)

    # Get page number and size from request
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 25)

    try:
        page_size = int(page_size)
        if page_size < 1 or page_size > 100:
            page_size = 25
    except ValueError:
        page_size = 25

    # Create cache key for statistics
    cache_key = f'clergy_stats_{page_size}'
    cached_stats = cache.get(cache_key)

    if cached_stats:
        context = cached_stats.copy()
        # Update pagination-specific data
        context.update({
            'search_query': request.GET.get('search', '').strip(),
            'status_filter': request.GET.get('status', '').strip(),
            'page_size': page_size,
        })
    else:
        # Get all clergy with optimized query - only select needed fields
        all_clergy_qs = ClergyDetails.objects.only(
            'clergy_id', 'first_name', 'middle_name', 'last_name', 'reg_number',
            'gender', 'email_address', 'telephone', 'parish', 'nationality'
        ).order_by('-clergy_id')

        # Get total count for statistics
        total_clergy = all_clergy_qs.count()

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

        # Cache the statistics for 5 minutes
        cached_stats = {
            'total_count': total_clergy,
            'active_count': total_clergy,
            'recent_count': 10,  # Approximate
            'male_count': male_count,
            'female_count': female_count,
            'nationality_stats': list(nationality_stats),  # Convert to list for caching
        }
        cache.set(cache_key, cached_stats, 300)  # 5 minutes

        context = cached_stats.copy()

    # Apply search and status filters (these can't be cached)
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Get filtered queryset
    filtered_qs = ClergyDetails.objects.only(
        'clergy_id', 'first_name', 'middle_name', 'last_name', 'reg_number',
        'gender', 'email_address', 'telephone', 'parish', 'nationality'
    ).order_by('-clergy_id')

    if search_query:
        filtered_qs = filtered_qs.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(reg_number__icontains=search_query) |
            Q(email_address__icontains=search_query) |
            Q(telephone__icontains=search_query)
        )

    if status_filter:
        pass  # Add status filtering logic if needed

    # Create paginator with filtered queryset
    paginator = Paginator(filtered_qs, page_size)

    try:
        clergy_page = paginator.page(page)
    except PageNotAnInteger:
        clergy_page = paginator.page(1)
    except EmptyPage:
        clergy_page = paginator.page(paginator.num_pages)

    # Update context with pagination and filter data
    context.update({
        'all_clergy': clergy_page,
        'paginator': paginator,
        'page_obj': clergy_page,
        'is_paginated': paginator.num_pages > 1,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_size': page_size,
        'page_title': 'Clergy Directory',
        'page_subtitle': f'Comprehensive list of all registered clergy members (Page {clergy_page.number} of {paginator.num_pages})',
        'add_new_url': reverse('register_clergy'),
        'add_new_text': 'Register New Clergy',
        'table_icon': 'fas fa-users',
        'table_card_title': 'Clergy Members',
        'load_time': round(time.time() - start_time, 2),  # Performance metric
    })

    return render(request, 'clergy_reg/all_clergy_new.html', context)


def all_clergy_datatables(request):
    """
    Handle DataTables server-side processing for clergy data.
    """
    from django.db.models import Q
    import json

    # DataTables parameters
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '').strip()

    # Column ordering
    order_column_index = int(request.GET.get('order[0][column]', 0))
    order_direction = request.GET.get('order[0][dir]', 'desc')

    # Map column index to field name
    column_mapping = {
        0: 'clergy_id',  # Checkbox column (not sortable)
        1: 'first_name',  # Name
        2: 'reg_number',  # Registration No
        3: 'email_address',  # Email
        4: 'telephone',  # Mobile
        5: 'clergy_id',  # Rank (using clergy_id for now)
    }

    order_field = column_mapping.get(order_column_index, 'clergy_id')

    # Base queryset
    queryset = ClergyDetails.objects.only(
        'clergy_id', 'first_name', 'middle_name', 'last_name', 'reg_number',
        'gender', 'email_address', 'telephone', 'parish', 'nationality',
        'profile_picture', 'present_annointment'
    )

    # Apply search filter
    if search_value:
        queryset = queryset.filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(reg_number__icontains=search_value) |
            Q(email_address__icontains=search_value) |
            Q(telephone__icontains=search_value)
        )

    # Get total records count (before filtering)
    total_records = ClergyDetails.objects.count()

    # Get filtered records count
    records_filtered = queryset.count()

    # Apply ordering
    if order_direction == 'desc':
        queryset = queryset.order_by(f'-{order_field}')
    else:
        queryset = queryset.order_by(order_field)

    # Apply pagination
    queryset = queryset[start:start + length]

    # Prepare data for DataTables (array format for server-side processing)
    data = []
    for clergy in queryset:
        # Get latest appointment for rank
        latest_appointment = clergy.annointmentgazzette_set.first()
        rank = latest_appointment.rank if latest_appointment else getattr(clergy, 'present_annointment', 'N/A')

        # Create row data in array format for DataTables
        row = [
            f'<div class="form-check"><input class="form-check-input row-checkbox" type="checkbox" value="{clergy.clergy_id}" id="check-{clergy.clergy_id}"></div>',  # checkbox
            f'''
                <div class="d-flex align-items-center">
                    <div class="avatar-wrapper me-3">
                        {'<img class="rounded-circle avatar-sm" src="' + clergy.profile_picture.url + f'" alt="{clergy}" style="width: 40px; height: 40px; object-fit: cover;">' if clergy.profile_picture else '<div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center avatar-sm" style="width: 40px; height: 40px;"><i class="fas fa-user"></i></div>'}
                    </div>
                    <div>
                        <div class="fw-semibold text-dark">{clergy}</div>
                        <small class="text-muted">{clergy.gender or "--"}</small>
                    </div>
                </div>
            ''',  # name
            clergy.reg_number or '',  # reg_number
            f'<a href="mailto:{clergy.email_address}" class="text-decoration-none">{clergy.email_address}</a>' if clergy.email_address else '',  # email
            f'<a href="tel:{clergy.telephone}" class="text-decoration-none">{clergy.telephone}</a>' if clergy.telephone else '',  # mobile
            f'<span class="badge bg-success">{rank}</span>',  # rank
            f'''
                <div class="action-buttons d-flex justify-content-center align-items-center gap-1">
                    <a href="/clergy/view_clergy/{clergy.clergy_id}/" class="btn btn-xs btn-outline-primary" title="View Profile" data-bs-toggle="tooltip">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="/clergy/edit_clergy/{clergy.clergy_id}/" class="btn btn-xs btn-outline-success" title="Edit Clergy" data-bs-toggle="tooltip">
                        <i class="fas fa-edit"></i>
                    </a>
                    <a href="/clergy/view-and-add-annointment/{clergy.clergy_id}/" class="btn btn-xs btn-outline-info" title="View Appointments" data-bs-toggle="tooltip">
                        <i class="fas fa-crown"></i>
                    </a>
                    <a href="/clergy/generate_clergy_pdf/{clergy.clergy_id}/" class="btn btn-xs btn-outline-secondary" title="Download PDF" data-bs-toggle="tooltip" target="_blank">
                        <i class="fas fa-download"></i>
                    </a>
                </div>
            '''  # actions
        ]
        data.append(row)

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': records_filtered,
        'data': data
    }

    return JsonResponse(response)


@login_required
def view_clergy(request, id):
    # Retrieve the ClergyDetails object based on the clergy_id
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)
    
    # Calculate age from date of birth
    from datetime import date
    today = date.today()
    if clergy.dob:
        age = today.year - clergy.dob.year - ((today.month, today.day) < (clergy.dob.month, clergy.dob.day))
    else:
        age = None
    
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
            'Date of Birth': clergy.dob.strftime('%B %d, %Y') if clergy.dob else 'N/A',
            'Age': f"{age} years old" if age is not None else 'N/A',
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
            'Entry Date in CCC': clergy.entry_date_in_ccc.strftime('%B %d, %Y') if clergy.entry_date_in_ccc else 'N/A',
            'First Parish': clergy.first_parish,
            'Former Religion': clergy.former_religion or 'N/A',
            'Denomination': clergy.denomination or 'N/A',
            'Status in Former Religion': clergy.status_former_religion or 'N/A',
        },
        
        # Baptism Information Section
        'baptism_info': {
            'Date When Baptized': clergy.date_when_baptized.strftime('%B %d, %Y') if clergy.date_when_baptized else 'N/A',
            'Parish Where Baptized': clergy.parish_where_baptized,
            'Shepherd Who Baptized': clergy.shepherd_who_baptized_you,
            'Shepherd Who Sanctified': clergy.shepherd_who_sanctified_you,
        },
        
        # Appointment Information Section
        'appointment_info': {
            'First Appointment': clergy.get_first_annointment_display(),
            'Date of First Appointment': clergy.date_of_first_annointment.strftime('%B %d, %Y') if clergy.date_of_first_annointment else 'N/A',
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
        if not request.user.is_superuser and not request.user.groups.filter(name='clergyadmin').exists():
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

    # Check if profile picture exists before getting URL
    if clergy.profile_picture and clergy.profile_picture.name:
        profile_picture_url = request.build_absolute_uri(clergy.profile_picture.url)
    else:
        profile_picture_url = None

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