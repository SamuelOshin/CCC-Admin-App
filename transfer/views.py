from django.shortcuts import render, redirect, get_object_or_404, redirect
from .forms import TransferDataForm, ClergyTrfbioForm, PostinghistoryForm
from .models import ClergyDetails, ClergyTrfbio, TransferData, ParishRestructure, PostingHistory
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dal import autocomplete
from django.db.models import Q, Count
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import ParishRestructureSerializer
import datetime
from django.utils import timezone
from django.db import models

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
    
    # Get current designation from most recent posting history
    current_designation = None
    try:
        latest_posting = PostingHistory.objects.filter(clergy=clergy).order_by('-date_of_entry').first()
        if latest_posting:
            current_designation = latest_posting.designation
    except:
        current_designation = None

    if request.method == 'POST':
        transfer_form = TransferDataForm(request.POST)
        if transfer_form.is_valid():
            transfer_instance = transfer_form.save(commit=False)
            transfer_instance.clergy = clergy  # Associate the transfer with the clergy
            transfer_instance.save()
            
            # After saving the transfer, call the method to update floating status
            clergy.clergytrfbio.update_floating_status()
            messages.success(request, 'Transfer Successfully Done.')
            return render(request, 'transfer/trfForm.html', {'transfer_form': transfer_form, 'clergy': clergy,'parishes': parishes, 'current_designation': current_designation})
        else:
            messages.error(request, 'Something went wrong, Check Form Fields.')
    else:
        transfer_form = TransferDataForm(initial={'clergy': clergy})
    
    context = {
        'transfer_form': transfer_form, 
        'clergy': clergy,
        'parishes': parishes,
        'current_designation': current_designation,
    }    

    return render(request, 'transfer/trfForm.html', context)

@login_required
def new_trf_table(request):
    # Fetch all transfer data with associated clergy details
    trf_data_with_clergy = TransferData.objects.select_related('clergy', 'parishFrm__parish', 'parishTo__parish').order_by('-date_transfered')

    # Calculate statistics for dashboard
    total_transfers = trf_data_with_clergy.count()
    pending_transfers = trf_data_with_clergy.filter(trf_status='Pending').count()
    approved_transfers = trf_data_with_clergy.filter(trf_status='Approved').count()

    # Calculate recent transfers (this month)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_transfers = trf_data_with_clergy.filter(date_transfered__gte=thirty_days_ago).count()

    # Get all parishes for filter dropdown
    parishes = ParishRestructure.objects.select_related('parish').all()

    # Pass the data to the template with enhanced context
    context = {
        'trf_data_with_clergy': trf_data_with_clergy,
        'total_transfers': total_transfers,
        'pending_transfers': pending_transfers,
        'approved_transfers': approved_transfers,
        'recent_transfers': recent_transfers,
        'parishes': parishes,
    }

    return render(request, 'transfer/trfTable.html', context)
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
    transfer_form.fields.pop('date_transffered', None)
    
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
    parishes = ParishRestructure.objects.all()
    transfer_form = TransferDataForm(instance=transfer_instance)
    context = {
        'transfer_form': transfer_form,
        'clergy': clergy,
        'parishes': parishes,
        'transfer_id': transfer_instance.id,
    }
    return render(request, 'transfer/view_transfer.html', context)
