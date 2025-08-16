# Frontend Deployment Guide - Vercel

## Quick Deployment Steps

### 1. Prerequisites

- GitHub account with your project repository
- Vercel account (free tier available)

### 2. Deploy to Vercel

#### Option A: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy (follow prompts)
vercel

# For production deployment
vercel --prod
```

#### Option B: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Select the `frontend` folder as the root directory
5. Vercel will auto-detect React settings
6. Click "Deploy"

### 3. Configure Environment Variables

In Vercel Dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variables:

```
REACT_APP_API_URL = https://your-backend-domain.onrender.com
REACT_APP_ENVIRONMENT = production
```

### 4. Custom Domain (Optional)

1. In project settings, go to "Domains"
2. Add your custom domain
3. Follow DNS configuration instructions

## Configuration Files

### vercel.json

- Configures build settings and routing
- Handles SPA routing with fallback to index.html
- Sets up caching headers for static assets

### .env.production

- Production environment variables
- Overridden by Vercel environment variables

## Automatic Deployments

Once connected to GitHub:

- Every push to `main` branch triggers production deployment
- Pull requests create preview deployments
- Rollback available through Vercel dashboard

## Troubleshooting

### Build Failures

- Check build logs in Vercel dashboard
- Ensure all dependencies are in package.json
- Verify TypeScript compilation

### Environment Variables

- Variables must start with `REACT_APP_`
- Set in Vercel dashboard, not in code
- Restart deployment after changing variables

### Routing Issues

- vercel.json handles SPA routing
- All routes fallback to index.html
- Check browser console for errors
