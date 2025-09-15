#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cccadminapp.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from ParishRestructure.models import ParishDirectory, ParishRegistration
from transfer.models import TransferData
from clergy_registration.models import ClergyDetails, AnnointmentGazzette

def test_querysets():
    print("Testing querysets...")

    # Test ParishDirectory queryset
    try:
        pd_queryset = ParishDirectory.objects.all()
        print(f'ParishDirectory queryset: {pd_queryset.count()} records')
        if pd_queryset.exists():
            print(f'First record: {pd_queryset.first().name}')
    except Exception as e:
        print(f'ParishDirectory error: {e}')

    # Test ParishRegistration queryset
    try:
        pr_queryset = ParishRegistration.objects.select_related('parish', 'diocese')
        print(f'ParishRegistration queryset: {pr_queryset.count()} records')
        if pr_queryset.exists():
            first = pr_queryset.first()
            parish_name = first.parish.name if first.parish else "No parish"
            diocese_name = first.diocese.name if first.diocese else "No diocese"
            print(f'First record: {parish_name} - {diocese_name}')
    except Exception as e:
        print(f'ParishRegistration error: {e}')

    # Test TransferData queryset
    try:
        td_queryset = TransferData.objects.select_related('clergy', 'parishFrm', 'parishTo')
        print(f'TransferData queryset: {td_queryset.count()} records')
        if td_queryset.exists():
            first = td_queryset.first()
            clergy_name = first.clergy.get_full_name() if first.clergy else "No clergy"
            from_parish = first.parishFrm.parish.name if first.parishFrm and first.parishFrm.parish else "No from parish"
            print(f'First record: {clergy_name} - {from_parish}')
    except Exception as e:
        print(f'TransferData error: {e}')

    # Test AnnointmentGazzette queryset
    try:
        ag_queryset = AnnointmentGazzette.objects.select_related('clergy')
        print(f'AnnoinmentGazzette queryset: {ag_queryset.count()} records')
        if ag_queryset.exists():
            first = ag_queryset.first()
            clergy_name = first.clergy.get_full_name() if first.clergy else "No clergy"
            print(f'First record: {clergy_name}')
    except Exception as e:
        print(f'AnnoinmentGazzette error: {e}')

    print('All tests completed!')

if __name__ == '__main__':
    test_querysets()
