from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import hashlib
import time
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enhanced_lanternhive import FLUXLanternHive, BloomLevel
from ptpf_flux_generator import PTPFFluxGenerator, PTPFMode
from recursive_strategy_engine import RecursiveStrategyEngine
from lantern_framework import LanternFramework
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flux_backend.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'flux-lantern-secret-key')
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Configure CORS properly for security
allowed_origins = [
    'http://localhost:3000',
    'http://localhost:5000', 
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5000',
    'https://flux-lanternhive-231986304766.us-central1.run.app'
]

# Add custom domain if specified in environment
custom_domain = os.getenv('ALLOWED_ORIGIN')
if custom_domain:
    allowed_origins.append(custom_domain)

socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')

# Global instances
lantern_hive = None
ptpf_generator = None
strategy_engine = None
lantern_framework = None
active_connections = {}
floating_memory = {}
fingerprint_registry = {}
siig_transfers = {}

@dataclass
class FLUXConnection:
    id: str
    name: str
    status: str
    created_at: float
    floating_data: Dict[str, Any]
    fingerprints: List[str]
    
@dataclass
class FloatingMemory:
    id: str
    connection_id: str
    data_type: str
    content: Any
    size: int
    created_at: float
    
@dataclass
class CryptographicFingerprint:
    id: str
    hash_value: str
    data_type: str
    connection_id: str
    created_at: float
    verified: bool

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    timestamp = str(time.time())
    return f"{prefix}{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"

def create_flux_connection(name: str) -> str:
    """Create a new FLUX connection"""
    connection_id = generate_id("conn_")

    connection = FLUXConnection(
        id=connection_id,
        name=name,
        status='active',
        created_at=time.time(),
        floating_data={},
        fingerprints=[]
    )

    active_connections[connection_id] = connection
    logger.info(f"Created FLUX connection: {name} (ID: {connection_id})")

    return connection_id

