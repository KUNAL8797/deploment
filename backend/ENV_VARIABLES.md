# Environment Variables Configuration Guide

## Required Environment Variables for Render Deployment

### 1. Database Configuration

#### DATABASE_URL (Required)

```bash
# Supabase PostgreSQL (Recommended)
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Render PostgreSQL (Alternative)
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]

# Format explanation:
# postgresql://username:password@host:port/database_name
```

**How to get Supabase DATABASE_URL:**

1. Go to your Supabase project dashboard
2. Settings → Database
3. Copy the connection string
4. Replace `[password]` with your actual password

### 2. Security Configuration

#### SECRET_KEY (Required)

```bash
# Let Render auto-generate this
SECRET_KEY=[auto-generated-by-render]
```

**How to set:**

1. In Render dashboard, go to Environment Variables
2. Add `SECRET_KEY`
3. Click "Generate" to auto-create a secure key

#### GEMINI_API_KEY (Required)

```bash
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

**How to get Gemini API Key:**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add to Render environment variables

### 3. Application Configuration

#### ENVIRONMENT (Required)

```bash
ENVIRONMENT=production
```

#### CORS_ORIGINS (Required)

```bash
# Initially set to placeholder, update after frontend deployment
CORS_ORIGINS=https://your-frontend-domain.vercel.app

# Multiple origins (comma-separated)
CORS_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
```

### 4. Optional Configuration

#### LOG_LEVEL (Optional)

```bash
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### REDIS_URL (Optional)

```bash
# If using Render Redis addon
REDIS_URL=[auto-configured-by-render]

# External Redis
REDIS_URL=redis://username:password@host:port/database
```

## Step-by-Step Configuration in Render

### 1. Access Environment Variables

1. **Go to your Render service dashboard**
2. **Click on your web service** (ideaforge-ai-backend)
3. **Navigate to "Environment"** tab
4. **Click "Add Environment Variable"**

### 2. Add Required Variables

Add each variable one by one:

#### Variable 1: DATABASE_URL

- **Key**: `DATABASE_URL`
- **Value**: Your Supabase connection string
- **Click "Add"**

#### Variable 2: SECRET_KEY

- **Key**: `SECRET_KEY`
- **Click "Generate"** to auto-create
- **Click "Add"**

#### Variable 3: GEMINI_API_KEY

- **Key**: `GEMINI_API_KEY`
- **Value**: Your Google Gemini API key
- **Click "Add"**

#### Variable 4: ENVIRONMENT

- **Key**: `ENVIRONMENT`
- **Value**: `production`
- **Click "Add"**

#### Variable 5: CORS_ORIGINS

- **Key**: `CORS_ORIGINS`
- **Value**: `https://your-frontend-domain.vercel.app` (update later)
- **Click "Add"**

### 3. Optional Variables

#### LOG_LEVEL

- **Key**: `LOG_LEVEL`
- **Value**: `INFO`
- **Click "Add"**

### 4. Save and Deploy

1. **Click "Save Changes"**
2. **Render will automatically redeploy** your service
3. **Monitor the deployment** in the logs

## Environment Variable Templates

### Development Template (.env)

```bash
# Development environment variables (local only)
DATABASE_URL=sqlite:///./ai_incubator.db
SECRET_KEY=dev-secret-key-change-in-production
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=DEBUG
```

### Production Template (Render)

```bash
# Production environment variables (set in Render dashboard)
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
SECRET_KEY=[auto-generated-32-char-string]
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ENVIRONMENT=production
CORS_ORIGINS=https://ideaforge-ai.vercel.app
LOG_LEVEL=INFO
```

## Verification Steps

### 1. Check Environment Variables

After setting variables in Render:

1. **Go to Environment tab**
2. **Verify all required variables are present**
3. **Check for typos in variable names**
4. **Ensure sensitive values are not exposed in logs**

### 2. Test Configuration

```bash
# Test health endpoint after deployment
curl https://your-backend.onrender.com/health

# Should return:
{
  "status": "healthy",
  "timestamp": "2025-01-16T...",
  "service": "ai-innovation-incubator",
  "version": "1.0.0",
  "environment": "production",
  "database": "healthy",
  "checks": {
    "database_connection": true,
    "gemini_api_configured": true
  }
}
```

### 3. Check Logs

Monitor Render logs for:

- ✅ Successful database connection
- ✅ Environment variables loaded
- ✅ Application started successfully
- ❌ Any configuration errors

## Common Configuration Issues

### Database Connection Errors

**Issue**: `connection to server failed`
**Solution**:

- Verify DATABASE_URL format
- Check Supabase credentials
- Ensure database is accessible

**Issue**: `password authentication failed`
**Solution**:

- Double-check password in DATABASE_URL
- Verify username is correct
- Check for special characters that need URL encoding

### CORS Errors

**Issue**: `CORS policy: No 'Access-Control-Allow-Origin' header`
**Solution**:

- Update CORS_ORIGINS with actual frontend URL
- Include protocol (https://)
- Remove trailing slashes
- Use comma separation for multiple origins

### API Key Errors

**Issue**: `Gemini API authentication failed`
**Solution**:

- Verify API key is correct
- Check API key permissions
- Ensure no extra spaces in the key

### Secret Key Issues

**Issue**: `Invalid secret key`
**Solution**:

- Generate new secret key in Render
- Ensure key is at least 32 characters
- Use Render's auto-generation feature

## Security Best Practices

### 1. Environment Variable Security

- ✅ Never commit environment variables to git
- ✅ Use Render's secure variable storage
- ✅ Generate strong secret keys
- ✅ Rotate API keys regularly

### 2. Database Security

- ✅ Use strong database passwords
- ✅ Enable SSL connections (default in Supabase)
- ✅ Restrict database access by IP (if possible)
- ✅ Regular database backups

### 3. API Security

- ✅ Restrict CORS origins to known domains
- ✅ Use HTTPS only (enforced by Render)
- ✅ Implement rate limiting
- ✅ Validate all inputs

## Updating Environment Variables

### During Development

1. Update variables in Render dashboard
2. Service will automatically redeploy
3. Monitor logs for successful restart

### For Production Updates

1. Plan maintenance window if needed
2. Update variables in Render dashboard
3. Test thoroughly after deployment
4. Monitor application health

## Environment Variable Checklist

Before deployment, ensure:

- [ ] DATABASE_URL is set and tested
- [ ] SECRET_KEY is generated and secure
- [ ] GEMINI_API_KEY is valid and working
- [ ] ENVIRONMENT is set to "production"
- [ ] CORS_ORIGINS includes frontend domain
- [ ] LOG_LEVEL is appropriate for production
- [ ] No sensitive data in logs
- [ ] All variables are properly formatted
- [ ] Service deploys successfully
- [ ] Health check passes
