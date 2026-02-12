from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.config import ModelConfig
from backend.utils.get_device import get_device


SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question based ONLY on the "
    "provided context. Give a detailed and complete answer. "
    "If the context does not contain the answer, say "
    "'I don't have enough information to answer that question.'"
)

RAG_PROMPT_TEMPLATE = """Use the following pieces of context to answer the question. Provide a detailed answer in 3-5 sentences minimum.

Context:
{context}

Question: {question}

Detailed Answer:"""


class LLMService:
    """Generates responses using the self-hosted Qwen language model."""

    def __init__(self, config: ModelConfig):
        self._model_name = config.llm_model_name
        self._device = get_device()
        self._max_new_tokens = config.max_new_token
        self._tokenizer = None
        self._model = None

    def load(self) -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(
            self._model_name,
            trust_remote_code=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_name,
            trust_remote_code=True,
        )
        self._model.to(self._device)
        self._model.eval()

    def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Generate an answer based on retrieved context chunks."""
        self._ensure_model_loaded()

        context = self._format_context(context_chunks)
        prompt = self._build_prompt(question, context)
        return self._generate(prompt)

    def _format_context(self, chunks: list[str]) -> str:
        numbered_chunks = [f"[{i + 1}] {chunk}" for i, chunk in enumerate(chunks)]
        return "\n\n".join(numbered_chunks)

    def _build_prompt(self, question: str, context: str) -> str:
        user_message = RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        return self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _generate(self, prompt: str) -> str:
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)

        outputs = self._model.generate(
            **inputs,
            max_new_tokens=self._max_new_tokens,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.2,
        )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1] :]
        return self._tokenizer.decode(generated_tokens, skip_special_tokens=True)

    def _ensure_model_loaded(self) -> None:
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("LLM not loaded. Call load() before generate.")
