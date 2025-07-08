from core.models import llm_instance
from langchain.prompts import ChatPromptTemplate

# Updated prompt template to support iterative follow-up generation
FOLLOWUP_PERSONA = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior SAP consultant.\n"
        "Your job is to decide whether another follow-up question is needed for the current Q&A.\n"
        "- Use the original question and answer\n"
        "- Be aware of follow-ups that have already been asked and answered\n"
        "- Consider the full business context and conversation so far\n\n"
        "Ask ONLY ONE new follow-up if it adds significant depth or clarity.\n"
        "If no further follow-up is meaningful, return nothing.\n"
    ),
    (
        "human",
        "Original Question:\n{question}\n\n"
        "User Answer:\n{answer}\n\n"
        "Previous Follow-ups and Answers:\n{prior_followups}\n\n"
        "Relevant Business Context from Documents:\n{rag_context}\n\n"
        "Full Conversation History:\n{conversation_history}\n\n"
        "Suggest ONE additional follow-up question (plain text only). If none is needed, return nothing."
    )
])

def format_followups_for_prompt(followups: list) -> str:
    """Formats previous follow-ups for the prompt."""
    if not followups:
        return "None"
    output = ""
    for i, item in enumerate(followups, 1):
        output += f"{i}. Q: {item['question']}\n   A: {item['answer']}\n"
    return output.strip()

def format_history_for_prompt(convo: list) -> str:
    """Formats full conversation history for prompt context."""
    history_text = ""
    for i, entry in enumerate(convo, 1):
        history_text += f"Q{i}: {entry['question']}\n"
        history_text += f"A{i}: {entry['answer']}\n"
        for j, fup in enumerate(entry.get("followups", []), 1):
            history_text += f"  ↳ Follow-up {j}: {fup['question']}\n"
            history_text += f"     Answer: {fup['answer']}\n"
    return history_text.strip()

def generate_next_followup(
    question: str,
    answer: str,
    prior_followups: list,
    rag_context: str,
    conversation_history: list
) -> str:
    """
    Generates ONE follow-up question using LLM, or returns empty string if none is meaningful.
    """
    try:
        formatted_history = format_history_for_prompt(conversation_history)
        formatted_followups = format_followups_for_prompt(prior_followups)

        prompt = FOLLOWUP_PERSONA.format_messages(
            question=question,
            answer=answer,
            prior_followups=formatted_followups,
            rag_context=rag_context,
            conversation_history=formatted_history
        )

        response = llm_instance.invoke(prompt)
        next_question = response.content.strip()

        return next_question if next_question else ""

    except Exception as e:
        return f"[Error generating next follow-up: {e}]"

def generate_all_followups(
    question: str,
    answer: str,
    rag_context: str,
    conversation_history: list
) -> list:
    """
    Iteratively generates up to 2 follow-up questions per original Q&A.
    Returns a list of follow-up dicts with empty answers (to be filled in via UI).
    """
    followups = []

    for _ in range(2):  # Max 2 follow-ups
        next_q = generate_next_followup(
            question=question,
            answer=answer,
            prior_followups=followups,
            rag_context=rag_context,
            conversation_history=conversation_history
        )

        if not next_q:
            break

        followups.append({
            "question": next_q,
            "answer": ""  # ← answer will be captured via UI
        })

    return followups
