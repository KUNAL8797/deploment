# Frontend Environment Variables Configuration

## Required Environment Variables for Vercel

### 1. API Configuration

#### REACT_APP_API_URL (Required)

```bash
# Production backend URL (update with your actual Render URL)
REACT_APP_API_URL=https://ideaforge-ai-backend.onrender.com

# Format: https://your-service-name.onrender.com
# No trailing slash
```

**How to get your backend URL:**

1. Go to your Render dashboard
2. Click on your backend service
3. Copy the URL from the service overview
4. It will look like: `https://your-service-name.onrender.com`

#### REACT_APP_ENVIRONMENT (Required)

```bash
REACT_APP_ENVIRONMENT=production
```

### 2. Optional Configuration Variables

#### REACT_APP_APP_NAME (Optional)

```bash
REACT_APP_APP_NAME=IdeaForge AI
```

#### REACT_APP_VERSION (Optional)

```bash
REACT_APP_VERSION=1.0.0
```

## Step-by-Step Configuration in Vercel

### 1. Access Environment Variables

1. **Go to Vercel Dashboard**

   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click on your project

2. **Navigate to Settings**
   - Click "Settings" tab
   - Click "Environment Variables" in the sidebar

### 2. Add Environment Variables

#### Variable 1: REACT_APP_API_URL

- **Name**: `REACT_APP_API_URL`
- **Value**: `https://your-backend-service.onrender.com`
- **Environments**: Check all (Production, Preview, Development)
- **Click "Save"**

#### Variable 2: REACT_APP_ENVIRONMENT

- **Name**: `REACT_APP_ENVIRONMENT`
- **Value**: `production`
- **Environments**: Check "Production" only
- **Click "Save"**

### 3. Trigger Redeploy

After adding environment variables:

1. **Go to Deployments tab**
2. **Click "Redeploy" on the latest deployment**
3. **Or push a new commit to trigger automatic deployment**

## Environment Variable Templates

### Development (.env.local)

```bash
# Local development environment
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_APP_NAME=IdeaForge AI (Dev)
```

### Production (Vercel Dashboard)

```bash
# Production environment variables (set in Vercel dashboard)
REACT_APP_API_URL=https://ideaforge-ai-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_APP_NAME=IdeaForge AI
```

### Preview/Staging (Vercel Dashboard)

```bash
# Preview environment (for pull requests)
REACT_APP_API_URL=https://staging-backend.onrender.com
REACT_APP_ENVIRONMENT=staging
REACT_APP_APP_NAME=IdeaForge AI (Preview)
```

## Using Environment Variables in Code

### 1. Accessing Variables

```typescript
// In your React components
const apiUrl = process.env.REACT_APP_API_URL;
const environment = process.env.REACT_APP_ENVIRONMENT;

// Example usage in API service
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});
```

### 2. Environment-Specific Configuration

```typescript
// config/environment.ts
export const config = {
  apiUrl: process.env.REACT_APP_API_URL || "http://localhost:8000",
  environment: process.env.REACT_APP_ENVIRONMENT || "development",
  appName: process.env.REACT_APP_APP_NAME || "IdeaForge AI",

  // Environment checks
  isDevelopment: process.env.REACT_APP_ENVIRONMENT === "development",
  isProduction: process.env.REACT_APP_ENVIRONMENT === "production",

  // Feature flags based on environment
  enableDebugMode: process.env.REACT_APP_ENVIRONMENT !== "production",
  enableAnalytics: process.env.REACT_APP_ENVIRONMENT === "production",
};
```

### 3. API Service Configuration

```typescript
// services/api.ts
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL;

if (!API_BASE_URL) {
  throw new Error("REACT_APP_API_URL environment variable is not set");
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Verification Steps

### 1. Check Build Process

After setting environment variables:

```bash
# Local verification
npm run build

# Check if variables are accessible
echo "API URL: $REACT_APP_API_URL"
```

### 2. Verify in Deployed App

1. **Open Browser Developer Tools**
2. **Go to your deployed Vercel URL**
3. **Check Console for any environment variable errors**
4. **Test API calls to ensure they're hitting the right backend**

### 3. Test API Connection

```javascript
// In browser console on your deployed site
console.log("API URL:", process.env.REACT_APP_API_URL);
console.log("Environment:", process.env.REACT_APP_ENVIRONMENT);

// Test API connection
fetch(process.env.REACT_APP_API_URL + "/health")
  .then((response) => response.json())
  .then((data) => console.log("API Health:", data));
```

## Common Issues and Solutions

### 1. Environment Variables Not Working

**Issue**: Variables are undefined in the app
**Solutions**:

- Ensure variable names start with `REACT_APP_`
- Check for typos in variable names
- Redeploy after adding variables
- Clear browser cache

### 2. API Connection Errors

**Issue**: Cannot connect to backend API
**Solutions**:

- Verify REACT_APP_API_URL is correct
- Check backend CORS configuration
- Ensure backend is deployed and running
- Test backend URL directly

### 3. Build Failures

**Issue**: Build fails after adding environment variables
**Solutions**:

- Check for syntax errors in environment values
- Ensure no spaces around the `=` sign
- Verify all required variables are set
- Check build logs for specific errors

### 4. CORS Issues

**Issue**: CORS policy blocks API requests
**Solutions**:

- Update backend CORS_ORIGINS with frontend URL
- Ensure frontend URL matches exactly (no trailing slash)
- Check protocol (http vs https)
- Verify backend is configured correctly

## Environment-Specific Features

### 1. Development Features

```typescript
// Show debug information only in development
if (process.env.REACT_APP_ENVIRONMENT === "development") {
  console.log("Debug mode enabled");
  // Enable React DevTools
  // Show detailed error messages
}
```

### 2. Production Optimizations

```typescript
// Production-only features
if (process.env.REACT_APP_ENVIRONMENT === "production") {
  // Enable analytics
  // Disable console logs
  // Enable error reporting
}
```

### 3. Feature Flags

```typescript
// Feature flags based on environment
const features = {
  enableBetaFeatures: process.env.REACT_APP_ENVIRONMENT !== "production",
  enableAnalytics: process.env.REACT_APP_ENVIRONMENT === "production",
  showDebugInfo: process.env.REACT_APP_ENVIRONMENT === "development",
};
```

## Security Considerations

### 1. Environment Variable Security

- ✅ Never put sensitive data in REACT*APP* variables
- ✅ All REACT*APP* variables are public in the built app
- ✅ Use backend environment variables for secrets
- ✅ Validate environment variables at build time

### 2. API Security

- ✅ Use HTTPS for all API calls
- ✅ Implement proper authentication
- ✅ Validate API responses
- ✅ Handle errors gracefully

## Environment Variable Checklist

Before deployment:

- [ ] REACT_APP_API_URL is set and correct
- [ ] REACT_APP_ENVIRONMENT is set to "production"
- [ ] All variables start with REACT*APP*
- [ ] No sensitive data in environment variables
- [ ] Backend CORS is configured for frontend URL
- [ ] Variables are set for all environments (prod, preview, dev)
- [ ] Build succeeds with new variables
- [ ] API connection works in deployed app
- [ ] No console errors related to environment variables

## Testing Environment Configuration

### 1. Local Testing

```bash
# Test with production-like environment
REACT_APP_API_URL=https://your-backend.onrender.com npm start
```

### 2. Preview Testing

- Create a pull request
- Vercel will create a preview deployment
- Test with preview environment variables

### 3. Production Testing

- Deploy to production
- Test all functionality
- Monitor for any environment-related errors
