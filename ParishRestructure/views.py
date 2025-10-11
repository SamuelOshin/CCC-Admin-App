from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import *
from .forms import ParishForm, LocationForm, ParishRegForm, ParishDirectoryForm, ParishRegForm1
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
import logging
import json
import csv
from django.db.models.functions import TruncMonth
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import Http404

# Set up logger
logger = logging.getLogger(__name__)
#api
from rest_framework import viewsets
from .serializers import ParishDirectorySerializer
import datetime

# Setup logger
logger = logging.getLogger(__name__)
from django.http import Http404
from django.db import IntegrityError
from django.core.exceptions import ValidationError

#api
class ParishDirectoryViewSet(viewsets.ModelViewSet):
    queryset = ParishDirectory.objects.all()
    serializer_class = ParishDirectorySerializer
#endapi    
@login_required    
def restructure_parish(request):
    """
    Handle parish restructuring form submission and display.
    
    This view manages the creation of ParishRestructure instances,
    including form validation, error handling, and user feedback.
    """
    try:
        # Calculate dashboard statistics
        try:
            from transfer.models import TransferData
            pending_transfers = TransferData.objects.filter(trf_status='Pending').count()
        except ImportError:
            pending_transfers = 0
            
        total_parishes = ParishDirectory.objects.count()
        recent_registrations = ParishRegistration.objects.filter(date_applied__gte=timezone.now() - timedelta(days=30)).count()
        
        stats = {
            'total_parishes': total_parishes,
            'pending_transfers': pending_transfers,
            'recent_registrations': recent_registrations,
        }
        
        if request.method == 'POST':
            form = ParishForm(request.POST)
            if form.is_valid():
                try:
                    parish_instance = form.save(commit=False)
                    
                    # Determine the appropriate location based on form hierarchy
                    location = None
                    if form.cleaned_data.get('zone'):
                        location = form.cleaned_data['zone']
                    elif form.cleaned_data.get('district'):
                        location = form.cleaned_data['district']
                    elif form.cleaned_data.get('area'):
                        location = form.cleaned_data['area']
                    elif form.cleaned_data.get('division'):
                        location = form.cleaned_data['division']
                    elif form.cleaned_data.get('state'):
                        location = form.cleaned_data['state']
                    elif form.cleaned_data.get('region'):
                        location = form.cleaned_data['region']
                    elif form.cleaned_data.get('diocese'):
                        location = form.cleaned_data['diocese']
                    
                    if location:
                        parish_instance.location = location
                    else:
                        messages.error(request, 'Please select at least a diocese for the parish location.')
                        return render(request, 'ParishRestructure/restructure.html', {'form': form, 'stats': stats})
                    
                    parish_instance.save()
                    messages.success(request, f'Parish "{parish_instance.parish.name}" has been successfully restructured.')
                    logger.info(f'Parish restructured: {parish_instance.parish.name} by user {request.user.username}')
                    return redirect('parish_dashboard')
                    
                except Exception as e:
                    logger.error(f'Error saving parish restructure: {str(e)}', exc_info=True)
                    messages.error(request, 'An error occurred while saving the parish restructure. Please try again.')
                    return render(request, 'ParishRestructure/restructure.html', {'form': form, 'stats': stats})
            else:
                messages.error(request, 'Please correct the errors below and try again.')
        else:
            form = ParishForm()
            
    except Exception as e:
        logger.error(f'Unexpected error in restructure_parish view: {str(e)}', exc_info=True)
        messages.error(request, 'An unexpected error occurred. Please contact support if this persists.')
        form = ParishForm()
        stats = {
            'total_parishes': 0,
            'pending_transfers': 0,
            'recent_registrations': 0,
        }
    
    return render(request, 'ParishRestructure/restructure.html', {'form': form, 'stats': stats})


@login_required  
def get_regions_and_areas(request):
    if request.method == 'GET':
        diocese_id = request.GET.get('diocese_id')  # Extract diocese ID from query parameters
        region_id = request.GET.get('region_id')    # Extract region ID from query parameters
        state_id = request.GET.get('state_id')      # Extract state ID from query parameters
        division_id = request.GET.get('division_id') # Extract division ID from query parameters
        subdivision_id = request.GET.get('subdivision_id') # Extract subdivision ID from query parameters
        area_id = request.GET.get('area_id')        # Extract area ID from query parameters
        district_id = request.GET.get('district_id') # Extract district ID from query parameters

        # Initialize empty lists for regions, states, divisions, subdivisions, areas, districts, and zones
        regions = []
        states = []
        divisions = []
        subdivisions = []
        areas = []
        districts = []
        zones = []

        # Fetch regions for the selected diocese if diocese_id is provided and not empty
        if diocese_id and diocese_id.strip():
            try:
                regions = Location.objects.filter(parent_id=int(diocese_id), level='region')
            except (ValueError, TypeError):
                regions = []

        # Fetch states for the selected region if region_id is provided and not empty
        if region_id and region_id.strip():
            try:
                states = Location.objects.filter(parent_id=int(region_id), level='state')
            except (ValueError, TypeError):
                states = []

        # Fetch divisions for the selected state if state_id is provided and not empty
        if state_id and state_id.strip():
            try:
                divisions = Location.objects.filter(parent_id=int(state_id), level='division')
            except (ValueError, TypeError):
                divisions = []

        # Fetch subdivisions for the selected division if division_id is provided and not empty
        if division_id and division_id.strip():
            try:
                subdivisions = Location.objects.filter(parent_id=int(division_id), level='subdivision')
            except (ValueError, TypeError):
                subdivisions = []

        # Fetch areas for the selected subdivision if subdivision_id is provided and not empty
        if subdivision_id and subdivision_id.strip():
            try:
                areas = Location.objects.filter(parent_id=int(subdivision_id), level='area')
            except (ValueError, TypeError):
                areas = []

        # Fetch districts for the selected area if area_id is provided and not empty
        if area_id and area_id.strip():
            try:
                districts = Location.objects.filter(parent_id=int(area_id), level='district')
            except (ValueError, TypeError):
                districts = []

        # Fetch zones for the selected district if district_id is provided and not empty
        if district_id and district_id.strip():
            try:
                zones = Location.objects.filter(parent_id=int(district_id), level='zone')
            except (ValueError, TypeError):
                zones = []

        # Serialize regions, states, divisions, subdivisions, areas, districts, and zones data
        serialized_regions = [{'id': region.id, 'name': region.name} for region in regions]
        serialized_states = [{'id': state.id, 'name': state.name} for state in states]
        serialized_divisions = [{'id': division.id, 'name': division.name} for division in divisions]
        serialized_subdivisions = [{'id': subdivision.id, 'name': subdivision.name} for subdivision in subdivisions]
        serialized_areas = [{'id': area.id, 'name': area.name} for area in areas]
        serialized_districts = [{'id': district.id, 'name': district.name} for district in districts]
        serialized_zones = [{'id': zone.id, 'name': zone.name} for zone in zones]

        # Return JSON response with all location data
        return JsonResponse({
            'regions': serialized_regions, 
            'states': serialized_states,
            'divisions': serialized_divisions,
            'subdivisions': serialized_subdivisions,
            'areas': serialized_areas,
            'districts': serialized_districts,
            'zones': serialized_zones
        })


def determine_location_from_hierarchy(form_data):
    """
    Determine the most specific location from the form hierarchy.

    This function takes form cleaned_data and returns the most specific
    location object based on the hierarchy: zone > district > area > division > state > region > diocese

    Args:
        form_data (dict): Cleaned form data containing location fields

    Returns:
        Location or None: The most specific location object, or None if no location is found
    """
    try:
        # Check hierarchy from most specific to least specific
        if form_data.get('zone'):
            return form_data['zone']
        elif form_data.get('district'):
            return form_data['district']
        elif form_data.get('area'):
            return form_data['area']
        elif form_data.get('division'):
            return form_data['division']
        elif form_data.get('state'):
            return form_data['state']
        elif form_data.get('region'):
            return form_data['region']
        elif form_data.get('diocese'):
            return form_data['diocese']
        else:
            return None
    except Exception as e:
        logger.error(f"Error determining location from hierarchy: {str(e)}")
        return None

def is_parish_admin(user):
    return user.groups.filter(name='parishadmin').exists() or user.is_superuser

