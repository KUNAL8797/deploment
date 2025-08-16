# Render Backend Deployment Guide

## Step-by-Step Render Deployment

### 1. Prepare GitHub Repository

1. **Ensure Code is Pushed to GitHub**

   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify Repository Structure**
   ```
   your-repo/
   ├── ai-innovation-incubator/
   │   ├── backend/
   │   │   ├── app/
   │   │   ├── render.yaml
   │   │   ├── requirements.txt
   │   │   └── ...
   │   └── frontend/
   ```

### 2. Create Render Account and Service

1. **Sign Up for Render**

   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended)
   - Connect your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Choose your repository
   - Click "Connect"

### 3. Configure Web Service Settings

#### Basic Settings

- **Name**: `ideaforge-ai-backend`
- **Region**: Choose closest to your users (e.g., Oregon)
- **Branch**: `main`
- **Root Directory**: `ai-innovation-incubator/backend`

#### Build Settings

- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker`

#### Advanced Settings

- **Plan**: Free (512 MB RAM, shared CPU)
- **Health Check Path**: `/health`
- **Auto-Deploy**: Yes (deploy on git push)

### 4. Configure Environment Variables

In the Render dashboard, add these environment variables:

#### Required Variables

```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
SECRET_KEY=[auto-generated-by-render]
GEMINI_API_KEY=your-gemini-api-key-here
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

#### Optional Variables

```bash
LOG_LEVEL=INFO
REDIS_URL=[auto-configured-if-using-render-redis]
```

### 5. Deploy the Service

1. **Start Deployment**

   - Click "Create Web Service"
   - Render will start building your application
   - Monitor build logs in real-time

2. **Build Process**

   - Install Python dependencies
   - Set up environment
   - Start the application
   - Run health checks

3. **Deployment URL**
   - Your service will be available at: `https://ideaforge-ai-backend.onrender.com`
   - Note: Free tier services sleep after 15 minutes of inactivity

### 6. Alternative: Deploy Using render.yaml

If you prefer Infrastructure as Code:

1. **Use Existing render.yaml**

   - The `render.yaml` file is already configured
   - Includes web service, database, and Redis

2. **Deploy via Blueprint**
   - In Render dashboard, click "New +" → "Blueprint"
   - Connect your repository
   - Select the `render.yaml` file
   - Review and deploy

### 7. Configure Database Connection

#### Option A: Use Render PostgreSQL

```yaml
# Already configured in render.yaml
databases:
  - name: ideaforge-db
    databaseName: ideaforge_ai
    user: ideaforge_user
```

#### Option B: Use Supabase (Recommended)

- Set `DATABASE_URL` environment variable to your Supabase connection string
- Remove database section from render.yaml if using external database

### 8. Set Up Redis Cache (Optional)

#### Using Render Redis

```yaml
# Already configured in render.yaml
services:
  - type: redis
    name: ideaforge-redis
    plan: free
```

#### Using External Redis

- Set `REDIS_URL` environment variable
- Remove Redis service from render.yaml

## Post-Deployment Configuration

### 1. Update CORS Origins

Once your frontend is deployed, update the CORS_ORIGINS environment variable:

```bash
CORS_ORIGINS=https://your-actual-frontend-domain.vercel.app
```

### 2. Test API Endpoints

```bash
# Test health endpoint
curl https://ideaforge-ai-backend.onrender.com/health

# Test root endpoint
curl https://ideaforge-ai-backend.onrender.com/

# Test user registration
curl -X POST "https://ideaforge-ai-backend.onrender.com/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

### 3. Run Database Migrations

If using Render PostgreSQL:

```bash
# SSH into your service (paid plans only)
# Or run via startup script
python scripts/deploy_database.py
```

### 4. Monitor Service Health

- **Render Dashboard**: Monitor logs, metrics, and deployments
- **Health Checks**: Automatic health monitoring at `/health`
- **Alerts**: Set up notifications for service issues

## Render Service Features

### 1. Automatic Deployments

- Deploy on every git push to main branch
- Build logs and deployment history
- Rollback to previous deployments

### 2. Environment Management

- Secure environment variable storage
- Auto-generated secrets
- Environment-specific configurations

### 3. Scaling and Performance

- **Free Tier**: 512 MB RAM, shared CPU
- **Paid Tiers**: More resources and features
- **Auto-scaling**: Available on paid plans

### 4. Monitoring and Logs

- Real-time application logs
- Performance metrics
- Error tracking and alerts

## Troubleshooting

### Common Issues

**Build Failures**

- Check requirements.txt for missing dependencies
- Verify Python version compatibility
- Review build logs for specific errors

**Start Command Errors**

- Ensure gunicorn is in requirements.txt
- Verify app.main:app path is correct
- Check for import errors in application code

**Database Connection Issues**

- Verify DATABASE_URL format
- Check database credentials
- Ensure database is accessible from Render

**Environment Variable Issues**

- Verify all required variables are set
- Check for typos in variable names
- Ensure sensitive values are properly escaped

**CORS Errors**

- Update CORS_ORIGINS with actual frontend URL
- Include protocol (https://) in origins
- Check for trailing slashes

### Performance Optimization

**Free Tier Limitations**

- Service sleeps after 15 minutes of inactivity
- Cold start time: 10-30 seconds
- 750 hours/month limit

**Optimization Tips**

- Use connection pooling for database
- Implement caching with Redis
- Optimize database queries
- Use async/await for I/O operations

### Monitoring Commands

```bash
# Check service status
curl -I https://ideaforge-ai-backend.onrender.com/health

# Monitor logs (via dashboard)
# View metrics (via dashboard)
# Set up alerts (via dashboard)
```

## Security Considerations

### Production Checklist

- [ ] Strong SECRET_KEY generated
- [ ] Database credentials secured
- [ ] CORS origins properly configured
- [ ] HTTPS enforced (automatic on Render)
- [ ] Environment variables not exposed
- [ ] API documentation disabled in production
- [ ] Rate limiting implemented
- [ ] Input validation enabled

### Backup Strategy

- Database backups (automatic with Render PostgreSQL)
- Environment variable backup
- Code repository backup (GitHub)
- Deployment configuration backup

## Next Steps

After successful backend deployment:

1. ✅ Backend service running on Render
2. ➡️ Deploy frontend to Vercel
3. ➡️ Configure frontend to use backend API
4. ➡️ Test end-to-end functionality
5. ➡️ Set up monitoring and alerts

## Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Community Forum**: [community.render.com](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)
- **Support**: Available via dashboard (paid plans)
