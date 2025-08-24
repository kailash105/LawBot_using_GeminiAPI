#!/bin/bash

echo "🚀 IPC Crime Analyzer - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js v16 or higher."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    print_success "All prerequisites are installed!"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Are you in the correct directory?"
        exit 1
    fi
    
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
    
    npm run build
    if [ $? -ne 0 ]; then
        print_error "Failed to build frontend"
        exit 1
    fi
    
    print_success "Frontend built successfully!"
}

# Prepare backend
prepare_backend() {
    print_status "Preparing backend..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ -d ".venv" ]; then
        print_status "Using existing virtual environment..."
        source .venv/bin/activate
    else
        print_status "Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
    fi
    
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install backend dependencies"
        exit 1
    fi
    
    print_success "Backend dependencies installed!"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f ".env.example" ]; then
        print_warning ".env.example not found. Creating basic environment file..."
        cat > .env.example << EOF
# Frontend Environment Variables
VITE_API_URL=http://localhost:5001
VITE_APP_NAME=IPC Crime Analyzer
VITE_APP_VERSION=1.0.0

# Backend Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
USE_AI_MODEL=GEMINI
GEMINI_MODEL=gemini-1.5-flash
USE_LLM_ENHANCEMENT=true
USE_SEMANTIC_SEARCH=true
SIMILARITY_THRESHOLD=0.3
ENABLE_CONVERSATION_LOGS=true
LOG_LEVEL=INFO
FLASK_ENV=development
EOF
    fi
    
    if [ ! -f ".env" ]; then
        print_warning "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please update .env file with your actual API keys!"
    else
        print_success ".env file already exists"
    fi
}

# Create deployment files
create_deployment_files() {
    print_status "Creating deployment files..."
    
    # Create Procfile if it doesn't exist
    if [ ! -f "Procfile" ]; then
        echo "web: python app.py" > Procfile
        print_success "Created Procfile"
    fi
    
    # Create runtime.txt if it doesn't exist
    if [ ! -f "runtime.txt" ]; then
        echo "python-3.11.0" > runtime.txt
        print_success "Created runtime.txt"
    fi
    
    # Create .ebextensions directory and config for AWS Elastic Beanstalk
    if [ ! -d ".ebextensions" ]; then
        mkdir .ebextensions
        print_success "Created .ebextensions directory"
    fi
    
    if [ ! -f ".ebextensions/01_environment.config" ]; then
        cat > .ebextensions/01_environment.config << EOF
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
EOF
        print_success "Created AWS Elastic Beanstalk configuration"
    fi
}

# Test the application
test_application() {
    print_status "Testing application..."
    
    # Activate virtual environment for testing
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Start backend in background
    print_status "Starting backend server..."
    python app.py &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    # Test backend health
    if curl -s http://localhost:5001/api/status > /dev/null; then
        print_success "Backend is running and responding!"
    else
        print_error "Backend is not responding. Check the logs above."
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Test frontend build
    if [ -d "dist" ]; then
        print_success "Frontend build directory exists!"
    else
        print_error "Frontend build directory not found"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Stop backend
    kill $BACKEND_PID 2>/dev/null
    print_success "Application test completed successfully!"
}

# Main deployment process
main() {
    echo ""
    print_status "Starting deployment preparation..."
    echo ""
    
    check_prerequisites
    echo ""
    
    build_frontend
    echo ""
    
    prepare_backend
    echo ""
    
    setup_environment
    echo ""
    
    create_deployment_files
    echo ""
    
    test_application
    echo ""
    
    print_success "🎉 Deployment preparation completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update .env file with your actual API keys"
    echo "2. Choose your deployment platform:"
    echo "   - Vercel + Railway (Recommended)"
    echo "   - Netlify + Heroku"
    echo "   - AWS S3 + Elastic Beanstalk"
    echo "3. Follow the deployment guide in DEPLOYMENT.md"
    echo "4. Update CORS settings in app.py for your domain"
    echo ""
    echo "📚 For detailed instructions, see DEPLOYMENT.md"
    echo ""
}

# Run main function
main