@login_required  
@user_passes_test(is_parish_admin)
def parish_dashboard(request):
    context = {}
    
    try:
        # Check if chart data is in cache
        chart_data = cache.get('parish_chart_data')
        region_chart_data = cache.get('region_chart_data')
        dashboard_stats = cache.get('dashboard_stats')
        
        # If not in cache, generate the data
        if not chart_data or not region_chart_data or not dashboard_stats:
            # Get current date and past dates for chart
            today = timezone.now()
            six_months_ago = today - timedelta(days=180)
            
            # Get monthly data for the last 6 months
            months = []
            registrations_data = []
            approved_data = []
            pending_data = []
            
            # Loop through the last 6 months
            for i in range(6):
                # Calculate the start and end of this month
                month_start = today.replace(day=1) - timedelta(days=30*i)
                if i == 0:  # Current month
                    month_end = today
                else:
                    next_month = month_start.replace(day=28) + timedelta(days=4)
                    month_end = next_month.replace(day=1) - timedelta(days=1)
                    
                # Add month name to labels
                months.insert(0, month_start.strftime('%b %Y'))
                
                # Count registrations for this month
                new_registrations = ParishRegistration.objects.filter(
                    date_applied__gte=month_start,
                    date_applied__lte=month_end
                ).count()
                registrations_data.insert(0, new_registrations)
                
                # Count approved registrations for this month
                approved = ParishRegistration.objects.filter(
                    date_approved__gte=month_start,
                    date_approved__lte=month_end
                ).count()
                approved_data.insert(0, approved)
                
                # Count pending at end of month
                pending = ParishRegistration.objects.filter(
                    date_applied__lte=month_end,
                    date_approved__isnull=True
                ).count()
                pending_data.insert(0, pending)
            
            # UPDATED: Get diocese distribution data from ParishRestructure (with hierarchy traversal)
            # This ensures we use real parish data and group by diocese, even if parishes are linked to districts/regions
            parishes_with_locations = ParishRestructure.objects.select_related('location').filter(location__isnull=False)
            
            diocese_counts = {}
            for parish_restructure in parishes_with_locations:
                location = parish_restructure.location
                # Traverse up the hierarchy to find the diocese
                current_location = location
                diocese_name = None
                while current_location:
                    if current_location.level.lower() == 'diocese':
                        diocese_name = current_location.name
                        break
                    current_location = current_location.parent
                
                if diocese_name:
                    diocese_counts[diocese_name] = diocese_counts.get(diocese_name, 0) + 1
            
            # Prepare data for chart (sort by count descending)
            sorted_diocese = sorted(diocese_counts.items(), key=lambda x: x[1], reverse=True)
            region_names = [name for name, count in sorted_diocese]
            region_counts = [count for name, count in sorted_diocese]
            
            # If no data from ParishRestructure, fall back to all dioceses with 0 count (preserves structure)
            if not region_names:
                dioceses = Location.objects.filter(level__iexact='diocese')
                for diocese in dioceses:
                    region_names.append(diocese.name)
                    region_counts.append(0)
            
            # Get summary statistics
            total_parishes = ParishDirectory.objects.count()
            pending_registrations = ParishRegistration.objects.filter(date_approved__isnull=True).count()
            
            # Approved this month
            first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            approved_this_month = ParishRegistration.objects.filter(
                date_approved__gte=first_day_of_month
            ).count()
            
            # Parishes in restructuring process
            restructuring_count = ParishRestructure.objects.all().count()
            
            # Total clergy count
            try:
                from clergy_registration.models import ClergyDetails
                total_clergy = ClergyDetails.objects.count()
            except ImportError:
                total_clergy = 0
                logger.warning("ClergyDetails model not found, setting total_clergy to 0")
            
            # Pending transfers count
            try:
                from transfer.models import TransferData
                pending_transfers = TransferData.objects.filter(trf_status='Pending').count()
            except ImportError:
                pending_transfers = 0
                logger.warning("TransferData model not found, setting pending_transfers to 0")
            
            # Prepare chart data for JavaScript
            chart_data = {
                'labels': months,
                'datasets': [
                    {
                        'label': 'New Registrations',
                        'data': registrations_data,
                        'borderColor': '#5e35b1',
                        'backgroundColor': 'rgba(94, 53, 177, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    },
                    {
                        'label': 'Approved',
                        'data': approved_data,
                        'borderColor': '#4caf50',
                        'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    },
                    {
                        'label': 'Pending',
                        'data': pending_data,
                        'borderColor': '#ff9800',
                        'backgroundColor': 'rgba(255, 152, 0, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    }
                ]
            }
            
            region_chart_data = {
                'labels': region_names,
                'datasets': [{
                    'data': region_counts,
                    'backgroundColor': [
                        '#5e35b1',
                        '#3949ab',
                        '#4caf50',
                        '#ff9800',
                        '#03a9f4'
                    ],
                    'borderWidth': 2,
                    'borderColor': '#ffffff'
                }]
            }
            
            # Calculate growth percentages
            month_growth = 0
            if total_parishes > 0:
                # Get count from previous month for comparison
                prev_month_start = first_day_of_month - timedelta(days=30)
                prev_month_approved = ParishRegistration.objects.filter(
                    date_approved__gte=prev_month_start,
                    date_approved__lt=first_day_of_month
                ).count()
                
                if prev_month_approved > 0:
                    month_growth = ((approved_this_month - prev_month_approved) / prev_month_approved) * 100
            
            # Weekly growth for pending registrations
            week_growth = 0
            one_week_ago = today - timedelta(days=7)
            two_weeks_ago = today - timedelta(days=14)
            
            pending_last_week = ParishRegistration.objects.filter(
                date_applied__gte=one_week_ago,
                date_approved__isnull=True
            ).count()
            
            pending_previous_week = ParishRegistration.objects.filter(
                date_applied__gte=two_weeks_ago,
                date_applied__lt=one_week_ago,
                date_approved__isnull=True
            ).count()
            
            if pending_previous_week > 0:
                week_growth = ((pending_last_week - pending_previous_week) / pending_previous_week) * 100
            
            # Create dashboard stats dictionary
            dashboard_stats = {
                'total_parishes': total_parishes,
                'pending_registrations': pending_registrations,
                'approved_this_month': approved_this_month,
                'restructuring_count': restructuring_count,
                'total_clergy': total_clergy,
                'pending_transfers': pending_transfers,
                'month_growth': round(month_growth, 1),
                'week_growth': round(week_growth, 1),
            }
            
            # Cache the results for 1 hour (3600 seconds)
            cache.set('parish_chart_data', json.dumps(chart_data), 3600)
            cache.set('region_chart_data', json.dumps(region_chart_data), 3600)
            cache.set('dashboard_stats', dashboard_stats, 3600)
        
        # Add data to context
        context.update({
            'chart_data': chart_data if isinstance(chart_data, str) else json.dumps(chart_data),
            'region_chart_data': region_chart_data if isinstance(region_chart_data, str) else json.dumps(region_chart_data),
        })
        
        # Add dashboard stats to context
        if dashboard_stats:
            context.update(dashboard_stats)
            
    except Exception as e:
        # Log the error
        logger.error(f"Error generating dashboard data: {str(e)}", exc_info=True)
        
        # Add error to context and show simplified dashboard
        messages.warning(request, "Could not load dashboard analytics. Using simplified view.")
        
        # Fallback: fetch basic data for simplified dashboard
        try:
            # Basic parish statistics
            total_parishes = ParishDirectory.objects.count()
            pending_registrations = ParishRegistration.objects.filter(date_approved__isnull=True).count()
            
            # Additional statistics with error handling
            try:
                from clergy_registration.models import ClergyDetails
                total_clergy = ClergyDetails.objects.count()
            except ImportError:
                total_clergy = 0
            
            try:
                from transfer.models import TransferData
                pending_transfers = TransferData.objects.filter(trf_status='Pending').count()
            except ImportError:
                pending_transfers = 0
            
            context.update({
                'total_parishes': total_parishes,
                'pending_registrations': pending_registrations,
                'total_clergy': total_clergy,
                'pending_transfers': pending_transfers,
                'error_occurred': True
            })
        except Exception as inner_e:
            logger.error(f"Error generating simplified dashboard: {str(inner_e)}", exc_info=True)
            context.update({'critical_error': True})
    
    return render(request, 'ParishRestructure/parish_dashboard.html', context)

@login_required
def main_dashboard(request):
    return render(request, 'ParishRestructure/index.html')

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
    """
    Recursively retrieve all parishes under a location and its children.
    
    This function traverses the location hierarchy to collect all parishes
    associated with the given location and all its sub-locations.
    
    Args:
        location: Location instance to get parishes for
        
    Returns:
        list: List of ParishRestructure objects under the location hierarchy
        
    Raises:
        Exception: If there's an error accessing the database
    """
    parishes = []
    
    try:
        # Validate input
        if not location:
            logger.warning("get_all_parishes_in_children called with None location")
            return parishes
            
        logger.debug(f"Getting parishes for location: {location.name} (Level: {location.level})")
        
        # Check if the location is "Arch Diocese" or "Special District"
        if location.level in ['archdiocese', 'specialdistrict']:
            try:
                # Retrieve all parishes associated with the current location
                location_parishes = location.parishrestructure_set.select_related('parish', 'location').all()
                parishes.extend(location_parishes)
                logger.debug(f"Found {len(location_parishes)} parishes directly under {location.name}")
            except Exception as e:
                logger.error(f"Error getting parishes for location {location.name}: {str(e)}")
                raise
        else:
            try:
                # Recursively traverse the hierarchy of child locations
                for child_location in location.children.select_related().all():
                    try:
                        logger.debug(f"Processing child location: {child_location.name}")
                        
                        # Retrieve all parishes associated with the current child location
                        child_location_parishes = child_location.parishrestructure_set.select_related('parish', 'location').all()
                        parishes.extend(child_location_parishes)
                        
                        # Recursively collect parishes from the child location's children
                        parishes.extend(get_all_parishes_in_children(child_location))
                        
                    except Exception as e:
                        logger.error(f"Error processing child location {child_location.name}: {str(e)}")
                        # Continue with other children instead of failing completely
                        continue
                        
            except Exception as e:
                logger.error(f"Error getting children for location {location.name}: {str(e)}")
                raise
                
        logger.info(f"Total parishes found under {location.name}: {len(parishes)}")
        return parishes
        
    except Exception as e:
        logger.error(f"Unexpected error in get_all_parishes_in_children for location {location.name if location else 'None'}: {str(e)}", exc_info=True)
        raise


def get_all_parishes_queryset(location):
    """
    Get a QuerySet of all parishes under a location and its children.

    This function builds a QuerySet that includes all parishes associated with
    the given location and all its sub-locations in the hierarchy.

    Args:
        location: Location instance to get parishes for

    Returns:
        QuerySet: QuerySet of ParishRestructure objects under the location hierarchy

    Raises:
        Exception: If there's an error accessing the database
    """
    try:
        # Validate input
        if not location:
            logger.warning("get_all_parishes_queryset called with None location")
            return ParishRestructure.objects.none()

        logger.debug(f"Building QuerySet for parishes under location: {location.name} (Level: {location.level})")

        # Get all location IDs in the hierarchy
        location_ids = []

        def collect_location_ids(loc):
            location_ids.append(loc.id)
            for child in loc.children.all():
                collect_location_ids(child)

        collect_location_ids(location)

        # Build QuerySet for all parishes under these locations
        parishes_queryset = ParishRestructure.objects.filter(
            location_id__in=location_ids
        ).select_related('parish', 'location')

        logger.debug(f"Built QuerySet for {parishes_queryset.count()} parishes under {location.name}")
        return parishes_queryset

    except Exception as e:
        logger.error(f"Unexpected error in get_all_parishes_queryset for location {location.name if location else 'None'}: {str(e)}", exc_info=True)
        raise




@login_required  
def view_parishes(request):
    """
    Handle parish viewing by location hierarchy with comprehensive error handling.
    
    This view allows users to select a location and view all parishes under that
    location and its sub-locations in the hierarchy. Includes proper exception
    handling and user feedback.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered template with parish data or error messages
        
    Raises:
        Location.DoesNotExist: When selected location doesn't exist
        Exception: For any other unexpected errors
    """
    locations = LocationForm(request.POST or None)
    selected_location = None
    parishes = []
    
    try:
        # Check if this is a DataTables server-side request (GET with draw parameter)
        if request.method == 'GET' and request.GET.get('draw'):
            location_id = request.GET.get('location_id')
            logger.info(f"DataTables request received: draw={request.GET.get('draw')}, location_id={location_id}")
            if not location_id:
                logger.warning("DataTables request missing location_id")
                return JsonResponse({
                    'draw': int(request.GET.get('draw', 1)),
                    'recordsTotal': 0,
                    'recordsFiltered': 0,
                    'data': []
                })
            
            try:
                selected_location = Location.objects.get(pk=location_id)
                parishes = get_all_parishes_queryset(selected_location)
                logger.info(f"DataTables: Found {parishes.count()} parishes for location {selected_location.name}")
                
                # Handle DataTables server-side processing
                draw = int(request.GET.get('draw', 1))
                start = int(request.GET.get('start', 0))
                length = int(request.GET.get('length', 10))
                search_value = request.GET.get('search[value]', '')
                logger.info(f"DataTables params: draw={draw}, start={start}, length={length}, search='{search_value}'")
                
                # Store total count before filtering
                total_count = parishes.count()
                
                # Apply search filter if provided
                if search_value:
                    parishes = parishes.filter(
                        Q(parish__name__icontains=search_value) |
                        Q(address__icontains=search_value) |
                        Q(location__name__icontains=search_value)
                    )
                    logger.info(f"DataTables: After search filter, {parishes.count()} parishes remain")
                
                # Get filtered count
                filtered_count = parishes.count()
                
                # Apply ordering
                order_column = int(request.GET.get('order[0][column]', 1))
                order_dir = request.GET.get('order[0][dir]', 'asc')
                
                # Map column index to field name
                column_mapping = {
                    1: 'parish__name',
                    2: 'address', 
                    3: 'location__name',
                    4: 'parish__phone_number',
                    5: 'created_at'
                }
                
                if order_column in column_mapping:
                    order_field = column_mapping[order_column]
                    if order_dir == 'desc':
                        order_field = f'-{order_field}'
                    parishes = parishes.order_by(order_field)
                
                # Apply pagination
                parishes = parishes[start:start + length]
                logger.info(f"DataTables: Returning {len(parishes)} parishes (page {start//length + 1})")
                
                # Format data for DataTables
                data = []
                for parish in parishes:
                    data.append([
                        f'<div class="form-check"><input class="form-check-input" type="checkbox" value="{parish.id}" id="check-{parish.id}"></div>',  # Checkbox
                        f'<div class="d-flex align-items-center"><div class="avatar avatar-sm me-3"><div class="avatar-initial bg-primary rounded-circle"><i class="fas fa-church text-white"></i></div></div><div><h6 class="mb-0">{parish.parish.name if parish.parish else "N/A"}</h6><small class="text-muted">ID: {parish.id}</small></div></div>',  # Parish Name
                        f'<span class="badge bg-light text-dark">{parish.address or "N/A"}</span>',  # Address
                        f'<span class="badge bg-info">{parish.location.name if parish.location else "N/A"}</span><br><small class="text-muted">{parish.location.get_level_display() if parish.location else "N/A"}</small>',  # Location
                        f'<span class="badge bg-secondary">{selected_location.name}</span>',  # Selected Location
                        f'<div class="btn-group" role="group"><a href="/parish/edit_parish/{parish.id}/" class="btn btn-outline-primary btn-sm" title="Edit Parish"><i class="fas fa-edit"></i></a><a href="/parish/view/{parish.id}/" class="btn btn-outline-info btn-sm" title="View Details"><i class="fas fa-eye"></i></a><button type="button" class="btn btn-outline-danger btn-sm" title="Delete Parish" onclick="showDeleteRestructureModal({parish.id}, \'{parish.parish.name if parish.parish else "this parish"}\')"><i class="fas fa-trash"></i></button></div>'  # Actions
                    ])
                
                logger.info(f"DataTables: Sending response with {len(data)} rows")
                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': total_count,
                    'recordsFiltered': filtered_count,
                    'data': data
                })
            except Location.DoesNotExist:
                return JsonResponse({
                    'draw': int(request.GET.get('draw', 1)),
                    'recordsTotal': 0,
                    'recordsFiltered': 0,
                    'data': []
                })
        
        if request.method == 'POST':
            location_id = request.POST.get('parent')
            
            # Validate location_id
            if not location_id or location_id.strip() == '':
                messages.error(request, 'Please select a valid location.')
                return render(request, 'ParishRestructure/select_parish_new.html', {
                    'locations': locations,
                    'selected_location': selected_location,
                    'parishes': parishes
                })
            
            try:
                # Get the selected location
                selected_location = Location.objects.get(pk=location_id)
                logger.info(f"User {request.user} selected location: {selected_location.name} (ID: {selected_location.id})")
                
            except Location.DoesNotExist:
                logger.error(f"Location with ID {location_id} does not exist")
                messages.error(request, f'The selected location could not be found. Please try again.')
                return render(request, 'ParishRestructure/select_parish_new.html', {
                    'locations': locations,
                    'selected_location': selected_location,
                    'parishes': parishes
                })
            
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid location ID format: {location_id}, Error: {str(e)}")
                messages.error(request, 'Invalid location selection. Please select a valid location.')
                return render(request, 'ParishRestructure/select_parish_new.html', {
                    'locations': locations,
                    'selected_location': selected_location,
                    'parishes': parishes
                })
            
            try:
                # Get all parishes under the selected location
                parishes = get_all_parishes_in_children(selected_location)
                logger.info(f"Found {len(parishes)} parishes under location {selected_location.name}")
                
                # Check if this is a regular AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Return JSON response for AJAX requests
                    parishes_data = []
                    for parish in parishes:
                        parishes_data.append({
                            'id': parish.id,
                            'parish': {
                                'name': parish.parish.name if parish.parish else 'N/A',
                                'id': parish.parish.id if parish.parish else None
                            },
                            'address': parish.address,
                            'location': {
                                'id': parish.location.id if parish.location else None,
                                'name': parish.location.name if parish.location else 'N/A',
                                'level': parish.location.get_level_display() if parish.location else 'N/A'
                            }
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'parishes': parishes_data,
                        'selected_location': {
                            'id': selected_location.id,
                            'name': selected_location.name,
                            'level': selected_location.get_level_display()
                        },
                        'stats': {
                            'total_parishes': len(parishes),
                            'location_name': selected_location.name,
                            'location_level': selected_location.get_level_display(),
                            'sub_locations': selected_location.children.count()
                        },
                        'message': f'Found {len(parishes)} parish(es) under {selected_location.name}'
                    })
                
                if parishes:
                    messages.success(request, f'Found {len(parishes)} parish(es) under {selected_location.name}')
                    return render(request, 'ParishRestructure/select_parish_new.html', {
                        'selected_location': selected_location, 
                        'parishes': parishes, 
                        'locations': locations
                    })
                else:
                    messages.warning(request, f'No parishes found under {selected_location.name}. This location may not have any parishes assigned to it or its sub-locations.')
                    return render(request, 'ParishRestructure/select_parish_new.html', {
                        'selected_location': selected_location,
                        'parishes': parishes,
                        'locations': locations
                    })
                    
            except Exception as e:
                logger.error(f"Error retrieving parishes for location {selected_location.name}: {str(e)}", exc_info=True)
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'An error occurred while retrieving parish data. Please try again.',
                        'parishes': [],
                        'selected_location': {
                            'id': selected_location.id,
                            'name': selected_location.name
                        }
                    }, status=500)
                
                messages.error(request, 'An error occurred while retrieving parish data. Please try again or contact support if the problem persists.')
                return render(request, 'ParishRestructure/select_parish_new.html', {
                    'locations': locations,
                    'selected_location': selected_location,
                    'parishes': parishes
                })
        
        # GET request - show initial form
        return render(request, 'ParishRestructure/select_parish_new.html', {
            'locations': locations,
            'selected_location': selected_location,
            'parishes': parishes
        })
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in view_parishes view: {str(e)}", exc_info=True)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.',
                'parishes': []
            }, status=500)
        
        messages.error(request, 'An unexpected error occurred. Please try again or contact support if the problem persists.')
        
        # Return safe fallback
        try:
            return render(request, 'ParishRestructure/select_parish_new.html', {
                'locations': LocationForm(),
                'selected_location': None,
                'parishes': []
            })
        except Exception as fallback_error:
            logger.critical(f"Fallback render failed: {str(fallback_error)}", exc_info=True)
            # Last resort - return basic error page
            return render(request, 'dashboard/base.html', {
                'error_message': 'A critical error occurred. Please contact support.'
            })

