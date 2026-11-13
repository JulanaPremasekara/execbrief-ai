from execbrief.domain.interfaces.response_provider import ResponseProvider

class AskExecutiveUseCase:
    def __init__(self, provider: ResponseProvider):
        self.provider = provider

    async def execute(self, question: str, history: list[dict]):
        sources = [{"id": "mock", "filename": "Fictional Phase 1 business fixtures"}]
        yield "status", dict(stage="preparing", message="Preparing fictional demonstration", stream_mode="mock")
        for position, block in enumerate(self.provider.respond(question, history)):
            yield "block_start", dict(block_id=block.id, block_type=block.type, position=position)
            if block.type == "text":
                for offset in range(0, len(block.content), 32):
                    yield "text_delta", dict(block_id=block.id, delta=block.content[offset:offset+32])
            else:
                yield "chart", dict(block_id=block.id, spec=block.spec, dataset=block.dataset)
            yield "block_end", dict(block_id=block.id, sources=sources)
        yield "done", dict(outcome="completed", sources=sources, stream_mode="mock")

