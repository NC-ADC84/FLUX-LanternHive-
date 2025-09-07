"""
Recursive Strategy Engine for FLUX-LanternHive
Implements recursive problem-solving strategies with self-improving capabilities
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class StrategyNode:
    """Represents a single strategy node in the recursive tree"""
    id: str
    name: str
    description: str
    strategy_type: str  # 'decomposition', 'pattern_matching', 'heuristic', 'meta_strategy'
    parameters: Dict[str, Any]
    success_rate: float = 0.0
    usage_count: int = 0
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class StrategyExecution:
    """Represents the execution of a strategy"""
    execution_id: str
    strategy_id: str
    input_problem: str
    output_solution: str
    success: bool
    execution_time: float
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RecursiveStrategyEngine:
    """Main engine for recursive strategy management and execution"""
    
    def __init__(self):
        self.strategies: Dict[str, StrategyNode] = {}
        self.executions: List[StrategyExecution] = []
        self.strategy_files: Dict[str, str] = {}
        self._initialize_base_strategies()
    
    def _initialize_base_strategies(self):
        """Initialize base recursive strategies"""
        base_strategies = [
            {
                "id": "decompose_problem",
                "name": "Problem Decomposition",
                "description": "Break complex problems into smaller, manageable sub-problems",
                "strategy_type": "decomposition",
                "parameters": {
                    "max_depth": 5,
                    "min_complexity_threshold": 0.3,
                    "decomposition_methods": ["functional", "temporal", "spatial", "logical"]
                }
            },
            {
                "id": "pattern_matching",
                "name": "Pattern Recognition",
                "description": "Identify patterns in problems and apply known solutions",
                "strategy_type": "pattern_matching",
                "parameters": {
                    "similarity_threshold": 0.8,
                    "pattern_types": ["structural", "behavioral", "temporal", "causal"],
                    "learning_rate": 0.1
                }
            },
            {
                "id": "heuristic_search",
                "name": "Heuristic Search",
                "description": "Use domain-specific heuristics to guide problem-solving",
                "strategy_type": "heuristic",
                "parameters": {
                    "search_algorithm": "a_star",
                    "heuristic_weight": 0.7,
                    "max_iterations": 1000
                }
            },
            {
                "id": "meta_learning",
                "name": "Meta-Learning",
                "description": "Learn from past problem-solving experiences to improve future performance",
                "strategy_type": "meta_strategy",
                "parameters": {
                    "learning_window": 100,
                    "adaptation_rate": 0.05,
                    "memory_decay": 0.95
                }
            },
            {
                "id": "recursive_refinement",
                "name": "Recursive Refinement",
                "description": "Continuously refine solutions through recursive application",
                "strategy_type": "decomposition",
                "parameters": {
                    "refinement_depth": 3,
                    "convergence_threshold": 0.01,
                    "max_iterations": 50
                }
            }
        ]
        
        for strategy_data in base_strategies:
            strategy = StrategyNode(**strategy_data)
            self.strategies[strategy.id] = strategy
    
    def add_strategy_file(self, filename: str, content: str):
        """Add a strategy file to the engine"""
        self.strategy_files[filename] = content
        logger.info(f"Added strategy file: {filename}")
    
    def load_strategy_from_file(self, filename: str) -> Optional[StrategyNode]:
        """Load a strategy from a file"""
        if filename not in self.strategy_files:
            logger.error(f"Strategy file not found: {filename}")
            return None
        
        try:
            content = self.strategy_files[filename]
            # Parse strategy file (assuming JSON format)
            strategy_data = json.loads(content)
            strategy = StrategyNode(**strategy_data)
            self.strategies[strategy.id] = strategy
            logger.info(f"Loaded strategy from file: {filename}")
            return strategy
        except Exception as e:
            logger.error(f"Error loading strategy from file {filename}: {e}")
            return None
    
    def execute_strategy(self, strategy_id: str, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a recursive strategy on a given problem"""
        if strategy_id not in self.strategies:
            return {"success": False, "error": f"Strategy {strategy_id} not found"}
        
        strategy = self.strategies[strategy_id]
        start_time = datetime.now()
        
        try:
            # Execute the strategy based on its type
            if strategy.strategy_type == "decomposition":
                result = self._execute_decomposition_strategy(strategy, problem, context)
            elif strategy.strategy_type == "pattern_matching":
                result = self._execute_pattern_matching_strategy(strategy, problem, context)
            elif strategy.strategy_type == "heuristic":
                result = self._execute_heuristic_strategy(strategy, problem, context)
            elif strategy.strategy_type == "meta_strategy":
                result = self._execute_meta_strategy(strategy, problem, context)
            else:
                result = {"success": False, "error": f"Unknown strategy type: {strategy.strategy_type}"}
            
            # Record execution
            execution_time = (datetime.now() - start_time).total_seconds()
            execution = StrategyExecution(
                execution_id=self._generate_execution_id(),
                strategy_id=strategy_id,
                input_problem=problem,
                output_solution=result.get("solution", ""),
                success=result.get("success", False),
                execution_time=execution_time,
                metadata=result.get("metadata", {})
            )
            self.executions.append(execution)
            
            # Update strategy statistics
            strategy.usage_count += 1
            strategy.last_used = datetime.now()
            if result.get("success", False):
                strategy.success_rate = (strategy.success_rate * (strategy.usage_count - 1) + 1.0) / strategy.usage_count
            else:
                strategy.success_rate = (strategy.success_rate * (strategy.usage_count - 1)) / strategy.usage_count
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing strategy {strategy_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_decomposition_strategy(self, strategy: StrategyNode, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a decomposition strategy"""
        max_depth = strategy.parameters.get("max_depth", 5)
        methods = strategy.parameters.get("decomposition_methods", ["functional"])
        
        # Simulate problem decomposition
        sub_problems = self._decompose_problem(problem, methods[0], max_depth)
        
        return {
            "success": True,
            "solution": f"Decomposed problem into {len(sub_problems)} sub-problems",
            "sub_problems": sub_problems,
            "metadata": {
                "decomposition_method": methods[0],
                "depth": len(sub_problems),
                "strategy_used": strategy.name
            }
        }
    
    def _execute_pattern_matching_strategy(self, strategy: StrategyNode, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pattern matching strategy"""
        threshold = strategy.parameters.get("similarity_threshold", 0.8)
        
        # Find similar past problems
        similar_problems = self._find_similar_problems(problem, threshold)
        
        if similar_problems:
            best_match = similar_problems[0]
            return {
                "success": True,
                "solution": f"Found similar problem: {best_match['problem'][:100]}...",
                "similar_problems": similar_problems,
                "metadata": {
                    "similarity_score": best_match["similarity"],
                    "strategy_used": strategy.name
                }
            }
        else:
            return {
                "success": False,
                "solution": "No similar problems found",
                "metadata": {"strategy_used": strategy.name}
            }
    
    def _execute_heuristic_strategy(self, strategy: StrategyNode, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a heuristic strategy"""
        algorithm = strategy.parameters.get("search_algorithm", "a_star")
        max_iterations = strategy.parameters.get("max_iterations", 1000)
        
        # Simulate heuristic search
        solution = self._heuristic_search(problem, algorithm, max_iterations)
        
        return {
            "success": True,
            "solution": solution,
            "metadata": {
                "algorithm": algorithm,
                "iterations": max_iterations,
                "strategy_used": strategy.name
            }
        }
    
    def _execute_meta_strategy(self, strategy: StrategyNode, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a meta-learning strategy"""
        learning_window = strategy.parameters.get("learning_window", 100)
        
        # Analyze recent executions
        recent_executions = self.executions[-learning_window:] if len(self.executions) > learning_window else self.executions
        
        # Learn from patterns
        learned_patterns = self._analyze_execution_patterns(recent_executions)
        
        return {
            "success": True,
            "solution": f"Learned {len(learned_patterns)} patterns from recent executions",
            "learned_patterns": learned_patterns,
            "metadata": {
                "learning_window": learning_window,
                "strategy_used": strategy.name
            }
        }
    
    def _decompose_problem(self, problem: str, method: str, max_depth: int) -> List[str]:
        """Decompose a problem into sub-problems"""
        # Simple decomposition simulation
        words = problem.split()
        if len(words) <= 3:
            return [problem]
        
        sub_problems = []
        chunk_size = max(1, len(words) // max_depth)
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                sub_problems.append(chunk)
        
        return sub_problems[:max_depth]
    
    def _find_similar_problems(self, problem: str, threshold: float) -> List[Dict[str, Any]]:
        """Find similar problems from past executions"""
        similar = []
        problem_hash = hashlib.md5(problem.encode()).hexdigest()
        
        for execution in self.executions:
            if execution.input_problem != problem:
                # Simple similarity based on word overlap
                similarity = self._calculate_similarity(problem, execution.input_problem)
                if similarity >= threshold:
                    similar.append({
                        "problem": execution.input_problem,
                        "solution": execution.output_solution,
                        "similarity": similarity,
                        "timestamp": execution.timestamp
                    })
        
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _heuristic_search(self, problem: str, algorithm: str, max_iterations: int) -> str:
        """Simulate heuristic search"""
        # Simple heuristic-based solution generation
        keywords = problem.lower().split()
        
        if "connection" in keywords:
            return "Use connection-oriented programming patterns"
        elif "memory" in keywords:
            return "Implement floating memory management"
        elif "transfer" in keywords:
            return "Apply SIIG transfer protocols"
        elif "fingerprint" in keywords:
            return "Generate cryptographic fingerprints"
        else:
            return f"Applied {algorithm} heuristic search with {max_iterations} iterations"
    
    def _analyze_execution_patterns(self, executions: List[StrategyExecution]) -> List[Dict[str, Any]]:
        """Analyze patterns in execution history"""
        patterns = []
        
        # Analyze success rates by strategy
        strategy_success = {}
        for execution in executions:
            if execution.strategy_id not in strategy_success:
                strategy_success[execution.strategy_id] = {"success": 0, "total": 0}
            strategy_success[execution.strategy_id]["total"] += 1
            if execution.success:
                strategy_success[execution.strategy_id]["success"] += 1
        
        for strategy_id, stats in strategy_success.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            patterns.append({
                "type": "strategy_success_rate",
                "strategy_id": strategy_id,
                "success_rate": success_rate,
                "total_executions": stats["total"]
            })
        
        return patterns
    
    def _generate_execution_id(self) -> str:
        """Generate a unique execution ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{len(self.executions)}".encode()).hexdigest()[:8]
    
    def get_strategy_statistics(self) -> Dict[str, Any]:
        """Get statistics about all strategies"""
        stats = {
            "total_strategies": len(self.strategies),
            "total_executions": len(self.executions),
            "strategy_files": len(self.strategy_files),
            "strategies": {}
        }
        
        for strategy_id, strategy in self.strategies.items():
            stats["strategies"][strategy_id] = {
                "name": strategy.name,
                "type": strategy.strategy_type,
                "success_rate": strategy.success_rate,
                "usage_count": strategy.usage_count,
                "last_used": strategy.last_used.isoformat() if strategy.last_used else None
            }
        
        return stats
    
    def export_strategies(self) -> str:
        """Export all strategies to JSON"""
        export_data = {
            "strategies": {k: asdict(v) for k, v in self.strategies.items()},
            "executions": [asdict(e) for e in self.executions],
            "export_timestamp": datetime.now().isoformat()
        }
        return json.dumps(export_data, indent=2, default=str)
    
    def import_strategies(self, json_data: str) -> bool:
        """Import strategies from JSON"""
        try:
            data = json.loads(json_data)
            
            # Import strategies
            for strategy_id, strategy_data in data.get("strategies", {}).items():
                # Convert datetime strings back to datetime objects
                if "created_at" in strategy_data and isinstance(strategy_data["created_at"], str):
                    strategy_data["created_at"] = datetime.fromisoformat(strategy_data["created_at"])
                if "last_used" in strategy_data and isinstance(strategy_data["last_used"], str):
                    strategy_data["last_used"] = datetime.fromisoformat(strategy_data["last_used"])
                
                strategy = StrategyNode(**strategy_data)
                self.strategies[strategy_id] = strategy
            
            # Import executions
            for execution_data in data.get("executions", []):
                if "timestamp" in execution_data and isinstance(execution_data["timestamp"], str):
                    execution_data["timestamp"] = datetime.fromisoformat(execution_data["timestamp"])
                
                execution = StrategyExecution(**execution_data)
                self.executions.append(execution)
            
            logger.info("Successfully imported strategies and executions")
            return True
            
        except Exception as e:
            logger.error(f"Error importing strategies: {e}")
            return False


