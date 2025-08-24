# IPC Crime Analyzer - AI Legal Assistant

An AI-powered chatbot that identifies relevant Indian Penal Code (IPC) sections from crime descriptions in plain language. Built with React + Vite frontend and Flask backend.

## Features

- 🧠 **AI-Powered Analysis**: Advanced ML models with semantic search and LLM enhancement for accurate results
- 🔍 **Smart Search**: Semantic search using sentence transformers for better keyword matching
- ⚡ **LLM Suggestions**: AI-powered legal suggestions and recommendations for your case
- 📚 **Comprehensive Database**: Extensive collection of IPC sections with detailed descriptions and punishments
- 💬 **Conversation Logs**: All interactions are logged for future reference and analysis
- 🎨 **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- 🔍 **Multiple Crime Detection**: Can handle multiple crimes in a single query
- 📱 **Mobile Responsive**: Works seamlessly on all devices

## Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Sentence Transformers** - Semantic search and embeddings
- **OpenAI GPT** - LLM enhancement and suggestions
- **Scikit-learn** - TF-IDF and ML algorithms
- **PyTorch** - Deep learning framework
- **JSON** - Data storage

## Project Structure

```
lawbot/
├── src/                    # React frontend source
│   ├── App.jsx            # Main React component
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles with Tailwind
├── data/
│   └── ipc_sections.json  # IPC sections database
├── logs/                  # Conversation logs (auto-generated)
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── README.md             # This file
```

## Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lawbot
   ```

2. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables** (Required for AI features)
   ```bash
   cp env.example .env
   # Edit .env and add your Gemini API key
   ```

### Running the Application

1. **Start the Flask Backend** (Terminal 1)
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5001`

2. **Start the React Frontend** (Terminal 2)
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

### Automated Setup

Run the deployment script for automated setup:
```bash
./deploy.sh
```

## Usage

1. **Describe the Incident**: Enter a description of the crime in plain language
   - Example: "Someone stole my bike from outside my house"
   - Example: "My neighbor hit me with a stick during an argument"

2. **Get Analysis**: The AI will analyze your description and return relevant IPC sections

3. **Review Results**: Each result includes:
   - IPC Section number and title
   - Detailed description of the law
   - Punishment details
   - Confidence score

4. **Try Examples**: Click on the example queries to see how the system works

## API Endpoints

### POST `/api/analyze`
Analyzes a crime description and returns relevant IPC sections with AI enhancements.

**Request:**
```json
{
  "description": "Someone stole my bike"
}
```

**Response:**
```json
{
  "message": "Based on your description...",
  "sections": [...],
  "confidence": 0.85,
  "matched_keywords": ["stole", "bike"],
  "suggestions": ["File an FIR at the nearest police station", "Gather evidence like CCTV footage"],
  "enhanced_analysis": {
    "analysis": "Detailed AI analysis...",
    "additional_sections": ["section1", "section2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "considerations": ["consideration1", "consideration2"],
    "next_steps": ["step1", "step2"]
  }
}
```

### POST `/api/suggestions`
Get AI-powered suggestions for a query.

### GET `/api/status`
Get the status of ML models and features.

### GET `/api/sections`
Returns all available IPC sections.

### GET `/api/search?q=<query>`
Searches IPC sections by keyword.

### GET `/api/logs`
Returns conversation logs (for analysis).

## Adding New IPC Sections

To add new IPC sections, edit `data/ipc_sections.json`:

```json
{
  "section_number": "XXX",
  "title": "Section Title",
  "keywords": ["keyword1", "keyword2", "synonyms"],
  "description": "Detailed description of the section",
  "punishment": "Punishment details"
}
```

## Customization

### Styling
- Modify `src/index.css` for global styles
- Update `tailwind.config.js` for theme customization
- Edit component styles in `src/App.jsx`

### Backend Logic
- Modify `app.py` for API changes
- Update similarity thresholds in `find_relevant_sections()`
- Add new preprocessing in `extract_keywords()`

### Data
- Expand `data/ipc_sections.json` with more sections
- Add new keywords for better matching
- Include additional legal acts beyond IPC

## Development

### Frontend Development
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development
```bash
python app.py        # Run Flask development server
```

## 🚀 Deployment

### Quick Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

### Automated Deployment Preparation

```bash
# Run the automated deployment script
./deploy.sh
```

This script will:
- ✅ Check all prerequisites
- ✅ Build the frontend
- ✅ Install backend dependencies
- ✅ Set up environment files
- ✅ Create deployment configurations
- ✅ Test the application

### Deployment Options

#### 🎯 Recommended: Vercel + Railway
- **Frontend**: Deploy to Vercel (free tier available)
- **Backend**: Deploy to Railway (free tier available)
- **Database**: Built-in JSON storage

#### 🌐 Alternative: Netlify + Heroku
- **Frontend**: Deploy to Netlify
- **Backend**: Deploy to Heroku
- **Database**: Built-in JSON storage

#### ☁️ Enterprise: AWS
- **Frontend**: S3 + CloudFront
- **Backend**: Elastic Beanstalk
- **Database**: RDS (if needed)

### Environment Variables

#### Frontend (.env.production)
```bash
VITE_API_URL=https://your-backend-url.com
VITE_APP_NAME=IPC Crime Analyzer
VITE_APP_VERSION=1.0.0
```

#### Backend (.env.production)
```bash
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

### Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] CORS settings updated for your domain
- [ ] API endpoints accessible
- [ ] Frontend-backend communication working
- [ ] Error handling and logging configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Legal Disclaimer

⚠️ **Important**: This tool provides general legal information based on the Indian Penal Code and should not be considered as legal advice. For specific legal guidance, please consult with a qualified lawyer or legal professional.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the legal community**
