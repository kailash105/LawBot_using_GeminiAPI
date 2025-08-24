# 🚀 IPC Crime Analyzer - Deployment Guide

This guide covers deployment options for both the React frontend and Flask backend of your IPC Crime Analyzer application.

## 📋 Prerequisites

- **Git** installed on your system
- **Node.js** (v16 or higher) for frontend deployment
- **Python** (v3.8 or higher) for backend deployment
- **GitHub account** (for code hosting)
- **API Keys**: Gemini API key configured

## 🎯 Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) - Recommended

#### Frontend Deployment on Vercel

1. **Prepare for Deployment**
   ```bash
   # Ensure your code is committed to Git
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com) and sign up/login
   - Click "New Project"
   - Import your GitHub repository
   - Configure build settings:
     - **Framework Preset**: Vite
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
     - **Install Command**: `npm install`
   - Add environment variables:
     ```
     VITE_API_URL=https://your-backend-url.railway.app
     ```
   - Click "Deploy"

3. **Update API Configuration**
   - In `vite.config.js`, update the proxy to point to your deployed backend:
   ```javascript
   proxy: {
     '/api': {
       target: 'https://your-backend-url.railway.app',
       changeOrigin: true
     }
   }
   ```

#### Backend Deployment on Railway

1. **Prepare Backend**
   ```bash
   # Create a Procfile for Railway
   echo "web: python app.py" > Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app) and sign up/login
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     USE_AI_MODEL=GEMINI
     GEMINI_MODEL=gemini-1.5-flash
     USE_LLM_ENHANCEMENT=true
     USE_SEMANTIC_SEARCH=true
     SIMILARITY_THRESHOLD=0.3
     ENABLE_CONVERSATION_LOGS=true
     LOG_LEVEL=INFO
     ```
   - Railway will automatically detect Python and install dependencies

3. **Update CORS Settings**
   - In `app.py`, update CORS to allow your Vercel domain:
   ```python
   CORS(app, origins=[
       "https://your-app.vercel.app",
       "http://localhost:3000"  # for local development
   ])
   ```

### Option 2: Netlify (Frontend) + Heroku (Backend)

#### Frontend Deployment on Netlify

1. **Build Locally**
   ```bash
   npm run build
   ```

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com) and sign up/login
   - Drag and drop your `dist` folder to deploy
   - Or connect your GitHub repository for automatic deployments
   - Add environment variables in Netlify dashboard:
     ```
     VITE_API_URL=https://your-backend-url.herokuapp.com
     ```

#### Backend Deployment on Heroku

1. **Prepare for Heroku**
   ```bash
   # Create Procfile
   echo "web: gunicorn app:app" > Procfile
   
   # Add gunicorn to requirements.txt
   echo "gunicorn==21.2.0" >> requirements.txt
   
   # Create runtime.txt
   echo "python-3.11.0" > runtime.txt
   ```

2. **Deploy to Heroku**
   ```bash
   # Install Heroku CLI
   # Then run:
   heroku create your-app-name
   heroku config:set GEMINI_API_KEY=your_gemini_api_key_here
   heroku config:set USE_AI_MODEL=GEMINI
   heroku config:set GEMINI_MODEL=gemini-1.5-flash
   heroku config:set USE_LLM_ENHANCEMENT=true
   heroku config:set USE_SEMANTIC_SEARCH=true
   heroku config:set SIMILARITY_THRESHOLD=0.3
   heroku config:set ENABLE_CONVERSATION_LOGS=true
   heroku config:set LOG_LEVEL=INFO
   git push heroku main
   ```

### Option 3: AWS Deployment

#### Frontend on AWS S3 + CloudFront

1. **Build and Upload**
   ```bash
   npm run build
   aws s3 sync dist/ s3://your-bucket-name
   ```

2. **Configure CloudFront**
   - Create CloudFront distribution pointing to S3 bucket
   - Configure custom domain (optional)

#### Backend on AWS Elastic Beanstalk

1. **Prepare Application**
   ```bash
   # Create .ebextensions/01_environment.config
   mkdir .ebextensions
   ```

2. **Create Configuration File**
   ```yaml
   # .ebextensions/01_environment.config
   option_settings:
     aws:elasticbeanstalk:application:environment:
       GEMINI_API_KEY: your_gemini_api_key_here
       USE_AI_MODEL: GEMINI
       GEMINI_MODEL: gemini-1.5-flash
       USE_LLM_ENHANCEMENT: true
       USE_SEMANTIC_SEARCH: true
       SIMILARITY_THRESHOLD: 0.3
       ENABLE_CONVERSATION_LOGS: true
       LOG_LEVEL: INFO
   ```

3. **Deploy**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

## 🔧 Environment Variables Setup

### Frontend Environment Variables
```bash
# .env.production
VITE_API_URL=https://your-backend-url.com
VITE_APP_NAME=IPC Crime Analyzer
VITE_APP_VERSION=1.0.0
```

### Backend Environment Variables
```bash
# .env.production
GEMINI_API_KEY=your_gemini_api_key_here
USE_AI_MODEL=GEMINI
GEMINI_MODEL=gemini-1.5-flash
USE_LLM_ENHANCEMENT=true
USE_SEMANTIC_SEARCH=true
SIMILARITY_THRESHOLD=0.3
ENABLE_CONVERSATION_LOGS=true
LOG_LEVEL=INFO
FLASK_ENV=production
```

## 📁 Required Files for Deployment

### Frontend Files
```
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   └── index.css
└── .env.production
```

### Backend Files
```
├── app.py
├── ml_enhancer.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── data/
│   └── ipc_sections.json
└── .env.production
```

## 🚀 Quick Deployment Script

Create a deployment script to automate the process:

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Starting deployment..."

# Frontend deployment
echo "📦 Building frontend..."
npm run build

# Backend deployment
echo "🐍 Preparing backend..."
pip install -r requirements.txt

# Environment setup
echo "⚙️ Setting up environment..."
cp .env.example .env.production

echo "✅ Deployment preparation complete!"
echo "📝 Next steps:"
echo "1. Update .env.production with your API keys"
echo "2. Deploy to your chosen platform"
echo "3. Update CORS settings in app.py"
```