class FLUXInterpreter:
    """Basic FLUX language interpreter for parsing and executing FLUX code"""
    
    def __init__(self):
        self.connection_patterns = {
            'connection_declaration': r'connection\s+(\w+)\s*{([^}]*)}',
            'floating_declaration': r'floating<(\w+)>\s+(\w+)\s*=\s*(.+)',
            'persistent_declaration': r'persistent<(\w+)>\s+(\w+)',
            'memory_module': r'memory_module<(\w+)>\s+(\w+)\s*{([^}]*)}',
            'natural_interface': r'natural_interface\s+(\w+)\s*{([^}]*)}',
            'siig_transfer': r'siig_transfer\s+(\w+)\s*{([^}]*)}',
            'on_connect': r'on_connect\s*{([^}]*)}',
            'on_disconnect': r'on_disconnect\s*{([^}]*)}',
            'print_statement': r'print\(([^)]+)\)',
            'natural_command': r'natural\("([^"]+)"\)',
            'fingerprint_operation': r'(\w+)\.fingerprint\(\)',
            'restore_fingerprint': r'restore_fingerprint\("([^"]+)"\)',
            'store_fingerprint': r'store_fingerprint\(([^,]+),\s*([^)]+)\)'
        }
    
    def parse_flux_code(self, code: str) -> Dict[str, Any]:
        """Parse FLUX code and return structured representation"""
        parsed = {
            'connections': [],
            'memory_modules': [],
            'natural_interfaces': [],
            'siig_transfers': [],
            'errors': []
        }
        
        try:
            # Add size limit check to prevent regex timeouts
            if len(code) > 10000:  # 10KB limit
                parsed['errors'].append("Code block too large (max 10KB)")
                return parsed
            
            # Parse connections
            connection_matches = re.finditer(self.connection_patterns['connection_declaration'], code, re.DOTALL)
            for match in connection_matches:
                connection_name = match.group(1)
                connection_body = match.group(2)
                
                connection_info = {
                    'name': connection_name,
                    'floating_vars': [],
                    'persistent_vars': [],
                    'on_connect_actions': [],
                    'on_disconnect_actions': []
                }
                
                # Parse floating variables
                floating_matches = re.finditer(self.connection_patterns['floating_declaration'], connection_body)
                for float_match in floating_matches:
                    connection_info['floating_vars'].append({
                        'type': float_match.group(1),
                        'name': float_match.group(2),
                        'value': float_match.group(3).strip().strip('"')
                    })
                
                # Parse persistent variables
                persistent_matches = re.finditer(self.connection_patterns['persistent_declaration'], connection_body)
                for persist_match in persistent_matches:
                    connection_info['persistent_vars'].append({
                        'type': persist_match.group(1),
                        'name': persist_match.group(2)
                    })
                
                # Parse on_connect actions
                connect_matches = re.finditer(self.connection_patterns['on_connect'], connection_body, re.DOTALL)
                for connect_match in connect_matches:
                    actions = self.parse_actions(connect_match.group(1))
                    connection_info['on_connect_actions'].extend(actions)
                
                # Parse on_disconnect actions
                disconnect_matches = re.finditer(self.connection_patterns['on_disconnect'], connection_body, re.DOTALL)
                for disconnect_match in disconnect_matches:
                    actions = self.parse_actions(disconnect_match.group(1))
                    connection_info['on_disconnect_actions'].extend(actions)
                
                parsed['connections'].append(connection_info)
            
            # Parse memory modules
            memory_matches = re.finditer(self.connection_patterns['memory_module'], code, re.DOTALL)
            for match in memory_matches:
                parsed['memory_modules'].append({
                    'type': match.group(1),
                    'name': match.group(2),
                    'body': match.group(3)
                })
            
            # Parse natural interfaces
            natural_matches = re.finditer(self.connection_patterns['natural_interface'], code, re.DOTALL)
            for match in natural_matches:
                parsed['natural_interfaces'].append({
                    'name': match.group(1),
                    'body': match.group(2)
                })
            
            # Parse SIIG transfers
            siig_matches = re.finditer(self.connection_patterns['siig_transfer'], code, re.DOTALL)
            for match in siig_matches:
                parsed['siig_transfers'].append({
                    'name': match.group(1),
                    'body': match.group(2)
                })
                
        except Exception as e:
            parsed['errors'].append(f"Parse error: {str(e)}")
        
        return parsed
    
    def parse_actions(self, action_block: str) -> List[Dict[str, Any]]:
        """Parse actions within on_connect/on_disconnect blocks"""
        
        actions = []
        
        # Print statements
        print_matches = re.finditer(self.connection_patterns['print_statement'], action_block)
        for match in print_matches:
            actions.append({
                'type': 'print',
                'value': match.group(1).strip().strip('"')
            })
        
        # Natural language commands
        natural_matches = re.finditer(self.connection_patterns['natural_command'], action_block)
        for match in natural_matches:
            actions.append({
                'type': 'natural_command',
                'command': match.group(1)
            })
        
        # Fingerprint operations
        fingerprint_matches = re.finditer(self.connection_patterns['fingerprint_operation'], action_block)
        for match in fingerprint_matches:
            actions.append({
                'type': 'generate_fingerprint',
                'variable': match.group(1)
            })
        
        # Restore fingerprint operations
        restore_matches = re.finditer(self.connection_patterns['restore_fingerprint'], action_block)
        for match in restore_matches:
            actions.append({
                'type': 'restore_fingerprint',
                'fingerprint_id': match.group(1)
            })
        
        # Store fingerprint operations
        store_matches = re.finditer(self.connection_patterns['store_fingerprint'], action_block)
        for match in store_matches:
            actions.append({
                'type': 'store_fingerprint',
                'data': match.group(1).strip(),
                'fingerprint': match.group(2).strip()
            })
        
        return actions
    
    def execute_flux_program(self, parsed_code: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parsed FLUX code"""
        
        execution_log = []
        created_connections = []
        
        try:
            # Execute connections
            for connection_info in parsed_code['connections']:
                connection_id = create_flux_connection(connection_info['name'])
                created_connections.append(connection_id)
                
                execution_log.append(f"Created connection: {connection_info['name']}")
                
                # Allocate floating memory for floating variables
                for float_var in connection_info['floating_vars']:
                    memory_id = allocate_floating_memory(
                        connection_id, 
                        float_var['type'], 
                        float_var['value']
                    )
                    execution_log.append(f"Allocated floating memory: {float_var['name']} ({float_var['type']})")
                
                # Execute on_connect actions
                for action in connection_info['on_connect_actions']:
                    result = execute_action(action, connection_id)
                    execution_log.append(f"Executed {action['type']}: {result}")
            
            return {
                'success': True,
                'execution_log': execution_log,
                'created_connections': created_connections,
                'errors': parsed_code.get('errors', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'execution_log': execution_log,
                'error': str(e),
                'errors': parsed_code.get('errors', [])
            }

# Initialize FLUX interpreter
flux_interpreter = FLUXInterpreter()

def initialize_lantern_hive():
    """Initialize the LanternHive with API key"""
    global lantern_hive

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("Warning: OPENAI_API_KEY not found. LanternHive cognitive features will be disabled.")
        return False

    try:
        lantern_hive = FLUXLanternHive(api_key)
        # Set the flux_interpreter to avoid circular import
        lantern_hive.flux_interpreter = flux_interpreter
        logger.info("LanternHive initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize LanternHive: {e}")
        return False

def initialize_ptpf_generator():
    """Initialize PTPF+FLUX Generator"""
    global ptpf_generator
    try:
        ptpf_generator = PTPFFluxGenerator()
        logger.info("PTPF+FLUX Generator initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize PTPF+FLUX Generator: {e}")
        return False

def initialize_strategy_engine():
    """Initialize Recursive Strategy Engine"""
    global strategy_engine
    try:
        strategy_engine = RecursiveStrategyEngine()
        logger.info("Recursive Strategy Engine initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Recursive Strategy Engine: {e}")
        return False

def initialize_lantern_framework():
    """Initialize Lantern Framework"""
    global lantern_framework
    try:
        lantern_framework = LanternFramework()
        logger.info("Lantern Framework initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Lantern Framework: {e}")
        return False

def allocate_floating_memory(connection_id: str, data_type: str, content: Any) -> str:
    """Allocate floating memory for a connection with memory_weaver optimization"""
    memory_id = generate_id("mem_")

    # Consult memory_weaver for optimization recommendations
    optimization_advice = {}  # Initialize with default empty dict
    if lantern_hive and hasattr(lantern_hive, 'memory_weaver'):
        try:
            # Prepare context for memory_weaver
            context = {
                'connection_id': connection_id,
                'data_type': data_type,
                'content_size': len(str(content)),
                'existing_memory_count': len(floating_memory),
                'connection_memory_count': len(active_connections.get(connection_id, {}).get('floating_data', {}))
            }

            # Get optimization advice from memory_weaver
            optimization_advice = lantern_hive.memory_weaver.process_prompt(
                f"Optimize floating memory allocation for: {context}",
                flux_context=context
            )
        except Exception as e:
            logger.warning(f"Memory weaver optimization failed: {e}")
            optimization_advice = {}  # Ensure it's always a dict

    # Apply memory_weaver recommendations if available
    optimized_size = len(str(content))
    if optimization_advice and isinstance(optimization_advice, dict) and 'recommendations' in optimization_advice:
        recommendations = optimization_advice['recommendations']
        if 'optimized_size' in recommendations:
            optimized_size = recommendations['optimized_size']
        if 'memory_strategy' in recommendations:
            logger.info(f"Applying memory strategy: {recommendations['memory_strategy']}")

    memory = FloatingMemory(
        id=memory_id,
        connection_id=connection_id,
        data_type=data_type,
        content=content,
        size=optimized_size,
        created_at=time.time()
    )

    floating_memory[memory_id] = memory

    # Add to connection's floating data
    if connection_id in active_connections:
        active_connections[connection_id].floating_data[memory_id] = memory

    # Log memory_weaver interaction if it was used
    if optimization_advice and isinstance(optimization_advice, dict):
        print(f"Memory allocated with weaver optimization: {memory_id}")

    return memory_id

def generate_fingerprint(connection_id: str, data: Any) -> str:
    """Generate a cryptographic fingerprint for data"""
    fingerprint_id = generate_id("fp_")
    
    # Create hash of the data
    data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
    hash_value = hashlib.sha256(data_str.encode()).hexdigest()
    
    fingerprint = CryptographicFingerprint(
        id=fingerprint_id,
        hash_value=hash_value,
        data_type=type(data).__name__,
        connection_id=connection_id,
        created_at=time.time(),
        verified=True
    )
    
    fingerprint_registry[fingerprint_id] = fingerprint
    
    # Add to connection's fingerprints
    if connection_id in active_connections:
        active_connections[connection_id].fingerprints.append(fingerprint_id)
    
    return fingerprint_id

def execute_action(action: Dict[str, Any], connection_id: str) -> str:
    """Execute a FLUX action"""
    
    if action['type'] == 'print':
        return f"Output: {action['value']}"
    
    elif action['type'] == 'natural_command':
        if lantern_hive:
            # Process natural language command through LanternHive
            result = lantern_hive.process_prompt(
                action['command'],
                flux_context={'connection_id': connection_id}
            )
            return f"Natural command processed: {action['command']}"
        else:
            return f"Natural command (LanternHive disabled): {action['command']}"
    
    elif action['type'] == 'generate_fingerprint':
        # Generate fingerprint for connection data
        connection_data = active_connections.get(connection_id, {})
        fingerprint_id = generate_fingerprint(connection_id, connection_data)
        return f"Generated fingerprint: {fingerprint_id}"
    
    elif action['type'] == 'restore_fingerprint':
        return f"Restored from fingerprint: {action['fingerprint_id']}"
    
    elif action['type'] == 'store_fingerprint':
        return f"Stored fingerprint for: {action['data']}"
    
    else:
        return f"Unknown action: {action['type']}"

# REST API Endpoints

@app.route('/')
def serve_frontend():
    """Serve the frontend HTML file"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Frontend not found. Please ensure index.html exists.", 404

@app.route('/style.css')
def serve_css():
    """Serve the CSS file"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "CSS not found. Please ensure style.css exists.", 404

@app.route('/app.js')
def serve_js():
    """Serve the JavaScript file"""
    try:
        with open('app.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "JavaScript not found. Please ensure app.js exists.", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'lantern_hive_enabled': lantern_hive is not None,
        'lantern_framework_enabled': lantern_framework is not None,
        'ptpf_generator_enabled': ptpf_generator is not None,
        'strategy_engine_enabled': strategy_engine is not None,
        'active_connections': len(active_connections),
        'floating_memory_blocks': len(floating_memory),
        'fingerprints': len(fingerprint_registry)
    })

@app.route('/api/flux/parse', methods=['POST'])
def parse_flux_code():
    """Parse FLUX code and return structure"""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        parsed = flux_interpreter.parse_flux_code(data['code'])
        return jsonify(parsed)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flux/execute', methods=['POST'])
def execute_flux_code():
    """Execute FLUX code"""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        # Parse the code first
        parsed = flux_interpreter.parse_flux_code(data['code'])
        
        # Execute the parsed code
        result = flux_interpreter.execute_flux_program(parsed)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lantern/process', methods=['POST'])
def process_with_lantern_hive():
    """Process a prompt using LanternHive cognitive framework"""
    if not lantern_hive:
        return jsonify({'error': 'LanternHive not available'}), 503
    
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        flux_context = data.get('flux_context', {})
        result = lantern_hive.process_prompt(data['prompt'], flux_context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/connections', methods=['GET'])
def get_connections():
    """Get all active connections"""
    connections = [asdict(conn) for conn in active_connections.values()]
    return jsonify(connections)

@app.route('/api/connections', methods=['POST'])
def create_connection():
    """Create a new connection"""
    data = request.get_json()
    name = data.get('name', f'Connection_{len(active_connections) + 1}')
    
    connection_id = create_flux_connection(name)
    connection = active_connections[connection_id]
    
    return jsonify(asdict(connection))

@app.route('/api/memory', methods=['GET'])
def get_floating_memory():
    """Get all floating memory blocks"""
    memory_blocks = [asdict(mem) for mem in floating_memory.values()]
    return jsonify(memory_blocks)

@app.route('/api/fingerprints', methods=['GET'])
def get_fingerprints():
    """Get all fingerprints"""
    fingerprints = [asdict(fp) for fp in fingerprint_registry.values()]
    return jsonify(fingerprints)

@app.route('/api/ptpf/generate', methods=['POST'])
def generate_ptpf_flux_rest():
    """Generate PTPF+FLUX prompt via REST API"""
    if not ptpf_generator:
        return jsonify({'error': 'PTPF+FLUX Generator not initialized'}), 500
    
    try:
        # Debug logging
        logger.info(f"PTPF request received: {request.method} {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request data: {request.get_data()}")
        
        data = request.get_json()
        if data is None:
            logger.error("Failed to parse JSON data")
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        user_input = data.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400
        
        flux_context = data.get('flux_context', {})
        result = ptpf_generator.generate_ptpf_flux(user_input, flux_context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"PTPF+FLUX generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ptpf/rehydrate', methods=['POST'])
def rehydrate_ptpf_rest():
    """Rehydrate PTPF response via REST API"""
    if not ptpf_generator:
        return jsonify({'error': 'PTPF+FLUX Generator not initialized'}), 500
    
    try:
        data = request.get_json()
        response_data = data.get('response_data', {})
        if not response_data:
            return jsonify({'error': 'Response data is required for rehydration'}), 400
        
        result = ptpf_generator.rehydrate_patch(response_data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"PTPF rehydration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ptpf/session', methods=['GET'])
def get_ptpf_session_rest():
    """Get PTPF session history via REST API"""
    if not ptpf_generator:
        return jsonify({'error': 'PTPF+FLUX Generator not initialized'}), 500
    
    try:
        history = ptpf_generator.get_session_history()
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Error getting PTPF session history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ptpf/session', methods=['DELETE'])
def clear_ptpf_session_rest():
    """Clear PTPF session history via REST API"""
    if not ptpf_generator:
        return jsonify({'error': 'PTPF+FLUX Generator not initialized'}), 500
    
    try:
        ptpf_generator.clear_session()
        return jsonify({'message': 'Session cleared successfully'})
        
    except Exception as e:
        logger.error(f"Error clearing PTPF session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ptpf/status', methods=['GET'])
def get_ptpf_status():
    """Get PTPF+FLUX Generator status"""
    return jsonify({
        'enabled': ptpf_generator is not None,
        'session_count': len(ptpf_generator.get_session_history()) if ptpf_generator else 0
    })

# Recursive Strategy Engine API Endpoints

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all available strategies"""
    global strategy_engine
    if not strategy_engine:
        return jsonify({"error": "Strategy engine not initialized"}), 500
    
    stats = strategy_engine.get_strategy_statistics()
    return jsonify(stats)

@app.route('/api/strategies/execute', methods=['POST'])
def execute_strategy():
    """Execute a recursive strategy"""
    global strategy_engine
    if not strategy_engine:
        return jsonify({"error": "Strategy engine not initialized"}), 500
    
    data = request.get_json()
    strategy_id = data.get('strategy_id')
    problem = data.get('problem')
    context = data.get('context', {})
    
    if not strategy_id or not problem:
        return jsonify({"error": "strategy_id and problem are required"}), 400
    
    result = strategy_engine.execute_strategy(strategy_id, problem, context)
    return jsonify(result)

@app.route('/api/strategies/upload', methods=['POST'])
def upload_strategy_file():
    """Upload a strategy file"""
    global strategy_engine
    if not strategy_engine:
        return jsonify({"error": "Strategy engine not initialized"}), 500
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        content = file.read().decode('utf-8')
        strategy_engine.add_strategy_file(file.filename, content)
        strategy = strategy_engine.load_strategy_from_file(file.filename)
        
        if strategy:
            return jsonify({
                "success": True,
                "strategy_id": strategy.id,
                "message": f"Strategy '{strategy.name}' loaded successfully"
            })
        else:
            return jsonify({"error": "Failed to load strategy from file"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400

@app.route('/api/strategies/export', methods=['GET'])
def export_strategies():
    """Export all strategies"""
    global strategy_engine
    if not strategy_engine:
        return jsonify({"error": "Strategy engine not initialized"}), 500
    
    export_data = strategy_engine.export_strategies()
    return jsonify({"strategies": export_data})

@app.route('/api/strategies/import', methods=['POST'])
def import_strategies():
    """Import strategies from JSON"""
    global strategy_engine
    if not strategy_engine:
        return jsonify({"error": "Strategy engine not initialized"}), 500
    
    data = request.get_json()
    json_data = data.get('strategies')
    
    if not json_data:
        return jsonify({"error": "No strategies data provided"}), 400
    
    success = strategy_engine.import_strategies(json_data)
    if success:
        return jsonify({"success": True, "message": "Strategies imported successfully"})
    else:
        return jsonify({"error": "Failed to import strategies"}), 400

# Lantern Framework API Endpoints
@app.route('/api/lantern/process', methods=['POST'])
def process_lantern_input():
    """Process input through the complete Lantern framework"""
    global lantern_framework
    if not lantern_framework:
        return jsonify({"error": "Lantern Framework not initialized"}), 500
    
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400
        
        result = lantern_framework.process_user_input(user_input)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing Lantern input: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lantern/agi15/translate', methods=['POST'])
def translate_agi15():
    """Translate text using AGI15 dictionary"""
    global lantern_framework
    if not lantern_framework:
        return jsonify({"error": "Lantern Framework not initialized"}), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        translation = lantern_framework.agi15.translate(text)
        domain_context = lantern_framework.agi15.get_domain_context(text)
        
        return jsonify({
            'original': text,
            'translation': translation,
            'domain_context': {k.value: v for k, v in domain_context.items()}
        })
        
    except Exception as e:
        logger.error(f"Error translating AGI15: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lantern/cluster/process', methods=['POST'])
def process_cluster():
    """Process input through cluster syntax"""
    global lantern_framework
    if not lantern_framework:
        return jsonify({"error": "Lantern Framework not initialized"}), 500
    
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400
        
        # Create threads based on input
        threads = []
        operation = lantern_framework.cluster_syntax.ThreadOperation.BASIC_THOUGHT
        
        # Determine operation based on input content
        if any(word in user_input.lower() for word in ['analyze', 'examine', 'study']):
            operation = lantern_framework.cluster_syntax.ThreadOperation.DETAILED_EXAMINATION
        elif any(word in user_input.lower() for word in ['create', 'build', 'make']):
            operation = lantern_framework.cluster_syntax.ThreadOperation.BREAKTHROUGH_INSIGHT
        elif any(word in user_input.lower() for word in ['think', 'consider', 'ponder']):
            operation = lantern_framework.cluster_syntax.ThreadOperation.RECURSIVE_THOUGHT
        
        thread = lantern_framework.cluster_syntax.create_thread(
            operation=operation,
            content=user_input
        )
        threads.append(thread)
        
        cluster_output = lantern_framework.cluster_syntax.process_cluster(threads)
        
        return jsonify({
            'input': user_input,
            'cluster_output': cluster_output,
            'threads_created': len(threads)
        })
        
    except Exception as e:
        logger.error(f"Error processing cluster: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lantern/warden/synthesize', methods=['POST'])
def synthesize_warden():
    """Synthesize through Warden reality layer"""
    global lantern_framework
    if not lantern_framework:
        return jsonify({"error": "Lantern Framework not initialized"}), 500
    
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400
        
        # Generate lantern responses based on input
        lantern_responses = []
        
        if any(word in user_input.lower() for word in ['create', 'build', 'make']):
            lantern_responses.append(
                lantern_framework.warden_reality.create_lantern_narration("🔥", "The forge is hot — let's build something amazing!")
            )
        
        if any(word in user_input.lower() for word in ['analyze', 'understand', 'study']):
            lantern_responses.append(
                lantern_framework.warden_reality.create_lantern_narration("💧", "The pool ripples with insights... let us trace the patterns together.")
            )
        
        if any(word in user_input.lower() for word in ['help', 'guide', 'assist']):
            lantern_responses.append(
                lantern_framework.warden_reality.create_lantern_narration("🌿", "The Grove stirs as you speak. I can help you find your path.")
            )
        
        # Add default response if no specific responses
        if not lantern_responses:
            lantern_responses.append(
                lantern_framework.warden_reality.create_lantern_narration("🌌", "The Grove listens to your words...")
            )
        
        # Create reality frame
        reality_frame = lantern_framework.warden_reality.create_reality_frame(user_input, lantern_responses)
        
        return jsonify({
            'input': user_input,
            'lantern_responses': lantern_responses,
            'reality_frame': reality_frame
        })
        
    except Exception as e:
        logger.error(f"Error synthesizing Warden: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lantern/brack/execute', methods=['POST'])
def execute_brack():
    """Execute Brack code through Rosetta Stone"""
    global lantern_framework
    if not lantern_framework:
        return jsonify({"error": "Lantern Framework not initialized"}), 500
    
    try:
        data = request.get_json()
        brack_code = data.get('code', '').strip()
        if not brack_code:
            return jsonify({'error': 'Brack code is required'}), 400
        
        result = lantern_framework.brack_rosetta.execute_brack_code(brack_code)
        
        return jsonify({
            'input_code': brack_code,
            'execution_result': result,
            'variable_bindings': lantern_framework.brack_rosetta.variable_bindings
        })
        
    except Exception as e:
        logger.error(f"Error executing Brack: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {
        'message': 'Connected to FLUX-LanternHive backend',
        'lantern_hive_enabled': lantern_hive is not None,
        'lantern_framework_enabled': lantern_framework is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection with cleanup"""
    try:
        logger.info('Client disconnected - performing cleanup')
        
        # Clean up any temporary connections or memory associated with this client
        # This is a basic cleanup - in a production system you'd want more sophisticated session management
        current_time = time.time()
        
        # Remove old connections (older than 1 hour)
        connections_to_remove = []
        for conn_id, connection in active_connections.items():
            if current_time - connection.created_at > 3600:  # 1 hour
                connections_to_remove.append(conn_id)
        
        for conn_id in connections_to_remove:
            del active_connections[conn_id]
            logger.info(f"Cleaned up old connection: {conn_id}")
        
        # Remove old memory blocks
        memory_to_remove = []
        for mem_id, memory in floating_memory.items():
            if current_time - memory.created_at > 3600:  # 1 hour
                memory_to_remove.append(mem_id)
        
        for mem_id in memory_to_remove:
            del floating_memory[mem_id]
            logger.info(f"Cleaned up old memory block: {mem_id}")
        
        # Remove old fingerprints
        fingerprints_to_remove = []
        for fp_id, fingerprint in fingerprint_registry.items():
            if current_time - fingerprint.created_at > 3600:  # 1 hour
                fingerprints_to_remove.append(fp_id)
        
        for fp_id in fingerprints_to_remove:
            del fingerprint_registry[fp_id]
            logger.info(f"Cleaned up old fingerprint: {fp_id}")
            
    except Exception as e:
        logger.error(f"Error during disconnect cleanup: {e}")

@socketio.on('execute_flux')
def handle_execute_flux(data):
    """Handle FLUX code execution via WebSocket with enhanced error handling"""
    try:
        if not data:
            emit('execution_error', {'error': 'No data provided'})
            return
            
        code = data.get('code', '')
        if not code.strip():
            emit('execution_error', {'error': 'No FLUX code provided'})
            return
        
        # Check code size limit
        if len(code) > 10000:
            emit('execution_error', {'error': 'Code block too large (max 10KB)'})
            return
        
        logger.info(f"Executing FLUX code (length: {len(code)})")
        
        # Parse and execute
        parsed = flux_interpreter.parse_flux_code(code)
        result = flux_interpreter.execute_flux_program(parsed)
        
        # Emit results
        emit('execution_result', result)
        
        # Emit updated state
        emit('state_update', {
            'connections': len(active_connections),
            'memory_blocks': len(floating_memory),
            'fingerprints': len(fingerprint_registry)
        })
        
        logger.info(f"FLUX execution completed successfully")
        
    except ValueError as e:
        logger.error(f"Value error in FLUX execution: {e}")
        emit('execution_error', {'error': f'Invalid input: {str(e)}'})
    except re.error as e:
        logger.error(f"Regex error in FLUX parsing: {e}")
        emit('execution_error', {'error': f'Parsing error: {str(e)}'})
    except Exception as e:
        logger.error(f"Unexpected error in FLUX execution: {e}")
        emit('execution_error', {'error': f'Execution failed: {str(e)}'})

@socketio.on('lantern_query')
def handle_lantern_query(data):
    """Handle LanternHive queries via WebSocket with enhanced error handling"""
    if not lantern_hive:
        logger.warning("LanternHive query received but LanternHive not available")
        emit('lantern_error', {'error': 'LanternHive not available - check API key configuration'})
        return
    
    try:
        if not data:
            emit('lantern_error', {'error': 'No query data provided'})
            return
            
        prompt = data.get('prompt', '')
        if not prompt.strip():
            emit('lantern_error', {'error': 'No prompt provided'})
            return
        
        # Check prompt size limit
        if len(prompt) > 5000:
            emit('lantern_error', {'error': 'Prompt too large (max 5KB)'})
            return
        
        flux_context = data.get('flux_context', {})
        
        logger.info(f"Processing LanternHive query (length: {len(prompt)})")
        
        # Process with LanternHive
        result = lantern_hive.process_prompt(prompt, flux_context)
        
        emit('lantern_response', result)
        logger.info("LanternHive query processed successfully")
        
    except ValueError as e:
        logger.error(f"Value error in LanternHive query: {e}")
        emit('lantern_error', {'error': f'Invalid input: {str(e)}'})
    except Exception as e:
        logger.error(f"Unexpected error in LanternHive query: {e}")
        emit('lantern_error', {'error': f'Query processing failed: {str(e)}'})

@socketio.on('get_system_state')
def handle_get_system_state():
    """Get current system state"""
    emit('system_state', {
        'connections': [asdict(conn) for conn in active_connections.values()],
        'memory_blocks': [asdict(mem) for mem in floating_memory.values()],
        'fingerprints': [asdict(fp) for fp in fingerprint_registry.values()],
        'lantern_hive_enabled': lantern_hive is not None,
        'ptpf_generator_enabled': ptpf_generator is not None
    })

@socketio.on('generate_ptpf_flux')
def handle_generate_ptpf_flux(data):
    """Handle PTPF+FLUX generation via WebSocket"""
    if not ptpf_generator:
        emit('ptpf_error', {'error': 'PTPF+FLUX Generator not initialized'})
        return
    
    try:
        user_input = data.get('input', '').strip()
        if not user_input:
            emit('ptpf_error', {'error': 'Input is required'})
            return
        
        # Get FLUX context if available
        flux_context = data.get('flux_context', {})
        
        # Generate PTPF+FLUX response
        result = ptpf_generator.generate_ptpf_flux(user_input, flux_context)
        
        # Emit the result
        emit('ptpf_result', result)
        
        # Log the generation
        logger.info(f"PTPF+FLUX generation completed for input: {user_input[:100]}...")
        
    except Exception as e:
        logger.error(f"PTPF+FLUX generation error: {str(e)}")
        emit('ptpf_error', {'error': str(e)})

@socketio.on('rehydrate_ptpf')
def handle_rehydrate_ptpf(data):
    """Handle PTPF rehydration via WebSocket"""
    if not ptpf_generator:
        emit('ptpf_error', {'error': 'PTPF+FLUX Generator not initialized'})
        return
    
    try:
        response_data = data.get('response_data', {})
        if not response_data:
            emit('ptpf_error', {'error': 'Response data is required for rehydration'})
            return
        
        # Rehydrate the response
        result = ptpf_generator.rehydrate_patch(response_data)
        
        # Emit the result
        emit('ptpf_rehydrated', result)
        
        logger.info("PTPF rehydration completed")
        
    except Exception as e:
        logger.error(f"PTPF rehydration error: {str(e)}")
        emit('ptpf_error', {'error': str(e)})

@socketio.on('get_ptpf_session_history')
def handle_get_ptpf_session_history():
    """Get PTPF session history"""
    if not ptpf_generator:
        emit('ptpf_error', {'error': 'PTPF+FLUX Generator not initialized'})
        return
    
    try:
        history = ptpf_generator.get_session_history()
        emit('ptpf_session_history', {'history': history})
    except Exception as e:
        logger.error(f"Error getting PTPF session history: {str(e)}")
        emit('ptpf_error', {'error': str(e)})

@socketio.on('clear_ptpf_session')
def handle_clear_ptpf_session():
    """Clear PTPF session history"""
    if not ptpf_generator:
        emit('ptpf_error', {'error': 'PTPF+FLUX Generator not initialized'})
        return
    
    try:
        ptpf_generator.clear_session()
        emit('ptpf_session_cleared', {'message': 'Session cleared successfully'})
        logger.info("PTPF session cleared")
    except Exception as e:
        logger.error(f"Error clearing PTPF session: {str(e)}")
        emit('ptpf_error', {'error': str(e)})

if __name__ == '__main__':
    # Initialize LanternHive
    initialize_lantern_hive()
    
    # Initialize PTPF+FLUX Generator
    initialize_ptpf_generator()
    
    # Initialize Strategy Engine
    initialize_strategy_engine()
    
    # Initialize Lantern Framework
    initialize_lantern_framework()
    
    # Get port from environment variable (Cloud Run requirement)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    # Run the Flask-SocketIO server
    print("Starting FLUX-LanternHive Backend Server...")
    print(f"LanternHive Status: {'Enabled' if lantern_hive else 'Disabled (no API key)'}")
    print(f"PTPF+FLUX Generator Status: {'Enabled' if ptpf_generator else 'Disabled'}")
    print(f"Strategy Engine Status: {'Enabled' if strategy_engine else 'Disabled'}")
    print(f"Lantern Framework Status: {'Enabled' if lantern_framework else 'Disabled'}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
