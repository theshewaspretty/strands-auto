"""
Meta Agent - 다른 에이전트들을 관리하고 조율하는 에이전트
"""
import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .strands_agent import StrandsAgent

class MetaAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Meta Agent",
            description="다른 에이전트들을 관리하고 조율하는 메타 에이전트"
        )
        self.agents: Dict[str, StrandsAgent] = {}
        self.task_history = []
    
    def add_agent(self, agent: StrandsAgent):
        """Add a new agent to the meta agent"""
        self.agents[agent.name] = agent
    
    def remove_agent(self, agent_name: str):
        """Remove an agent from the meta agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents"""
        return [agent.get_specialty_info() for agent in self.agents.values()]
    
    def process(self, input_data: str) -> str:
        """Process input by routing to appropriate agent or handling directly"""
        # 적절한 에이전트 선택
        selected_agent = self._select_agent(input_data)
        
        if selected_agent:
            # 선택된 에이전트로 작업 위임
            response = selected_agent.process(input_data)
            result = f"[{selected_agent.name}] {response}"
        else:
            # 메타 에이전트가 직접 처리
            result = self._handle_meta_task(input_data)
        
        # 작업 기록 저장
        self.task_history.append({
            "input": input_data,
            "selected_agent": selected_agent.name if selected_agent else "Meta Agent",
            "output": result
        })
        
        return result
    
    def _select_agent(self, input_data: str) -> Optional[StrandsAgent]:
        """Select the most appropriate agent for the task"""
        if not self.agents:
            return None
        
        # 에이전트 선택을 위한 프롬프트
        agent_info = "\n".join([
            f"- {name}: {agent.specialty} ({agent.description})"
            for name, agent in self.agents.items()
        ])
        
        selection_prompt = f"""
다음 에이전트들 중에서 주어진 작업에 가장 적합한 에이전트를 선택해주세요.

사용 가능한 에이전트들:
{agent_info}

작업 요청: {input_data}

가장 적합한 에이전트의 이름만 답변해주세요. 만약 어떤 에이전트도 적합하지 않다면 "NONE"이라고 답변해주세요.
"""
        
        try:
            response = self.invoke_bedrock_model(selection_prompt, max_tokens=100)
            selected_name = response.strip()
            
            if selected_name in self.agents:
                return self.agents[selected_name]
            else:
                return None
        except:
            # 에러 발생 시 첫 번째 에이전트 반환
            return list(self.agents.values())[0] if self.agents else None
    
    def _handle_meta_task(self, input_data: str) -> str:
        """Handle tasks that don't require specific agents"""
        meta_prompt = f"""
당신은 메타 에이전트입니다. 다른 전문 에이전트들을 관리하고 조율하는 역할을 합니다.
현재 다음과 같은 에이전트들을 관리하고 있습니다:

{self._get_agents_summary()}

사용자 요청: {input_data}

이 요청에 대해 적절한 답변을 제공하거나, 필요한 경우 어떤 전문 에이전트가 필요한지 안내해주세요.
"""
        
        return self.invoke_bedrock_model(meta_prompt)
    
    def _get_agents_summary(self) -> str:
        """Get summary of all agents"""
        if not self.agents:
            return "현재 관리 중인 에이전트가 없습니다."
        
        return "\n".join([
            f"- {name}: {agent.specialty}"
            for name, agent in self.agents.items()
        ])
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task history"""
        return self.task_history
    
    def clear_task_history(self):
        """Clear task history"""
        self.task_history = []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "total_agents": len(self.agents),
            "agents": self.list_agents(),
            "total_tasks": len(self.task_history)
        }
