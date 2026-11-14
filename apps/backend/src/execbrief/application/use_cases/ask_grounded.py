import asyncio
from execbrief.application.services.query_planner import QueryPlanner
from execbrief.application.services.response_planner import ResponsePlanner
from execbrief.domain.interfaces.llm_provider import LLMProvider
from execbrief.domain.interfaces.analytics_provider import AnalyticsProvider
from execbrief.domain.interfaces.document_retriever import DocumentRetriever

class AskGroundedUseCase:
    stream_mode="validated_blocks"
    def __init__(self,llm: LLMProvider,analytics: AnalyticsProvider,retriever: DocumentRetriever):
        self.llm,self.analytics,self.retriever=llm,analytics,retriever

    async def execute(self,question,history):
        yield "status",dict(stage="planning",message="Planning evidence and analytics",stream_mode=self.stream_mode)
        plan=await QueryPlanner(self.llm).plan(question,history)
        datasets={}
        sources={}
        for operation in plan["operations"]:
            dataset=await asyncio.to_thread(self.analytics.calculate,operation,plan["start"],plan["end"])
            datasets[operation]=dataset
            for index,row in enumerate(dataset["rows"]):
                source_id=f"{operation}:{index}"
                sources[source_id]={"id":source_id,"filename":f"Verified {operation} analytics",
                    "content":operation+": "+", ".join(f"{key}={value}" for key,value in row.items())}
        yield "status",dict(stage="retrieving",message="Retrieving supporting evidence",stream_mode=self.stream_mode)
        documents=await asyncio.to_thread(self.retriever.retrieve,question) if plan["retrieve"] else []
        for index,document in enumerate(documents):
            source_id=f"evidence:{index}"
            sources[source_id]={"id":source_id,"filename":document.metadata.get("filename","Document"),
                "page":document.metadata.get("page"),"row":document.metadata.get("row"),"content":document.content}
        if not sources:
            blocks=[]
            from execbrief.domain.entities.response_block import Block
            blocks=[Block("b1","text","Insufficient evidence is available for this question.")]
        else:
            yield "status",dict(stage="generating",message="Validating the executive briefing",stream_mode=self.stream_mode)
            response=await self.llm.generate("response",{"question":question,"datasets":datasets,"evidence":sources})
            blocks=ResponsePlanner().resolve(response,datasets,sources)
        references=[{k:v for k,v in s.items() if k!="content"} for s in sources.values()]
        for position,block in enumerate(blocks):
            yield "block_start",dict(block_id=block.id,block_type=block.type,position=position)
            if block.type=="text":
                yield "text_delta",dict(block_id=block.id,delta=block.content)
            else:
                yield "chart",dict(block_id=block.id,spec=block.spec,dataset=block.dataset)
            yield "block_end",dict(block_id=block.id,sources=references)
        yield "done",dict(outcome="completed",sources=references,stream_mode=self.stream_mode)

