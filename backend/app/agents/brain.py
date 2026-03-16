import logging
import httpx
from app.core.config import settings
from app.llm.ollama import OllamaModelResolver
from app.core.model_routes import ModelRouteContext, openrouter_chat, select_model_route

logger = logging.getLogger(__name__)


class Brain:
    """
    The cognitive core of the HyperCode agent system.
    Powered by Perplexity AI (Sonar Pro) with fallback to Ollama + OpenRouter.

    Memory modes (inter-agent memory — Phase 1):
      none   — stateless, no memory read/write (default, backward-compatible)
      self   — reads + writes own conversation history only
      shared — reads handoff inbox + own history; writes both
    """

    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar-pro"
        preferred_patterns = [p.strip() for p in settings.OLLAMA_MODEL_PREFERRED.split(",") if p.strip()]
        self._ollama_model_resolver = OllamaModelResolver(
            ollama_host=settings.OLLAMA_HOST,
            preferred_patterns=preferred_patterns,
            max_size_mb=settings.OLLAMA_MAX_MODEL_SIZE_MB,
            refresh_seconds=settings.OLLAMA_MODEL_REFRESH_SECONDS,
        )

    # ------------------------------------------------------------------
    # Memory helpers
    # ------------------------------------------------------------------

    async def recall_context(self, query: str = None, limit: int = 5) -> str:
        """
        Retrieves context using Vector Search (RAG) if available,
        falling back to recent files.
        """
        context = []

        # 1. Try Vector Search (Semantic)
        try:
            from app.core.rag import rag
            if query:
                logger.info(f"[BRAIN] Semantic searching for: '{query}'")
                rag_results = rag.query(query, n_results=limit)
                if rag_results:
                    context.append("--- Semantic Memory (RAG) ---")
                    context.extend(rag_results)
                    return "\n\n".join(context)
        except Exception as e:
            logger.warning(f"[BRAIN] RAG search failed: {e}")

        # 2. Fallback to Recent Files (Temporal)
        try:
            from app.core.storage import get_storage
            storage = get_storage()
            files = storage.list_files(limit=limit)
            for file_key in files:
                if file_key.endswith(".md"):
                    content = storage.get_file_content(file_key)
                    summary = content[:1000] + "..." if len(content) > 1000 else content
                    context.append(f"--- Recent File: {file_key} ---\n{summary}\n")
            return "\n".join(context)
        except Exception as e:
            logger.error(f"[BRAIN] Error recalling context: {e}")
            return ""

    def _build_memory_context(
        self,
        conversation_id: str | None,
        agent_id: str,
        memory_mode: str,
        rag_context: str,
    ) -> str:
        """
        Assembles injected memory block in the correct order:
          1. Handoff inbox  (if shared mode)
          2. RAG snippets   (if available)
          3. Conversation history (if self or shared mode)

        Hard-capped to avoid prompt token overflow.
        Fails closed: if anything errors, returns empty string.
        """
        MAX_HANDOFF_CHARS = 1_500
        MAX_RAG_CHARS = 2_000
        MAX_HISTORY_CHARS = 2_000

        if memory_mode == "none" or not conversation_id:
            return rag_context  # preserve existing RAG behaviour

        try:
            from app.core.agent_memory import read_handoffs, get_history
            blocks: list[str] = []

            # 1. Handoff inbox
            if memory_mode == "shared":
                handoffs = read_handoffs(agent_id, limit=5, consume=False)
                if handoffs:
                    handoff_text = "\n".join(
                        f"- [{h['from_agent_id']}] {h['summary']}" for h in handoffs
                    )
                    handoff_text = handoff_text[:MAX_HANDOFF_CHARS]
                    blocks.append(f"--- Handoff Notes for {agent_id} ---\n{handoff_text}")

            # 2. RAG snippets (pass-through from caller)
            if rag_context:
                blocks.append(rag_context[:MAX_RAG_CHARS])

            # 3. Conversation history
            history = get_history(conversation_id, last_n=10)
            if history:
                history_lines = []
                for turn in history:
                    line = f"[{turn['agent_id']}|{turn['role']}] {turn['content']}"
                    history_lines.append(line)
                history_text = "\n".join(history_lines)[:MAX_HISTORY_CHARS]
                blocks.append(f"--- Conversation History ---\n{history_text}")

            return "\n\n".join(blocks)

        except Exception as exc:
            logger.warning(f"[BRAIN] _build_memory_context failed (failing closed): {exc}")
            return rag_context  # fall back to RAG only, never crash

    # ------------------------------------------------------------------
    # Core think() — stateful + backward-compatible
    # ------------------------------------------------------------------

    async def think(
        self,
        role: str,
        task_description: str,
        use_memory: bool = False,
        route_context: dict | None = None,
        # --- Phase 1: inter-agent memory ---
        conversation_id: str | None = None,
        agent_id: str = "brain",
        memory_mode: str = "none",  # none | self | shared
    ) -> str:
        """
        Process a task description and return a plan or code.

        Supports:
          1. Local LLM (Ollama)                    — Zero Cost
          2. Perplexity Session Auth (Comet/Spaces) — Zero Cost
          3. Cloud API (Perplexity/Anthropic)       — Paid Fallback

        Memory modes (new — Phase 1):
          none   — stateless, original behaviour (default)
          self   — reads + writes conversation history
          shared — reads handoffs + history; writes both
        """
        logger.info(f"[BRAIN] {role} is thinking about: {task_description} "
                    f"(memory_mode={memory_mode}, conversation_id={conversation_id})")

        # ------------------------------------------------------------------
        # 1. Recall long-term context (existing RAG / file fallback)
        # ------------------------------------------------------------------
        rag_context = ""
        if use_memory:
            logger.info("[BRAIN] Accessing Long-Term Memory...")
            rag_context = await self.recall_context(query=task_description)

        # ------------------------------------------------------------------
        # 2. Build injected memory block (new Phase 1 — fails closed)
        # ------------------------------------------------------------------
        memory_block = self._build_memory_context(
            conversation_id=conversation_id,
            agent_id=agent_id,
            memory_mode=memory_mode,
            rag_context=rag_context,
        )

        # ------------------------------------------------------------------
        # 3. Compose final prompt
        # ------------------------------------------------------------------
        if memory_block:
            full_prompt = f"Context:\n{memory_block}\n\nTask: {task_description}"
        else:
            full_prompt = task_description

        # ------------------------------------------------------------------
        # 4. Persist the user turn BEFORE we call the LLM
        #    (so history is consistent even if LLM errors)
        # ------------------------------------------------------------------
        if memory_mode != "none" and conversation_id:
            try:
                from app.core.agent_memory import append_turn
                append_turn(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    role="user",
                    content=task_description,
                )
            except Exception as exc:
                logger.warning(f"[BRAIN] Failed to persist user turn: {exc}")

        # ------------------------------------------------------------------
        # 5. LLM routing (unchanged from original)
        # ------------------------------------------------------------------
        result = await self._route_llm(role=role, prompt=full_prompt, route_context=route_context)

        # ------------------------------------------------------------------
        # 6. Persist assistant response turn
        # ------------------------------------------------------------------
        if memory_mode != "none" and conversation_id:
            try:
                from app.core.agent_memory import append_turn
                append_turn(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    role="assistant",
                    content=result,
                )
            except Exception as exc:
                logger.warning(f"[BRAIN] Failed to persist assistant turn: {exc}")

        return result

    # ------------------------------------------------------------------
    # LLM routing — extracted so think() stays readable
    # ------------------------------------------------------------------

    async def _route_llm(
        self,
        role: str,
        prompt: str,
        route_context: dict | None = None,
    ) -> str:
        """Try Ollama → Perplexity Session → OpenRouter → Perplexity API."""

        # 1. Local LLM (Ollama)
        if settings.OLLAMA_HOST:
            try:
                system_prompt = (
                    f"You are a {role}.\n"
                    "Always respond in two phases:\n"
                    "1) TL;DR (1-3 lines)\n"
                    "2) Details (headings + bullets)\n"
                    "Break work into micro-tasks and propose the next single step.\n\n"
                    f"Task:\n{prompt}"
                )
                async with httpx.AsyncClient(timeout=120.0) as client:
                    model = settings.DEFAULT_LLM_MODEL
                    if model.strip().lower() == "auto":
                        resolved = await self._ollama_model_resolver.resolve(client)
                        if resolved:
                            model = resolved
                    logger.info(f"[BRAIN] Routing to Local LLM (Ollama: {model})...")
                    response = await client.post(
                        f"{settings.OLLAMA_HOST}/api/generate",
                        json={
                            "model": model,
                            "prompt": system_prompt,
                            "stream": False,
                            "options": settings.ollama_generate_options(),
                        }
                    )
                    if response.status_code == 200:
                        return response.json()["response"]
                    logger.warning(f"[BRAIN] Local LLM failed ({response.status_code}), falling back...")
            except Exception as e:
                logger.warning(f"[BRAIN] Local LLM error: {e}. Falling back...")

        # 2. Perplexity Session Auth (Comet/Spaces)
        if settings.PERPLEXITY_SESSION_AUTH:
            logger.info("[BRAIN] Using Perplexity Session Auth (Simulated)...")
            return "Perplexity Session Auth is active. (Simulated Response)"

        # 3. OpenRouter fallback
        if route_context is not None and settings.OPENROUTER_API_KEY:
            try:
                ctx = ModelRouteContext(**route_context)
            except TypeError:
                ctx = ModelRouteContext(kind=str(route_context.get("kind", "general")))
            route = select_model_route(ctx, settings)
            if route is not None:
                try:
                    return await openrouter_chat(
                        base_url=route.base_url,
                        api_key=settings.OPENROUTER_API_KEY,
                        model=route.model,
                        max_tokens=route.max_tokens,
                        privacy_mode=route.privacy_mode,
                        messages=[
                            {"role": "system", "content": f"You are a {role}."},
                            {"role": "user", "content": prompt},
                        ],
                    )
                except Exception as e:
                    logger.warning(f"[BRAIN] OpenRouter route {route.name} failed: {e}. Falling back...")

        # 4. Perplexity API (paid fallback)
        if not self.api_key:
            return "Error: No valid LLM provider available (Local, Session, OpenRouter, or API Key)."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a {role}. Provide a detailed, step-by-step plan or code solution.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if response.status_code != 200:
                    logger.error(f"[BRAIN] Perplexity API Error: {response.text}")
                    return f"Error: API returned {response.status_code} - {response.text}"
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[BRAIN] Error thinking: {e}")
            return f"Error: {str(e)}"


# Global instance
brain = Brain()