@login_required
def clergy_details(request):
    # Get base queryset
    clergy_queryset = ClergyTrfbio.objects.select_related('clergy').all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        clergy_queryset = clergy_queryset.filter(
            Q(clergy__first_name__icontains=search_query) |
            Q(clergy__last_name__icontains=search_query) |
            Q(clergy__telephone__icontains=search_query) |
            Q(clergy__email_address__icontains=search_query)
        )

    # Filter by floating status
    floating_filter = request.GET.get('floating', '')
    if floating_filter == 'floating':
        clergy_queryset = clergy_queryset.filter(floating=True)
    elif floating_filter == 'not_floating':
        clergy_queryset = clergy_queryset.filter(floating=False)

    # Get statistics
    total_clergy = ClergyTrfbio.objects.count()
    floating_clergy = ClergyTrfbio.objects.filter(floating=True).count()
    not_floating_clergy = ClergyTrfbio.objects.filter(floating=False).count()

    # Get recent transfers for context
    recent_transfers = TransferData.objects.select_related(
        'clergy', 'parishTo'
    ).order_by('-date_transfered')[:5]

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(clergy_queryset, 25)  # 25 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'clergy': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'floating_filter': floating_filter,

        # Statistics for dashboard cards
        'total_clergy': total_clergy,
        'floating_clergy': floating_clergy,
        'not_floating_clergy': not_floating_clergy,
        'recent_transfers': recent_transfers,

        # Page metadata
        'page_title': 'Clergy Transfer Management',
        'page_subtitle': 'Select clergy members for transfer operations',
        'table_title': 'Available Clergy for Transfer',
        'table_subtitle': f'Showing {page_obj.start_index()}-{page_obj.end_index()} of {total_clergy} clergy members',

        # Action URLs
        'new_transfer_url': 'new_transfer',
        'posting_history_url': 'posting',
        'dashboard_url': 't_dashboard',
    }

    return render(request, 'transfer/clergyt_new.html', context)

@login_required
@user_passes_test(is_transfer_admin)
def transfer_dashboard(request):
    # Get transfer statistics
    total_transfers = TransferData.objects.count()
    pending_transfers = TransferData.objects.filter(trf_status='Pending').count()
    approved_transfers = TransferData.objects.filter(trf_status='Approved').count()
    withdrawn_transfers = TransferData.objects.filter(trf_status='Withdrawn').count()
    
    # Get recent transfers (last 30 days)
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    recent_transfers = TransferData.objects.filter(
        date_transfered__gte=thirty_days_ago
    ).select_related('clergy', 'parishTo').order_by('-date_transfered')[:10]
    
    # Get floating clergy count
    floating_clergy = ClergyTrfbio.objects.filter(floating=True).count()
    
    # Get transfers by status for chart data
    status_counts = TransferData.objects.values('trf_status').annotate(
        count=models.Count('trf_status')
    ).order_by('trf_status')
    
    # Get monthly transfer trends (last 6 months)
    six_months_ago = timezone.now().date() - timezone.timedelta(days=180)
    monthly_transfers = TransferData.objects.filter(
        date_transfered__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', date_transfered)"}
    ).values('month').annotate(
        count=models.Count('id')
    ).order_by('month')
    
    context = {
        'total_transfers': total_transfers,
        'pending_transfers': pending_transfers,
        'approved_transfers': approved_transfers,
        'withdrawn_transfers': withdrawn_transfers,
        'floating_clergy': floating_clergy,
        'recent_transfers': recent_transfers,
        'status_counts': list(status_counts),
        'monthly_transfers': list(monthly_transfers),
        'app_title': 'Transfer Management System',
    }
    
    return render(request, 'transfer/dashboard_new.html', context)

@login_required
def view_add_posting(request, id):
    """
    View for managing posting history for a specific clergy member.
    Handles both displaying existing posting history and adding new records.
    """
    clergy = get_object_or_404(ClergyDetails, clergy_id=id)

    if request.method == 'POST':
        posting_form = PostinghistoryForm(request.POST)
        if posting_form.is_valid():
            posting_instance = posting_form.save(commit=False)
            posting_instance.clergy = clergy
            posting_instance.save()
            messages.success(request, f'Posting history successfully added for {clergy}.')
            # Redirect to refresh the page and show updated list
            return redirect('posting', id=id)
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        posting_form = PostinghistoryForm(initial={'clergy': clergy})

    # Get all posting history for this clergy, ordered by most recent first
    posts = PostingHistory.objects.filter(clergy=clergy).order_by('-date_of_entry')

    context = {
        'posting_form': posting_form,
        'clergy': clergy,
        'posts': posts,
        'page_title': f'Posting History - {clergy}',
        'page_subtitle': f'Manage posting history records for {clergy}',
    }

    return render(request, 'transfer/postingH_form.html', context)