@login_required  
def edit_parish_reg(request, pk):
    """
    Edit registered parish details with comprehensive error handling.

    This view handles editing ParishDirectory instances with robust validation,
    error handling, and user feedback for registered parishes.
    """
    try:
        # Get the parish instance with error handling
        try:
            parish = get_object_or_404(ParishDirectory, pk=pk)
        except Http404:
            messages.error(request, 'Registered parish not found. It may have been deleted or the ID is invalid.')
            return redirect('approved')
        except Exception as e:
            logger.error(f"Error retrieving registered parish {pk}: {str(e)}")
            messages.error(request, 'An error occurred while retrieving the parish information.')
            return redirect('approved')

        if request.method == 'POST':
            try:
                parish_form = ParishDirectoryForm(request.POST, request.FILES, instance=parish)

                if parish_form.is_valid():
                    try:
                        # Save the parish instance
                        parish_instance = parish_form.save()

                        # Log successful edit
                        logger.info(f"Registered parish {parish.name} (ID: {pk}) edited successfully by user {request.user.username}")

                        messages.success(request, f'Registered parish "{parish_instance.name}" has been updated successfully.')
                        return redirect('approved')

                    except IntegrityError as e:
                        logger.error(f"Database integrity error while saving registered parish {pk}: {str(e)}")
                        messages.error(request, 'A database error occurred. Please ensure the parish name is unique.')
                        parish_form.add_error('name', 'A parish with this name already exists.')

                    except ValidationError as e:
                        logger.error(f"Validation error while saving registered parish {pk}: {str(e)}")
                        messages.error(request, 'Validation error occurred. Please check your input data.')
                        parish_form.add_error(None, str(e))

                    except Exception as e:
                        logger.error(f"Unexpected error while saving registered parish {pk}: {str(e)}")
                        messages.error(request, 'An unexpected error occurred while saving. Please try again.')
                        parish_form.add_error(None, 'An unexpected error occurred.')

                else:
                    # Form validation failed
                    logger.warning(f"Form validation failed for registered parish {pk}. Errors: {parish_form.errors}")
                    error_messages = []

                    # Collect specific field errors
                    for field, errors in parish_form.errors.items():
                        if field != '__all__':
                            error_messages.extend([f"{parish_form.fields[field].label}: {error}" for error in errors])

                    if error_messages:
                        messages.error(request, f'Please correct the following errors: {" ".join(error_messages[:3])}')
                    else:
                        messages.error(request, 'Please correct the form errors and try again.')

            except Exception as e:
                logger.error(f"Error processing POST request for registered parish {pk}: {str(e)}")
                messages.error(request, 'An error occurred while processing your request. Please try again.')

        else:
            # GET request - display the form
            try:
                parish_form = ParishDirectoryForm(instance=parish)
            except Exception as e:
                logger.error(f"Error creating form for registered parish {pk}: {str(e)}")
                messages.error(request, 'An error occurred while loading the form. Please try again.')
                return redirect('approved')

        # Context for template
        context = {
            'parish_form': parish_form,
            'parish': parish,
            'page_title': f'Edit Registered Parish: {parish.name}',
            'is_edit': True
        }

        return render(request, 'ParishRestructure/edit_directory.html', context)

    except Exception as e:
        logger.error(f"Unexpected error in edit_parish_reg view for parish {pk}: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please contact support if this persists.')
        return redirect('approved')

@login_required
def edit_parish(request, pk):
    """
    Edit parish details for ParishRestructure model with comprehensive error handling.

    This view handles editing parish information including location hierarchy,
    with robust validation, error handling, and user feedback.
    """
    try:
        # Get the parish instance with error handling
        try:
            parish = get_object_or_404(ParishRestructure, pk=pk)
        except Http404:
            messages.error(request, 'Parish not found. It may have been deleted or the ID is invalid.')
            return redirect('view_parishes')
        except Exception as e:
            logger.error(f"Error retrieving parish {pk}: {str(e)}")
            messages.error(request, 'An error occurred while retrieving the parish information.')
            return redirect('view_parishes')

        if request.method == 'POST':
            try:
                form = ParishForm(request.POST, instance=parish)

                if form.is_valid():
                    try:
                        # Save the form without committing to handle location separately
                        parish_instance = form.save(commit=False)

                        # Handle location hierarchy assignment
                        if 'location' in form.cleaned_data and form.cleaned_data['location']:
                            parish_instance.location_id = form.cleaned_data['location'].id
                        else:
                            # If no location is selected, try to determine from hierarchy
                            location = determine_location_from_hierarchy(form.cleaned_data)
                            if location:
                                parish_instance.location = location

                        # Save the instance
                        parish_instance.save()

                        # Log successful edit
                        logger.info(f"Parish {parish.name} (ID: {pk}) edited successfully by user {request.user.username}")

                        messages.success(request, f'Parish "{parish_instance.parish.name}" has been updated successfully.')
                        return redirect('view_parishes')

                    except IntegrityError as e:
                        logger.error(f"Database integrity error while saving parish {pk}: {str(e)}")
                        messages.error(request, 'A database error occurred. Please ensure all required fields are filled correctly.')
                        form.add_error(None, 'Database integrity constraint violation.')

                    except ValidationError as e:
                        logger.error(f"Validation error while saving parish {pk}: {str(e)}")
                        messages.error(request, 'Validation error occurred. Please check your input data.')
                        form.add_error(None, str(e))

                    except Exception as e:
                        logger.error(f"Unexpected error while saving parish {pk}: {str(e)}")
                        messages.error(request, 'An unexpected error occurred while saving. Please try again.')
                        form.add_error(None, 'An unexpected error occurred.')

                else:
                    # Form validation failed
                    logger.warning(f"Form validation failed for parish {pk}. Errors: {form.errors}")
                    error_messages = []

                    # Collect specific field errors
                    for field, errors in form.errors.items():
                        if field != '__all__':
                            error_messages.extend([f"{form.fields[field].label}: {error}" for error in errors])

                    if error_messages:
                        messages.error(request, f'Please correct the following errors: {" ".join(error_messages[:3])}')
                    else:
                        messages.error(request, 'Please correct the form errors and try again.')

            except Exception as e:
                logger.error(f"Error processing POST request for parish {pk}: {str(e)}")
                messages.error(request, 'An error occurred while processing your request. Please try again.')

        else:
            # GET request - display the form
            try:
                form = ParishForm(instance=parish)
            except Exception as e:
                logger.error(f"Error creating form for parish {pk}: {str(e)}")
                messages.error(request, 'An error occurred while loading the form. Please try again.')
                return redirect('view_parishes')

        # Context for template
        context = {
            'form': form,
            'parish': parish,
            'page_title': f'Edit Parish: {parish.parish.name if parish.parish else "Unknown Parish"}',
            'is_edit': True
        }

        return render(request, 'ParishRestructure/edit_parish.html', context)

    except Exception as e:
        logger.error(f"Unexpected error in edit_parish view for parish {pk}: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please contact support if this persists.')
        return redirect('view_parishes')


def determine_location_from_hierarchy(cleaned_data):
    """
    Determine the most specific location from the hierarchy selection.

    Args:
        cleaned_data: Form cleaned_data dictionary

    Returns:
        Location instance or None
    """
    location_hierarchy = ['zone', 'district', 'area', 'division', 'state', 'region', 'diocese']

    for location_type in location_hierarchy:
        if location_type in cleaned_data and cleaned_data[location_type]:
            return cleaned_data[location_type]

    return None


@login_required
def delete_restructure(request, pk):
    """
    Delete a parish restructure record with optimized database operations and proper error handling.

    This view handles the deletion of ParishRestructure instances with:
    - Transaction management for data integrity
    - Comprehensive error handling and user feedback
    - Optimized database queries
    """
    from django.db import transaction
    from django.contrib import messages

    try:
        with transaction.atomic():
            # Get the restructure record with select_related to optimize queries
            restructure = get_object_or_404(
                ParishRestructure.objects.select_related('parish'),
                pk=pk
            )

            # Store parish name for feedback
            parish_name = restructure.parish.name if restructure.parish else f"Restructure {pk}"

            # Perform the deletion
            restructure.delete()

            # Provide feedback
            messages.warning(request, f'Parish restructure for "{parish_name}" deleted successfully.')

    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error deleting restructure {pk}: {str(e)}", exc_info=True)
        messages.error(
            request,
            'An error occurred while deleting the restructure record. Please try again or contact support if the problem persists.'
        )

    return redirect('view_parishes')


# Delete Parish fo all parish data table
@login_required  
def delete_parish(request, pk):
    """
    Delete a parish with optimized database operations and proper error handling.
    
    This view handles the deletion of ParishDirectory instances with:
    - Transaction management for data integrity
    - Cascade deletion of related ParishRegistration and ParishRestructure objects
    - Comprehensive error handling and user feedback
    - Optimized database queries
    """
    from django.db import transaction
    from django.contrib import messages
    
    try:
        with transaction.atomic():
            # Get the parish with select_related to optimize queries
            parish = get_object_or_404(
                ParishDirectory.objects.select_related('parishregistration'), 
                pk=pk
            )
            
            # Store parish name for feedback
            parish_name = parish.name
            
            # Check for related objects that might cause issues
            related_restructure_count = parish.parishrestructure_set.count()
            
            # Perform the deletion (cascade will handle related objects)
            parish.delete()
            
            # Provide detailed feedback
            if related_restructure_count > 0:
                messages.warning(
                    request, 
                    f'Parish "{parish_name}" and {related_restructure_count} related restructure record(s) deleted successfully.'
                )
            else:
                messages.warning(request, f'Parish "{parish_name}" deleted successfully.')
            
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error deleting parish {pk}: {str(e)}", exc_info=True)
        messages.error(
            request, 
            'An error occurred while deleting the parish. Please try again or contact support if the problem persists.'
        )
    
    return redirect('all-parish')

@login_required  
def view_parish(request, pk):
    """View a single parish from ParishDirectory."""
    try:
        parish = get_object_or_404(ParishDirectory, pk=pk)
        
        # Additional context for the detail layout
        context = {
            'parish': parish,
            'page_title': f'CCC {parish.name}',
            'page_subtitle': 'Parish Directory Information',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'All Parishes', 'url': 'all-parish'},
                {'title': 'Parish Details', 'url': None, 'active': True}
            ],
            'show_registration_button': not parish.register_status,
            'registration_url': 'reg-old-parish' if not parish.register_status else None,
        }
        
        return render(request, 'ParishRestructure/view_parish.html', context)
        
    except ParishDirectory.DoesNotExist:
        messages.error(request, 'The requested parish could not be found.')
        return redirect('all-parish')
    except Exception as e:
        logger.error(f"Error in view_parish for pk={pk}: {str(e)}")
        messages.error(request, 'An error occurred while loading the parish details. Please try again.')
        return redirect('all-parish')

