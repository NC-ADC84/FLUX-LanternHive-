// FLUX-LanternHive Frontend Application
// Main JavaScript file for the FLUX Programming Language IDE

class FLUXIDE {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentCode = '';
        this.systemState = {
            connections: 0,
            memoryBlocks: 0,
            fingerprints: 0,
            lanternHiveEnabled: false,
            ptpfGeneratorEnabled: false,
            lanternFrameworkEnabled: false
        };
        
        this.ptpfSessionHistory = [];
        this.currentPTPFResponse = null;
        this.strategyEngineEnabled = false;
        this.availableStrategies = [];
        
        this.init();
    }

    // Security: Sanitize HTML to prevent XSS attacks
    sanitizeHTML(str) {
        if (typeof str !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.loadExampleCode();
        this.updateSystemStatus();
        this.initializeMemoryGrid();
    }

        initializeSocket() {
            // Initialize Socket.IO connection
            // Use Google Cloud server in production, localhost in development
            const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
            const backendUrl = isProduction ? 'https://flux-lanternhive-231986304766.us-central1.run.app' : 'http://localhost:5000';
        
        console.log(`Connecting to backend: ${backendUrl}`);
        this.socket = io(backendUrl);
        
        this.socket.on('connect', () => {
            console.log('Connected to FLUX backend');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.socket.emit('get_system_state');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from FLUX backend');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('status', (data) => {
            console.log('Backend status:', data);
            this.updateLanternHiveStatus(data.lantern_hive_enabled);
        });

        this.socket.on('execution_result', (result) => {
            this.handleExecutionResult(result);
        });

        this.socket.on('execution_error', (error) => {
            this.handleExecutionError(error);
        });

        this.socket.on('lantern_response', (response) => {
            this.handleLanternResponse(response);
        });

        this.socket.on('lantern_error', (error) => {
            this.handleLanternError(error);
        });

        this.socket.on('state_update', (state) => {
            this.updateSystemState(state);
        });

        // PTPF+FLUX Generator event listeners
        this.socket.on('ptpf_result', (result) => {
            this.handlePTPFResult(result);
        });

        this.socket.on('ptpf_error', (error) => {
            this.handlePTPFError(error);
        });

        this.socket.on('ptpf_rehydrated', (result) => {
            this.handlePTPFRehydrated(result);
        });

        this.socket.on('ptpf_session_history', (data) => {
            this.ptpfSessionHistory = data.history;
            this.updatePTPFSessionHistory();
        });

        this.socket.on('ptpf_session_cleared', (data) => {
            this.ptpfSessionHistory = [];
            this.updatePTPFSessionHistory();
            this.showNotification('PTPF session cleared successfully', 'success');
        });

        this.socket.on('system_state', (state) => {
            this.updateSystemState(state);
        });
    }

    setupEventListeners() {
        // Workflow Start button
        document.getElementById('start-workflow-btn').addEventListener('click', () => {
            this.startWorkflow();
        });

        // Strategy selection
        document.querySelectorAll('.strategy-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.selectStrategy(e.currentTarget.dataset.strategy);
            });
        });

        // FLUX execution
        document.getElementById('execute-flux-btn').addEventListener('click', () => {
            this.executeGeneratedFLUX();
        });

        // Copy FLUX code
        document.getElementById('copy-flux-btn').addEventListener('click', () => {
            this.copyFLUXCode();
        });

        // Reset workflow
        document.getElementById('reset-workflow-btn').addEventListener('click', () => {
            this.resetWorkflow();
        });

        // Workflow help
        document.getElementById('workflow-help-btn').addEventListener('click', () => {
            this.showWorkflowHelp();
        });

        // Continue to LanternHive button
        document.getElementById('continue-to-lanternhive-btn').addEventListener('click', () => {
            this.continueToLanternHive();
        });

        // Interactive controls
        document.getElementById('create-connection-btn').addEventListener('click', () => {
            this.createConnection();
        });

        document.getElementById('disconnect-all-btn').addEventListener('click', () => {
            this.disconnectAll();
        });

        document.getElementById('allocate-memory-btn').addEventListener('click', () => {
            this.allocateMemory();
        });

        document.getElementById('garbage-collect-btn').addEventListener('click', () => {
            this.garbageCollect();
        });

        document.getElementById('initiate-transfer-btn').addEventListener('click', () => {
            this.initiateTransfer();
        });

        document.getElementById('generate-fingerprint-btn').addEventListener('click', () => {
            this.generateFingerprint();
        });

        // Lantern Framework event listeners
        document.getElementById('translate-agi15-btn').addEventListener('click', () => {
            this.translateAGI15();
        });

        document.getElementById('process-cluster-btn').addEventListener('click', () => {
            this.processCluster();
        });

        document.getElementById('synthesize-warden-btn').addEventListener('click', () => {
            this.synthesizeWarden();
        });

        document.getElementById('execute-brack-btn').addEventListener('click', () => {
            this.executeBrack();
        });

        document.getElementById('process-complete-btn').addEventListener('click', () => {
            this.processCompleteFramework();
        });

    }

    loadExampleCode() {
        const examples = {
            'hello-world': `connection hello_world {
    floating<string> message = "Hello, FLUX World!"
    
    on_connect {
        print(message)
    }
}`,
            'session-management': `connection user_session {
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
}`,
            'data-transfer': `connection data_pipeline {
    floating<array> source_data
    persistent<array> processed_data
    
    on_connect {
        source_data = siig_transfer("data_source")
        processed_data = transform_data(source_data)
        print("Data transfer completed")
    }
    
    on_disconnect {
        store_fingerprint(processed_data, "pipeline_result")
    }
}

siig_transfer data_source {
    endpoint: "https://api.example.com/data"
    encryption: "AES-256"
    verification: "SHA-256"
}`,
            'natural-language': `connection natural_interface {
    floating<string> user_query
    persistent<response> ai_response
    
    on_connect {
        user_query = natural("What can you help me with?")
        ai_response = process_query(user_query)
        print(ai_response.content)
    }
}

natural_interface query_processor {
    model: "gpt-4"
    context: "FLUX programming assistant"
    max_tokens: 1000
}`
        };

        // Set default example
        this.switchExample('hello-world');
    }

    switchExample(exampleName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-example="${exampleName}"]`).classList.add('active');

        // Load example code
        const examples = {
            'hello-world': `connection hello_world {
    floating<string> message = "Hello, FLUX World!"
    
    on_connect {
        print(message)
    }
}`,
            'session-management': `connection user_session {
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
}`,
            'data-transfer': `connection data_pipeline {
    floating<array> source_data
    persistent<array> processed_data
    
    on_connect {
        source_data = siig_transfer("data_source")
        processed_data = transform_data(source_data)
        print("Data transfer completed")
    }
    
    on_disconnect {
        store_fingerprint(processed_data, "pipeline_result")
    }
}

siig_transfer data_source {
    endpoint: "https://api.example.com/data"
    encryption: "AES-256"
    verification: "SHA-256"
}`,
            'natural-language': `connection natural_interface {
    floating<string> user_query
    persistent<response> ai_response
    
    on_connect {
        user_query = natural("What can you help me with?")
        ai_response = process_query(user_query)
        print(ai_response.content)
    }
}

