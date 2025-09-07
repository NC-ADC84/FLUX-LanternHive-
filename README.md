# FLUX-LanternHive AI Development Platform

A comprehensive AI-powered development platform that combines the FLUX programming language with advanced AI capabilities including LanternHive cognitive framework, PTPF prompt engineering, and recursive strategy engines.

## 🚀 Features

### Core Components

- **FLUX Programming Language**: Connection-oriented language with floating memory, cryptographic fingerprinting, and natural language APIs
- **LanternHive Cognitive Framework**: Multi-agent AI system for code analysis and problem-solving
- **PTPF (PrimeTalk Vibe-Context Coding)**: Advanced prompt engineering framework for structured prompt generation
- **Recursive Strategy Engine**: Intelligent problem-solving strategies including decomposition, pattern recognition, heuristic search, and meta-learning

### Integrated Workflow

1. **Natural Language Input**: Describe what you want to build in plain English
2. **AI Strategy Selection**: Choose from 4 intelligent problem-solving approaches
3. **PTPF Prompt Engineering**: Generate structured prompts for optimal AI responses
4. **LanternHive Analysis**: AI-powered code generation and analysis
5. **FLUX Code Generation**: Automatic generation of executable FLUX code
6. **Real-time Execution**: Execute and test your generated code

## 🛠️ Technology Stack

- **Backend**: Python Flask with Socket.IO for real-time communication
- **Frontend**: HTML5, CSS3, JavaScript with modern UI/UX
- **AI Integration**: OpenAI GPT-5 for cognitive analysis
- **Deployment**: Google Cloud Run with Docker containerization
- **Database**: PostgreSQL with Redis caching

## 📋 Prerequisites

- Python 3.8+
- Node.js (for frontend dependencies)
- Google Cloud CLI (for deployment)
- OpenAI API key

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-github-repo-url>
   cd flux-lanternhive
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your OpenAI API key and other settings
   ```

4. **Start the development server**
   ```bash
   python start_server.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - The integrated workflow will guide you through the AI-powered development process

### Production Deployment

1. **Deploy to Google Cloud Run**
   ```bash
   # Build and deploy
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/flux-lanternhive
   gcloud run deploy flux-lanternhive --image gcr.io/YOUR_PROJECT_ID/flux-lanternhive --platform managed --region us-central1 --allow-unauthenticated
   ```

2. **Set environment variables**
   ```bash
   gcloud run services update flux-lanternhive --set-env-vars OPENAI_API_KEY=your_key_here
   ```

## 🎯 Usage

### Basic Workflow

1. **Describe Your Request**: Enter what you want to build in natural language
2. **Select AI Strategy**: Choose from:
   - **Problem Decomposition**: Break down complex problems into manageable components
   - **Pattern Recognition**: Apply proven architectural solutions
   - **Heuristic Search**: Use intelligent algorithms to find optimal approaches
   - **Meta-Learning**: Learn from similar problems and adapt solutions

3. **AI Processing**: The system automatically:
   - Generates PTPF prompts
   - Runs LanternHive analysis
   - Creates FLUX code
   - Provides execution results

### Example Requests

- "Create a user authentication system with session management"
- "Build a data processing pipeline for real-time analytics"
- "Design a microservices architecture for an e-commerce platform"
- "Implement a secure file transfer system with encryption"

## 📁 Project Structure

```
flux-lanternhive/
├── flux_backend.py          # Main Flask backend server
├── enhanced_lanternhive.py  # LanternHive cognitive framework
├── ptpf_flux_generator.py   # PTPF prompt engineering
├── recursive_strategy_engine.py # Strategy execution engine
├── index.html              # Frontend interface
├── style.css               # UI styling
├── app.js                  # Frontend JavaScript
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── cloudbuild.yaml        # Google Cloud Build config
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality
- `FLASK_ENV`: Set to 'production' for production deployment
- `SECRET_KEY`: Flask secret key for session management

### API Endpoints

- `POST /api/lantern/process`: LanternHive AI analysis
- `POST /api/ptpf/generate`: PTPF prompt generation
- `POST /api/strategies/execute`: Strategy execution
- `GET /api/health`: Health check endpoint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the FLUX language specification in `FLUX-language-spec.md`

## 🎉 Acknowledgments

- OpenAI for GPT-5 API
- Google Cloud Platform for hosting infrastructure
- The FLUX programming language community
- All contributors and testers

---

**Built with ❤️ using AI-powered development tools**