@login_required  
def view_parishh(request, pk):
    """View a single parish from ParishRestructure."""
    try:
        parish = get_object_or_404(ParishRestructure, pk=pk)
        
        # Additional context for the detail layout
        context = {
            'parish': parish,
            'page_title': f'CCC {parish.parish.name}',
            'page_subtitle': 'Parish Restructure Information',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'Parish List', 'url': 'view_parishes'},
                {'title': 'Parish Details', 'url': None, 'active': True}
            ],
            'show_registration_button': not parish.parish.register_status,
            'registration_url': 'reg-old-parish' if not parish.parish.register_status else None,
            'can_delete': True,  # Restructure parishes can be deleted
        }
        
        return render(request, 'ParishRestructure/view_parish copy.html', context)
        
    except ParishRestructure.DoesNotExist:
        messages.error(request, 'The requested parish could not be found.')
        return redirect('view_parishes')
    except Exception as e:
        logger.error(f"Error in view_parishh for pk={pk}: {str(e)}")
        messages.error(request, 'An error occurred while loading the parish details. Please try again.')
        return redirect('view_parishes')

@login_required  
@login_required
def reg_parish(request):
    """
    Handle parish registration form submission and display.

    This view manages the creation of new ParishDirectory and ParishRegistration instances,
    including comprehensive form validation, error handling, and user feedback.
    """
    try:
        if request.method == 'POST':
            parish_form = ParishDirectoryForm(request.POST, request.FILES)
            preg_form = ParishRegForm(request.POST, request.FILES)

            # Check if draft save is requested
            is_draft = request.POST.get('is_draft', False)

            if parish_form.is_valid() and preg_form.is_valid():
                try:
                    # Save parish directory first
                    parish = parish_form.save(commit=False)
                    parish.created_by = request.user
                    parish.save()

                    # Save parish registration details
                    parish_details = preg_form.save(commit=False)
                    parish_details.parish = parish
                    parish_details.created_by = request.user

                    if is_draft:
                        parish_details.is_draft = True
                        parish_details.save()
                        messages.success(request, 'Parish registration draft saved successfully. You can continue editing later.')
                        return JsonResponse({'success': True, 'message': 'Draft saved successfully'})
                    else:
                        parish_details.save()
                        messages.success(request, 'Parish registration submitted successfully and is pending approval.')
                        logger.info(f'New parish registration created: {parish.name} by {request.user.username}')
                        return redirect('parish_dashboard')

                except Exception as e:
                    logger.error(f'Error saving parish registration: {str(e)}')
                    messages.error(request, 'An error occurred while saving the parish registration. Please try again.')
                    return JsonResponse({'success': False, 'message': 'Error saving registration'})

            else:
                # Form validation failed
                if is_draft:
                    messages.error(request, 'Please correct the errors in the form before saving draft.')
                    return JsonResponse({'success': False, 'message': 'Form validation failed'})
                else:
                    messages.error(request, 'Please correct the errors in the form and try again.')

        else:
            preg_form = ParishRegForm()
            parish_form = ParishDirectoryForm()

        # Prepare context with additional information
        context = {
            'parish_form': parish_form,
            'preg_form': preg_form,
            'page_title': 'Add Parish Details',
            'form_action': 'Create New Parish',
            'breadcrumb_items': [
                {'name': 'Home', 'url': 'parish_dashboard'},
                {'name': 'Parish Registration', 'url': None}
            ],
            'help_text': {
                'directory': 'Basic parish information and contact details',
                'registration': 'Registration details and document submission',
                'documents': 'Upload required documents and mark submission checkboxes'
            }
        }

        return render(request, 'ParishRestructure/reg_parish_new.html', context)

    except Exception as e:
        logger.error(f'Unexpected error in reg_parish view: {str(e)}')
        messages.error(request, 'An unexpected error occurred. Please contact support if the problem persists.')
        return redirect('parish_dashboard')

