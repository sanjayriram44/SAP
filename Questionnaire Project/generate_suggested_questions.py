from core.models import llm_instance
from persona_prompt import QUESTION_PERSONA
from probing_focus import get_llm_probing_focus  


def format_history_for_prompt(conversation_history: list) -> str:
    """
    Convert structured Q&A history (including follow-ups) into a readable string for the LLM.
    """
    history_text = ""
    for i, entry in enumerate(conversation_history, 1):
        history_text += f"Q{i}: {entry['question']}\n"
        history_text += f"A{i}: {entry['answer']}\n"
        for j, fup in enumerate(entry.get("followups", []), 1):
            history_text += f"  ↳ Follow-up {j}: {fup['question']}\n"
            history_text += f"     Answer: {fup['answer']}\n"
    return history_text.strip()


def generate_suggested_questions(
    user_choices: dict,
    rag_context: str,
    conversation_history: list,
    sub_process_name: str
) -> list:
    """
    Generate the next suggested discovery question using:
    - User choices (filters)
    - RAG document chunks
    - Previous Q&A history (including follow-ups)
    - Subprocess name to scope the discussion

    Returns a list of 1 or more high-quality questions.
    """
    try:
        # Format the history for the prompt
        formatted_history = format_history_for_prompt(conversation_history)

        # 🔍 Get dynamic probing cues based on subprocess + user dimension filters
        probing_focus = get_llm_probing_focus(subprocess=sub_process_name, user_choices=user_choices)

        # Combine all context into a single dict for the persona prompt
        context_for_prompt = {
            "user_choices": user_choices,
            "rag_context": rag_context,
            "conversation_history": formatted_history,
            "sub_process_name": sub_process_name,
            "probing_focus": get_llm_probing_focus(sub_process_name, user_choices) # ✅ Injected into the prompt context
        }

        # Fill in the persona template
        formatted_prompt = QUESTION_PERSONA.format_messages(context=context_for_prompt)

        # Call the LLM
        response = llm_instance.invoke(formatted_prompt)

        # Extract and clean the questions
        lines = response.content.strip().split("\n")
        questions = [
            line.strip("-•* ").strip()
            for line in lines
            if line.strip()
        ]

        return questions

    except Exception as e:
        return [f"[Error generating suggested questions: {e}]"]
