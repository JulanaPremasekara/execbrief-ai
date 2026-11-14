import asyncio

class LiveChat:
    """Own resources until blocking initialization/work completes, even on cancellation."""
    stream_mode="validated_blocks"
    def __init__(self,factory):
        self.factory=factory

    async def execute(self,question,history):
        yield "status",dict(stage="connecting",message="Connecting to evidence sources",stream_mode=self.stream_mode)
        task=asyncio.create_task(asyncio.to_thread(self.factory))
        engine=None
        try:
            try:
                engine,use_case=await asyncio.shield(task)
            except asyncio.CancelledError:
                # The worker cannot be killed; dispose its result when it finishes.
                def cleanup(completed):
                    if not completed.cancelled() and completed.exception() is None:
                        completed.result()[0].dispose()
                task.add_done_callback(cleanup)
                raise
            iterator=use_case.execute(question,history)
            try:
                async for event in iterator:
                    yield event
            finally:
                await iterator.aclose()
        finally:
            if engine is not None:
                engine.dispose()