@login_required  
def edit_reg_parish(request, pk):
    
    parish = get_object_or_404(ParishRegistration, pk=pk)
    
    if request.method == 'POST':
        print(request.POST)  # Print the POST data
        print(request.FILES)  # Print the FILES data (file uploads)
        form = ParishRegForm1(request.POST, request.FILES, instance=parish)
        if form.is_valid():
            # Form is valid, process the data
            parish = form.save(commit=False) 
            parish.save()
            messages.success(request, 'Parish updated successfully.')
            return redirect('approved')  # Redirect to success page or any other URL
        else:
            # Form is invalid, print errors for debugging
            print(form.errors)  # This will print validation errors to the console
            messages.error(request, 'Form validation failed. Please check the errors below.')
    else:
        form = ParishRegForm1(instance=parish)
        print(f"Form initial data: {form.initial}")  # Debug: print initial form data
        print(f"Parish instance: {parish.__dict__}")  # Debug: print parish instance data
        
        
    return render(request, 'ParishRestructure/edit_regparish.html', {'form': form})


@login_required
def regparish(request, pk):
    """
    Handle parish registration for existing parish directory entry.

    This view manages the registration process for an existing ParishDirectory instance,
    including comprehensive form validation, error handling, and user feedback.
    """
    try:
        # Get the parish directory instance
        parish = get_object_or_404(ParishDirectory, pk=pk)

        if request.method == 'POST':
            parish_form = ParishDirectoryForm(request.POST, request.FILES, instance=parish)
            preg_form = ParishRegForm(request.POST, request.FILES)

            # Check if draft save is requested
            is_draft = request.POST.get('is_draft', False)

            if parish_form.is_valid() and preg_form.is_valid():
                try:
                    # Save parish directory updates
                    parish = parish_form.save(commit=False)
                    parish.updated_by = request.user
                    parish.save()

                    # Check if registration already exists
                    existing_registration = ParishRegistration.objects.filter(parish=parish).first()

                    if existing_registration:
                        # Update existing registration
                        parish_details = preg_form.save(commit=False)
                        parish_details.pk = existing_registration.pk
                        parish_details.parish = parish
                        parish_details.updated_by = request.user
                    else:
                        # Create new registration
                        parish_details = preg_form.save(commit=False)
                        parish_details.parish = parish
                        parish_details.created_by = request.user

                    if is_draft:
                        parish_details.is_draft = True
                        parish_details.save()
                        messages.success(request, 'Parish registration draft saved successfully. You can continue editing later.')
                        return JsonResponse({'success': True, 'message': 'Draft saved successfully'})
                    else:
                        parish_details.save()
                        messages.success(request, 'Parish registration submitted successfully and is pending approval.')
                        logger.info(f'Parish registration updated: {parish.name} by {request.user.username}')
                        return redirect('parish_dashboard')

                except Exception as e:
                    logger.error(f'Error saving parish registration: {str(e)}')
                    messages.error(request, 'An error occurred while saving the parish registration. Please try again.')
                    return JsonResponse({'success': False, 'message': 'Error saving registration'})

            else:
                # Form validation failed
                if is_draft:
                    messages.error(request, 'Please correct the errors in the form before saving draft.')
                    return JsonResponse({'success': False, 'message': 'Form validation failed'})
                else:
                    messages.error(request, 'Please correct the errors in the form and try again.')

        else:
            preg_form = ParishRegForm()
            parish_form = ParishDirectoryForm(instance=parish)

        # Prepare context with additional information
        context = {
            'parish_form': parish_form,
            'preg_form': preg_form,
            'parish': parish,
            'page_title': f'Register Parish: {parish.name}',
            'form_action': f'Complete Registration for {parish.name}',
            'breadcrumb_items': [
                {'name': 'Home', 'url': 'parish_dashboard'},
                {'name': 'Parish Directory', 'url': 'all_parish'},
                {'name': parish.name, 'url': None}
            ],
            'help_text': {
                'registration': 'Complete registration details and document submission',
                'documents': 'Upload required documents and mark submission checkboxes',
                'existing_data': f'Updating registration for existing parish: {parish.name}'
            }
        }

        return render(request, 'ParishRestructure/regparish_new.html', context)

    except ParishDirectory.DoesNotExist:
        messages.error(request, 'The requested parish was not found.')
        return redirect('all_parish')
    except Exception as e:
        logger.error(f'Unexpected error in regparish view: {str(e)}')
        messages.error(request, 'An unexpected error occurred. Please contact support if the problem persists.')
        return redirect('parish_dashboard')


