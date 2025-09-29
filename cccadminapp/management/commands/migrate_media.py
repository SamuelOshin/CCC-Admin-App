from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Migrate existing media files from local storage to Supabase Storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--source-dir',
            type=str,
            default='cccadminapp/media',
            help='Source directory containing media files (relative to BASE_DIR)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        source_dir = options['source_dir']

        # Get the absolute path to the source directory
        base_dir = Path(settings.BASE_DIR)
        source_path = base_dir / source_dir

        if not source_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Source directory does not exist: {source_path}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting media migration from: {source_path}')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will be uploaded')
            )

        total_files = 0
        uploaded_files = 0
        skipped_files = 0
        error_files = 0

        # Walk through all files in the source directory
        for root, dirs, files in os.walk(source_path):
            for file in files:
                total_files += 1
                file_path = Path(root) / file

                # Get relative path from source directory
                relative_path = file_path.relative_to(source_path)

                self.stdout.write(f'Processing: {relative_path}')

                try:
                    if dry_run:
                        self.stdout.write(f'  Would upload: {relative_path}')
                        uploaded_files += 1
                        continue

                    # Read the file and create a file-like object
                    with open(file_path, 'rb') as f:
                        from django.core.files.base import ContentFile
                        file_content = ContentFile(f.read(), name=str(relative_path))

                    # Upload to Supabase Storage
                    saved_path = default_storage.save(str(relative_path), file_content)

                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Uploaded: {relative_path} -> {saved_path}')
                    )
                    uploaded_files += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Failed to upload {relative_path}: {str(e)}')
                    )
                    error_files += 1

        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        self.stdout.write(f'  Total files processed: {total_files}')
        self.stdout.write(f'  Files uploaded: {uploaded_files}')
        self.stdout.write(f'  Files skipped: {skipped_files}')
        self.stdout.write(f'  Files with errors: {error_files}')

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING(
                'This was a dry run. Run without --dry-run to perform actual migration.'
            ))
        else:
            self.stdout.write('\n' + self.style.SUCCESS(
                'Migration completed! You can now safely remove the local media files.'
            ))
            self.stdout.write(self.style.WARNING(
                'IMPORTANT: Test your application thoroughly before deleting local files!'
            ))