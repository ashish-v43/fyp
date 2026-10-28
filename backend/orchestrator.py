from agents.planner_agent import PlannerAgent
from agents.security_agent import SecurityAgent
from agents.analyst_agent import AnalystAgent
from agents.retrieval_agent import RetrievalAgent
from agents.task_agent import TaskAgent
from agents.insight_agent import InsightAgent
from agents.report_agent import ReportAgent

import asyncio

import time

class AgentOrchestrator:

    def __init__(self):

        self.planner = PlannerAgent()

        self.security = SecurityAgent()

        self.analyst = AnalystAgent()

        self.retrieval = RetrievalAgent()

        self.task = TaskAgent()

        self.insight = InsightAgent()

        self.report = ReportAgent()

    async def execute(
    self,
    text: str
):
        
        start = time.time()

        
        # -----------------------------------
# Run Independent Agents in Parallel
# -----------------------------------

        (
            planner_result,
            security_result,
            retrieval_result,
            task_result
        ) = await asyncio.gather(

            self.planner.run(
                text
            ),

            self.security.run(
                text
            ),

            self.retrieval.run(
                text
            ),

            self.task.run(
                text
            )
        )

        # -----------------------------------
        # Build Context for Analyst
        # -----------------------------------

        context = "\n\n".join(
            [
                doc["content"]
                for doc in retrieval_result
            ]
        )

        # -----------------------------------
        # Analyst depends on Retrieval
        # -----------------------------------

        analysis_result = await self.analyst.run(
            text,
            context
        )

        # -----------------------------------
        # Insight depends on Analysis + Tasks
        # -----------------------------------

        insight_result = await self.insight.run(
            text,
            analysis_result,
            task_result
        )

        # -----------------------------------
        # Report depends on everything
        # -----------------------------------

        report_result = await self.report.run(
            analysis_result,
            task_result,
            insight_result,
            security_result
        )


                # -----------------------------------
        # AGENT TRACEABILITY DATA
        # -----------------------------------

        agent_trace = {

            "planner": {
                "tasks_found": len(
                    task_result.get(
                        "tasks",
                        []
                    )
                )
            },


            "retrieval": {
                "sources_used": [
                   doc.get(
                        "document",
                        "Knowledge Base"
                    )
                    for doc in retrieval_result
             ]
        },

            "analyst": {
                "decisions": len(
                    analysis_result.get(
                        "key_decisions",
                        []
                    )
                ),

                "risks": len(
                    analysis_result.get(
                        "risks",
                        []
                    )
                ),

                "recommendations": len(
                    analysis_result.get(
                        "recommendations",
                        []
                    )
                )
            },

            "insight": {
                "insights": len(
                    insight_result.get(
                        "productivity_insights",
                        []
                    )
                )
            },

            "report": {
                "generated": True
            }
        }

        result = {

            "planner": planner_result,

            "security": security_result,

            "retrieval": retrieval_result,

            "analysis": analysis_result,

            "tasks": task_result,

            "insights": insight_result,

            "report": report_result,

            "agent_trace": agent_trace
        }

        print(result)

        print(
    f"Total execution time: "
    f"{time.time() - start:.2f} seconds"
)
        return result
