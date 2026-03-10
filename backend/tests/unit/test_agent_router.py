import pytest


@pytest.mark.asyncio
async def test_router_routes_research_by_type(monkeypatch):
    import app.agents.router as router_mod
    from app.agents.router import AgentRouter

    called: dict = {}

    class Researcher:
        async def process(self, payload: str, context: dict | None = None) -> str:
            called["payload"] = payload
            called["context"] = context
            return "research-ok"

    monkeypatch.setattr(router_mod, "researcher", Researcher())

    router = AgentRouter()
    router.routes["research"] = router_mod.researcher

    result = await router.route_task("research", "topic", context={"task_id": "t1"})
    assert result == "research-ok"
    assert called["payload"] == "topic"
    assert called["context"] == {"task_id": "t1"}


@pytest.mark.asyncio
async def test_router_keyword_detection_defaults_to_research(monkeypatch):
    import app.agents.router as router_mod
    from app.agents.router import AgentRouter

    class Researcher:
        async def process(self, payload: str, context: dict | None = None) -> str:
            return "research-ok"

    monkeypatch.setattr(router_mod, "researcher", Researcher())

    router = AgentRouter()
    router.routes["research"] = router_mod.researcher
    router.routes["general"] = None

    result = await router.route_task("general", "please research this", context={"task_id": "t1"})
    assert result == "research-ok"


@pytest.mark.asyncio
async def test_router_falls_back_to_brain_when_no_match(monkeypatch):
    import app.agents.router as router_mod
    from app.agents.router import AgentRouter

    captured: dict = {}

    class Brain:
        async def think(self, role: str, payload: str, use_memory: bool = False) -> str:
            captured["role"] = role
            captured["payload"] = payload
            captured["use_memory"] = use_memory
            return "brain-ok"

    monkeypatch.setattr(router_mod, "brain", Brain())
    router = AgentRouter()

    result = await router.route_task("general", "do something else", context={"task_id": "t1"})
    assert result == "brain-ok"
    assert captured["use_memory"] is True
