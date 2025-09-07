# FLUX-LanternHive Integration

A revolutionary programming environment that combines the FLUX programming language with the LanternHive cognitive framework, creating an intelligent IDE with AI-powered code assistance and multi-agent cognitive processing.

## 🌟 Overview

This project integrates two powerful systems:

- **FLUX Programming Language**: A connection-oriented programming language with floating memory, cryptographic fingerprinting, and natural language APIs
- **LanternHive Cognitive Framework**: A multi-agent AI system with specialized "Lanterns" for complex problem-solving and code analysis

## 🚀 Features

### FLUX Language Features
- **Connection-Oriented Programming**: All operations exist within connection contexts
- **Floating Memory Management**: Dynamic memory allocation tied to connection lifecycles
- **Cryptographic Fingerprinting**: Data persistence through cryptographic signatures
- **Natural Language API**: Human-readable system commands and interfaces
- **SIIG Data Transfer**: Secure, point-to-point data transmission
- **Modular Architecture**: Reusable memory modules and transfer protocols

### LanternHive Cognitive Features
- **Multi-Agent Processing**: Specialized Lanterns for different aspects of problem-solving
- **Bloom Taxonomy Classification**: Automatic complexity assessment of queries
- **Internal Dialogue**: Lanterns collaborate on complex problems
- **Symbolic Processing**: Brack notation and AGI Rosetta compression
- **Real-time Code Analysis**: Intelligent suggestions and optimization recommendations

### Integrated IDE Features
- **Real-time Backend Communication**: WebSocket-based connection to Python backend
- **Cognitive Assistance Panel**: Interactive AI-powered code assistance
- **Lantern Dialogue Visualization**: See the internal AI reasoning process
- **Live Code Execution**: Execute FLUX programs with real-time feedback
- **Interactive Visualizations**: Memory, connections, fingerprints, and transfers
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web IDE)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   FLUX Editor   │  │ LanternHive UI  │  │ Visualizer  │ │
│  │   (app.js)      │  │   (Cognitive)   │  │  (Memory,   │ │
│  │                 │  │                 │  │ Connections)│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Python Flask)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ FLUX Interpreter│  │ Enhanced        │  │   REST API  │ │
│  │   (Parser &     │  │ LanternHive     │  │ & WebSocket │ │
│  │   Executor)     │  │ (Multi-Agent)   │  │   Server    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OpenAI API                               │
│              (GPT-4 Turbo for Lanterns)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for development)
- OpenAI API key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd flux-lanternhive-integration
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_flask_secret_key_here
```

### 4. Start the Backend Server
```bash
python flux_backend.py
```

The backend will start on `http://localhost:5000`

### 5. Open the Frontend
Open `index.html` in your web browser, or serve it using a local web server:
```bash
# Using Python's built-in server
python -m http.server 8080

# Then open http://localhost:8080 in your browser
```

## 🎯 Usage

### Basic FLUX Programming

1. **Select an Example**: Choose from Hello World, Session Management, Data Transfer, or Natural Language API examples
2. **Write FLUX Code**: Use the integrated editor with syntax highlighting
3. **Execute Programs**: Click "Execute" to run your FLUX code
4. **Monitor Execution**: Watch real-time logs and visualizations

### LanternHive Cognitive Assistance

1. **Ask Questions**: Use the cognitive query textarea to ask questions about your code
2. **Analyze Code**: Click "Analyze Current Code" for AI-powered code review
3. **View Dialogue**: Watch the internal Lantern dialogue for complex queries
4. **Get Suggestions**: Receive optimization and improvement recommendations

### Example FLUX Programs

#### Hello World
```flux
connection hello_world {
    floating<string> message = "Hello, FLUX World!"
    
    on_connect {
        print(message)
    }
}
```

#### Session Management with Authentication
```flux
connection user_session {
    floating<string> username = "john_doe"
    persistent<preferences> user_prefs
    
    on_connect {
        user_prefs = restore_fingerprint("user_config_v1")
        authenticate(natural("retrieve my login"))
    }
    
    on_disconnect {
        store_fingerprint(user_prefs, username.fingerprint())
    }
}

memory_module<auth_data> auth_module {
    api_key floating_key
    codename<"secure_session"> session_id
}
```

