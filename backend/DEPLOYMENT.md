# Backend Deployment Guide - Render

## Quick Deployment Steps

### 1. Prerequisites

- GitHub account with your project repository
- Render account (free tier available)
- Supabase account for PostgreSQL database

### 2. Deploy to Render

#### Option A: Render Dashboard (Recommended)

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository and branch
5. Configure settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker`

#### Option B: render.yaml (Infrastructure as Code)

The `render.yaml` file in the backend directory defines:

- Web service configuration
- PostgreSQL database
- Redis cache
- Environment variables

### 3. Configure Environment Variables

In Render Dashboard, set these environment variables:

**Required:**

```
DATABASE_URL = postgresql://username:password@host:port/database
SECRET_KEY = your-secret-key-here
GEMINI_API_KEY = your-gemini-api-key
ENVIRONMENT = production
CORS_ORIGINS = https://your-frontend-domain.vercel.app
```

**Optional:**

```
REDIS_URL = redis://localhost:6379/0
```

### 4. Database Setup

#### Using Render PostgreSQL:

- Automatically configured via render.yaml
- Connection string provided as DATABASE_URL

#### Using Supabase (Recommended):

1. Create Supabase project
2. Get connection string from Settings → Database
3. Set as DATABASE_URL environment variable

### 5. Health Checks

The application includes health check endpoints:

- `/health` - Basic health status
- `/` - API information and status

## Configuration Files

### render.yaml

- Defines complete infrastructure
- Includes web service, database, and Redis
- Configures environment variables and scaling

### requirements.txt

- Python dependencies
- Includes production server (gunicorn)
- All necessary packages for deployment

## Production Optimizations

### Gunicorn Configuration

- 2 worker processes for free tier
- Uvicorn worker class for async support
- Proper binding to Render's PORT

### Security

- CORS configured for production frontend
- Environment-based configuration
- Secure secret key generation

### Database

- Connection pooling via SQLAlchemy
- Automatic table creation
- Migration support with Alembic

## Monitoring and Logs

### Render Dashboard

- Real-time logs and metrics
- Performance monitoring
- Error tracking

### Health Endpoints

```bash
# Check service health
curl https://your-backend.onrender.com/health

# Get API information
curl https://your-backend.onrender.com/
```

## Troubleshooting

### Common Issues

**Build Failures:**

- Check requirements.txt for missing dependencies
- Verify Python version compatibility
- Review build logs in Render dashboard

**Database Connection:**

- Verify DATABASE_URL format
- Check database credentials
- Ensure database is accessible

**CORS Errors:**

- Update CORS_ORIGINS environment variable
- Match exact frontend domain
- Include protocol (https://)

**Performance:**

- Monitor worker processes
- Check memory usage
- Optimize database queries

### Debugging Commands

```bash
# Test locally with production settings
export DATABASE_URL="your-database-url"
export SECRET_KEY="your-secret-key"
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker

# Check API endpoints
curl -X GET "https://your-backend.onrender.com/docs"
curl -X POST "https://your-backend.onrender.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'
```

## Automatic Deployments

- Connected to GitHub repository
- Auto-deploy on push to main branch
- Manual deploy option available
- Rollback capability through dashboard
