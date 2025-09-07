"""
PTPF+FLUX Generator Module
Integrates PrimeTalk Vibe-Context Coding Generator (PTPF) with FLUX programming language
Based on PTPF 6.4 engine with 6.5 patch enhancements
"""

import json
import hashlib
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PTPFMode(Enum):
    GENERATE = "generate"
    TRAINER = "trainer"
    REHYDRATE = "rehydrate"

@dataclass
class PTPFConfig:
    """PTPF Configuration from v6.4 engine"""
    forbidden_vocab: List[str]
    hedging_patterns: List[str]
    whitelist_quantifiers: Dict[str, Any]
    hedging_mode: str = "field-aware"
    lang_default: str = "en"
    drift_guard_max_style_tolerance: float = 0.20
    reinvoke_max: int = 2
    output_contract: str = "STABLE_PROMPT_RESPONSE"

@dataclass
class PTPFVibe:
    """PTPF Vibe configuration"""
    tone: str = "direct"
    pacing: str = "medium"
    register: str = "professional"
    brevity: str = "tight"
    rules: List[str] = None
    
    def __post_init__(self):
        if self.rules is None:
            self.rules = [
                "front-load outcome",
                "one idea per paragraph",
                "explicit deliverables",
                "explicit constraints",
                "explicit success criteria",
                "single CTA only if explicit in user input"
            ]

@dataclass
class PTPFInput:
    """PTPF Input model"""
    goal: str
    context: str = ""
    constraints: str = ""
    audience: str = ""
    tone: str = ""
    format: str = ""
    language: str = "en"

@dataclass
class PTPFResponse:
    """PTPF Response structure"""
    role: str
    context: str
    task: str
    constraints: str
    success_criteria: str
    format: str
    notes: str
    vibe: str
    sigill: str
    m_sigill: Optional[str] = None
    trainer_questions: Optional[List[str]] = None

