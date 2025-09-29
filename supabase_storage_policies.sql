-- Supabase Storage Security Policies for ccc-admin-media Bucket
-- NOTE: These policies CANNOT be set via SQL Editor due to permissions
-- Use Supabase Dashboard → Storage → [Your Bucket] → Policies tab instead

-- Alternative Approach: Since Django uses service role key, RLS policies are bypassed
-- Security is handled entirely in Django views and authentication

-- If you need to set policies manually, use the Supabase Dashboard:
-- 1. Go to Storage → ccc-admin-media → Policies
-- 2. Create policies through the UI (not SQL)

-- For now, skip RLS setup since Django handles authentication
-- The service role key (SUPABASE_SECRET_KEY) bypasses all RLS restrictions

-- Verification: Test file upload from Django - it should work without RLS policies

-- Verification queries (run these to test the policies):

-- Check existing policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'objects' AND schemaname = 'storage';

-- Check bucket contents
SELECT name, bucket_id, created_at, updated_at, metadata
FROM storage.objects
WHERE bucket_id = 'ccc-admin-media'
LIMIT 10;

-- Check bucket exists
SELECT id, name, public, created_at
FROM storage.buckets
WHERE name = 'ccc-admin-media';