"""
Strands Agent - 특정 도메인 작업을 수행하는 에이전트
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent

class StrandsAgent(BaseAgent):
    def __init__(self, name: str, description: str, specialty: str):
        super().__init__(name, description)
        self.specialty = specialty
        self.conversation_history = []
    
    def process(self, input_data: str) -> str:
        """Process input using specialized knowledge"""
        # 전문 분야에 맞는 프롬프트 구성
        specialized_prompt = self._create_specialized_prompt(input_data)
        
        # Bedrock 모델 호출
        response = self.invoke_bedrock_model(specialized_prompt)
        
        # 대화 기록 저장
        self.conversation_history.append({
            "input": input_data,
            "output": response
        })
        
        return response
    
    def _create_specialized_prompt(self, input_data: str) -> str:
        """Create specialized prompt based on agent's specialty"""
        base_prompt = f"""
당신은 {self.specialty} 전문가입니다.
다음 요청에 대해 전문적이고 정확한 답변을 제공해주세요.

전문 분야: {self.specialty}
에이전트 설명: {self.description}

사용자 요청: {input_data}

답변:
"""
        return base_prompt
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_specialty_info(self) -> Dict[str, str]:
        """Get specialty information"""
        info = self.get_info()
        info["specialty"] = self.specialty
        return info
