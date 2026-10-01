"""
Hermes Agent Wrapper (Forwarding to AgentRouter)
"""

from tools.agent_router import AgentRouter

class HermesAgent(AgentRouter):
    def process_query(self, user_query: str, honcho_context: str = ""):
        return self.route_query(user_query, honcho_context)
