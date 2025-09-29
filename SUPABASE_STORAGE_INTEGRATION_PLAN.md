# Supabase Storage Integration Plan for Django Application

## Overview
This document outlines the comprehensive plan to integrate Supabase Storage as the new media storage backend for the CCC Administrative Application, replacing the current local file system storage.

**Current Configuration:**
- MEDIA_URL: `/media/`
- MEDIA_ROOT: `BASE_DIR/cccadminapp/media` (local file system)
- Storage Backend: FileSystemStorage

**Target Configuration:**
- Storage Service: Supabase Storage (S3-compatible)
- Benefits: Scalable, secure, CDN-enabled file storage

## Prerequisites
- Active Supabase project with Storage enabled
- Supabase API keys (URL, anon key, service role key)
- Dedicated storage bucket for media files

## Detailed Implementation Steps

### 1. Research and Setup Dependencies
**Objective:** Install and configure required packages for Supabase Storage integration.

**Tasks:**
- Install `django-storages` for Django storage backends
- Install `boto3` for S3-compatible API interactions
- Confirm Supabase Storage S3 compatibility
- Update `requirements.txt`:
  ```
  django-storages>=1.14.2
  boto3>=1.34.0
  ```

**Expected Outcome:** All dependencies installed and compatible with Django 4.2.5.

### 2. Create Supabase Storage Bucket
**Objective:** Set up a dedicated bucket for media files in Supabase.

**Tasks:**
- Access Supabase Dashboard → Storage
- Create new bucket named `media` or `django-media`
- Configure bucket settings:
  - Public: False (serve via Django for security)
  - File Size Limit: 50MB (adjust based on needs)
  - Allowed MIME Types: images/*, application/pdf, etc.
- Document bucket ID for configuration

**Expected Outcome:** Private bucket ready for media file storage.

### 3. Update Django Settings Configuration
**Objective:** Configure Django to use Supabase Storage instead of local filesystem.

**Tasks:**
- Add `storages` to `INSTALLED_APPS`
- Configure environment variables in `.env`:
  ```
  SUPABASE_URL=https://your-project-id.supabase.co
  SUPABASE_ACCESS_KEY=your-anon-key
  SUPABASE_SECRET_KEY=your-service-role-key
  SUPABASE_STORAGE_BUCKET=media
  ```
- Update `settings.py` storage configuration:
  ```python
  # Supabase Storage Configuration
  AWS_ACCESS_KEY_ID = config('SUPABASE_ACCESS_KEY')
  AWS_SECRET_ACCESS_KEY = config('SUPABASE_SECRET_KEY')
  AWS_STORAGE_BUCKET_NAME = config('SUPABASE_STORAGE_BUCKET')
  AWS_S3_ENDPOINT_URL = f"{config('SUPABASE_URL')}/storage/v1/s3"
  AWS_S3_REGION_NAME = 'us-east-1'
  AWS_S3_CUSTOM_DOMAIN = f"{config('SUPABASE_URL').replace('https://', '')}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

  STORAGES = {
      "default": {
          "BACKEND": "storages.backends.s3.S3Storage",
          "OPTIONS": {
              "bucket_name": AWS_STORAGE_BUCKET_NAME,
              "endpoint_url": AWS_S3_ENDPOINT_URL,
              "access_key": AWS_ACCESS_KEY_ID,
              "secret_key": AWS_SECRET_ACCESS_KEY,
              "region_name": AWS_S3_REGION_NAME,
              "file_overwrite": False,
              "querystring_auth": True,
          },
      },
      "staticfiles": {
          "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
      },
  }

  # Update MEDIA_URL
  MEDIA_URL = f"https://{config('SUPABASE_URL').replace('https://', '')}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}/"
  ```

**Expected Outcome:** Django configured to use Supabase Storage for media files.

### 4. Implement Storage Security Policies
**Objective:** Set up Row Level Security (RLS) policies for proper access control.

**Tasks:**
- Create RLS policies in Supabase SQL Editor:
  ```sql
  -- Allow authenticated users to upload to media bucket
  CREATE POLICY "Allow authenticated uploads" ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'media');

  -- Allow users to access their own uploaded files
  CREATE POLICY "Allow users to access own files" ON storage.objects
  FOR SELECT TO authenticated
  USING (bucket_id = 'media' AND auth.uid()::text = (storage.foldername(name))[1]);

  -- Allow public read access for certain file types (if needed)
  CREATE POLICY "Public read access" ON storage.objects
  FOR SELECT TO public
  USING (bucket_id = 'media' AND storage.extension(name) IN ('jpg', 'png', 'pdf'));
  ```
- Test policies with different user roles

**Expected Outcome:** Secure access control for media files based on authentication.

### 5. Update File Upload Handling
**Objective:** Ensure Django models and forms work with the new storage backend.

**Tasks:**
- Review all models using `FileField` or `ImageField`
- Test file upload forms in Django admin
- Update any custom file handling in views
- Verify file validation and processing

**Expected Outcome:** All file uploads work seamlessly with Supabase Storage.

### 6. Migrate Existing Media Files
**Objective:** Move current media files from local storage to Supabase.

**Tasks:**
- Create Django management command for migration:
  ```python
  # management/commands/migrate_media.py
  from django.core.management.base import BaseCommand
  from django.core.files.storage import default_storage
  import os

  class Command(BaseCommand):
      def handle(self, *args, **options):
          media_root = 'cccadminapp/media'
          for root, dirs, files in os.walk(media_root):
              for file in files:
                  file_path = os.path.join(root, file)
                  relative_path = os.path.relpath(file_path, media_root)
                  with open(file_path, 'rb') as f:
                      default_storage.save(relative_path, f)
  ```
- Run migration: `python manage.py migrate_media`
- Update any hardcoded file paths in templates/views
- Verify all existing files are accessible

**Expected Outcome:** All existing media files migrated to Supabase Storage.

### 7. Testing and Validation
**Objective:** Thoroughly test the integration for reliability and performance.

**Test Cases:**
- File uploads through Django admin and user forms
- File downloads and display in templates
- Access control (public vs private files)
- Error handling for upload failures
- Performance with various file sizes
- Image transformations (if implemented)

**Expected Outcome:** Integration fully tested and validated.

## Benefits of Integration
- **Scalability:** Handle growing media storage needs
- **Performance:** CDN delivery for faster file access
- **Security:** RLS policies for fine-grained access control
- **Cost Efficiency:** Pay only for storage used
- **Reliability:** Automatic backups and redundancy

## Potential Challenges & Mitigations
- **Migration Complexity:** Plan migration during low-traffic periods
- **Cost Monitoring:** Set up alerts for storage usage
- **Latency:** Implement caching strategies if needed
- **Dependencies:** Test deployment with new packages

## Rollback Plan
- Keep local storage as backup during transition
- Document all configuration changes
- Test rollback procedure before full migration
- Maintain backup of all media files locally

## Timeline Estimate
- Research & Dependencies: 1-2 days
- Bucket Setup & Security: 1 day
- Django Configuration: 1-2 days
- File Upload Updates: 1 day
- Migration: 1-2 days
- Testing: 2-3 days
- **Total:** 7-11 days

## Success Criteria
- All file uploads work with Supabase Storage
- Existing media files accessible after migration
- Security policies properly enforced
- No performance degradation
- Cost monitoring in place

## Next Steps
1. Review and approve this plan
2. Set up Supabase project and obtain API keys
3. Begin implementation following the steps above
4. Schedule migration during maintenance window

---
*Document Version: 1.0*
*Date: September 28, 2025*
*Prepared for: CCC Administrative Application*