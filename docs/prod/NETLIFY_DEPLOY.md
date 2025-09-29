# Netlify Deployment Guide

## Quick Deploy

### Option 1: Git-based Deployment (Recommended)

1. Push your code to GitHub/GitLab/Bitbucket
2. Connect your repository to Netlify:
   - Go to [Netlify](https://netlify.com) and sign up/login
   - Click "Add new site" > "Import an existing project"
   - Choose your Git provider and repository
   - Netlify will auto-detect the build settings from `netlify.toml`

### Option 2: Manual Deployment

```bash
# Build the project
npm run build

# Install Netlify CLI (if not already installed)
npm install -g netlify-cli

# Deploy to Netlify
netlify deploy --prod --dir=dist
```

## Build Configuration

The project is configured with:
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Node Version**: 18

## Environment Variables

If you need environment variables:
1. Go to your Netlify dashboard
2. Site settings > Environment variables
3. Add your variables (e.g., `VITE_API_URL`)

## Custom Domain

To use a custom domain:
1. Go to Site settings > Domain management
2. Add your custom domain
3. Configure DNS as instructed

## Features Included

- ✅ Single Page Application (SPA) routing support
- ✅ Security headers
- ✅ Static asset caching
- ✅ Automatic HTTPS
- ✅ Form handling (if needed)
- ✅ Deploy previews for pull requests

## Performance Optimizations

The `netlify.toml` includes:
- Cache headers for static assets (1 year)
- Security headers
- SPA fallback routing

## Troubleshooting

**Build fails with dependency issues?**
- Try: `npm install --legacy-peer-deps`
- Ensure Node version is 18+

**Routes not working?**
- The `netlify.toml` includes SPA redirect rules
- All routes will fallback to `/index.html`

**Environment variables not working?**
- Ensure they start with `VITE_` prefix
- Add them in Netlify dashboard, not `.env` files for production