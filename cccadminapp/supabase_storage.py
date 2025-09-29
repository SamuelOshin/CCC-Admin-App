from django.core.files.storage import Storage
from django.core.files.base import File
from storage3 import create_client
from decouple import config
import os
from io import BytesIO


class SupabaseStorage(Storage):
    """
    Custom Django storage backend for Supabase Storage
    """

    def __init__(self):
        self.bucket_name = config('SUPABASE_STORAGE_BUCKET')
        self.supabase_url = config('SUPABASE_URL')
        self.supabase_key = config('SUPABASE_SECRET_KEY')  # Use service role for full access

        # Create storage client with proper headers
        headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'apikey': config('SUPABASE_ACCESS_KEY')
        }

        self.client = create_client(
            url=f"{self.supabase_url}/storage/v1",
            headers=headers,
            is_async=False
        )

    def _save(self, name, content):
        """
        Save a file to Supabase Storage
        """
        try:
            # Read content
            if hasattr(content, 'read'):
                if hasattr(content, 'seek'):
                    content.seek(0)
                file_content = content.read()
            else:
                file_content = content

            # If content is bytes, keep as is; if string, encode
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')

            # Upload to Supabase Storage
            response = self.client.from_(self.bucket_name).upload(
                path=name,
                file=file_content,
                file_options={
                    "content-type": getattr(content, 'content_type', 'application/octet-stream'),
                    "cache-control": "3600"
                }
            )

            # Check if upload was successful
            if hasattr(response, 'status_code') and response.status_code in [200, 201]:
                return name
            elif hasattr(response, 'path'):  # Supabase response object
                return name
            else:
                raise Exception(f"Upload failed: {response}")

        except Exception as e:
            raise Exception(f"Supabase storage save failed: {str(e)}")

    def _open(self, name, mode='rb'):
        """
        Open a file from Supabase Storage
        """
        try:
            # Download file from Supabase
            response = self.client.from_(self.bucket_name).download(name)

            if hasattr(response, 'content'):
                file_content = response.content
            else:
                file_content = response

            # Create a file-like object
            file_obj = BytesIO(file_content)
            file_obj.seek(0)

            return File(file_obj, name)

        except Exception as e:
            raise Exception(f"Supabase storage open failed: {str(e)}")

    def exists(self, name):
        """
        Check if a file exists in Supabase Storage
        """
        try:
            # Try to download file info (this is a simple check)
            self.client.from_(self.bucket_name).download(name)
            return True
        except Exception:
            return False

    def delete(self, name):
        """
        Delete a file from Supabase Storage
        """
        try:
            self.client.from_(self.bucket_name).remove([name])
            return True
        except Exception:
            return False

    def url(self, name):
        """
        Generate a URL for the file
        """
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"