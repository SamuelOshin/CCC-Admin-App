#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cccadminapp.settings')
django.setup()

import storage3
from decouple import config

def check_buckets():
    """Check available Supabase Storage buckets"""
    try:
        url = config('SUPABASE_URL')
        key = config('SUPABASE_SECRET_KEY')

        client = storage3.create_client(url + '/storage/v1', headers={'Authorization': f'Bearer {key}', 'apiKey': key}, is_async=False)
        buckets = client.list_buckets()

        print('Available Supabase Storage buckets:')
        print('=' * 40)
        for bucket in buckets:
            print(f'  - Name: {bucket.name}')
            print(f'    ID: {bucket.id}')
            print(f'    Created: {getattr(bucket, "created_at", "N/A")}')
            print()

        if not buckets:
            print('No buckets found. Please create a bucket in Supabase Dashboard.')

        return buckets

    except Exception as e:
        print(f'Error checking buckets: {e}')
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    check_buckets()