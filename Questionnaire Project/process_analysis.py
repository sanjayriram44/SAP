from core.models import llm_instance


def generate_process_understanding(conversation_history: list) -> str:
    """
    Generates a bullet-point summary of the user's As-Is process understanding.
    """
    prompt = f"You are a SAP consultant. Based on this conversation history, summarize the user's current sourcing process:\n\n"
    for i, item in enumerate(conversation_history, 1):
        prompt += f"Q{i}: {item['question']}\nA{i}: {item['answer']}\n"
        for j, fup in enumerate(item['followups'], 1):
            prompt += f"  ↳ F{j}: {fup['question']}\n     A: {fup['answer']}\n"
    prompt += "\nGive a summary of the user's current process understanding in bullet points."

    response = llm_instance.invoke(prompt)
    return response.content.strip()


def update_process_understanding_with_input(conversation_history: list, user_input: str, current_understanding: str) -> str:
    """
    Updates the process understanding summary based on user input.
    """
    correction_prompt = f"""You are a SAP consultant. Here is the current summary of the user's sourcing process:

{current_understanding}

The user has provided the following correction or addition:
{user_input}

Please regenerate a revised and corrected process understanding summary, integrating the user's input clearly and accurately, in bullet points."""
    response = llm_instance.invoke(correction_prompt)
    return response.content.strip()


def generate_process_recommendation(conversation_history: list) -> str:
    """
    Generates a detailed SAP Ariba process recommendation based on discovery conversation.
    """
    design_prompt = """
You are a senior SAP Ariba consultant in a BBP discovery session.

Your task:
Based on the discovery Q&A below, design a detailed process recommendation for SAP Ariba Sourcing tailored to the client's current sourcing practices, business goals, and IT environment.

Key Instructions:
- Structure the process recommendation in clear, detailed sections with headings, organized logically.
- Focus on real, actionable design changes — not general advice.
- Be specific about what is enabled/configured in Ariba — e.g., “Auto-publish enabled for RFQ after approval,” or “Standard template with 5 mandatory fields applied to all sourcing events.”

Formatting Instructions:
- Use clear SAP/Ariba terminology as used in real BBPs.
- Give headings and content for each section point.

Here is the discovery Q&A:
"""
    for item in conversation_history:
        design_prompt += f"Q: {item['question']}\nA: {item['answer']}\n"
        for f in item.get("followups", []):
            design_prompt += f"↳ Follow-up: {f['question']}\nAnswer: {f['answer']}\n"

    response = llm_instance.invoke(design_prompt)
    return response.content.strip()
