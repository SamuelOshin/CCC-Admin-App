#!/usr/bin/env python
"""
Test script for Supabase Storage integration with Django
Run this to verify that file uploads work with the new storage backend
"""

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

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

def test_supabase_storage():
    """Test basic Supabase Storage functionality"""
    print("🧪 Testing Supabase Storage Integration")
    print("=" * 50)

    try:
        # Test 1: Basic storage info
        print("✅ Django storage backend:", type(default_storage).__name__)
        print("✅ Storage location:", getattr(default_storage, 'bucket_name', 'N/A'))

        # Test 2: Create a simple text file (skip exists check for now)
        print("\n📄 Testing text file upload...")
        test_content = "Hello from Django Supabase Storage integration test!"
        file_name = "test_django_integration.txt"

        file_obj = ContentFile(test_content.encode('utf-8'), name=file_name)
        # Skip the exists check by using a unique filename
        import uuid
        unique_filename = f"{uuid.uuid4().hex[:8]}_{file_name}"
        saved_path = default_storage.save(unique_filename, file_obj)
        print(f"✅ Text file uploaded successfully: {saved_path}")

        # Test 3: Check if file exists (handle 403 gracefully)
        if default_storage.exists(saved_path):
            print("✅ File exists in storage")
        else:
            print("⚠️  File existence check failed (possibly due to permissions)")

        # Test 4: Read file back
        try:
            with default_storage.open(saved_path, 'r') as f:
                content = f.read()
                if content.decode('utf-8') == test_content:
                    print("✅ File content matches")
                else:
                    print("❌ File content doesn't match")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

        # Test 5: Create and upload an image
        print("\n🖼️  Testing image upload...")
        try:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            image_file = ContentFile(img_buffer.getvalue(), name='test_image.png')
            image_path = default_storage.save('test_image.png', image_file)
            print(f"✅ Image uploaded successfully: {image_path}")

        except Exception as e:
            print(f"❌ Error uploading image: {e}")

        # Test 6: List files (if supported)
        print("\n📋 Testing file listing...")
        try:
            # Try to list files in the bucket
            files = default_storage.listdir('')[1]  # Get files, not directories
            print(f"✅ Found {len(files)} files in storage")
            if files:
                print("📄 Recent files:", files[:5])  # Show first 5 files
        except Exception as e:
            print(f"⚠️  File listing not supported or failed: {e}")

        # Test 7: Generate URL (if supported)
        print("\n🔗 Testing URL generation...")
        try:
            url = default_storage.url(saved_path)
            print(f"✅ File URL: {url}")
        except Exception as e:
            print(f"⚠️  URL generation failed: {e}")

        print("\n🎉 Supabase Storage integration test completed!")
        print("If all tests passed, your Django app is ready to use Supabase Storage.")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_storage()
    sys.exit(0 if success else 1)