## 🧠 LanternHive Lanterns

The system includes both cognitive and FLUX-specific Lanterns:

### Cognitive Lanterns
- **Planner** 🧭: Architecture and system design
- **Cogsworth** 📜: Compliance and technical requirements
- **Intuitor** 👁️: Risk assessment and security analysis
- **Archiva** 🧠: Pattern recognition and historical analysis
- **Eidolon** 🕯️: Final synthesis and integration

### FLUX-Specific Lanterns
- **Connection Architect** 🔗: FLUX connection design and optimization
- **Memory Weaver** 🧵: Floating memory and fingerprint management
- **Natural Interpreter** 🗣️: Natural language API translation
- **SIIG Guardian** 🛡️: Secure data transfer protocols
- **Symbolic Sage** 🔮: Brack notation and symbolic processing

## 📁 Project Structure

```
flux-lanternhive-integration/
├── README.md                 # This file
├── TODO.md                   # Development progress tracker
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── flux_backend.py           # Flask backend server
├── enhanced_lanternhive.py   # Enhanced LanternHive framework
├── lanternHive.py           # Original LanternHive implementation
├── index.html               # Main web interface
├── app.js                   # Frontend JavaScript application
├── style.css                # Comprehensive styling
├── FLUX-language-spec.md    # FLUX language specification
├── flux-implementation.md   # Implementation details
├── Hive_mind_thought.md     # LanternHive cognitive framework docs
└── script*.py               # Various utility scripts
```

## 🔧 API Endpoints

### REST API
- `GET /api/health` - Health check and system status
- `POST /api/flux/parse` - Parse FLUX code
- `POST /api/flux/execute` - Execute FLUX programs
- `POST /api/lantern/process` - Process queries with LanternHive
- `GET /api/connections` - Get active connections
- `GET /api/memory` - Get floating memory blocks
- `GET /api/fingerprints` - Get cryptographic fingerprints

### WebSocket Events
- `execute_flux` - Execute FLUX code in real-time
- `lantern_query` - Process cognitive queries
- `get_system_state` - Retrieve current system state
- `execution_result` - Receive execution results
- `lantern_response` - Receive cognitive responses

## 🎨 Customization

### Adding New Lanterns
1. Define the Lantern in `enhanced_lanternhive.py`
2. Add the icon mapping in `app.js`
3. Update the CSS styling if needed

### Extending FLUX Language
1. Add new patterns to `FLUXInterpreter` class
2. Implement execution logic in `execute_action`
3. Update the language specification

### UI Customization
- Modify `style.css` for visual changes
- Update `index.html` for structural changes
- Extend `app.js` for new functionality

## 🐛 Troubleshooting

### Backend Connection Issues
- Ensure the Flask server is running on port 5000
- Check that the OpenAI API key is properly configured
- Verify WebSocket connection in browser developer tools

### LanternHive Not Working
- Confirm OpenAI API key is valid and has sufficient credits
- Check the console for error messages
- Ensure the backend shows "LanternHive initialized successfully"

### FLUX Code Execution Problems
- Verify FLUX syntax matches the language specification
- Check the execution logs in the console
- Try the provided example programs first

## 🚀 Development

### Running in Development Mode
```bash
# Backend with debug mode
python flux_backend.py

# Frontend with live reload (if using a development server)
npm install -g live-server
live-server --port=8080
```

### Testing
```bash
# Run Python tests
pytest

# Test individual components
python enhanced_lanternhive.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT-4 API that powers LanternHive
- The FLUX language design inspired by connection-oriented computing research
- Socket.IO for real-time communication
- Flask for the robust backend framework

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the TODO.md for current development status
- Review the language specifications for detailed documentation

---

**FLUX-LanternHive Integration** - Where connection-oriented programming meets cognitive AI assistance.