@login_required
def all_parish(request):
    """
    Display all parishes in the directory with enhanced context for the dashboard.

    Provides comprehensive parish data with statistics and management options.
    Includes optimized pagination for large datasets with caching.
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.core.cache import cache
    import time

    start_time = time.time()

    # Check if this is a DataTables AJAX request
    if request.GET.get('draw'):
        return all_parish_datatables(request)

    # For initial page load, just provide basic context without Django pagination
    # DataTables will handle all pagination, sorting, and filtering via AJAX
    try:
        # Get total statistics
        total_parishes = ParishDirectory.objects.count()
        registered_parishes = ParishDirectory.objects.filter(register_status=True).count()
        unregistered_parishes = total_parishes - registered_parishes
        registration_percentage = round((registered_parishes / total_parishes * 100), 1) if total_parishes > 0 else 0

        context = {
            'total_parishes': total_parishes,
            'registered_parishes': registered_parishes,
            'unregistered_parishes': unregistered_parishes,
            'registration_percentage': registration_percentage,
            'page_title': 'Parish Directory',
            'page_subtitle': 'Complete overview of all parishes in the system',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'All Parishes', 'url': None, 'active': True}
            ],
            'quick_stats': [
                {
                    'title': 'Total Parishes',
                    'value': total_parishes,
                    'icon': 'bi-building',
                    'color': 'primary'
                },
                {
                    'title': 'Registered',
                    'value': registered_parishes,
                    'icon': 'bi-check-circle-fill',
                    'color': 'success'
                },
                {
                    'title': 'Pending Registration',
                    'value': unregistered_parishes,
                    'icon': 'bi-clock',
                    'color': 'warning'
                }
            ],
        }

        return render(request, 'ParishRestructure/view_allparish.html', context)

    except Exception as e:
        logger.error(f"Error in all_parish view: {str(e)}")
        messages.error(request, 'An error occurred while loading the parish directory. Please try again.')
        return redirect('parish_dashboard')



def all_parish_datatables(request):
    """
    Handle DataTables server-side processing for parish data.
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
    order_direction = request.GET.get('order[0][dir]', 'asc')

    # Map column index to field name (matching template column definitions)
    column_mapping = {
        0: 'id',  # Checkbox column (not sortable)
        1: 'name',  # Parish Name
        2: 'address',  # Address
        3: 'register_status',  # Status
        4: 'id',  # Actions column (not sortable, use id for consistency)
    }

    order_field = column_mapping.get(order_column_index, 'name')

    # Base queryset with optimized fields
    queryset = ParishDirectory.objects.select_related('parishregistration').only(
        'id', 'name', 'address', 'register_status',
        'parishregistration__country', 'parishregistration__state',
        'parishregistration__city', 'parishregistration__diocese__name'
    )

    # Apply search filter
    if search_value:
        queryset = queryset.filter(
            Q(name__icontains=search_value) |
            Q(address__icontains=search_value) |
            Q(parishregistration__country__icontains=search_value) |
            Q(parishregistration__state__icontains=search_value) |
            Q(parishregistration__city__icontains=search_value) |
            Q(parishregistration__diocese__name__icontains=search_value)
        )

    # Get total records count (before filtering)
    total_records = ParishDirectory.objects.count()

    # Get filtered records count
    records_filtered = queryset.count()

    # Apply ordering
    if order_direction == 'desc':
        queryset = queryset.order_by(f'-{order_field}')
    else:
        queryset = queryset.order_by(order_field)

    # Apply pagination
    queryset = queryset[start:start + length]

    # Prepare data for DataTables
    data = []
    for parish in queryset:
        # Get registration details
        registration = parish.parishregistration if hasattr(parish, 'parishregistration') else None

        # Status badge with registration link for unregistered parishes
        if parish.register_status:
            status_badge = '<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="bi bi-check-circle-fill me-1"></i>Registered</span>'
        elif registration and registration.date_approved is None:
            status_badge = '<span class="badge bg-warning-subtle text-warning border border-warning-subtle"><i class="bi bi-clock me-1"></i>Waiting for Approval</span>'
        else:
            status_badge = f'''
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-danger-subtle text-danger border border-danger-subtle">
                        <i class="bi bi-x-circle-fill me-1"></i>Not Registered
                    </span>
                    <a href="/parish/reg_parish/{parish.id}" class="btn btn-sm btn-outline-primary"
                       title="Register Parish" data-bs-toggle="tooltip">
                        <i class="bi bi-plus-circle-dotted"></i>
                    </a>
                </div>
            '''

        row = {
            'DT_RowId': f'row_{parish.id}',
            'checkbox': f'<div class="form-check"><input class="form-check-input row-checkbox" type="checkbox" value="{parish.id}" id="check-{parish.id}"></div>',
            'name': f'''
            <div class="d-flex align-items-center">
                <div class="avatar-wrapper me-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center avatar-sm" style="width: 40px; height: 40px;">
                    <i class="fas fa-building"></i>
                </div>
                </div>
                <div>
                <div class="fw-semibold text-dark">{parish.name}</div>
                <small class="text-muted">ID: {parish.id}</small>
                </div>
            </div>
            ''',
            'address': parish.address or 'N/A',
            'status': status_badge,
            'country': registration.country if registration else 'N/A',
            'state': registration.state if registration else 'N/A',
            'city': registration.city if registration else 'N/A',
            'actions': f'''
            <div class="action-buttons d-flex justify-content-center align-items-center gap-1">
                <a href="/parish/view_parish/{parish.id}/" class="btn btn-xs btn-outline-primary" title="View Details" data-bs-toggle="tooltip">
                <i class="fas fa-eye"></i>
                </a>
                <a href="/parish/edit/{parish.id}/" class="btn btn-xs btn-outline-success" title="Edit Parish" data-bs-toggle="tooltip">
                <i class="fas fa-edit"></i>
                </a>
                <button type="button" class="btn btn-xs btn-outline-danger" title="Delete Parish" data-bs-toggle="tooltip" 
                        onclick="showDeleteModal({parish.id}, '{parish.name.replace(chr(39), chr(92) + chr(39))}')">
                <i class="fas fa-trash"></i>
                </button>
            </div>
            '''
        }
        data.append(row)

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': records_filtered,
        'data': data
    }

    return JsonResponse(response)


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
@login_required
def approval_queue(request):
    """
    Display parishes pending approval with enhanced filtering and context.

    This view provides a comprehensive approval queue with:
    - Diocese-based filtering
    - Document completion status
    - Enhanced error handling
    - Statistics and summary information
    """
    try:
        # Check if this is a DataTables AJAX request
        if request.GET.get('draw'):
            return approval_queue_datatables(request)

        # Get filter parameters
        diocese_filter = request.GET.get('diocese', '')
        status_filter = request.GET.get('status', '')

        # Base queryset for pending parishes
        parishes_queryset = ParishRegistration.objects.filter(date_approved__isnull=True).select_related('parish', 'diocese')

        # Apply diocese filter if specified
        if diocese_filter:
            try:
                diocese_id = int(diocese_filter)
                parishes_queryset = parishes_queryset.filter(diocese_id=diocese_id)
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid diocese filter provided.')

        # Apply status filter if specified
        if status_filter:
            if status_filter == 'complete':
                # Parishes with all required documents
                parishes_queryset = parishes_queryset.filter(
                    application_for_registration=True,
                    original_receipt_of_land=True,
                    original_survey_plan=True,
                    building_plan=True,
                    sworn_affidavit=True,
                    passport_photograph=True,
                    payment_proof_of_auditorium=True,
                    approval_from_government_diaspora=True
                )
            elif status_filter == 'incomplete':
                # Parishes missing at least one document
                parishes_queryset = parishes_queryset.exclude(
                    application_for_registration=True,
                    original_receipt_of_land=True,
                    original_survey_plan=True,
                    building_plan=True,
                    sworn_affidavit=True,
                    passport_photograph=True,
                    payment_proof_of_auditorium=True,
                    approval_from_government_diaspora=True
                )

        # Get parishes with ordering
        parishes = parishes_queryset.order_by('-date_applied')

        # Get all dioceses for filter dropdown
        dioceses = Location.objects.filter(level='diocese').order_by('name')

        # Calculate statistics
        total_pending = ParishRegistration.objects.filter(date_approved__isnull=True).count()
        complete_applications = parishes_queryset.filter(
            application_for_registration=True,
            original_receipt_of_land=True,
            original_survey_plan=True,
            building_plan=True,
            sworn_affidavit=True,
            passport_photograph=True,
            payment_proof_of_auditorium=True,
            approval_from_government_diaspora=True
        ).count()

        # Calculate document completion for each parish
        parishes_with_completion = []
        for parish in parishes:
            doc_count = sum([
                parish.application_for_registration or False,
                parish.original_receipt_of_land or False,
                parish.original_survey_plan or False,
                parish.building_plan or False,
                parish.sworn_affidavit or False,
                parish.passport_photograph or False,
                parish.payment_proof_of_auditorium or False,
                parish.approval_from_government_diaspora or False
            ])
            completion_percentage = (doc_count / 8) * 100
            parishes_with_completion.append({
                'parish': parish,
                'doc_count': doc_count,
                'completion_percentage': completion_percentage
            })

        # Enhanced context
        context = {
            'parishes': parishes_with_completion,
            'dioceses': dioceses,
            'current_diocese': diocese_filter,
            'current_status': status_filter,
            'total_pending': total_pending,
            'complete_applications': complete_applications,
            'incomplete_applications': total_pending - complete_applications,
            'completion_rate': round((complete_applications / total_pending * 100), 1) if total_pending > 0 else 0,
            'page_title': 'Parish Approval Queue',
            'page_subtitle': f'Manage {total_pending} pending parish registrations',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'Approval Queue', 'url': None, 'active': True}
            ]
        }

        return render(request, 'ParishRestructure/approval_queue.html', context)

    except Exception as e:
        logger.error(f"Error in approval_queue view: {str(e)}")
        messages.error(request, 'An error occurred while loading the approval queue. Please try again.')
        return render(request, 'ParishRestructure/approval_queue.html', {
            'parishes': [],
            'dioceses': [],
            'error_message': 'Unable to load parish data at this time.'
        })


