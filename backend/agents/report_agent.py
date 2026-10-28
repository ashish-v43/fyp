from agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):

    async def run(
        self,
        analysis: dict,
        tasks: dict,
        insights: dict,
        security: dict
    ):

        priority_actions = []

        for task in tasks.get("tasks", []):

            task_name = task.get(
                "task",
                ""
            )

            owner = task.get(
                "owner",
                ""
            )

            deadline = task.get(
                "deadline",
                ""
            )

            action = task_name

            if owner:
                action += f" (Owner: {owner})"

            if deadline:
                action += f" - Due: {deadline}"

            priority_actions.append(
                action
            )

        top_risks = []

        for risk in analysis.get(
            "risks",
            []
        ):

            if isinstance(
                risk,
                dict
            ):

                top_risks.append(
                    risk.get(
                        "risk",
                        str(risk)
                    )
                )

            else:

                top_risks.append(
                    str(risk)
                )

        key_insights = []

        for insight in insights.get(
            "productivity_insights",
            []
        ):

            if isinstance(
                insight,
                dict
            ):

                key_insights.append(
                    insight.get(
                        "insight",
                        str(insight)
                    )
                )

            else:

                key_insights.append(
                    str(insight)
                )

        # ----------------------------
        # BUSINESS IMPACT GENERATION
        # ----------------------------

        total_tasks = len(
            tasks.get("tasks", [])
        )

        total_risks = len(
            top_risks
        )

        total_insights = len(
            key_insights
        )

        business_impact = (
            f"This meeting generated "
            f"{total_tasks} actionable tasks, "
            f"{total_risks} identified risks, and "
            f"{total_insights} productivity insights. "
            f"Early visibility into delivery risks and "
            f"responsibilities can improve execution, "
            f"reduce project delays, and strengthen "
            f"cross-team collaboration."
        )

        return {

            "executive_summary":
                analysis.get(
                    "summary",
                    ""
                ),

            "business_impact":
                business_impact,

            "priority_actions":
                priority_actions,

            "top_risks":
                top_risks,

            "key_insights":
                key_insights,

            "security_score":
                security.get(
                    "security_score",
                    0
                )
        }