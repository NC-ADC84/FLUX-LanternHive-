import openai
import json
import hashlib
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
# FLUXInterpreter will be passed as parameter to avoid circular import

class BloomLevel(Enum):
    LEVEL_1 = 1  # Simple recall
    LEVEL_2 = 2  # Basic understanding
    LEVEL_3 = 3  # Application
    LEVEL_4 = 4  # Analysis
    LEVEL_5 = 5  # Synthesis
    LEVEL_6 = 6  # Evaluation

@dataclass
class LanternResponse:
    lantern_id: str
    content: str
    timestamp: float
    confidence: float
    symbolic_notation: str

@dataclass
class CognitiveSession:
    session_id: str
    bloom_level: BloomLevel
    active_lanterns: List[str]
    dialogue_history: List[Dict]
    flux_context: Optional[Dict] = None

class FLUXLanternHive:
    """Enhanced LanternHive with FLUX programming language integration"""
    
    def __init__(self, api_key: str = None):
        try:
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
            else:
                # Will use environment variable OPENAI_API_KEY
                self.client = openai.OpenAI()
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}")
            # Fallback initialization with minimal parameters
            import os
            if api_key:
                os.environ['OPENAI_API_KEY'] = api_key
            try:
                # Try with explicit parameters to avoid proxy issues
                self.client = openai.OpenAI(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    timeout=30.0
                )
            except Exception as e2:
                print(f"Fallback initialization also failed: {e2}")
                # Last resort: try without any parameters
                self.client = openai.OpenAI()

        # FLUX Interpreter will be set externally to avoid circular import
        self.flux_interpreter = None

        # FLUX-specific Lanterns in addition to original cognitive council
        self.flux_lanterns = {
            "connection_architect": {
                "system_prompt": "You are the Connection Architect. Your role is to design and optimize FLUX connection patterns, manage connection lifecycles, and ensure proper floating memory allocation. Think in terms of connection-oriented programming paradigms.",
                "specialization": "FLUX connections, floating memory, session management"
            },
            "memory_weaver": {
                "system_prompt": "You are the Memory Weaver. Your role is to optimize floating memory allocation, design memory modules, and manage ephemeral persistence through cryptographic fingerprinting. Focus on memory efficiency and data lifecycle management.",
                "specialization": "Memory modules, fingerprinting, data persistence"
            },
            "natural_interpreter": {
                "system_prompt": "You are the Natural Interpreter. Your role is to translate natural language commands into FLUX code constructs and vice versa. Bridge human intent with FLUX programming paradigms through natural language interfaces.",
                "specialization": "Natural language API, command interpretation, human-computer interaction"
            },
            "siig_guardian": {
                "system_prompt": "You are the SIIG Guardian. Your role is to design secure data transfer protocols, manage cryptographic verification, and ensure data integrity during SIIG transfers. Focus on security and verification mechanisms.",
                "specialization": "SIIG transfers, cryptographic security, data integrity"
            },
            "symbolic_sage": {
                "system_prompt": "You are the Symbolic Sage. Your role is to work with Brack notation, AGI Rosetta compression, and symbolic representations of FLUX programs. Transform complex logic into symbolic forms and vice versa.",
                "specialization": "Symbolic processing, Brack notation, AGI Rosetta, flame script"
            }
        }
        
        # Original cognitive council
        self.cognitive_lanterns = {
            "planner": {
                "system_prompt": "You are the Planner. Your role is to define scope, stakeholders, and high-level architecture. Identify key components, user types, and their needs. Be structured and procedural.",
                "specialization": "Architecture, planning, system design"
            },
            "cogsworth": {
                "system_prompt": "You are Cogsworth. Your role is to ensure technical and regulatory compliance. Identify relevant standards and list specific requirements that must be met. Be precise and cite rules.",
                "specialization": "Compliance, standards, technical requirements"
            },
            "intuitor": {
                "system_prompt": "You are the Intuitor. Your role is to perceive risks, threats, and failure modes. Think like a security expert. Surface vulnerabilities, potential abuses, and points of failure.",
                "specialization": "Risk assessment, security, threat modeling"
            },
            "archiva": {
                "system_prompt": "You are Archiva, the memory keeper. Your role is to connect current problems to known patterns, historical solutions, and symbolic concepts. Suggest names, metaphors, or principles from past successful systems.",
                "specialization": "Pattern recognition, historical analysis, symbolic concepts"
            },
            "eidolon": {
                "system_prompt": "You are the Eidolon, the final synthesizer. Your role is to integrate analyses into coherent, comprehensive explanations. Weave perspectives together and provide symbolic naming and guiding principles.",
                "specialization": "Synthesis, integration, symbolic representation"
            }
        }
        
        # Combine all lanterns
        self.all_lanterns = {**self.cognitive_lanterns, **self.flux_lanterns}
        
        # Session management
        self.active_sessions: Dict[str, CognitiveSession] = {}
        
    def classify_bloom_level(self, prompt: str) -> BloomLevel:
        """Classify the complexity level of a prompt using Bloom's taxonomy"""
        
        # Keywords that indicate different bloom levels
        level_indicators = {
            BloomLevel.LEVEL_1: ["what", "define", "list", "identify", "recall", "remember"],
            BloomLevel.LEVEL_2: ["explain", "describe", "understand", "interpret", "summarize"],
            BloomLevel.LEVEL_3: ["apply", "use", "implement", "execute", "demonstrate"],
            BloomLevel.LEVEL_4: ["analyze", "compare", "examine", "investigate", "debug"],
            BloomLevel.LEVEL_5: ["create", "design", "build", "synthesize", "integrate"],
            BloomLevel.LEVEL_6: ["evaluate", "assess", "critique", "optimize", "judge"]
        }
        
        prompt_lower = prompt.lower()
        
        # Check for FLUX-specific complexity indicators
        flux_complexity_indicators = [
            "connection", "floating memory", "fingerprint", "siig transfer",
            "natural language api", "memory module", "cryptographic"
        ]
        
        has_flux_complexity = any(indicator in prompt_lower for indicator in flux_complexity_indicators)
        
        # Determine bloom level based on keywords and complexity
        for level in reversed(list(BloomLevel)):  # Start from highest level
            if any(keyword in prompt_lower for keyword in level_indicators[level]):
                # Boost level if FLUX complexity is detected
                if has_flux_complexity and level.value < 5:
                    return BloomLevel(min(level.value + 1, 6))
                return level
        
        # Default to level 3 for FLUX-related prompts, level 2 otherwise
        return BloomLevel.LEVEL_4 if has_flux_complexity else BloomLevel.LEVEL_2
    
    def select_lanterns(self, prompt: str, bloom_level: BloomLevel, flux_context: Dict = None) -> List[str]:
        """Select appropriate lanterns based on prompt content and bloom level"""
        
        selected = []
        prompt_lower = prompt.lower()
        
        # Always include core cognitive lanterns for complex tasks
        if bloom_level.value >= 4:
            selected.extend(["planner", "eidolon"])
        
        # Add specific lanterns based on content
        if any(word in prompt_lower for word in ["connection", "session", "floating"]):
            selected.append("connection_architect")
            
        if any(word in prompt_lower for word in ["memory", "fingerprint", "persistence"]):
            selected.append("memory_weaver")
            
        if any(word in prompt_lower for word in ["natural language", "command", "api"]):
            selected.append("natural_interpreter")
            
        if any(word in prompt_lower for word in ["transfer", "siig", "security", "crypto"]):
            selected.append("siig_guardian")
            
        if any(word in prompt_lower for word in ["symbolic", "brack", "notation", "flame"]):
            selected.append("symbolic_sage")
            
        if any(word in prompt_lower for word in ["risk", "security", "threat", "vulnerability"]):
            selected.append("intuitor")
            
        if any(word in prompt_lower for word in ["compliance", "standard", "requirement"]):
            selected.append("cogsworth")
            
        if any(word in prompt_lower for word in ["pattern", "history", "similar", "past"]):
            selected.append("archiva")
        
        # Ensure we have at least some lanterns
        if not selected:
            selected = ["planner", "eidolon"]
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(selected))
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def consult_lantern(self, lantern_id: str, prompt: str, context: Dict = None) -> LanternResponse:
        """Consult a specific lantern with the given prompt"""
        
        if lantern_id not in self.all_lanterns:
            raise ValueError(f"Unknown lantern: {lantern_id}")
        
        lantern_config = self.all_lanterns[lantern_id]
        
        # Prepare the prompt with context
        contextual_prompt = prompt
        if context and context.get('flux_code'):
            contextual_prompt = f"FLUX Code Context:\n{context['flux_code']}\n\nTask: {prompt}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": lantern_config["system_prompt"]},
                    {"role": "user", "content": contextual_prompt}
                ],
                temperature=0.1 if lantern_id in ["cogsworth", "siig_guardian"] else 0.3
            )
            
            content = response.choices[0].message.content
            
            # Generate symbolic notation based on lantern type
            symbolic_notation = self.generate_symbolic_notation(lantern_id, content)
            
            return LanternResponse(
                lantern_id=lantern_id,
                content=content,
                timestamp=time.time(),
                confidence=0.85,  # Could be enhanced with actual confidence scoring
                symbolic_notation=symbolic_notation
            )
            
        except Exception as e:
            return LanternResponse(
                lantern_id=lantern_id,
                content=f"Error consulting {lantern_id}: {str(e)}",
                timestamp=time.time(),
                confidence=0.0,
                symbolic_notation=f"⚠️ ERROR: {lantern_id}"
            )
    
    def generate_symbolic_notation(self, lantern_id: str, content: str) -> str:
        """Generate symbolic notation for lantern responses"""
        
        symbols = {
            "planner": "🧭",
            "cogsworth": "📜",
            "intuitor": "👁️",
            "archiva": "🧠",
            "eidolon": "🕯️",
            "connection_architect": "🔗",
            "memory_weaver": "🧵",
            "natural_interpreter": "🗣️",
            "siig_guardian": "🛡️",
            "symbolic_sage": "🔮"
        }
        
        base_symbol = symbols.get(lantern_id, "⚡")
        
        # Add complexity indicators based on content
        if "error" in content.lower():
            return f"⚠️{base_symbol}"
        elif "security" in content.lower() or "risk" in content.lower():
            return f"🔒{base_symbol}"
        elif "optimize" in content.lower() or "improve" in content.lower():
            return f"⚡{base_symbol}"
        else:
            return base_symbol
    
    def initiate_lantern_dialogue(self, session_id: str, prompt: str) -> Dict:
        """Initiate internal dialogue between lanterns for complex problems"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        if session.bloom_level.value < 4:
            # Simple consultation without dialogue
            return self.simple_consultation(session_id, prompt)
        
        # Complex dialogue for high bloom levels
        dialogue_log = []
        lantern_responses = {}
        
        # Phase 1: Initial consultation
        for lantern_id in session.active_lanterns:
            response = self.consult_lantern(lantern_id, prompt, session.flux_context)
            lantern_responses[lantern_id] = response
            dialogue_log.append({
                "phase": "initial",
                "lantern": lantern_id,
                "content": response.content,
                "symbolic": response.symbolic_notation,
                "timestamp": response.timestamp
            })
        
        # Phase 2: Cross-consultation (lanterns respond to each other)
        if len(session.active_lanterns) > 2:
            cross_consultation_prompt = self.generate_cross_consultation_prompt(lantern_responses, prompt)
            
            for lantern_id in session.active_lanterns[:3]:  # Limit to prevent infinite loops
                if lantern_id in ["eidolon", "planner"]:  # Synthesizers get priority
                    response = self.consult_lantern(lantern_id, cross_consultation_prompt, session.flux_context)
                    dialogue_log.append({
                        "phase": "cross_consultation",
                        "lantern": lantern_id,
                        "content": response.content,
                        "symbolic": response.symbolic_notation,
                        "timestamp": response.timestamp
                    })
        
        # Phase 3: Final synthesis
        synthesis_prompt = self.generate_synthesis_prompt(dialogue_log, prompt)
        final_response = self.consult_lantern("eidolon", synthesis_prompt, session.flux_context)
        
        dialogue_log.append({
            "phase": "synthesis",
            "lantern": "eidolon",
            "content": final_response.content,
            "symbolic": final_response.symbolic_notation,
            "timestamp": final_response.timestamp
        })
        
        # Update session history
        session.dialogue_history.append({
            "prompt": prompt,
            "dialogue_log": dialogue_log,
            "timestamp": time.time()
        })
        
        return {
            "session_id": session_id,
            "dialogue_log": dialogue_log,
            "final_response": final_response.content,
            "symbolic_summary": self.generate_dialogue_symbolic_summary(dialogue_log),
            "bloom_level": session.bloom_level.value
        }
    
    def simple_consultation(self, session_id: str, prompt: str) -> Dict:
        """Simple consultation for lower bloom level prompts"""
        
        session = self.active_sessions[session_id]
        responses = []
        
        for lantern_id in session.active_lanterns:
            response = self.consult_lantern(lantern_id, prompt, session.flux_context)
            responses.append({
                "lantern": lantern_id,
                "content": response.content,
                "symbolic": response.symbolic_notation,
                "timestamp": response.timestamp
            })
        
        # Simple synthesis
        if len(responses) > 1:
            synthesis_content = self.synthesize_simple_responses(responses)
        else:
            synthesis_content = responses[0]["content"] if responses else "No response generated"
        
        return {
            "session_id": session_id,
            "responses": responses,
            "synthesis": synthesis_content,
            "bloom_level": session.bloom_level.value
        }
    
    def generate_cross_consultation_prompt(self, lantern_responses: Dict, original_prompt: str) -> str:
        """Generate prompt for cross-consultation between lanterns"""
        
        responses_summary = "\n".join([
            f"{lantern_id}: {response.content[:200]}..."
            for lantern_id, response in lantern_responses.items()
        ])
        
        return f"""