## 🔍 Post-Deployment Checklist

- [ ] **Frontend**
  - [ ] API URL correctly configured
  - [ ] Environment variables set
  - [ ] Build successful
  - [ ] Domain configured (if using custom domain)

- [ ] **Backend**
  - [ ] Environment variables configured
  - [ ] CORS settings updated
  - [ ] API endpoints accessible
  - [ ] Database/Storage configured (if needed)

- [ ] **Integration**
  - [ ] Frontend can communicate with backend
  - [ ] API calls working
  - [ ] Error handling working
  - [ ] Logs accessible

## 🛠️ Troubleshooting

### Common Issues

1. **CORS Errors**
   ```python
   # Update app.py CORS settings
   CORS(app, origins=["https://your-frontend-domain.com"])
   ```

2. **Environment Variables Not Loading**
   ```python
   # Ensure .env file is in root directory
   # Check variable names match exactly
   ```

3. **Build Failures**
   ```bash
   # Clear cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **API Connection Issues**
   ```javascript
   // Check API URL in frontend
   // Ensure backend is running
   // Verify network connectivity
   ```

## 📊 Monitoring and Maintenance

### Health Checks
- Set up health check endpoints
- Monitor API response times
- Track error rates

### Logs
- Configure log aggregation
- Set up alerts for errors
- Monitor API usage

### Updates
- Regular dependency updates
- Security patches
- Feature updates

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Restrict origins to your domains only
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **HTTPS**: Always use HTTPS in production
5. **Input Validation**: Validate all user inputs

## 📞 Support

For deployment issues:
1. Check platform-specific documentation
2. Review error logs
3. Test locally first
4. Use platform support channels

---

**🎉 Your IPC Crime Analyzer is now ready for production deployment!**
