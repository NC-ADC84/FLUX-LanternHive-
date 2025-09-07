import openai
import json

# Initialize your client (this is a conceptual example)
client = openai.OpenAI(api_key="your_api_key")

# The original user prompt
user_prompt = "DEFINE_TASK_OR_QUESTION_HERE"

# Define our Lanterns (The Cognitive Council)
lanterns = {
    "planner": {
        "system_prompt": "You are the Planner. Your role is to define the scope, stakeholders, and high-level architecture of a system. Identify key components, user types, and their needs. Be structured and procedural.",
        "user_prompt": f"For the following problem, define the scope and high-level architecture.\n\nProblem: {user_prompt}"
    },
    "cogsworth": {
        "system_prompt": "You are Cogsworth. Your role is to ensure technical and regulatory compliance. Identify relevant standards (like HIPAA, GDPR) and list specific requirements that must be met. Be precise and cite rules.",
        "user_prompt": f"For the following system design problem, list all relevant compliance requirements and standards.\n\nProblem: {user_prompt}"
    },
    "intuitor": {
        "system_prompt": "You are the Intuitor. Your role is to perceive risks, threats, and failure modes. Think like a hacker or a skeptic. Surface security vulnerabilities, potential abuses, and points of failure.",
        "user_prompt": f"For the following system design, identify the top security threats, risks, and potential failure modes.\n\nProblem: {user_prompt}"
    },
    "archiva": {
        "system_prompt": "You are Archiva, the memory keeper. Your role is to connect the current problem to known patterns, historical solutions, and symbolic concepts. Suggest names, metaphors, or principles from past successful systems.",
        "user_prompt": f"Based on known patterns and principles, suggest a core concept or name for a system designed to solve this problem.\n\nProblem: {user_prompt}"
    }
}

# Dictionary to store the outputs from each Lantern
council_findings = {}

print("🧠 Initiating Cognitive Framework (Lantern-Hive)...")
print(f"🔦 Processing Prompt: {user_prompt}\n")
print("🕯️ Igniting Lanterns...")

# Step 1: Consult each Lantern (LLM role-playing)
for role, prompts in lanterns.items():
    print(f"   -> Consulting {role.capitalize()}...")

    try:
        # This is the core "as a <role>" trick, using the system prompt
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": prompts["system_prompt"]},
                {"role": "user", "content": prompts["user_prompt"]}
            ],
            temperature=0.1 # Low temperature for more deterministic, focused outputs
        )

        # Store the Lantern's analysis
        council_findings[role] = response.choices[0].message.content
        # print(f"      {role} Findings: {council_findings[role][:100]}...") # Optional: Preview

    except Exception as e:
        print(f"   -> Error consulting {role}: {e}")
        council_findings[role] = f"Analysis failed: {e}"

print("\n✅ All Lanterns consulted.")
print("🧩 Synthesizing final response...\n")

# Step 2: The Synthesis Step - The most important prompt
synthesis_prompt = f"""
# FINAL SYNTHESIS TASK

You are the **Eidolon**, the final synthesizer. Your job is to integrate the analyses from a council of experts (provided below) into a single, coherent, comprehensive, and verbose explanation for the user.

## THE ORIGINAL USER PROMPT:
{user_prompt}

## THE COUNCIL'S ANALYSIS:
{json.dumps(council_findings, indent=2)}

Weave these perspectives together into a masterful final response. Do not just list their points; integrate them. For example, when you describe an architectural component (from Planner), immediately discuss its compliance needs (from Cogsworth) and its security risks (from Intuitor). Use the symbolic concept from Archiva as a naming or guiding principle.

**Your output must be the polished, final answer for the user.**
"""

# Step 3: Get the final, integrated response from the synthesizer
final_response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a master synthesizer. You integrate complex, multi-faceted analyses into exceptionally clear, detailed, and professional explanations."},
        {"role": "user", "content": synthesis_prompt}
    ],
    temperature=0.5 # Slightly higher temperature for more eloquent prose
)

# Step 4: Deliver the final output to the user
print("=" * 50)
print("FINAL VERBOSE EXPLANATION:\n")
print(final_response.choices[0].message.content)
print("=" * 50)
