import os
from decouple import config

print('=== Supabase Storage Configuration Check ===')
print(f'SUPABASE_URL: {config("SUPABASE_URL")}')
print(f'SUPABASE_ACCESS_KEY: {"***" + config("SUPABASE_ACCESS_KEY")[-4:] if config("SUPABASE_ACCESS_KEY") else "NOT SET"}')
print(f'SUPABASE_SECRET_KEY: {"***" + config("SUPABASE_SECRET_KEY")[-4:] if config("SUPABASE_SECRET_KEY") else "NOT SET"}')
print(f'SUPABASE_STORAGE_BUCKET: {config("SUPABASE_STORAGE_BUCKET")}')
print()

# Test S3 connection
try:
    import boto3
    from botocore.client import Config

    s3_client = boto3.client(
        's3',
        aws_access_key_id=config('SUPABASE_ACCESS_KEY'),
        aws_secret_access_key=config('SUPABASE_SECRET_KEY'),
        endpoint_url=f"{config('SUPABASE_URL')}/storage/v1/s3",
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # List buckets
    response = s3_client.list_buckets()
    print('✅ S3 Connection successful')
    print('Available buckets:')
    for bucket in response['Buckets']:
        print(f'  - {bucket["Name"]}')

    # Check if our bucket exists
    bucket_name = config('SUPABASE_STORAGE_BUCKET')
    bucket_exists = any(b['Name'] == bucket_name for b in response['Buckets'])
    print(f'\nTarget bucket "{bucket_name}" exists: {bucket_exists}')

except Exception as e:
    print(f'❌ S3 Connection failed: {e}')
    import traceback
    traceback.print_exc()