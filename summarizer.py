
from ctransformers import AutoModelForCausalLM
from pathlib import Path

# =========================
# Model Configuration
# =========================

MODEL_PATH = Path(__file__).parent / "tinyllama.gguf"

# Load the model
llm = AutoModelForCausalLM.from_pretrained(
    str(MODEL_PATH),
    model_type="llama",
    max_new_tokens=100,  # Reduced output token limit to prevent cutoff
    temperature=0.2
)

# TinyLlama 512 context safe input budget
MAX_INPUT_TOKENS = 260


# =========================
# Utility: Token Counter
# =========================

def count_tokens(text):
    # Approximate token count based on word length
    return len(text.split())


# =========================
# Context Chunking
# =========================

def split_context(context_list):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for item in context_list:
        tokens = count_tokens(item)

        if current_tokens + tokens > MAX_INPUT_TOKENS:
            chunks.append(current_chunk)
            current_chunk = [item]
            current_tokens = tokens
        else:
            current_chunk.append(item)
            current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# =========================
# Bullet Point Summary Generation (Stage 1)
# =========================

def build_section_prompt(section_name, context_chunk):
    context_text = "\n".join(f"- {c}" for c in context_chunk)

    return f"""
Section: {section_name}

Context:
{context_text}

Generate concise, unique bullet points summarizing the key points for this section. Avoid repeating content from other sections and focus on the most relevant details.
"""


def generate_section_bullet_summary(section_name, context_chunks):
    section_outputs = []

    for chunk in context_chunks:
        prompt = build_section_prompt(section_name, chunk)
        output = llm(prompt)
        section_outputs.append(output.strip())

    # Merge chunk outputs for the section
    return "\n".join(section_outputs)


# =========================
# Detailed Expansion (Stage 2)
# =========================

def build_expansion_prompt(section_name, bullet_summary):
    return f"""
Section: {section_name}

Bullet Summary:
{bullet_summary}

Expand the summary into a detailed paragraph, focusing on adding depth while avoiding repetition across sections. Ensure coherence and clarity.
"""


def generate_section_expansion(section_name, bullet_summary):
    prompt = build_expansion_prompt(section_name, bullet_summary)
    return llm(prompt).strip()


# =========================
# Main Summary Generation Function
# =========================

def generate_summary(context_list):
    """
    This function generates a bullet-point summary based on the context provided.
    It returns only the bullet-point summary string and not the detailed section summary.
    """
    if not context_list or not isinstance(context_list, list):
        return "No context available."

    # Step 1: Split context into manageable chunks
    context_chunks = split_context(context_list)

    # Step 2: Define sections (removed "Next Steps / TODO List" and "Recent Changes Since Last Checkpoint")
    sections = [
        "Current Progress Summary",
        "Decisions Taken and Rationale",
        "Open Issues / Blockers"
    ]

    # Step 3: Generate concise bullet summary for each section (Stage 1)
    bullet_summary = {}

    for section in sections:
        bullet_summary[section] = generate_section_bullet_summary(section, context_chunks)

    # Step 4: Return the bullet-point summary (only the final output string)
    final_output = "\n".join([f"{section}:\n{bullet_summary[section]}\n" for section in sections])

    return final_output.strip()


# =========================
# Detailed Expansion Request
# =========================

def expand_section(section_name, bullet_summary, generate_expansion=False):
    """
    Expands the given section if requested.
    """
    if generate_expansion:
        expanded = generate_section_expansion(section_name, bullet_summary[section_name])
        return expanded
    else:
        # Otherwise, return the bullet-point summary
        return bullet_summary[section_name]