natural_interface query_processor {
    model: "gpt-4"
    context: "FLUX programming assistant"
    max_tokens: 1000
}`
        };

        const codeInput = document.getElementById('code-input');
        codeInput.value = examples[exampleName] || '';
        this.currentCode = codeInput.value;
        this.updateLineNumbers();
    }

    // Integrated Workflow Methods
    async startWorkflow() {
        const userRequest = document.getElementById('user-request-input').value.trim();
        if (!userRequest) {
            this.addConsoleMessage('Error: Please describe what you want to do', 'error');
            return;
        }

        this.currentWorkflow = {
            request: userRequest,
            strategy: null,
            ptpfResult: null,
            lanternhiveResult: null,
            fluxCode: null
        };

        // Move to step 2: Strategy Selection
        this.completeStep('step-request');
        this.activateStep('step-strategy');
        
        this.addConsoleMessage('Workflow started. Please select an AI strategy.', 'info');
    }

    selectStrategy(strategyId) {
        // Remove previous selection
        document.querySelectorAll('.strategy-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked card
        const selectedCard = document.querySelector(`[data-strategy="${strategyId}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        // Store strategy selection
        this.currentWorkflow.strategy = strategyId;

        // Show selected strategy info
        const strategyInfo = this.getStrategyInfo(strategyId);
        document.getElementById('strategy-name').textContent = strategyInfo.name;
        document.getElementById('strategy-description').textContent = strategyInfo.description;
        document.getElementById('selected-strategy').style.display = 'block';

        // Add console message
        this.addConsoleMessage(`Strategy selected: ${strategyInfo.name}`, 'info');

        // Auto-advance to PTPF step immediately
        this.completeStep('step-strategy');
        this.activateStep('step-ptpf');
        this.generatePTPF();
    }

    getStrategyInfo(strategyId) {
        const strategies = {
            'decompose_problem': {
                name: 'Problem Decomposition',
                description: 'Breaking down complex problems into manageable, interconnected components for systematic solution development.'
            },
            'pattern_recognition': {
                name: 'Pattern Recognition',
                description: 'Identifying common patterns and applying proven architectural solutions to similar problems.'
            },
            'heuristic_search': {
                name: 'Heuristic Search',
                description: 'Using intelligent search algorithms to explore solution spaces and find optimal approaches.'
            },
            'meta_learning': {
                name: 'Meta-Learning',
                description: 'Learning from similar problems and adapting successful solutions to new contexts.'
            }
        };
        return strategies[strategyId] || strategies['decompose_problem'];
    }

    async generatePTPF() {
        // Show loading indicator
        document.getElementById('ptpf-loading').style.display = 'block';
        document.getElementById('ptpf-output').style.display = 'none';
        
        // Reset progress bars
        this.resetProgressBars();
        
        this.addConsoleMessage('Generating PTPF prompt structure...', 'info');

        try {
            // Simulate progress steps
            this.animateProgressStep('prime-context', 1000);
            
            const ptpfRequest = {
                input: this.currentWorkflow.request,
                flux_context: {
                    task: 'Generate structured prompt for FLUX code generation',
                    strategy: this.currentWorkflow.strategy
                }
            };

            const response = await fetch('/api/ptpf/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ptpfRequest)
            });

            const result = await response.json();
            
            // Complete remaining progress steps
            this.animateProgressStep('task-definition', 500);
            this.animateProgressStep('vibe-profile', 500);
            
            // Wait for progress animation to complete
            setTimeout(() => {
                // Hide loading, show output
                document.getElementById('ptpf-loading').style.display = 'none';
                document.getElementById('ptpf-output').style.display = 'block';
                
                if (result.success) {
                    this.currentWorkflow.ptpfResult = result;
                    this.displayPTPFResult(result);
                    this.addConsoleMessage('PTPF prompt structure generated successfully!', 'success');
                    
                    // Show continue button
                    document.getElementById('continue-to-lanternhive-btn').style.display = 'block';
                    
                    // Auto-advance to LanternHive step after 2 seconds
                    setTimeout(() => {
                        this.continueToLanternHive();
                    }, 2000);
                } else {
                    this.addConsoleMessage('Error: PTPF generation failed', 'error');
                    // Show fallback content
                    this.displayFallbackPTPF();
                    document.getElementById('continue-to-lanternhive-btn').style.display = 'block';
                }
            }, 1000);
            
        } catch (error) {
            // Hide loading, show output
            document.getElementById('ptpf-loading').style.display = 'none';
            document.getElementById('ptpf-output').style.display = 'block';
            
            this.addConsoleMessage(`Error: ${error.message}`, 'error');
            // Show fallback content
            this.displayFallbackPTPF();
            document.getElementById('continue-to-lanternhive-btn').style.display = 'block';
        }
    }

    resetProgressBars() {
        document.getElementById('progress-fill-prime-context').style.width = '0%';
        document.getElementById('progress-fill-task-definition').style.width = '0%';
        document.getElementById('progress-fill-vibe-profile').style.width = '0%';
    }

    animateProgressStep(stepName, duration) {
        const progressFill = document.getElementById(`progress-fill-${stepName}`);
        if (progressFill) {
            setTimeout(() => {
                progressFill.style.width = '100%';
            }, 100);
        }
    }

    resetLanternHiveProgressBars() {
        document.getElementById('progress-fill-cognitive-analysis').style.width = '0%';
        document.getElementById('progress-fill-strategy-application').style.width = '0%';
        document.getElementById('progress-fill-flux-generation').style.width = '0%';
    }

    animateLanternHiveProgressStep(stepName, duration) {
        const progressFill = document.getElementById(`progress-fill-${stepName}`);
        if (progressFill) {
            setTimeout(() => {
                progressFill.style.width = '100%';
            }, 100);
        }
    }

    displayPTPFResult(result) {
        document.getElementById('ptpf-prime-context').textContent = result.prime_context || 'Generated prime context...';
        document.getElementById('ptpf-task-definition').textContent = result.task_definition || 'Generated task definition...';
        document.getElementById('ptpf-vibe-profile').textContent = result.vibe_profile || 'Generated vibe profile...';
    }

    displayFallbackPTPF() {
        const strategy = this.currentWorkflow.strategy;
        const request = this.currentWorkflow.request;
        
        document.getElementById('ptpf-prime-context').textContent = `Prime Context: ${strategy} approach for "${request}" - focusing on systematic problem-solving and optimal solution generation.`;
        document.getElementById('ptpf-task-definition').textContent = `Task Definition: Generate FLUX code that implements ${request} using ${strategy} methodology with proper connections, memory allocation, and data flow.`;
        document.getElementById('ptpf-vibe-profile').textContent = `Vibe Profile: Professional, systematic, and solution-oriented approach with emphasis on scalability, security, and maintainability.`;
    }

    continueToLanternHive() {
        this.completeStep('step-ptpf');
        this.activateStep('step-lanternhive');
        this.runLanternHiveAnalysis();
    }

    async runLanternHiveAnalysis() {
        this.showLanternHiveThinking();
        
        // Reset LanternHive progress bars
        this.resetLanternHiveProgressBars();

        try {
            // Simulate progress steps
            this.animateLanternHiveProgressStep('cognitive-analysis', 1500);
            
            const lanternRequest = {
                prompt: this.currentWorkflow.request,
                flux_context: {
                    task: 'Generate FLUX code based on user request',
                    strategy: this.currentWorkflow.strategy,
                    ptpf_context: this.currentWorkflow.ptpfResult
                }
            };

            const response = await fetch('/api/lantern/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(lanternRequest)
            });

            const result = await response.json();
            
            // Complete remaining progress steps
            this.animateLanternHiveProgressStep('strategy-application', 1000);
            this.animateLanternHiveProgressStep('flux-generation', 1000);
            
            // Wait for progress animation to complete
            setTimeout(() => {
                if (result.final_response) {
                    this.currentWorkflow.lanternhiveResult = result;
                    this.displayLanternHiveResult(result);
                    
                    // Generate FLUX code
                    const fluxCode = this.generateFLUXFromWorkflow();
                    this.currentWorkflow.fluxCode = fluxCode;
                    
                    // Auto-advance to FLUX step
                    setTimeout(() => {
                        this.completeStep('step-lanternhive');
                        this.activateStep('step-flux');
                        this.displayFLUXCode(fluxCode);
                    }, 2000);
                } else {
                    this.hideLanternHiveThinking();
                    this.addConsoleMessage('Error: LanternHive analysis failed', 'error');
                }
            }, 1500);
            
        } catch (error) {
            this.hideLanternHiveThinking();
            this.addConsoleMessage(`Error: ${error.message}`, 'error');
        }
    }

    showLanternHiveThinking() {
        document.getElementById('lanternhive-thinking').style.display = 'block';
    }

    hideLanternHiveThinking() {
        document.getElementById('lanternhive-thinking').style.display = 'none';
    }

    displayLanternHiveResult(result) {
        this.hideLanternHiveThinking();
        document.getElementById('lanternhive-analysis').textContent = result.final_response;
        document.getElementById('lanternhive-response').style.display = 'block';
    }

    generateFLUXFromWorkflow() {
        const request = this.currentWorkflow.request.toLowerCase();
        const strategy = this.currentWorkflow.strategy;
        
        // Enhanced FLUX generation based on strategy and request
        if (strategy === 'decompose_problem') {
            return this.generateDecomposedFLUX(request);
        } else if (strategy === 'pattern_recognition') {
            return this.generatePatternBasedFLUX(request);
        } else if (strategy === 'heuristic_search') {
            return this.generateHeuristicFLUX(request);
        } else if (strategy === 'meta_learning') {
            return this.generateMetaLearningFLUX(request);
        }
        
        return this.generateGenericFLUX(request);
    }

    generateDecomposedFLUX(request) {
        return `// Problem Decomposition Strategy - Breaking down: ${this.currentWorkflow.request}
// Component 1: Core System
connect("core_system", "https://api.example.com/core")
connect("data_layer", "postgresql://localhost:5432/main_db")

// Component 2: Authentication Layer
connect("auth_service", "https://auth.example.com")
connect("session_store", "redis://localhost:6379")

// Component 3: Business Logic Layer
connect("business_logic", "https://logic.example.com")
connect("cache_layer", "redis://localhost:6380")

allocate_memory("system_buffer", 8192)
allocate_memory("auth_cache", 4096)
allocate_memory("business_cache", 4096)

create_fingerprint("system_identity", "core_system_hash")
create_fingerprint("auth_token", "authentication_hash")
create_fingerprint("business_process", "logic_hash")

initiate_siig_transfer("client", "auth_service", "login_request")
initiate_siig_transfer("auth_service", "core_system", "authenticated_request")
initiate_siig_transfer("core_system", "business_logic", "processed_request")`;
    }

    generatePatternBasedFLUX(request) {
        return `// Pattern Recognition Strategy - Applying proven patterns to: ${this.currentWorkflow.request}
// MVC Pattern Implementation
connect("model_layer", "postgresql://localhost:5432/models")
connect("view_layer", "https://views.example.com")
connect("controller_layer", "https://controllers.example.com")

// Repository Pattern
connect("user_repository", "postgresql://localhost:5432/users")
connect("product_repository", "postgresql://localhost:5432/products")
connect("order_repository", "postgresql://localhost:5432/orders")

// Service Layer Pattern
connect("user_service", "https://services.example.com/users")
connect("product_service", "https://services.example.com/products")
connect("order_service", "https://services.example.com/orders")

allocate_memory("pattern_cache", 12288)
allocate_memory("repository_cache", 6144)

create_fingerprint("mvc_pattern", "model_view_controller_hash")
create_fingerprint("repository_pattern", "data_access_hash")
create_fingerprint("service_pattern", "business_logic_hash")

initiate_siig_transfer("view_layer", "controller_layer", "user_request")
initiate_siig_transfer("controller_layer", "service_layer", "business_request")
initiate_siig_transfer("service_layer", "repository_layer", "data_request")`;
    }

    generateHeuristicFLUX(request) {
        return `// Heuristic Search Strategy - Optimizing solution for: ${this.currentWorkflow.request}
// Search Space Definition
connect("search_engine", "https://search.example.com")
connect("optimization_service", "https://optimize.example.com")
connect("evaluation_metrics", "https://metrics.example.com")

// Heuristic Functions
connect("cost_heuristic", "https://heuristics.example.com/cost")
connect("performance_heuristic", "https://heuristics.example.com/performance")
connect("scalability_heuristic", "https://heuristics.example.com/scalability")

// Solution Space
connect("solution_space", "postgresql://localhost:5432/solutions")
connect("best_solution", "postgresql://localhost:5432/optimal")

allocate_memory("search_buffer", 16384)
allocate_memory("heuristic_cache", 8192)
allocate_memory("solution_cache", 4096)

create_fingerprint("search_state", "current_search_hash")
create_fingerprint("heuristic_value", "heuristic_evaluation_hash")
create_fingerprint("optimal_solution", "best_solution_hash")

initiate_siig_transfer("search_engine", "heuristic_functions", "evaluation_request")
initiate_siig_transfer("heuristic_functions", "optimization_service", "optimization_request")
initiate_siig_transfer("optimization_service", "solution_space", "solution_storage")`;
    }

    generateMetaLearningFLUX(request) {
        return `// Meta-Learning Strategy - Learning from similar problems: ${this.currentWorkflow.request}
// Knowledge Base
connect("knowledge_base", "postgresql://localhost:5432/knowledge")
connect("experience_store", "postgresql://localhost:5432/experiences")
connect("pattern_library", "postgresql://localhost:5432/patterns")

// Learning Components
connect("similarity_engine", "https://similarity.example.com")
connect("adaptation_service", "https://adapt.example.com")
connect("learning_algorithm", "https://learn.example.com")

// Meta-Learning Process
connect("meta_controller", "https://meta.example.com")
connect("transfer_learning", "https://transfer.example.com")

allocate_memory("knowledge_cache", 20480)
allocate_memory("learning_buffer", 10240)
allocate_memory("adaptation_cache", 5120)

create_fingerprint("knowledge_graph", "learned_patterns_hash")
create_fingerprint("similarity_score", "problem_similarity_hash")
create_fingerprint("adapted_solution", "transferred_solution_hash")

initiate_siig_transfer("similarity_engine", "knowledge_base", "pattern_lookup")
initiate_siig_transfer("knowledge_base", "adaptation_service", "solution_adaptation")
initiate_siig_transfer("adaptation_service", "learning_algorithm", "meta_learning")`;
    }

    displayFLUXCode(fluxCode) {
        document.getElementById('flux-code-display').textContent = fluxCode;
        document.getElementById('flux-code-section').style.display = 'block';
        this.addConsoleMessage('FLUX code generated successfully!', 'success');
    }

    async executeGeneratedFLUX() {
        if (!this.currentWorkflow.fluxCode) {
            this.addConsoleMessage('Error: No FLUX code to execute', 'error');
            return;
        }

        this.addConsoleMessage('Executing generated FLUX code...', 'info');
        this.socket.emit('execute_flux', { code: this.currentWorkflow.fluxCode });
    }

    copyFLUXCode() {
        if (!this.currentWorkflow.fluxCode) {
            this.addConsoleMessage('Error: No FLUX code to copy', 'error');
            return;
        }

        navigator.clipboard.writeText(this.currentWorkflow.fluxCode).then(() => {
            this.addConsoleMessage('FLUX code copied to clipboard!', 'success');
        }).catch(err => {
            this.addConsoleMessage('Error copying to clipboard', 'error');
        });
    }

    resetWorkflow() {
        // Reset all steps
        document.querySelectorAll('.workflow-step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Activate first step
        this.activateStep('step-request');
        
        // Clear all content
        document.getElementById('user-request-input').value = '';
        document.getElementById('selected-strategy').style.display = 'none';
        document.getElementById('ptpf-output').style.display = 'none';
        document.getElementById('lanternhive-response').style.display = 'none';
        document.getElementById('flux-code-section').style.display = 'none';
        
        // Clear strategy selection
        document.querySelectorAll('.strategy-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset workflow state
        this.currentWorkflow = null;
        
        this.addConsoleMessage('Workflow reset. Ready for new request.', 'info');
    }

    completeStep(stepId) {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('active');
            step.classList.add('completed');
        }
    }

    activateStep(stepId) {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.add('active');
        }
    }

    showWorkflowHelp() {
        const helpSection = document.getElementById('help-section');
        if (helpSection) {
            const isVisible = helpSection.style.display !== 'none';
            helpSection.style.display = isVisible ? 'none' : 'block';
        }
    }

    handleExecutionResult(result) {
        if (result.success) {
            this.addConsoleMessage('✓ Execution completed successfully', 'success');
            
            if (result.execution_log) {
                result.execution_log.forEach(log => {
                    this.addConsoleMessage(`> ${log}`, 'info');
                });
            }
            
            if (result.created_connections) {
                this.addConsoleMessage(`Created ${result.created_connections.length} connections`, 'success');
                this.updateConnectionsVisualization(result.created_connections);
            }
        } else {
            this.addConsoleMessage(`✗ Execution failed: ${result.error}`, 'error');
        }

        if (result.errors && result.errors.length > 0) {
            result.errors.forEach(error => {
                this.addConsoleMessage(`Error: ${error}`, 'error');
            });
        }
    }

    handleExecutionError(error) {
        this.addConsoleMessage(`✗ Execution error: ${error.error}`, 'error');
    }

    handleLanternResponse(response) {
        console.log('LanternHive response:', response);
        // This would be used for the cognitive assistant panel
        // For now, we'll just log it
    }

    handleLanternError(error) {
        console.error('LanternHive error:', error);
        this.addConsoleMessage(`LanternHive error: ${error.error}`, 'error');
    }

    // PTPF+FLUX Generator handlers
    handlePTPFResult(result) {
        console.log('PTPF+FLUX result:', result);
        this.currentPTPFResponse = result;
        
        if (result.mode === 'trainer') {
            this.showPTPFTrainerQuestions(result);
        } else if (result.mode === 'generate') {
            this.showPTPFGeneratedPrompt(result.response);
        } else if (result.mode === 'drift_lock') {
            this.showPTPFDriftLock(result);
        } else if (result.mode === 'error') {
            this.showNotification(`PTPF Error: ${result.error}`, 'error');
        }
    }

    handlePTPFError(error) {
        console.error('PTPF+FLUX error:', error);
        this.showNotification(`PTPF Error: ${error.error}`, 'error');
    }

    handlePTPFRehydrated(result) {
        console.log('PTPF rehydrated:', result);
        if (result.mode === 'rehydrated') {
            this.showPTPFGeneratedPrompt(result.response);
            this.showNotification('PTPF response rehydrated successfully', 'success');
        } else if (result.mode === 'rehydration_limit') {
            this.showNotification('Maximum rehydration cycles reached', 'warning');
        }
    }

    addConsoleMessage(message, type = 'info') {
        const console = document.getElementById('console-output');
        const line = document.createElement('div');
        line.className = `console-line ${type}`;
        line.textContent = message;
        console.appendChild(line);
        console.scrollTop = console.scrollHeight;
    }

    clearConsole() {
        const console = document.getElementById('console-output');
        console.innerHTML = '<div class="console-line">FLUX Runtime Ready</div><div class="console-line">Waiting for program execution...</div>';
    }

    updateLineNumbers() {
        const textarea = document.getElementById('code-input');
        const lineNumbers = document.getElementById('line-numbers');
        const lines = textarea.value.split('\n');
        
        lineNumbers.innerHTML = lines.map((_, index) => index + 1).join('\n');
    }

    updateConnectionStatus(connected) {
        const statusElements = document.querySelectorAll('.status-value');
        // Update connection status indicators
    }

    updateLanternHiveStatus(enabled) {
        // Update LanternHive status indicators
        console.log(`LanternHive ${enabled ? 'enabled' : 'disabled'}`);
        this.systemState.lanternHiveEnabled = enabled;
        this.updateSystemStatus();
    }

    updateSystemState(state) {
        // Map backend field names to frontend field names
        this.systemState = {
            connections: state.connections ? state.connections.length : 0,
            memoryBlocks: state.memory_blocks ? state.memory_blocks.length : 0,
            fingerprints: state.fingerprints ? state.fingerprints.length : 0,
            lanternHiveEnabled: state.lantern_hive_enabled || false,
            ptpfGeneratorEnabled: state.ptpf_generator_enabled || false
        };
        this.updateSystemStatus();
        this.updatePTPFStatus(state.ptpf_generator_enabled, this.ptpfSessionHistory.length);
    }

    updateSystemStatus() {
        document.getElementById('connection-count').textContent = this.systemState.connections || 0;
        document.getElementById('memory-usage').textContent = `${this.systemState.memoryBlocks || 0}KB`;
        document.getElementById('fingerprint-count').textContent = this.systemState.fingerprints || 0;
        this.updateLanternHiveStatus();
        this.updateStrategyEngineStatus();
    }

    updateLanternHiveStatus() {
        const statusIndicator = document.getElementById('ai-status-indicator');
        const statusText = document.getElementById('ai-status-text');
        
        if (this.systemState.lanternHiveEnabled) {
            statusIndicator.style.color = '#2db2ae'; // Teal
            statusText.textContent = 'Ready for cognitive analysis';
        } else {
            statusIndicator.style.color = '#666';
            statusText.textContent = 'LanternHive disabled';
        }
    }

    updateStrategyEngineStatus() {
        // Update strategy engine status in UI
        if (this.strategyEngineEnabled) {
            console.log('Strategy Engine: Enabled');
        } else {
            console.log('Strategy Engine: Disabled');
        }
    }

    initializeMemoryGrid() {
        const memoryGrid = document.querySelector('.memory-grid');
        if (!memoryGrid) return;

        // Create 400 memory blocks (20x20 grid)
        for (let i = 0; i < 400; i++) {
            const block = document.createElement('div');
            block.className = 'memory-block';
            block.dataset.index = i;
            memoryGrid.appendChild(block);
        }
    }

    highlightSyntax() {
        // For now, we'll use a simple approach
        // In production, consider using a proper syntax highlighter like Prism.js or CodeMirror
        const textarea = document.getElementById('code-input');
        const code = textarea.value;
        
        // This is a placeholder for syntax highlighting
        // The actual highlighting would require a more sophisticated approach
        // with overlays or contentEditable divs
        console.log('Syntax highlighting for:', code.substring(0, 50) + '...');
    }

    updateConnectionsVisualization(connections) {
        const container = document.getElementById('connections-container');
        container.innerHTML = '';
        
        connections.forEach(connId => {
            const node = document.createElement('div');
            node.className = 'connection-node active';
            
            const nameDiv = document.createElement('div');
            nameDiv.className = 'connection-name';
            nameDiv.textContent = connId; // Safe: using textContent instead of innerHTML
            
            const statusDiv = document.createElement('div');
            statusDiv.className = 'connection-status';
            statusDiv.textContent = 'Active';
            
            node.appendChild(nameDiv);
            node.appendChild(statusDiv);
            container.appendChild(node);
        });
    }

    // Interactive control methods
    createConnection() {
        if (!this.isConnected) {
            this.addConsoleMessage('Error: Not connected to backend', 'error');
            return;
        }
        
        const name = prompt('Enter connection name:', 'New Connection');
        if (name) {
            const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
            const backendUrl = isProduction ? 'https://flux-lanternhive-231986304766.us-central1.run.app' : 'http://localhost:5000';
            
            fetch(`${backendUrl}/api/connections`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            })
            .then(response => response.json())
            .then(data => {
                this.addConsoleMessage(`Created connection: ${data.name}`, 'success');
                this.socket.emit('get_system_state');
            })
            .catch(error => {
                this.addConsoleMessage(`Error creating connection: ${error}`, 'error');
            });
        }
    }

    disconnectAll() {
        if (!this.isConnected) {
            this.addConsoleMessage('Error: Not connected to backend', 'error');
            return;
        }
        
        this.addConsoleMessage('Disconnecting all connections...', 'info');
        // This would need to be implemented in the backend
    }

    allocateMemory() {
        this.addConsoleMessage('Memory allocation requested', 'info');
        // This would trigger memory allocation in the backend
    }

    garbageCollect() {
        this.addConsoleMessage('Garbage collection requested', 'info');
        // This would trigger garbage collection in the backend
    }

    initiateTransfer() {
        this.addConsoleMessage('SIIG transfer initiated', 'info');
        // This would initiate a SIIG transfer
    }

    generateFingerprint() {
        this.addConsoleMessage('Generating fingerprint...', 'info');
        // This would generate a cryptographic fingerprint
    }


    // PTPF+FLUX Generator UI methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#4CAF50';
                break;
            case 'error':
                notification.style.backgroundColor = '#f44336';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ff9800';
                break;
            default:
                notification.style.backgroundColor = '#2196F3';
        }
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    showPTPFTrainerQuestions(result) {
        const modal = document.createElement('div');
        modal.className = 'ptpf-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>PTPF Trainer Questions</h3>
                <p>Your input needs more specificity. Please answer these questions:</p>
                <div class="missing-specifics">
                    <h4>Missing Specifics:</h4>
                    <ul>
                        ${result.missing_specifics.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="trainer-questions">
                    <h4>Questions:</h4>
                    <ol>
                        ${result.questions.map(q => `<li>${q}</li>`).join('')}
                    </ol>
                </div>
                <div class="examples">
                    <h4>Examples:</h4>
                    <ul>
                        ${result.examples.map(ex => `<li>${ex}</li>`).join('')}
                    </ul>
                </div>
                <button onclick="this.closest('.ptpf-modal').remove()">Close</button>
            </div>
        `;
        
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        modal.querySelector('.modal-content').style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        document.body.appendChild(modal);
    }

    showPTPFGeneratedPrompt(response) {
        const modal = document.createElement('div');
        modal.className = 'ptpf-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>PTPF+FLUX Generated Prompt</h3>
                <div class="ptpf-response">
                    <div class="response-section">
                        <h4>Role:</h4>
                        <p>${response.role}</p>
                    </div>
                    <div class="response-section">
                        <h4>Context:</h4>
                        <p>${response.context}</p>
                    </div>
                    <div class="response-section">
                        <h4>Task:</h4>
                        <p>${response.task}</p>
                    </div>
                    <div class="response-section">
                        <h4>Constraints:</h4>
                        <p>${response.constraints}</p>
                    </div>
                    <div class="response-section">
                        <h4>Success Criteria:</h4>
                        <p>${response.success_criteria}</p>
                    </div>
                    <div class="response-section">
                        <h4>Format:</h4>
                        <p>${response.format}</p>
                    </div>
                    <div class="response-section">
                        <h4>Notes:</h4>
                        <p>${response.notes}</p>
                    </div>
                    <div class="response-section">
                        <h4>Vibe:</h4>
                        <p>${response.vibe}</p>
                    </div>
                    ${response.m_sigill ? `<div class="response-section">
                        <h4>M-Sigill:</h4>
                        <p>${response.m_sigill}</p>
                    </div>` : ''}
                    <div class="response-section sigill">
                        <h4>Prime Sigill:</h4>
                        <pre>${response.sigill}</pre>
                    </div>
                </div>
                <div class="modal-actions">
                    <button onclick="this.closest('.ptpf-modal').remove()">Close</button>
                    <button onclick="window.fluxIDE.rehydratePTPF()">Rehydrate</button>
                    <button onclick="window.fluxIDE.copyPTPFResponse()">Copy to Clipboard</button>
                </div>
            </div>
        `;
        
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        modal.querySelector('.modal-content').style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        document.body.appendChild(modal);
    }

    showPTPFDriftLock(result) {
        const modal = document.createElement('div');
        modal.className = 'ptpf-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>PTPF DriftLock Activated</h3>
                <p>Your input has triggered DriftLock due to the following issues:</p>
                <ul>
                    ${result.issues.map(issue => `<li>${issue}</li>`).join('')}
                </ul>
                <p>Please refine your input and try again.</p>
                <button onclick="this.closest('.ptpf-modal').remove()">Close</button>
            </div>
        `;
        
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        modal.querySelector('.modal-content').style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 500px;
        `;
        
        document.body.appendChild(modal);
    }

    updatePTPFSessionHistory() {
        console.log('PTPF Session History updated:', this.ptpfSessionHistory);
    }

    rehydratePTPF() {
        if (this.currentPTPFResponse && this.currentPTPFResponse.response) {
            this.socket.emit('rehydrate_ptpf', {
                response_data: this.currentPTPFResponse.response
            });
        }
    }

    copyPTPFResponse() {
        if (this.currentPTPFResponse && this.currentPTPFResponse.response) {
            const response = this.currentPTPFResponse.response;
            const text = `Role: ${response.role}\nContext: ${response.context}\nTask: ${response.task}\nConstraints: ${response.constraints}\nSuccess Criteria: ${response.success_criteria}\nFormat: ${response.format}\nNotes: ${response.notes}\nVibe: ${response.vibe}\n\n${response.sigill}`;
            
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('PTPF response copied to clipboard', 'success');
            }).catch(err => {
                this.showNotification('Failed to copy to clipboard', 'error');
            });
        }
    }

    // PTPF+FLUX Generator methods
    generatePTPFFlux(input, fluxContext = {}) {
        if (!this.isConnected) {
            this.showNotification('Not connected to backend', 'error');
            return;
        }
        
        this.socket.emit('generate_ptpf_flux', {
            input: input,
            flux_context: fluxContext
        });
    }


    updatePTPFStatus(enabled, sessionCount = 0) {
        const statusElement = document.getElementById('ptpf-status');
        const sessionCountElement = document.getElementById('ptpf-session-count');
        
        if (statusElement) {
            statusElement.textContent = enabled ? 'Enabled' : 'Disabled';
            statusElement.className = `status-value ${enabled ? 'enabled' : 'disabled'}`;
        }
        
        if (sessionCountElement) {
            sessionCountElement.textContent = sessionCount.toString();
        }
    }

    // Strategy Engine Methods
    async loadStrategies() {
        try {
            const response = await fetch('/api/strategies');
            const data = await response.json();
            
            if (data.strategies) {
                this.availableStrategies = Object.values(data.strategies);
                this.strategyEngineEnabled = true;
                console.log('Loaded strategies:', this.availableStrategies);
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    }

    async executeStrategy(strategyId, problem) {
        try {
            const response = await fetch('/api/strategies/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    strategy_id: strategyId,
                    problem: problem,
                    context: {}
                })
            });
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error executing strategy:', error);
            return { success: false, error: error.message };
        }
    }

    // LanternHive Methods
    async analyzeWithLanternHive(problem) {
        if (!this.systemState.lanternHiveEnabled) {
            return { success: false, error: 'LanternHive not enabled' };
        }

        try {
            // Show thinking indicator
            this.showLanternHiveThinking();
            
            const response = await fetch('/api/lantern/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: problem,
                    flux_context: {
                        task: 'Convert natural language request to FLUX programming language code',
                        instructions: 'Generate FLUX code that implements the requested functionality. Use connect(), allocate_memory(), create_fingerprint(), and initiate_siig_transfer() operations as needed.'
                    }
                })
            });
            
            const result = await response.json();
            
            // If this is a natural language to FLUX conversion request
            if (result.final_response) {
                // Try to extract FLUX code from the analysis
                const fluxCode = this.extractFLUXCode(result.final_response);
                if (fluxCode) {
                    result.flux_code = fluxCode;
                    result.success = true;
                } else {
                    // If no FLUX code found, generate it based on the request
                    const naturalLanguageInput = document.getElementById('natural-language-input').value.trim();
                    result.flux_code = this.generateFLUXFromRequest(naturalLanguageInput);
                    result.success = true;
                }
            } else {
                result.success = false;
                result.error = 'No response from LanternHive';
            }
            
            this.showLanternHiveResponse(result);
            return result;
        } catch (error) {
            console.error('Error with LanternHive analysis:', error);
            this.hideLanternHiveThinking();
            return { success: false, error: error.message };
        }
    }

    extractFLUXCode(analysis) {
        // Look for FLUX code patterns in the analysis
        const fluxPattern = /```flux\s*([\s\S]*?)\s*```/i;
        const match = analysis.match(fluxPattern);
        
        if (match) {
            return match[1].trim();
        }
        
        // If no code blocks found, try to generate basic FLUX code based on common patterns
        const lowerAnalysis = analysis.toLowerCase();
        
        if (lowerAnalysis.includes('database') || lowerAnalysis.includes('db')) {
            return this.generateDatabaseFLUX(analysis);
        } else if (lowerAnalysis.includes('authentication') || lowerAnalysis.includes('login')) {
            return this.generateAuthFLUX(analysis);
        } else if (lowerAnalysis.includes('api') || lowerAnalysis.includes('service')) {
            return this.generateAPIFLUX(analysis);
        } else if (lowerAnalysis.includes('file') || lowerAnalysis.includes('transfer')) {
            return this.generateFileTransferFLUX(analysis);
        }
        
        // Default generic FLUX code
        return this.generateGenericFLUX(analysis);
    }

    generateDatabaseFLUX(analysis) {
        return `// Database connection and management
connect("main_database", "postgresql://localhost:5432/app_db")
connect("cache_db", "redis://localhost:6379")

allocate_memory("query_cache", 4096)
allocate_memory("session_data", 2048)

create_fingerprint("db_connection", "database_identity")
create_fingerprint("user_session", "session_data_hash")

initiate_siig_transfer("client", "main_database", "user_query")`;
    }

    generateAuthFLUX(analysis) {
        return `// User authentication system
connect("auth_database", "postgresql://localhost:5432/auth_db")
connect("session_store", "redis://localhost:6379")

allocate_memory("user_credentials", 1024)
allocate_memory("session_tokens", 2048)

create_fingerprint("user_123", "password_hash")
create_fingerprint("session_token", "token_data")

initiate_siig_transfer("login_form", "auth_database", "credentials")
initiate_siig_transfer("auth_database", "session_store", "session_data")`;
    }

    generateAPIFLUX(analysis) {
        return `// API service connections
connect("user_api", "https://api.example.com/users")
connect("payment_api", "https://api.example.com/payments")
connect("notification_api", "https://api.example.com/notifications")

allocate_memory("api_cache", 8192)
allocate_memory("request_buffer", 4096)

create_fingerprint("api_key", "service_identity")
create_fingerprint("request_id", "request_data_hash")

initiate_siig_transfer("client", "user_api", "user_request")
initiate_siig_transfer("user_api", "payment_api", "payment_data")`;
    }

    generateFileTransferFLUX(analysis) {
        return `// Secure file transfer system
connect("source_storage", "/path/to/source/files")
connect("destination_storage", "/path/to/destination")
connect("transfer_queue", "rabbitmq://localhost:5672")

allocate_memory("file_buffer", 10485760)
allocate_memory("transfer_metadata", 1024)

create_fingerprint("file_001", "file_content_hash")
create_fingerprint("transfer_session", "session_data")

initiate_siig_transfer("source_storage", "file_buffer", "file_data")
initiate_siig_transfer("file_buffer", "destination_storage", "processed_file")`;
    }

    generateGenericFLUX(analysis) {
        return `// Generated FLUX code for: ${analysis.substring(0, 50)}...
connect("primary_service", "https://api.example.com/service")
connect("data_store", "postgresql://localhost:5432/data")

allocate_memory("processing_buffer", 4096)
allocate_memory("result_cache", 2048)

create_fingerprint("operation_id", "operation_data_hash")
create_fingerprint("data_integrity", "data_hash")

initiate_siig_transfer("input_source", "primary_service", "input_data")
initiate_siig_transfer("primary_service", "data_store", "processed_data")`;
    }

    generateFLUXFromRequest(request) {
        // Generate FLUX code directly from natural language request
        const lowerRequest = request.toLowerCase();
        
        if (lowerRequest.includes('database') || lowerRequest.includes('db')) {
            return this.generateDatabaseFLUX(request);
        } else if (lowerRequest.includes('authentication') || lowerRequest.includes('login') || lowerRequest.includes('auth')) {
            return this.generateAuthFLUX(request);
        } else if (lowerRequest.includes('api') || lowerRequest.includes('service')) {
            return this.generateAPIFLUX(request);
        } else if (lowerRequest.includes('file') || lowerRequest.includes('transfer')) {
            return this.generateFileTransferFLUX(request);
        } else if (lowerRequest.includes('web') || lowerRequest.includes('website') || lowerRequest.includes('frontend')) {
            return this.generateWebFLUX(request);
        } else if (lowerRequest.includes('microservice') || lowerRequest.includes('microservices')) {
            return this.generateMicroservicesFLUX(request);
        } else if (lowerRequest.includes('security') || lowerRequest.includes('secure')) {
            return this.generateSecurityFLUX(request);
        } else if (lowerRequest.includes('data') || lowerRequest.includes('processing')) {
            return this.generateDataProcessingFLUX(request);
        }
        
        // Default generic FLUX code
        return this.generateGenericFLUX(request);
    }

    generateWebFLUX(request) {
        return `// Web application system
connect("web_server", "http://localhost:3000")
connect("api_gateway", "https://api.example.com")
connect("static_assets", "https://cdn.example.com")

allocate_memory("session_cache", 2048)
allocate_memory("request_buffer", 4096)

create_fingerprint("user_session", "session_token_hash")
create_fingerprint("api_request", "request_signature")

initiate_siig_transfer("browser", "web_server", "http_request")
initiate_siig_transfer("web_server", "api_gateway", "api_call")`;
    }

    generateMicroservicesFLUX(request) {
        return `// Microservices architecture
connect("user_service", "http://user-service:8080")
connect("order_service", "http://order-service:8081")
connect("payment_service", "http://payment-service:8082")
connect("notification_service", "http://notification-service:8083")

allocate_memory("service_registry", 4096)
allocate_memory("message_queue", 8192)

create_fingerprint("service_discovery", "service_identity")
create_fingerprint("inter_service_call", "call_signature")

initiate_siig_transfer("user_service", "order_service", "order_request")
initiate_siig_transfer("order_service", "payment_service", "payment_data")`;
    }

    generateSecurityFLUX(request) {
        return `// Security and encryption system
connect("vault_service", "https://vault.example.com")
connect("certificate_store", "https://certs.example.com")
connect("audit_log", "https://audit.example.com")

allocate_memory("encryption_keys", 1024)
allocate_memory("security_tokens", 2048)

create_fingerprint("encryption_key", "key_fingerprint")
create_fingerprint("security_token", "token_hash")

initiate_siig_transfer("client", "vault_service", "key_request")
initiate_siig_transfer("vault_service", "audit_log", "access_log")`;
    }

    generateDataProcessingFLUX(request) {
        return `// Data processing pipeline
connect("data_source", "postgresql://source:5432/data")
connect("processing_engine", "spark://cluster:7077")
connect("data_warehouse", "postgresql://warehouse:5432/analytics")

allocate_memory("data_buffer", 10485760)
allocate_memory("processing_cache", 5242880)

create_fingerprint("data_batch", "batch_hash")
create_fingerprint("processing_job", "job_signature")

initiate_siig_transfer("data_source", "processing_engine", "raw_data")
initiate_siig_transfer("processing_engine", "data_warehouse", "processed_data")`;
    }

    showLanternHiveThinking() {
        const thinking = document.getElementById('ai-thinking');
        const response = document.getElementById('ai-response');
        
        if (thinking) thinking.style.display = 'block';
        if (response) response.style.display = 'none';
    }

    hideLanternHiveThinking() {
        const thinking = document.getElementById('ai-thinking');
        if (thinking) thinking.style.display = 'none';
    }

    showLanternHiveResponse(result) {
        const thinking = document.getElementById('ai-thinking');
        const response = document.getElementById('ai-response');
        const content = document.getElementById('response-content');
        
        this.hideLanternHiveThinking();
        
        if (response && content) {
            if (result.success) {
                const successDiv = document.createElement('div');
                successDiv.className = 'response-success';
                successDiv.textContent = result.analysis || result.message;
                content.innerHTML = '';
                content.appendChild(successDiv);
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'response-error';
                errorDiv.textContent = `Error: ${result.error}`;
                content.innerHTML = '';
                content.appendChild(errorDiv);
            }
            response.style.display = 'block';
        }
    }



    // PTPF Methods - Duplicate method removed (using the main generatePTPF method above)

    showPTPFOutput(result) {
        const output = document.getElementById('ptpf-output');
        const content = document.getElementById('ptpf-output-content');

        if (output && content) {
            if (result.success) {
                const successDiv = document.createElement('div');
                successDiv.className = 'output-success';
                successDiv.textContent = result.generated_prompt || result.message;
                content.innerHTML = '';
                content.appendChild(successDiv);
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'output-error';
                errorDiv.textContent = `Error: ${result.error}`;
                content.innerHTML = '';
                content.appendChild(errorDiv);
            }
            output.style.display = 'block';
        }
    }

    clearPTPFOutput() {
        const output = document.getElementById('ptpf-output');
        if (output) {
            output.style.display = 'none';
        }
    }

    // Strategy Methods
    async executeStrategyFromUI(strategyId, problem) {
        try {
            const result = await this.executeStrategy(strategyId, problem);
            this.showStrategyOutput(result);
        } catch (error) {
            console.error('Error executing strategy:', error);
            this.showStrategyOutput({ success: false, error: error.message });
        }
    }

    showStrategyOutput(result) {
        const output = document.getElementById('strategy-output');
        const content = document.getElementById('strategy-output-content');

        if (output && content) {
            if (result.success) {
                const successDiv = document.createElement('div');
                successDiv.className = 'output-success';
                successDiv.textContent = result.solution || result.message;
                content.innerHTML = '';
                content.appendChild(successDiv);
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'output-error';
                errorDiv.textContent = `Error: ${result.error}`;
                content.innerHTML = '';
                content.appendChild(errorDiv);
            }
            output.style.display = 'block';
        }
    }

    uploadStrategyFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/strategies/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert(`Strategy '${result.strategy_id}' loaded successfully!`);
                        this.loadStrategies(); // Reload strategies
                    } else {
                        alert(`Error: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Error uploading strategy:', error);
                    alert(`Error uploading strategy: ${error.message}`);
                }
            }
        };
        input.click();
    }

    // Control Event Listeners
    addControlEventListeners() {
        // Connection Controls
        const createConnectionBtn = document.getElementById('create-connection-btn');
        const disconnectAllBtn = document.getElementById('disconnect-all-btn');

        if (createConnectionBtn) {
            createConnectionBtn.addEventListener('click', () => {
                this.createConnection();
            });
        }

        if (disconnectAllBtn) {
            disconnectAllBtn.addEventListener('click', () => {
                this.disconnectAllConnections();
            });
        }

        // Memory Controls
        const allocateMemoryBtn = document.getElementById('allocate-memory-btn');
        const garbageCollectBtn = document.getElementById('garbage-collect-btn');

        if (allocateMemoryBtn) {
            allocateMemoryBtn.addEventListener('click', () => {
                this.allocateFloatingMemory();
            });
        }

        if (garbageCollectBtn) {
            garbageCollectBtn.addEventListener('click', () => {
                this.garbageCollect();
            });
        }

        // Transfer Controls
        const initiateTransferBtn = document.getElementById('initiate-transfer-btn');
        const generateFingerprintBtn = document.getElementById('generate-fingerprint-btn');

        if (initiateTransferBtn) {
            initiateTransferBtn.addEventListener('click', () => {
                this.initiateSIIGTransfer();
            });
        }

        if (generateFingerprintBtn) {
            generateFingerprintBtn.addEventListener('click', () => {
                this.generateFingerprint();
            });
        }

        // Natural Language
    }

    // Control Methods
    createConnection() {
        const connectionId = this.generateId('conn_');
        this.socket.emit('create_connection', { connection_id: connectionId });
        this.addConsoleMessage(`Creating connection: ${connectionId}`);
    }

    disconnectAllConnections() {
        this.socket.emit('disconnect_all_connections');
        this.addConsoleMessage('Disconnecting all connections');
    }

    allocateFloatingMemory() {
        const memoryId = this.generateId('mem_');
        this.socket.emit('allocate_memory', { 
            memory_id: memoryId, 
            data_type: 'string', 
            content: 'Sample floating memory allocation' 
        });
        this.addConsoleMessage(`Allocating floating memory: ${memoryId}`);
    }

    garbageCollect() {
        this.socket.emit('garbage_collect');
        this.addConsoleMessage('Running garbage collection');
    }

    initiateSIIGTransfer() {
        const transferId = this.generateId('transfer_');
        this.socket.emit('initiate_siig_transfer', { 
            transfer_id: transferId, 
            source: 'memory', 
            destination: 'fingerprint' 
        });
        this.addConsoleMessage(`Initiating SIIG transfer: ${transferId}`);
    }

    generateFingerprint() {
        const fingerprintId = this.generateId('fp_');
        this.socket.emit('generate_fingerprint', { 
            fingerprint_id: fingerprintId, 
            data: 'Sample data for fingerprinting' 
        });
        this.addConsoleMessage(`Generating fingerprint: ${fingerprintId}`);
    }

    processNaturalLanguageCommand(command) {
        this.addConsoleMessage(`Processing natural language: ${command}`);
        
        // Send to LanternHive for processing
        this.analyzeWithLanternHive(command);
        
        // Clear the input
        const naturalLanguageInput = document.getElementById('natural-language-input');
        if (naturalLanguageInput) {
            naturalLanguageInput.value = '';
        }
    }

    generateId(prefix) {
        return prefix + Math.random().toString(36).substr(2, 9);
    }

    addConsoleMessage(message) {
        const consoleOutput = document.getElementById('console-output');
        if (consoleOutput) {
            const timestamp = new Date().toLocaleTimeString();
            const messageElement = document.createElement('div');
            messageElement.className = 'console-line';
            messageElement.textContent = `[${timestamp}] ${message}`;
            consoleOutput.appendChild(messageElement);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    }

    // Lantern Framework Methods
    async translateAGI15() {
        const input = document.getElementById('agi15-input').value.trim();
        if (!input) {
            this.showNotification('Please enter text to translate', 'error');
            return;
        }

        try {
            const response = await fetch('/api/lantern/agi15/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: input })
            });

            const result = await response.json();
            
            if (response.ok) {
                const resultDiv = document.getElementById('agi15-result');
                resultDiv.innerHTML = `
                    <strong>Original:</strong> ${this.sanitizeHTML(result.original)}<br><br>
                    <strong>AGI15 Translation:</strong><br>
                    ${this.sanitizeHTML(result.translation)}<br><br>
                    <strong>Domain Context:</strong><br>
                    ${Object.entries(result.domain_context).map(([domain, words]) => 
                        `<strong>${domain}:</strong> ${words.join(', ')}`
                    ).join('<br>')}
                `;
                resultDiv.classList.add('show');
                this.showNotification('AGI15 translation completed', 'success');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('AGI15 translation error:', error);
            this.showNotification('Failed to translate text', 'error');
        }
    }

    async processCluster() {
        const input = document.getElementById('cluster-input').value.trim();
        if (!input) {
            this.showNotification('Please enter text for cluster processing', 'error');
            return;
        }

        try {
            const response = await fetch('/api/lantern/cluster/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: input })
            });

            const result = await response.json();
            
            if (response.ok) {
                const resultDiv = document.getElementById('cluster-result');
                resultDiv.innerHTML = `
                    <strong>Input:</strong> ${this.sanitizeHTML(result.input)}<br><br>
                    <strong>Threads Created:</strong> ${result.threads_created}<br><br>
                    <strong>Cluster Output:</strong><br>
                    <pre>${this.sanitizeHTML(result.cluster_output)}</pre>
                `;
                resultDiv.classList.add('show');
                this.showNotification('Cluster processing completed', 'success');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Cluster processing error:', error);
            this.showNotification('Failed to process cluster', 'error');
        }
    }

    async synthesizeWarden() {
        const input = document.getElementById('warden-input').value.trim();
        if (!input) {
            this.showNotification('Please enter text for Warden synthesis', 'error');
            return;
        }

        try {
            const response = await fetch('/api/lantern/warden/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: input })
            });

            const result = await response.json();
            
            if (response.ok) {
                const resultDiv = document.getElementById('warden-result');
                resultDiv.innerHTML = `
                    <strong>Input:</strong> ${this.sanitizeHTML(result.input)}<br><br>
                    <strong>Lantern Responses:</strong><br>
                    ${result.lantern_responses.map(response => 
                        `<div style="margin: 10px 0; padding: 10px; background: rgba(45, 166, 178, 0.1); border-radius: 5px;">
                            ${this.sanitizeHTML(response)}
                        </div>`
                    ).join('')}<br>
                    <strong>Reality Frame:</strong><br>
                    <pre>${this.sanitizeHTML(result.reality_frame)}</pre>
                `;
                resultDiv.classList.add('show');
                this.showNotification('Warden synthesis completed', 'success');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Warden synthesis error:', error);
            this.showNotification('Failed to synthesize Warden', 'error');
        }
    }

    async executeBrack() {
        const input = document.getElementById('brack-input').value.trim();
        if (!input) {
            this.showNotification('Please enter Brack code to execute', 'error');
            return;
        }

        try {
            const response = await fetch('/api/lantern/brack/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: input })
            });

            const result = await response.json();
            
            if (response.ok) {
                const resultDiv = document.getElementById('brack-result');
                resultDiv.innerHTML = `
                    <strong>Input Code:</strong><br>
                    <pre>${this.sanitizeHTML(result.input_code)}</pre><br>
                    <strong>Execution Result:</strong><br>
                    <pre>${this.sanitizeHTML(result.execution_result)}</pre><br>
                    <strong>Variable Bindings:</strong><br>
                    <pre>${JSON.stringify(result.variable_bindings, null, 2)}</pre>
                `;
                resultDiv.classList.add('show');
                this.showNotification('Brack execution completed', 'success');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Brack execution error:', error);
            this.showNotification('Failed to execute Brack code', 'error');
        }
    }

    async processCompleteFramework() {
        const input = document.getElementById('complete-input').value.trim();
        if (!input) {
            this.showNotification('Please enter text for complete framework processing', 'error');
            return;
        }

        try {
            const response = await fetch('/api/lantern/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: input })
            });

            const result = await response.json();
            
            if (response.ok) {
                const resultDiv = document.getElementById('complete-result');
                resultDiv.innerHTML = `
                    <strong>Original Input:</strong> ${this.sanitizeHTML(result.original_input)}<br><br>
                    <strong>Final Output:</strong><br>
                    <pre>${this.sanitizeHTML(result.final_output)}</pre><br>
                    <strong>AGI15 Translation:</strong><br>
                    ${result.agi15_translation ? this.sanitizeHTML(result.agi15_translation) : 'N/A'}<br><br>
                    <strong>Domain Context:</strong><br>
                    ${result.domain_context ? Object.entries(result.domain_context).map(([domain, words]) => 
                        `<strong>${domain}:</strong> ${words.join(', ')}`
                    ).join('<br>') : 'N/A'}
                `;
                resultDiv.classList.add('show');
                this.showNotification('Complete framework processing completed', 'success');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Complete framework processing error:', error);
            this.showNotification('Failed to process complete framework', 'error');
        }
    }
}

// Initialize the application when the DOM is loaded

document.addEventListener('DOMContentLoaded', () => {
    window.fluxIDE = new FLUXIDE();
    
        // Load strategies on startup
        setTimeout(() => {
            window.fluxIDE.loadStrategies();
        }, 1000);

        // Add event listeners for new panels
        window.fluxIDE.addControlEventListeners();
});


// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FLUXIDE;
}

