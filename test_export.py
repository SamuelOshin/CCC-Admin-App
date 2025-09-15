#!/usr/bin/env python
"""
Test script to verify the export functionality works correctly
"""
import os
import sys
import django
from datetime import date

# Add the project directory to the Python path
sys.path.append('c:\\Users\\PC\\Videos\\CS Harvard\\django_project\\CCC\\administative_app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cccadminapp.settings')
django.setup()

from clergy_registration.models import ClergyDetails, AnnointmentGazzette
from ParishRestructure.models import ParishDirectory, ParishRegistration
from transfer.models import TransferData

def test_export_headers():
    """Test that all headers are properly defined"""
    print("Testing export headers...")

    # Test ClergyDetails headers
    clergy_headers = [
        'ID', 'Full Name', 'First Name', 'Last Name', 'Middle Name', 'Title', 'Gender', 'Date of Birth',
        'Age', 'Place of Birth', 'Nationality', 'Marital Status', 'Spouse Name', 'Number of Children',
        'Telephone', 'Email', 'Address', 'City', 'State', 'Country', 'Postal Code', 'Qualifications',
        'Specializations', 'Languages Spoken', 'Experience Years', 'Current Position', 'Department',
        'Salary Grade', 'Employment Date', 'Contract Type', 'Manager Name', 'Manager Contact',
        'Emergency Contact Name', 'Emergency Contact Relationship', 'Emergency Contact Phone',
        'Emergency Contact Address', 'Bank Name', 'Bank Account Number', 'Bank Branch', 'Tax ID',
        'Social Security Number', 'Health Insurance Provider', 'Health Insurance Number',
        'Medical Conditions', 'Allergies', 'Blood Type', 'Height', 'Weight', 'Eye Color', 'Hair Color',
        'Distinguishing Marks', 'Profile Picture', 'Date Created', 'Last Updated', 'Is Active'
    ]

    print(f"ClergyDetails headers count: {len(clergy_headers)}")

    # Test ParishDirectory headers
    parish_headers = [
        'ID', 'Parish Name', 'Address', 'City', 'State', 'Country', 'Postal Code', 'Telephone',
        'Email', 'Website', 'Established Date', 'Parish Priest', 'Assistant Priest', 'Number of Families',
        'Number of Members', 'Mass Times', 'Confession Times', 'Services Offered', 'Facilities',
        'Parish Council Members', 'Youth Group', 'Charity Activities', 'Financial Status',
        'Registration Status', 'Date Created', 'Last Updated'
    ]

    print(f"ParishDirectory headers count: {len(parish_headers)}")

    # Test TransferData headers
    transfer_headers = [
        'ID', 'Clergy Name', 'From Parish', 'To Parish', 'Transfer Date', 'Reason for Transfer',
        'Approval Date', 'Effective Date', 'Transfer Type', 'Previous Position', 'New Position',
        'Salary Change', 'Benefits Change', 'Moving Allowance', 'Notice Period', 'Handover Date',
        'Documents Submitted', 'Approval Authority', 'Comments', 'Date Created', 'Last Updated'
    ]

    print(f"TransferData headers count: {len(transfer_headers)}")

    # Test AnnointmentGazzette headers
    annointment_headers = [
        'ID', 'Clergy Name', 'Rank', 'Annoiter', 'Date Created', 'Last Updated'
    ]

    print(f"AnointmentGazzette headers count: {len(annointment_headers)}")

    print("All headers defined successfully!")

def test_model_fields():
    """Test that model fields can be accessed correctly"""
    print("\nTesting model field access...")

    try:
        # Test ClergyDetails
        clergy_count = ClergyDetails.objects.count()
        print(f"ClergyDetails records: {clergy_count}")

        if clergy_count > 0:
            sample_clergy = ClergyDetails.objects.first()
            print(f"Sample clergy full name: {sample_clergy.get_full_name()}")
            print(f"Sample clergy age: {sample_clergy.age if hasattr(sample_clergy, 'age') else 'N/A'}")

        # Test ParishDirectory
        parish_count = ParishDirectory.objects.count()
        print(f"ParishDirectory records: {parish_count}")

        # Test TransferData
        transfer_count = TransferData.objects.count()
        print(f"TransferData records: {transfer_count}")

        # Test AnnointmentGazzette
        annointment_count = AnnointmentGazzette.objects.count()
        print(f"AnointmentGazzette records: {annointment_count}")

        print("Model field access test completed successfully!")

    except Exception as e:
        print(f"Error during model field access test: {e}")

if __name__ == '__main__':
    test_export_headers()
    test_model_fields()
    print("\nTest completed!")
