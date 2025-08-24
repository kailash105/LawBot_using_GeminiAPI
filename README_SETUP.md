# IPC Crime Analyzer - Setup & Usage Guide

An AI-powered chatbot that identifies relevant Indian Penal Code (IPC) sections from crime descriptions in plain language. Built with React + Vite frontend and Flask backend.

## 🚀 Features

- 🧠 **AI-Powered Analysis**: Advanced ML models with semantic search and LLM enhancement for accurate results
- 🔍 **Smart Search**: TF-IDF vectorization for better keyword matching
- ⚡ **LLM Suggestions**: AI-powered legal suggestions and recommendations for your case
- 📚 **Comprehensive Database**: Extensive collection of IPC sections with detailed descriptions and punishments
- 💬 **Conversation Logs**: All interactions are logged for future reference and analysis
- 🎨 **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS
- 🔍 **Multiple Crime Detection**: Can handle multiple crimes in a single query
- 📱 **Mobile Responsive**: Works seamlessly on all devices

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Google Gemini AI** - LLM enhancement and suggestions
- **Scikit-learn** - TF-IDF and ML algorithms
- **NumPy & Pandas** - Data handling
- **JSON** - Data storage

## 📁 Project Structure

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
├── ml_enhancer.py         # AI/ML logic module
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
├── deploy.sh              # Automated setup script
└── README.md             # Main documentation
```

## ⚡ Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **Git**

### 🚀 Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lawbot
   ```

2. **Run the automated setup script**
   ```bash
   ./deploy.sh
   ```
   
   This script will:
   - ✅ Check all prerequisites
   - ✅ Install frontend dependencies
   - ✅ Create and configure Python virtual environment
   - ✅ Install backend dependencies
   - ✅ Set up environment files
   - ✅ Build the frontend
   - ✅ Test the application

3. **Configure API Keys**
   ```bash
   # Edit the .env file with your Gemini API key
   nano .env
   ```

### 🔧 Manual Setup

If you prefer manual setup:

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
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env and add your Gemini API key
   ```

## 🏃‍♂️ Running the Application

### Development Mode

1. **Start the Flask Backend** (Terminal 1)
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python app.py
   ```
   The backend will run on `http://localhost:5001`

2. **Start the React Frontend** (Terminal 2)
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

### Production Build

1. **Build the frontend**
   ```bash
   npm run build
   ```

2. **Serve the production build**
   ```bash
   npm run preview
   ```

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```bash
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
```

### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and add it to your `.env` file

## 💬 Usage

### Basic Usage

1. **Open the application** in your browser
2. **Type a crime description** in plain language
3. **Submit** and get relevant IPC sections
4. **Review AI analysis** and suggestions

### Example Queries

- "Someone stole my phone"
- "My neighbor hit me with a stick during an argument"
- "Someone threatened me with a knife"
- "A person broke into my house and stole my laptop"
- "Someone posted my private photos online without permission"

### Features

- **Smart Matching**: The AI analyzes your description and finds the most relevant IPC sections
- **Confidence Scores**: Each result shows how confident the system is about the match
- **AI Analysis**: Get detailed legal analysis and suggestions
- **Additional Sections**: Discover related IPC sections that might apply
- **Next Steps**: Get practical advice on what to do next

## 🔧 Configuration

### ML Model Settings

In your `.env` file, you can configure:

- `USE_AI_MODEL`: Enable/disable AI enhancement (GEMINI/OFF)
- `USE_SEMANTIC_SEARCH`: Enable/disable semantic search
- `SIMILARITY_THRESHOLD`: Minimum confidence score (0.0-1.0)
- `GEMINI_MODEL`: Choose Gemini model (gemini-1.5-flash/gemini-1.5-pro)

### Logging

- `ENABLE_CONVERSATION_LOGS`: Save conversation history
- `LOG_LEVEL`: Set logging level (DEBUG/INFO/WARNING/ERROR)

## 📊 API Endpoints

### Core Endpoints

- `POST /api/analyze` - Analyze crime description
- `POST /api/suggestions` - Get AI suggestions
- `GET /api/status` - Check system status
- `GET /api/sections` - Get all IPC sections
- `GET /api/search?q=<query>` - Search sections by keyword

### Example API Usage

```bash
# Analyze a crime description
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"description": "Someone stole my phone"}'

# Get system status
curl http://localhost:5001/api/status
```

## 🗃️ Data Management

### Adding New IPC Sections

Edit `data/ipc_sections.json` to add new sections:

```json
{
  "section_number": "XXX",
  "title": "Section Title",
  "keywords": ["keyword1", "keyword2", "synonyms"],
  "description": "Detailed description of the section",
  "punishment": "Punishment details"
}
```

### Conversation Logs

Logs are automatically saved to the `logs/` directory:
- `conversation_logs.json` - Structured conversation data
- `app.log` - Application logs

## 🛠️ Development

### Frontend Development

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run Flask development server
python app.py

# Run with debug mode
FLASK_ENV=development python app.py
```

### Code Structure

- **Frontend**: React components in `src/`
- **Backend**: Flask app in `app.py`
- **AI Logic**: ML enhancer in `ml_enhancer.py`
- **Data**: IPC sections in `data/ipc_sections.json`

## 🔍 Troubleshooting

### Common Issues

1. **Port 5001 already in use**
   ```bash
   # Kill existing process
   pkill -f "python app.py"
   # Or change port in app.py
   ```

2. **Module not found errors**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **API key errors**
   - Check `.env` file exists
   - Verify Gemini API key is correct
   - Ensure API key has sufficient quota

4. **Frontend build errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
# Backend
FLASK_ENV=development python app.py

# Frontend
npm run dev
```

## 📚 Learning Resources

- [Indian Penal Code](https://legislative.gov.in/indian-penal-code) - Official IPC
- [React Documentation](https://react.dev/) - React framework
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [Google Gemini AI](https://ai.google.dev/) - AI model documentation

## ⚖️ Legal Disclaimer

⚠️ **Important**: This tool provides general legal information based on the Indian Penal Code and should not be considered as legal advice. For specific legal guidance, please consult with a qualified lawyer or legal professional.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support:
1. Check the troubleshooting section above
2. Review the logs in `logs/` directory
3. Open an issue on GitHub
4. Contact the development team

---

**🎉 Your IPC Crime Analyzer is ready to use!**

Start by running `./deploy.sh` for automated setup, or follow the manual setup instructions above.