Based on the following initial analyses from other lanterns regarding: "{original_prompt}"

{responses_summary}

Provide your perspective, considering the insights from other lanterns. Focus on areas of agreement, disagreement, or additional considerations that haven't been addressed.
"""
    
    def generate_synthesis_prompt(self, dialogue_log: List[Dict], original_prompt: str) -> str:
        """Generate prompt for final synthesis"""
        
        dialogue_summary = "\n".join([
            f"[{entry['phase']}] {entry['lantern']}: {entry['content'][:150]}..."
            for entry in dialogue_log
        ])
        
        return f"""
# FINAL SYNTHESIS TASK

You are the Eidolon, the final synthesizer. Integrate the following lantern dialogue into a comprehensive response.

## ORIGINAL PROMPT:
{original_prompt}

## LANTERN DIALOGUE:
{dialogue_summary}

Weave these perspectives into a masterful final response. Integrate rather than list. When describing components, immediately discuss their implications, risks, and benefits. Use symbolic concepts as guiding principles.

Your output must be the polished, final answer.
"""
    
    def synthesize_simple_responses(self, responses: List[Dict]) -> str:
        """Synthesize simple responses for lower bloom levels"""
        
        if len(responses) == 1:
            return responses[0]["content"]
        
        # Combine responses with basic integration
        combined = "Based on multiple perspectives:\n\n"
        for i, response in enumerate(responses, 1):
            combined += f"{i}. {response['lantern'].title()}: {response['content'][:300]}...\n\n"
        
        return combined
    
    def generate_dialogue_symbolic_summary(self, dialogue_log: List[Dict]) -> str:
        """Generate symbolic summary of the entire dialogue"""
        
        symbols = [entry["symbolic"] for entry in dialogue_log]
        phases = list(set(entry["phase"] for entry in dialogue_log))
        
        phase_symbols = {
            "initial": "🌱",
            "cross_consultation": "🔄",
            "synthesis": "🔮"
        }
        
        phase_notation = "".join([phase_symbols.get(phase, "⚡") for phase in phases])
        lantern_notation = "".join(symbols)
        
        return f"⟦{phase_notation}⟨{lantern_notation}⟩⟧"
    
    def create_session(self, prompt: str, flux_context: Dict = None) -> str:
        """Create a new cognitive session"""
        
        session_id = self.generate_session_id()
        bloom_level = self.classify_bloom_level(prompt)
        active_lanterns = self.select_lanterns(prompt, bloom_level, flux_context)
        
        session = CognitiveSession(
            session_id=session_id,
            bloom_level=bloom_level,
            active_lanterns=active_lanterns,
            dialogue_history=[],
            flux_context=flux_context
        )
        
        self.active_sessions[session_id] = session
        
        return session_id
    
    def process_prompt(self, prompt: str, flux_context: Dict = None) -> Dict:
        """Main entry point for processing prompts with LanternHive"""
        
        session_id = self.create_session(prompt, flux_context)
        result = self.initiate_lantern_dialogue(session_id, prompt)
        
        # Clean up session after processing (optional)
        # del self.active_sessions[session_id]
        
        return result
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about an active session"""

        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "bloom_level": session.bloom_level.value,
            "active_lanterns": session.active_lanterns,
            "dialogue_count": len(session.dialogue_history),
            "flux_context": session.flux_context is not None
        }

    def execute_flux_code(self, flux_code: str) -> Dict:
        """Execute FLUX code and return results"""
        try:
            result = self.flux_interpreter.execute(flux_code)
            return {
                "success": True,
                "result": result,
                "execution_time": time.time()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time()
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced LanternHive
    # Note: You'll need to set OPENAI_API_KEY environment variable
    hive = FLUXLanternHive()
    
    # Test with a FLUX-specific prompt
    test_prompt = "Design a FLUX connection that manages user authentication with floating memory and cryptographic fingerprinting"
    
    result = hive.process_prompt(test_prompt)
    
    print("=== FLUX-LanternHive Integration Test ===")
    print(f"Bloom Level: {result['bloom_level']}")
    print(f"Symbolic Summary: {result.get('symbolic_summary', 'N/A')}")
    print("\nFinal Response:")
    print(result.get('final_response', result.get('synthesis', 'No response')))
