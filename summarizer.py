from ctransformers import AutoModelForCausalLM
from pathlib import Path

# Load model once
MODEL_PATH = Path(__file__).parent / "tinyllama.gguf"

llm = AutoModelForCausalLM.from_pretrained(
    str(MODEL_PATH),
    model_type="llama",
    max_new_tokens=300,
    temperature=0.3
)


def build_prompt(context_list):
    bullets = []
    for c in context_list:
        if isinstance(c, str) and c.strip():
            bullets.append(f"- {c.strip()}")

    return f"""
You are a software task assistant.

Summarize the following development progress so the user can resume work.
Include:
- What was done
- Current state
- What remains

Task Progress:
{chr(10).join(bullets)}

Resume Summary:
"""


def generate_summary(context_list):
    if not context_list or not isinstance(context_list, list):
        return "No context available."

    prompt = build_prompt(context_list)

    try:
        output = llm(prompt)
        return output.strip()
    except Exception as e:
        return f"Model error: {str(e)}"