def approval_queue_datatables(request):
    """
    Handle DataTables server-side processing for approval queue data.
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
        1: 'parish__name',  # Parish Name (shifted due to checkbox column)
        2: 'diocese__name',  # Diocese
        3: 'date_applied',  # Applied Date
        4: 'id',  # Documents (calculated field)
        5: 'id',  # Actions (not sortable)
    }

    order_field = column_mapping.get(order_column_index, 'date_applied')

    # Base queryset
    queryset = ParishRegistration.objects.filter(date_approved__isnull=True).select_related('parish', 'diocese')

    # Apply search filter
    if search_value:
        queryset = queryset.filter(
            Q(parish__name__icontains=search_value) |
            Q(diocese__name__icontains=search_value) |
            Q(country__icontains=search_value) |
            Q(state__icontains=search_value) |
            Q(city__icontains=search_value)
        )

    # Get total records count (before filtering)
    total_records = ParishRegistration.objects.filter(date_approved__isnull=True).count()

    # Get filtered records count
    records_filtered = queryset.count()

    # Apply ordering
    if order_direction == 'desc':
        queryset = queryset.order_by(f'-{order_field}')
    else:
        queryset = queryset.order_by(order_field)

    # Apply pagination
    queryset = queryset[start:start + length]

    # Prepare data for DataTables
    data = []
    for registration in queryset:
        # Calculate document completion
        doc_count = sum([
            registration.application_for_registration or False,
            registration.original_receipt_of_land or False,
            registration.original_survey_plan or False,
            registration.building_plan or False,
            registration.sworn_affidavit or False,
            registration.passport_photograph or False,
            registration.payment_proof_of_auditorium or False,
            registration.approval_from_government_diaspora or False
        ])
        completion_percentage = (doc_count / 8) * 100

        # Progress bar for documents
        if completion_percentage == 100:
            progress_class = 'bg-success'
            status_text = 'Complete'
        elif completion_percentage >= 50:
            progress_class = 'bg-warning'
            status_text = 'Partial'
        else:
            progress_class = 'bg-danger'
            status_text = 'Incomplete'

        progress_bar = f'''
            <div class="progress" style="height: 20px;">
                <div class="progress-bar {progress_class}" role="progressbar"
                     style="width: {completion_percentage}%" aria-valuenow="{completion_percentage}"
                     aria-valuemin="0" aria-valuemax="100">
                    {doc_count}/8 ({completion_percentage:.0f}%)
                </div>
            </div>
            <small class="text-muted">{status_text}</small>
        '''

        row = {
            'DT_RowId': f'row_{registration.id}',
            'parish_name': f'''
                <div class="d-flex align-items-center">
                    <div class="avatar-wrapper me-3">
                        <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center avatar-sm" style="width: 40px; height: 40px;">
                            <i class="fas fa-building"></i>
                        </div>
                    </div>
                    <div>
                        <div class="fw-semibold text-dark">{registration.parish.name}</div>
                        <small class="text-muted">{registration.city or 'N/A'}, {registration.state or 'N/A'}</small>
                    </div>
                </div>
            ''',
            'diocese': registration.diocese.name if registration.diocese else 'N/A',
            'date_applied': registration.date_applied.strftime('%B %d, %Y') if registration.date_applied else 'N/A',
            'documents': progress_bar,
            'actions': f'''
                <div class="action-buttons d-flex justify-content-center align-items-center gap-1">
                    <a href="/parish/view-regparish/{registration.id}/" class="btn btn-xs btn-outline-primary" title="View Details" data-bs-toggle="tooltip">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="/parish/approve/{registration.id}/" class="btn btn-xs btn-outline-success" title="Approve" data-bs-toggle="tooltip" onclick="return confirm('Are you sure you want to approve this parish registration?')">
                        <i class="fas fa-check"></i>
                    </a>
                    <a href="/parish/reject/{registration.id}/" class="btn btn-xs btn-outline-danger" title="Reject" data-bs-toggle="tooltip" onclick="return confirm('Are you sure you want to reject this parish registration?')">
                        <i class="fas fa-times"></i>
                    </a>
                </div>
            '''
        }
        data.append(row)

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': records_filtered,
        'data': data
    }

    return JsonResponse(response)


@login_required
def approved(request):
    """
    Display approved parishes with enhanced filtering and context.

    This view provides a comprehensive approved parishes list with:
    - Diocese-based filtering
    - Approval date tracking
    - Enhanced error handling
    - Statistics and summary information
    """
    try:
        # Check if this is a DataTables AJAX request
        if request.GET.get('draw'):
            return approved_datatables(request)

        # Get filter parameters
        diocese_filter = request.GET.get('diocese', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        # Base queryset for approved parishes
        parishes_queryset = ParishRegistration.objects.filter(date_approved__isnull=False).select_related('parish', 'diocese')

        # Apply diocese filter if specified
        if diocese_filter:
            try:
                diocese_id = int(diocese_filter)
                parishes_queryset = parishes_queryset.filter(diocese_id=diocese_id)
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid diocese filter provided.')

        # Apply date range filter if specified
        if date_from:
            try:
                from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                parishes_queryset = parishes_queryset.filter(date_approved__date__gte=from_date)
            except ValueError:
                messages.warning(request, 'Invalid date format for start date.')

        if date_to:
            try:
                to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                parishes_queryset = parishes_queryset.filter(date_approved__date__lte=to_date)
            except ValueError:
                messages.warning(request, 'Invalid date format for end date.')

        # Get parishes with ordering (most recently approved first)
        parishes = parishes_queryset.order_by('-date_approved')

        # Get all dioceses for filter dropdown
        dioceses = Location.objects.filter(level='diocese').order_by('name')

        # Calculate statistics
        total_approved = ParishRegistration.objects.filter(date_approved__isnull=False).count()
        recent_approvals = ParishRegistration.objects.filter(
            date_approved__isnull=False,
            date_approved__gte=timezone.now() - timedelta(days=30)
        ).count()

        # Get approval trends (last 6 months) - simplified
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_queryset = ParishRegistration.objects.filter(
            date_approved__isnull=False,
            date_approved__gte=six_months_ago
        )

        # Simple count for now
        monthly_approvals_count = monthly_queryset.count()
        monthly_approvals = [{'count': monthly_approvals_count}] if monthly_approvals_count > 0 else []

        # Enhanced context
        context = {
            'parishes': parishes,
            'dioceses': dioceses,
            'current_diocese': diocese_filter,
            'date_from': date_from,
            'date_to': date_to,
            'total_count': total_approved,
            'active_count': total_approved,  # All approved parishes are active
            'pending_count': 0,  # No pending in approved view
            'recent_count': recent_approvals,
            'total_approved': total_approved,
            'recent_approvals': recent_approvals,
            'monthly_approvals': list(monthly_approvals),
            'page_title': 'Approved Parishes',
            'page_subtitle': f'View {total_approved} approved parish registrations',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'Approved Parishes', 'url': None, 'active': True}
            ]
        }

        return render(request, 'ParishRestructure/approved.html', context)

    except Exception as e:
        logger.error(f"Error in approved view: {str(e)}")
        messages.error(request, 'An error occurred while loading approved parishes. Please try again.')
        return render(request, 'ParishRestructure/approved.html', {
            'parishes': [],
            'dioceses': [],
            'total_count': 0,
            'recent_count': 0,
            'monthly_approvals': [],
            'error_message': 'Unable to load parish data at this time.'
        })


def approved_datatables(request):
    """
    Handle DataTables server-side processing for approved parishes data.
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
        1: 'parish__name',  # Parish Name (shifted due to checkbox column)
        2: 'diocese__name',  # Diocese
        3: 'date_approved',  # Approval Date
        4: 'date_issued_certificate',  # Certificate Date (not sortable, but included for consistency)
        5: 'id',  # Actions (not sortable)
    }

    order_field = column_mapping.get(order_column_index, 'date_approved')

    # Base queryset
    queryset = ParishRegistration.objects.filter(date_approved__isnull=False).select_related('parish', 'diocese')

    # Apply search filter
    if search_value:
        queryset = queryset.filter(
            Q(parish__name__icontains=search_value) |
            Q(diocese__name__icontains=search_value) |
            Q(country__icontains=search_value) |
            Q(state__icontains=search_value) |
            Q(city__icontains=search_value)
        )

    # Get total records count (before filtering)
    total_records = ParishRegistration.objects.filter(date_approved__isnull=False).count()

    # Get filtered records count
    records_filtered = queryset.count()

    # Apply ordering
    if order_direction == 'desc':
        queryset = queryset.order_by(f'-{order_field}')
    else:
        queryset = queryset.order_by(order_field)

    # Apply pagination
    queryset = queryset[start:start + length]

    # Prepare data for DataTables
    data = []
    for registration in queryset:
        row = {
            'DT_RowId': f'row_{registration.id}',
            'checkbox': f'<div class="form-check"><input class="form-check-input row-checkbox" type="checkbox" value="{registration.id}" id="check-{registration.id}"></div>',
            'parish_name': f'''
                <div class="d-flex align-items-center">
                    <div class="avatar-wrapper me-3">
                        <div class="bg-success text-white rounded-circle d-flex align-items-center justify-content-center avatar-sm" style="width: 40px; height: 40px;">
                            <i class="fas fa-check"></i>
                        </div>
                    </div>
                    <div>
                        <div class="fw-semibold text-dark">{registration.parish.name}</div>
                        <small class="text-muted">{registration.city or 'N/A'}, {registration.state or 'N/A'}</small>
                    </div>
                </div>
            ''',
            'diocese': registration.diocese.name if registration.diocese else 'N/A',
            'date_approved': registration.date_approved.strftime('%B %d, %Y') if registration.date_approved else 'N/A',
            'certificate_date': registration.date_issued_certificate.strftime('%B %d, %Y') if registration.date_issued_certificate else '<span class="text-muted">Pending</span>',
            'actions': f'''
                <div class="action-buttons d-flex justify-content-center align-items-center gap-1">
                    <a href="{reverse("view-parish", args=[registration.id])}" class="btn btn-xs btn-outline-primary" title="View Details" data-bs-toggle="tooltip">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="{reverse("edit_regparish", args=[registration.id])}" class="btn btn-xs btn-outline-success" title="Edit Registration" data-bs-toggle="tooltip">
                        <i class="fas fa-edit"></i>
                    </a>
                    <a href="/parish/generate_parish_pdf/{registration.id}/" class="btn btn-xs btn-outline-secondary" title="Download Certificate" data-bs-toggle="tooltip" target="_blank">
                        <i class="fas fa-download"></i>
                    </a>
                </div>
            '''
        }
        data.append(row)

    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': records_filtered,
        'data': data
    }

    return JsonResponse(response)


