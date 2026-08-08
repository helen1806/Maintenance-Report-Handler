import os
import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: str


REWRITE_PROMPT = """You are an AI assistant helping to rewrite user questions based on conversation history.
Your only job is to rewrite the follow-up question so it becomes a standalone question that can be understood without the context.
DO NOT answer the question. ONLY return the rewritten question.

CRITICAL INSTRUCTIONS:
1. If the user's follow-up question is a greeting (e.g., "hello", "hi") or pleasantry, DO NOT rewrite it. Return it exactly as it is.
2. If the user's follow-up question introduces a NEW topic or asks a broad/general question (e.g., "summarize all cases", "what details do you know"), DO NOT merge it with the previous context. Return it exactly as it is.
3. ONLY rewrite the question if it contains pronouns (it, that, them) or ambiguous references (the pump, the issue) that require the conversation history to make sense.

Conversation History:
{history_text}

Follow-up Question: {question}

Rewritten Standalone Question:"""


def _format_history(history: List[ChatMessage]) -> str:
    return "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in history])


def rewrite_question_with_context(question: str, history: List[ChatMessage]) -> str:
    """
    If history exists, uses a lightweight LLM call to rewrite the question into a standalone query.
    If the question does not need rewriting (e.g. 'Summarize the report'), the LLM should output it essentially unchanged,
    but resolved of any pronouns like 'it', 'that', 'the second one'.
    """
    if not history:
        return question

    try:
        llm = ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0,
        )

        prompt = PromptTemplate(
            template=REWRITE_PROMPT, input_variables=["history_text", "question"]
        )

        history_text = _format_history(history)

        # We can use invoke on the prompt piped to the LLM
        chain = prompt | llm

        logger.info("Rewriting question based on conversational context...")
        result = chain.invoke({"history_text": history_text, "question": question})

        rewritten_question = result.content.strip()
        logger.info(f"Original: {question} | Rewritten: {rewritten_question}")

        return rewritten_question
    except Exception as e:
        logger.error(f"Failed to rewrite question with context: {e}")
        # Fallback to the original question if rewriting fails to prevent crashing
        return question