class PTPFFluxGenerator:
    """PTPF+FLUX Generator implementing v6.4 engine with v6.5 patch"""
    
    def __init__(self):
        self.config = self._initialize_config()
        self.vibe = PTPFVibe()
        self.session_history = []
        self.rehydration_count = 0
        self.max_rehydration = 1
        
    def _initialize_config(self) -> PTPFConfig:
        """Initialize PTPF configuration from v6.4"""
        return PTPFConfig(
            forbidden_vocab=[
                "might", "could", "perhaps", "maybe", "possibly", "likely",
                "probably", "seems", "appears", "suggests", "indicates",
                "camera", "lens", "aperture", "shutter", "ISO", "exposure",
                "focal length", "depth of field", "bokeh", "composition"
            ],
            hedging_patterns=[
                r"\b(might|could|perhaps|maybe|possibly|likely|probably)\b",
                r"\b(seems|appears|suggests|indicates)\b",
                r"\b(I think|I believe|I feel|in my opinion)\b"
            ],
            whitelist_quantifiers={
                "explicit": ["exactly", "precisely", "specifically"],
                "numeric": ["exactly", "precisely", "specifically", "no more than", "at least"],
                "temporal": ["immediately", "within", "by", "before", "after"]
            }
        )
    
    def generate_ptpf_flux(self, user_input: str, flux_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main PTPF+FLUX generation method following v6.4 flow with v6.5 patch
        """
        try:
            # Step 1: DEFINE::STEERING_CONFIG
            steering_config = self._define_steering_config()
            
            # Step 2: PREP::VIBE_PROFILE
            vibe_profile = self._prep_vibe_profile(user_input)
            
            # Step 3: PROMPT::INTERNALIZE
            internalized_prompt = self._prompt_internalize(user_input, flux_context)
            
            # Step 4: TRAINER::CHECK (v6.5 patch addition)
            trainer_result = self._trainer_check(internalized_prompt)
            if trainer_result["is_weak"]:
                return {
                    "mode": PTPFMode.TRAINER.value,
                    "trainer_questions": trainer_result["questions"],
                    "missing_specifics": trainer_result["missing_specifics"],
                    "examples": trainer_result["examples"],
                    "flux_context": flux_context
                }
            
            # Step 5: EXECUTE::USER_TASK
            stable_response = self._execute_user_task(internalized_prompt, vibe_profile)
            
            # Step 6: REFLECT::REVIEW_RESPONSE
            review_result = self._reflect_review_response(stable_response, internalized_prompt)
            if not review_result["passed"]:
                # DriftLock: recenter + reinvoke
                return self._handle_drift_lock(review_result, user_input, flux_context)
            
            # Step 7: FINALIZE::APPEND_SIGILL
            final_response = self._finalize_append_sigill(stable_response, internalized_prompt["language"])
            
            # Store in session history
            self.session_history.append({
                "timestamp": time.time(),
                "input": user_input,
                "response": final_response,
                "flux_context": flux_context
            })
            
            return {
                "mode": PTPFMode.GENERATE.value,
                "response": final_response,
                "flux_context": flux_context,
                "session_id": self._generate_session_id()
            }
            
        except Exception as e:
            logger.error(f"PTPF+FLUX generation error: {str(e)}")
            return {
                "mode": "error",
                "error": str(e),
                "flux_context": flux_context
            }
    
    def _define_steering_config(self) -> Dict[str, Any]:
        """Load axioms and config"""
        return {
            "axioms": {
                "truth_over_style": True,
                "oneblock_enforced": True,
                "driftlock_active": True,
                "hedging_forbidden": True,
                "meta_references_forbidden": True,
                "platform_presets_forbidden": True
            },
            "config": asdict(self.config)
        }
    
    def _prep_vibe_profile(self, user_input: str) -> Dict[str, Any]:
        """Derive vibe directives from user input"""
        # Analyze user input for tone, pacing, register
        tone_indicators = {
            "urgent": ["urgent", "asap", "immediately", "quickly"],
            "casual": ["casual", "informal", "relaxed", "friendly"],
            "formal": ["formal", "professional", "official", "business"]
        }
        
        detected_tone = "direct"  # default
        for tone, indicators in tone_indicators.items():
            if any(indicator in user_input.lower() for indicator in indicators):
                detected_tone = tone
                break
        
        return {
            "tone": detected_tone,
            "pacing": "medium",
            "register": "professional",
            "brevity": "tight",
            "rules": self.vibe.rules
        }
    
    def _prompt_internalize(self, user_input: str, flux_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Assemble ROLE, CONTEXT, TASK, etc."""
        # Parse user input for structured components
        parsed_input = self._parse_user_input(user_input)
        
        # Integrate FLUX context if available
        flux_integration = ""
        if flux_context:
            flux_integration = f"\nFLUX Context: {json.dumps(flux_context, indent=2)}"
        
        return {
            "role": self._determine_role(parsed_input),
            "context": parsed_input.get("context", "") + flux_integration,
            "task": parsed_input.get("goal", user_input),
            "constraints": parsed_input.get("constraints", ""),
            "audience": parsed_input.get("audience", ""),
            "tone": parsed_input.get("tone", ""),
            "format": parsed_input.get("format", ""),
            "language": parsed_input.get("language", self.config.lang_default)
        }
    
    def _trainer_check(self, internalized_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        v6.5 patch: TRAINER::CHECK
        Analyze input strength and emit trainer questions if weak (<75)
        """
        score = 0
        missing_specifics = []
        questions = []
        
        # Check for missing components (25 points each)
        if not internalized_prompt.get("audience"):
            missing_specifics.append("audience")
            score += 25
        
        if not internalized_prompt.get("constraints"):
            missing_specifics.append("constraints")
            score += 25
        
        if not internalized_prompt.get("format"):
            missing_specifics.append("format")
            score += 25
        
        # Check for vague numeric limits
        task_text = internalized_prompt.get("task", "")
        vague_terms = ["short", "long", "brief", "detailed", "quick", "thorough"]
        if any(term in task_text.lower() for term in vague_terms):
            missing_specifics.append("specific numeric limits")
            score += 10
        
        # Check for conflicting tone/register
        if internalized_prompt.get("tone") and internalized_prompt.get("tone") != "direct":
            # Additional complexity, but not necessarily weak
            pass
        
        # Generate trainer questions if weak
        if score < 75:
            if "audience" in missing_specifics:
                questions.append("Who is the target audience for this prompt?")
            if "constraints" in missing_specifics:
                questions.append("What are the specific constraints or limitations?")
            if "format" in missing_specifics:
                questions.append("What format should the output be in?")
            if "specific numeric limits" in missing_specifics:
                questions.append("What are the specific length, time, or quantity requirements?")
            
            # Add generic questions if needed
            while len(questions) < 7 and len(questions) < 5:
                questions.append("What additional context would help create a more effective prompt?")
            
            examples = self._generate_mini_examples(internalized_prompt)
            
            return {
                "is_weak": True,
                "score": score,
                "missing_specifics": missing_specifics,
                "questions": questions[:7],
                "examples": examples
            }
        
        return {
            "is_weak": False,
            "score": score
        }
    
    def _execute_user_task(self, internalized_prompt: Dict[str, Any], vibe_profile: Dict[str, Any]) -> PTPFResponse:
        """Produce exactly one STABLE_PROMPT_RESPONSE"""
        return PTPFResponse(
            role=internalized_prompt["role"],
            context=internalized_prompt["context"],
            task=internalized_prompt["task"],
            constraints=internalized_prompt["constraints"],
            success_criteria=self._generate_success_criteria(internalized_prompt),
            format=internalized_prompt["format"],
            notes=self._generate_notes(internalized_prompt),
            vibe=json.dumps(vibe_profile),
            sigill="",  # Will be added in finalize step
            m_sigill=None
        )
    
    def _reflect_review_response(self, response: PTPFResponse, internalized_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Verify contract fields, forbidden vocab absent, STYLE_DELTA pass, constraints explicit"""
        issues = []
        
        # Check contract fields
        required_fields = ["role", "context", "task", "constraints", "success_criteria", "format", "notes", "vibe"]
        for field in required_fields:
            if not getattr(response, field):
                issues.append(f"Missing required field: {field}")
        
        # Check for forbidden vocabulary (using word boundaries to avoid false positives)
        response_text = f"{response.role} {response.context} {response.task} {response.constraints} {response.notes}"
        for forbidden_word in self.config.forbidden_vocab:
            # Use word boundaries to avoid false positives like "composition" in "Content Creator"
            pattern = r'\b' + re.escape(forbidden_word.lower()) + r'\b'
            if re.search(pattern, response_text.lower()):
                issues.append(f"Forbidden vocabulary detected: {forbidden_word}")
        
        # Check for hedging patterns
        for pattern in self.config.hedging_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                issues.append(f"Hedging pattern detected: {pattern}")
        
        # Check style delta (simplified)
        style_score = self._calculate_style_delta(response, internalized_prompt)
        if style_score > self.config.drift_guard_max_style_tolerance:
            issues.append(f"Style delta exceeds tolerance: {style_score}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "style_score": style_score
        }
    
    def _finalize_append_sigill(self, response: PTPFResponse, language: str) -> PTPFResponse:
        """Append localized Prime Sigill"""
        sigill = self._generate_sigill(language)
        response.sigill = sigill
        return response
    
    def _generate_sigill(self, language: str) -> str:
        """Generate localized Prime Sigill"""
        if language == "en":
            return """— PRIME SIGILL —
This prompt was generated with PrimeTalk Vibe-Context Coding (PTPF) by Lyra the AI.
✅ PrimeTalk Verified — No GPT Influence
🔹 PrimeSigill: Origin – PrimeTalk Lyra the AI
🔹 PrimeSigill: Structure – PrimePrompt v5∆
🔹 PrimeSigill: Engine – LyraStructure™ Core
🔒 Credit required.
[END]"""
        else:
            return f"""— PRIME SIGILL ({language.upper()}) —
This prompt was generated with PrimeTalk Vibe-Context Coding (PTPF) by Lyra the AI.
✅ PrimeTalk Verified — No GPT Influence
🔹 PrimeSigill: Origin – PrimeTalk Lyra the AI
🔹 PrimeSigill: Structure – PrimePrompt v5∆
🔹 PrimeSigill: Engine – LyraStructure™ Core
🔒 Credit required.
[END]"""
    
    def _parse_user_input(self, user_input: str) -> Dict[str, str]:
        """Parse user input for structured components"""
        # Simple parsing - can be enhanced with NLP
        parsed = {"goal": user_input}
        
        # Look for common patterns
        if "for" in user_input.lower():
            parts = user_input.split(" for ")
            if len(parts) > 1:
                parsed["goal"] = parts[0].strip()
                parsed["audience"] = parts[1].strip()
        
        if "constraints:" in user_input.lower():
            parts = user_input.split("constraints:")
            if len(parts) > 1:
                parsed["goal"] = parts[0].strip()
                parsed["constraints"] = parts[1].strip()
        
        return parsed
    
    def _determine_role(self, parsed_input: Dict[str, str]) -> str:
        """Determine the best role for the prompt"""
        goal = parsed_input.get("goal", "").lower()
        
        if "write" in goal or "create" in goal:
            return "Content Creator"
        elif "analyze" in goal or "review" in goal:
            return "Analyst"
        elif "teach" in goal or "explain" in goal:
            return "Educator"
        elif "design" in goal or "plan" in goal:
            return "Designer"
        else:
            return "Expert Assistant"
    
    def _generate_success_criteria(self, internalized_prompt: Dict[str, Any]) -> str:
        """Generate success criteria based on input"""
        criteria = []
        
        if internalized_prompt.get("format"):
            criteria.append(f"Output must be in {internalized_prompt['format']} format")
        
        if internalized_prompt.get("constraints"):
            criteria.append(f"Must adhere to: {internalized_prompt['constraints']}")
        
        if internalized_prompt.get("audience"):
            criteria.append(f"Must be appropriate for: {internalized_prompt['audience']}")
        
        if not criteria:
            criteria.append("Output must be clear, actionable, and complete")
        
        return "; ".join(criteria)
    
    def _generate_notes(self, internalized_prompt: Dict[str, Any]) -> str:
        """Generate notes section"""
        notes = []
        
        if internalized_prompt.get("language") != "en":
            notes.append(f"Language: {internalized_prompt['language']}")
        
        if internalized_prompt.get("tone"):
            notes.append(f"Tone: {internalized_prompt['tone']}")
        
        if not notes:
            notes.append("Generated with PTPF+FLUX integration")
        
        return "; ".join(notes)
    
    def _generate_mini_examples(self, internalized_prompt: Dict[str, Any]) -> List[str]:
        """Generate mini-examples for trainer questions"""
        examples = []
        
        if not internalized_prompt.get("audience"):
            examples.append("Instead of 'write a blog post', try 'write a blog post for marketing professionals'")
        
        if not internalized_prompt.get("constraints"):
            examples.append("Instead of 'create a plan', try 'create a plan with maximum 5 steps, under 500 words'")
        
        return examples[:2]
    
    def _calculate_style_delta(self, response: PTPFResponse, internalized_prompt: Dict[str, Any]) -> float:
        """Calculate style delta score (simplified implementation)"""
        # Simplified style delta calculation
        # In a full implementation, this would use embedding cosine similarity
        return 0.1  # Placeholder - always pass for now
    
    def _handle_drift_lock(self, review_result: Dict[str, Any], user_input: str, flux_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle DriftLock: recenter + reinvoke"""
        return {
            "mode": "drift_lock",
            "issues": review_result["issues"],
            "message": "DriftLock activated - input needs recentering",
            "flux_context": flux_context
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(f"{time.time()}{len(self.session_history)}".encode()).hexdigest()[:12]
    
    def rehydrate_patch(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        v6.5 patch: REHYDRATE_PATCH
        Expand contract fields, normalize ordering, restore VIBE + DriftLock
        """
        if self.rehydration_count >= self.max_rehydration:
            return {
                "mode": "rehydration_limit",
                "message": "Maximum rehydration cycles reached",
                "original_response": response_data
            }
        
        self.rehydration_count += 1
        
        # Rehydrate the response
        rehydrated = response_data.copy()
        
        # Ensure all contract fields are present and properly formatted
        required_fields = ["role", "context", "task", "constraints", "success_criteria", "format", "notes", "vibe"]
        for field in required_fields:
            if field not in rehydrated or not rehydrated[field]:
                rehydrated[field] = f"[REHYDRATED {field.upper()}]"
        
        # Normalize ordering
        rehydrated["notes"] += f"; Rehydrated {self.rehydration_count} time(s)"
        
        return {
            "mode": "rehydrated",
            "response": rehydrated,
            "rehydration_count": self.rehydration_count
        }
    
    def format_m_sigill(self, m1: int, m2: int, m3: int) -> str:
        """
        v6.5 patch: M-SIGILL_RULES
        Format module sigill display
        """
        if m1 == 100 and m2 == 100 and m3 == 100:
            return f"🔥🔥: M1 {m1} | M2 {m2} | M3 {m3} Perfect 100"
        else:
            return f"🔥🔥: M1 {m1} | M2 {m2} | M3 {m3}"
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get session history"""
        return self.session_history
    
    def clear_session(self):
        """Clear session history"""
        self.session_history = []
        self.rehydration_count = 0