@login_required  
def view_regparish(request, pk):
    """View a single registered parish with complete details."""
    try:
        parish = get_object_or_404(ParishRegistration, pk=pk)
        
        # Additional context for the detail layout
        context = {
            'parish': parish,
            'page_title': f'CCC {parish.parish.name}',
            'page_subtitle': 'Complete Registered Parish Information',
            'breadcrumb_items': [
                {'title': 'Dashboard', 'url': 'parish_dashboard'},
                {'title': 'Registered Parishes', 'url': 'approved'},
                {'title': 'Parish Details', 'url': None, 'active': True}
            ],
            'document_count': sum([
                parish.application_for_registration,
                parish.original_receipt_of_land,
                parish.original_survey_plan,
                parish.building_plan,
                parish.sworn_affidavit,
                parish.passport_photograph,
                parish.payment_proof_of_auditorium,
                parish.approval_from_government_diaspora
            ]),
            'total_documents': 8,
            'completion_percentage': round(sum([
                parish.application_for_registration,
                parish.original_receipt_of_land,
                parish.original_survey_plan,
                parish.building_plan,
                parish.sworn_affidavit,
                parish.passport_photograph,
                parish.payment_proof_of_auditorium,
                parish.approval_from_government_diaspora
            ]) / 8 * 100, 1),
        }
        
        return render(request, 'ParishRestructure/view_regparish.html', context)
        
    except ParishRegistration.DoesNotExist:
        messages.error(request, 'The requested registered parish could not be found.')
        return redirect('approved')
    except Exception as e:
        logger.error(f"Error in view_regparish for pk={pk}: {str(e)}")
        messages.error(request, 'An error occurred while loading the parish details. Please try again.')
        return redirect('approved')


@login_required
def bulk_export_approved(request):
    """
    Export selected approved parishes to CSV format.

    This view handles bulk export of approved parish data to CSV format
    for reporting and data analysis purposes.
    """
    try:
        # Get selected parish IDs from POST data
        selected_ids = request.POST.getlist('selected_parishes[]')

        if not selected_ids:
            messages.error(request, 'No parishes selected for export.')
            return redirect('approved')

        # Validate IDs are integers
        try:
            parish_ids = [int(pid) for pid in selected_ids]
        except (ValueError, TypeError):
            messages.error(request, 'Invalid parish selection.')
            return redirect('approved')

        # Get approved parishes
        parishes = ParishRegistration.objects.filter(
            id__in=parish_ids,
            date_approved__isnull=False
        ).select_related('parish', 'diocese').order_by('-date_approved')

        if not parishes.exists():
            messages.error(request, 'No valid approved parishes found for export.')
            return redirect('approved')

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="approved_parishes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Parish ID', 'Parish Name', 'Address', 'Diocese', 'Date Applied',
            'Date Approved', 'Application Complete', 'Land Receipt', 'Survey Plan',
            'Building Plan', 'Affidavit', 'Photograph', 'Payment Proof', 'Government Approval'
        ])

        for parish in parishes:
            writer.writerow([
                parish.id,
                parish.parish.name if parish.parish else '',
                parish.parish.address if parish.parish else '',
                parish.diocese.name if parish.diocese else '',
                parish.date_applied.strftime('%Y-%m-%d') if parish.date_applied else '',
                parish.date_approved.strftime('%Y-%m-%d') if parish.date_approved else '',
                'Yes' if parish.application_for_registration else 'No',
                'Yes' if parish.original_receipt_of_land else 'No',
                'Yes' if parish.original_survey_plan else 'No',
                'Yes' if parish.building_plan else 'No',
                'Yes' if parish.sworn_affidavit else 'No',
                'Yes' if parish.passport_photograph else 'No',
                'Yes' if parish.payment_proof_of_auditorium else 'No',
                'Yes' if parish.approval_from_government_diaspora else 'No'
            ])

        logger.info(f'Bulk export completed for {len(parishes)} approved parishes by user {request.user.username}')
        return response

    except Exception as e:
        logger.error(f"Error in bulk_export_approved: {str(e)}")
        messages.error(request, 'An error occurred during export. Please try again.')
        return redirect('approved')


@login_required
def bulk_delete_approved(request):
    """
    Bulk delete selected approved parishes.

    This view handles bulk deletion of approved parish registrations.
    Includes proper validation and error handling.
    """
    try:
        if request.method != 'POST':
            messages.error(request, 'Invalid request method.')
            return redirect('approved')

        # Get selected parish IDs from POST data
        selected_ids = request.POST.getlist('selected_parishes[]')

        if not selected_ids:
            messages.error(request, 'No parishes selected for deletion.')
            return redirect('approved')

        # Validate IDs are integers
        try:
            parish_ids = [int(pid) for pid in selected_ids]
        except (ValueError, TypeError):
            messages.error(request, 'Invalid parish selection.')
            return redirect('approved')

        # Get approved parishes to delete
        parishes_to_delete = ParishRegistration.objects.filter(
            id__in=parish_ids,
            date_approved__isnull=False
        ).select_related('parish')

        if not parishes_to_delete.exists():
            messages.error(request, 'No valid approved parishes found for deletion.')
            return redirect('approved')

        deleted_count = parishes_to_delete.count()
        parish_names = [p.parish.name for p in parishes_to_delete if p.parish]

        # Perform bulk delete
        parishes_to_delete.delete()

        logger.info(f'Bulk delete completed: {deleted_count} approved parishes deleted by user {request.user.username}')
        messages.success(request, f'Successfully deleted {deleted_count} approved parish(es).')

        return redirect('approved')

    except Exception as e:
        logger.error(f"Error in bulk_delete_approved: {str(e)}")
        messages.error(request, 'An error occurred during deletion. Please try again.')
        return redirect('approved')


@login_required
def bulk_edit_approved(request):
    """
    Bulk edit selected approved parishes.

    This view handles bulk editing of approved parish registrations.
    Allows updating common fields for multiple parishes at once.
    """
    try:
        if request.method != 'POST':
            messages.error(request, 'Invalid request method.')
            return redirect('approved')

        # Get selected parish IDs and edit data
        selected_ids = request.POST.getlist('selected_parishes[]')
        edit_action = request.POST.get('edit_action')

        if not selected_ids:
            messages.error(request, 'No parishes selected for editing.')
            return redirect('approved')

        if not edit_action:
            messages.error(request, 'No edit action specified.')
            return redirect('approved')

        # Validate IDs are integers
        try:
            parish_ids = [int(pid) for pid in selected_ids]
        except (ValueError, TypeError):
            messages.error(request, 'Invalid parish selection.')
            return redirect('approved')

        # Get parishes to edit
        parishes = ParishRegistration.objects.filter(
            id__in=parish_ids,
            date_approved__isnull=False
        )

        if not parishes.exists():
            messages.error(request, 'No valid approved parishes found for editing.')
            return redirect('approved')

        updated_count = 0

        if edit_action == 'mark_complete':
            # Mark all documents as complete
            updated_count = parishes.update(
                application_for_registration=True,
                original_receipt_of_land=True,
                original_survey_plan=True,
                building_plan=True,
                sworn_affidavit=True,
                passport_photograph=True,
                payment_proof_of_auditorium=True,
                approval_from_government_diaspora=True,
                updated_by=request.user
            )

        elif edit_action == 'mark_incomplete':
            # Mark all documents as incomplete
            updated_count = parishes.update(
                application_for_registration=False,
                original_receipt_of_land=False,
                original_survey_plan=False,
                building_plan=False,
                sworn_affidavit=False,
                passport_photograph=False,
                payment_proof_of_auditorium=False,
                approval_from_government_diaspora=False,
                updated_by=request.user
            )

        elif edit_action == 'update_diocese':
            new_diocese_id = request.POST.get('new_diocese')
            if new_diocese_id:
                try:
                    new_diocese = Location.objects.get(id=int(new_diocese_id), level='diocese')
                    updated_count = parishes.update(diocese=new_diocese, updated_by=request.user)
                except (ValueError, Location.DoesNotExist):
                    messages.error(request, 'Invalid diocese selected.')
                    return redirect('approved')

        if updated_count > 0:
            logger.info(f'Bulk edit completed: {edit_action} applied to {updated_count} parishes by user {request.user.username}')
            messages.success(request, f'Successfully updated {updated_count} parish(es).')
        else:
            messages.warning(request, 'No parishes were updated.')

        return redirect('approved')

    except Exception as e:
        logger.error(f"Error in bulk_edit_approved: {str(e)}")
        messages.error(request, 'An error occurred during bulk edit. Please try again.')
        return redirect('approved')