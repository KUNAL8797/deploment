# Supabase Database Setup Guide

## Step-by-Step Supabase Setup

### 1. Create Supabase Account and Project

1. **Sign up for Supabase**

   - Go to [supabase.com](https://supabase.com)
   - Click "Start your project"
   - Sign up with GitHub (recommended) or email

2. **Create New Project**

   - Click "New Project"
   - Choose your organization (or create one)
   - Fill in project details:
     - **Name**: `ideaforge-ai-db`
     - **Database Password**: Generate a strong password (save this!)
     - **Region**: Choose closest to your users
     - **Pricing Plan**: Free tier (500MB storage, 2GB bandwidth)

3. **Wait for Project Creation**
   - Takes 2-3 minutes to provision
   - You'll get a project dashboard when ready

### 2. Get Database Connection Details

1. **Navigate to Settings**

   - Go to Settings → Database
   - Find "Connection string" section

2. **Copy Connection Details**

   ```
   Host: db.[project-ref].supabase.co
   Database name: postgres
   Port: 5432
   User: postgres
   Password: [your-password]
   ```

3. **Get Full Connection String**
   ```
   postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
   ```

### 3. Configure Database Access

1. **Enable Connection Pooling** (Recommended)

   - Go to Settings → Database
   - Enable "Connection pooling"
   - Use port 6543 for pooled connections

2. **Set Up SSL** (Already enabled by default)
   - All connections use SSL/TLS
   - No additional configuration needed

### 4. Run Database Schema Setup

#### Option A: Using Supabase SQL Editor

1. Go to SQL Editor in Supabase dashboard
2. Copy and paste the contents of `sql/init_database.sql`
3. Click "Run" to execute the schema

#### Option B: Using psql Command Line

```bash
# Set your connection string
export DATABASE_URL="postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"

# Run the schema setup
psql $DATABASE_URL -f sql/init_database.sql
```

#### Option C: Using Python Script

```bash
# Set environment variable
export DATABASE_URL="postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres"

# Run deployment script
python scripts/deploy_database.py
```

### 5. Verify Database Setup

1. **Check Tables in Supabase Dashboard**

   - Go to Table Editor
   - Should see: users, ideas, idea_insights

2. **Test Connection**

   ```bash
   # Test connection
   psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
   ```

3. **Verify Admin User**
   - Check users table has admin user
   - Default credentials: admin / admin123

### 6. Configure Environment Variables

For your backend deployment, you'll need:

```bash
# Production environment variables
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Optional: Use connection pooling
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:6543/postgres
```

## Supabase Features Available

### 1. Database Management

- PostgreSQL 15+ with extensions
- Real-time subscriptions
- Row Level Security (RLS)
- Automatic backups

### 2. Built-in Tools

- SQL Editor with syntax highlighting
- Table Editor (GUI for data management)
- API auto-generation
- Real-time logs

### 3. Security Features

- SSL/TLS encryption
- Row Level Security policies
- API key management
- IP restrictions (paid plans)

## Optional: Enable Row Level Security

If you want to add extra security:

```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
ALTER TABLE idea_insights ENABLE ROW LEVEL SECURITY;

-- Create policies (example)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can manage own ideas" ON ideas
    FOR ALL USING (auth.uid()::text = created_by::text);
```

## Monitoring and Maintenance

### 1. Database Usage

- Monitor storage usage in dashboard
- Free tier: 500MB limit
- Upgrade when approaching limit

### 2. Connection Limits

- Free tier: 60 concurrent connections
- Use connection pooling for better performance
- Monitor connection usage

### 3. Backups

- Automatic daily backups (7 days retention)
- Point-in-time recovery available
- Manual backup via pg_dump

### 4. Performance Monitoring

- Query performance insights
- Slow query detection
- Index usage statistics

## Troubleshooting

### Common Issues

**Connection Timeout**

- Check if your IP is allowed
- Verify connection string format
- Try connection pooling port (6543)

**Permission Denied**

- Verify password is correct
- Check if database exists
- Ensure user has proper permissions

**SSL Connection Error**

- Supabase requires SSL
- Add `?sslmode=require` to connection string if needed

**Schema Creation Failed**

- Check for syntax errors in SQL
- Verify PostgreSQL version compatibility
- Run commands one by one to isolate issues

### Getting Help

1. **Supabase Documentation**: [docs.supabase.com](https://docs.supabase.com)
2. **Community Support**: [github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
3. **Discord Community**: [discord.supabase.com](https://discord.supabase.com)

## Next Steps

After Supabase setup:

1. ✅ Database created and configured
2. ➡️ Deploy backend to Render
3. ➡️ Configure backend environment variables
4. ➡️ Deploy frontend to Vercel
5. ➡️ Test end-to-end functionality

## Security Checklist

- [ ] Strong database password set
- [ ] Connection string stored securely
- [ ] Admin password changed from default
- [ ] SSL connections verified
- [ ] Backup strategy confirmed
- [ ] Monitoring enabled
