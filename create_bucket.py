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

def create_bucket():
    """Create a new Supabase Storage bucket with S3-compatible naming"""
    try:
        url = config('SUPABASE_URL')
        key = config('SUPABASE_SECRET_KEY')
        new_bucket_name = 'ccc-admin-media'

        client = storage3.create_client(url + '/storage/v1', headers={'Authorization': f'Bearer {key}', 'apiKey': key}, is_async=False)

        # Check if bucket already exists
        buckets = client.list_buckets()
        existing_names = [bucket.name for bucket in buckets]

        if new_bucket_name in existing_names:
            print(f'✅ Bucket "{new_bucket_name}" already exists')
            return True

        # Create new bucket
        result = client.create_bucket(new_bucket_name)
        print(f'✅ Successfully created bucket: {new_bucket_name}')
        print(f'   Result: {result}')

        # Verify bucket was created
        buckets = client.list_buckets()
        if any(bucket.name == new_bucket_name for bucket in buckets):
            print(f'✅ Bucket "{new_bucket_name}" verified in storage')
            return True
        else:
            print(f'❌ Bucket "{new_bucket_name}" was not found after creation')
            return False

    except Exception as e:
        print(f'❌ Error creating bucket: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_bucket()
    sys.exit(0 if success else 1)