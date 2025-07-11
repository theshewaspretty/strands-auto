# Strands Agents 완전 매뉴얼

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 구조](#시스템-구조)
3. [설치 및 설정](#설치-및-설정)
4. [코드 상세 분석](#코드-상세-분석)
5. [실행 방법](#실행-방법)
6. [문제 해결](#문제-해결)

---

## 프로젝트 개요

Strands Agents는 AWS Bedrock Claude 3를 활용한 멀티 에이전트 시스템입니다. 여러 AI 에이전트가 협력하여 다양한 작업을 수행할 수 있는 웹 기반 애플리케이션입니다.

### 주요 기능
- **다중 AI 에이전트**: 각각 다른 전문 분야를 담당
- **메타 에이전트**: 다른 에이전트들을 관리하고 조율
- **웹 인터페이스**: Streamlit을 통한 사용자 친화적 UI
- **AWS Bedrock 통합**: Claude 3 Haiku 모델 사용

---

## 시스템 구조

```
strands-auto/
├── app.py                     # 메인 Streamlit 애플리케이션
├── requirements.txt           # Python 의존성 패키지 목록
├── run.sh                    # 실행 스크립트
├── test_model.py             # 모델 테스트 스크립트
├── manual.md                 # 이 매뉴얼 파일
├── README.md                 # 프로젝트 설명서
├── .env.example              # 환경변수 예시 파일
└── strands-agents/           # 에이전트 시스템 코어
    ├── __init__.py
    ├── config/               # 설정 파일들
    │   └── aws_config.py     # AWS 설정
    ├── agents/               # 에이전트 클래스들
    │   ├── __init__.py
    │   ├── base_agent.py     # 기본 에이전트 클래스
    │   ├── strands_agent.py  # Strands 전용 에이전트
    │   └── meta_agent.py     # 메타 에이전트
    └── utils/                # 유틸리티 함수들
```

---

## 설치 및 설정

### 1. 의존성 설치

```bash
# Python 패키지 설치
pip install -r requirements.txt
```

**requirements.txt 파일 내용:**
```
streamlit>=1.28.0      # 웹 애플리케이션 프레임워크
boto3>=1.34.72         # AWS SDK for Python
langchain>=0.1.0       # LangChain 프레임워크
langchain-aws>=0.1.0   # LangChain AWS 통합
python-dotenv>=1.0.0   # 환경변수 관리
pydantic>=2.0.0        # 데이터 검증
typing-extensions>=4.8.0  # 타입 힌트 확장
```

### 2. AWS 자격 증명 설정

```bash
# AWS CLI 설정 (권장)
aws configure

# 또는 환경변수 설정
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

---

## 코드 상세 분석

### 1. AWS 설정 파일 (strands-agents/config/aws_config.py)

```python
"""
AWS Configuration for Strands Agents
"""
import boto3
from typing import Dict, Any

class AWSConfig:
    def __init__(self):
        # AWS 리전 설정 - 서울 리전 사용
        self.region = "ap-northeast-2"
        
        # Claude 3 Haiku 모델 ID (테스트를 통해 작동 확인됨)
        self.bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        # 클라이언트 인스턴스 초기화
        self.bedrock_runtime_client = None
        self.bedrock_agent_client = None
```

**코드 설명:**
- `self.region`: AWS 서비스를 사용할 리전 지정
- `self.bedrock_model_id`: 사용할 AI 모델의 고유 식별자
- 클라이언트 변수들: 나중에 필요할 때 생성되는 지연 초기화 방식

```python
    def get_bedrock_runtime_client(self):
        """Bedrock Runtime 클라이언트 반환 (지연 초기화)"""
        if not self.bedrock_runtime_client:
            self.bedrock_runtime_client = boto3.client(
                'bedrock-runtime',    # AWS Bedrock Runtime 서비스
                region_name=self.region
            )
        return self.bedrock_runtime_client
```

**호출 방법:**
```python
from config.aws_config import aws_config
client = aws_config.get_bedrock_runtime_client()
```

### 2. 기본 에이전트 클래스 (strands-agents/agents/base_agent.py)

```python
"""
Base Agent class for Strands Agents
"""
import json
import boto3
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from config.aws_config import aws_config

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name                    # 에이전트 이름
        self.description = description      # 에이전트 설명
        # AWS 클라이언트 초기화
        self.bedrock_client = aws_config.get_bedrock_runtime_client()
        self.model_config = aws_config.get_model_config()
        self.current_model_id = self.model_config["modelId"]
```

**코드 설명:**
- `ABC`: Abstract Base Class - 추상 클래스 생성
- `@abstractmethod`: 하위 클래스에서 반드시 구현해야 하는 메서드 표시
- `self.bedrock_client`: AWS Bedrock 서비스와 통신하는 클라이언트

```python
    def invoke_bedrock_model(self, prompt: str, max_tokens: int = 1000) -> str:
        """Bedrock 모델 호출 (여러 모델 시도)"""
        
        # 시도할 모델 목록 (우선순위 순)
        models_to_try = [self.current_model_id] + aws_config.try_alternative_models()
        
        for model_id in models_to_try:
            try:
                # Claude 모델용 요청 본문 구성
                body = {
                    "anthropic_version": "bedrock-2023-05-31",  # API 버전
                    "max_tokens": max_tokens,                   # 최대 응답 토큰 수
                    "messages": [
                        {
                            "role": "user",      # 사용자 역할
                            "content": prompt    # 실제 질문/요청
                        }
                    ]
                }
                
                # AWS Bedrock 모델 호출
                response = self.bedrock_client.invoke_model(
                    modelId=model_id,                           # 모델 ID
                    contentType=self.model_config["contentType"], # 요청 타입
                    accept=self.model_config["accept"],         # 응답 타입
                    body=json.dumps(body)                       # JSON 문자열로 변환
                )
                
                # 응답 파싱
                response_body = json.loads(response['body'].read())
                
                # 모델 변경 시 알림
                if model_id != self.current_model_id:
                    self.current_model_id = model_id
                    print(f"Successfully switched to model: {model_id}")
                
                # 응답 텍스트 반환
                return response_body['content'][0]['text']
                
            except Exception as e:
                error_msg = str(e)
                print(f"Failed to invoke model {model_id}: {error_msg}")
                
                # 마지막 모델까지 실패하면 에러 반환
                if model_id == models_to_try[-1]:
                    return f"Error: All models failed. Last error: {error_msg}"
                
                # 다음 모델 시도
                continue
        
        return "Error: No models available"
```

**호출 방법:**
```python
# 에이전트 생성 (추상 클래스이므로 직접 생성 불가)
class MyAgent(BaseAgent):
    def process(self, input_data: str) -> str:
        return self.invoke_bedrock_model(input_data)

agent = MyAgent("테스트", "테스트 에이전트")
response = agent.invoke_bedrock_model("안녕하세요!")
```

### 3. Strands 에이전트 (strands-agents/agents/strands_agent.py)

```python
"""
Strands Agent - 특정 도메인에 특화된 에이전트
"""
from .base_agent import BaseAgent

class StrandsAgent(BaseAgent):
    def __init__(self, name: str, description: str, specialty: str):
        super().__init__(name, description)  # 부모 클래스 초기화
        self.specialty = specialty           # 전문 분야
        
        # 전문 분야별 시스템 프롬프트 설정
        self.system_prompt = f"""
당신은 {specialty} 전문가입니다.
다음 지침을 따라 답변해주세요:
1. 전문적이고 정확한 정보 제공
2. 실용적인 조언과 해결책 제시
3. 필요시 단계별 설명 포함
4. 한국어로 친근하게 답변
"""
```

**코드 설명:**
- `super().__init__()`: 부모 클래스의 초기화 메서드 호출
- `self.specialty`: 에이전트의 전문 분야 저장
- `self.system_prompt`: AI 모델에게 역할을 지정하는 시스템 메시지

```python
    def process(self, input_data: str) -> str:
        """입력 데이터 처리 및 응답 생성"""
        # 시스템 프롬프트와 사용자 입력 결합
        full_prompt = f"{self.system_prompt}\n\n사용자 질문: {input_data}"
        
        # 부모 클래스의 모델 호출 메서드 사용
        return self.invoke_bedrock_model(full_prompt)
```

**호출 방법:**
```python
from agents.strands_agent import StrandsAgent

# 코딩 전문가 에이전트 생성
coding_agent = StrandsAgent(
    name="코딩 전문가",
    description="프로그래밍 및 소프트웨어 개발 전문",
    specialty="프로그래밍"
)

# 질문 처리
response = coding_agent.process("Python에서 리스트를 정렬하는 방법은?")
print(response)
```

### 4. 메타 에이전트 (strands-agents/agents/meta_agent.py)

```python
"""
Meta Agent - 다른 에이전트들을 관리하고 조율하는 에이전트
"""
from typing import Dict, List, Any
from .base_agent import BaseAgent

class MetaAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Meta Agent",
            description="다른 에이전트들을 관리하고 조율하는 메타 에이전트"
        )
        self.agents: Dict[str, BaseAgent] = {}  # 관리하는 에이전트들
        self.conversation_history: List[Dict] = []  # 대화 기록
```

**코드 설명:**
- `self.agents`: 딕셔너리 형태로 에이전트들을 저장 (이름: 에이전트 객체)
- `self.conversation_history`: 대화 기록을 리스트로 저장

```python
    def add_agent(self, agent: BaseAgent) -> bool:
        """새로운 에이전트 추가"""
        try:
            if agent.name not in self.agents:
                self.agents[agent.name] = agent
                return True
            return False  # 이미 존재하는 에이전트
        except Exception as e:
            print(f"Error adding agent: {str(e)}")
            return False
```

**호출 방법:**
```python
from agents.meta_agent import MetaAgent
from agents.strands_agent import StrandsAgent

# 메타 에이전트 생성
meta = MetaAgent()

# 전문 에이전트들 생성 및 추가
coding_agent = StrandsAgent("코딩 전문가", "프로그래밍 전문", "프로그래밍")
data_agent = StrandsAgent("데이터 분석가", "데이터 분석 전문", "데이터 분석")

meta.add_agent(coding_agent)
meta.add_agent(data_agent)

# 에이전트 목록 확인
agents = meta.list_agents()
print(agents)
```

### 5. 메인 애플리케이션 (app.py)

```python
import streamlit as st
import sys
import os

# 프로젝트 경로를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'strands-agents'))

from agents.meta_agent import MetaAgent
from agents.strands_agent import StrandsAgent

# Streamlit 페이지 설정
st.set_page_config(
    page_title="Strands Agents",      # 브라우저 탭 제목
    page_icon="🤖",                   # 브라우저 탭 아이콘
    layout="wide",                    # 와이드 레이아웃 사용
    initial_sidebar_state="expanded"   # 사이드바 기본 확장
)
```

**코드 설명:**
- `sys.path.append()`: Python이 모듈을 찾을 수 있도록 경로 추가
- `st.set_page_config()`: Streamlit 페이지의 기본 설정

```python
# 세션 상태 초기화
if 'meta_agent' not in st.session_state:
    st.session_state.meta_agent = MetaAgent()
    
    # 기본 에이전트들 추가
    default_agents = [
        StrandsAgent("코딩 전문가", "프로그래밍 및 소프트웨어 개발", "프로그래밍"),
        StrandsAgent("데이터 분석가", "데이터 분석 및 머신러닝", "데이터 분석"),
        StrandsAgent("AWS 전문가", "AWS 클라우드 서비스", "AWS")
    ]
    
    for agent in default_agents:
        st.session_state.meta_agent.add_agent(agent)

if 'messages' not in st.session_state:
    st.session_state.messages = []
```

**코드 설명:**
- `st.session_state`: Streamlit에서 상태를 유지하는 방법
- 페이지 새로고침 시에도 데이터가 유지됨
- 메타 에이전트와 메시지 기록을 세션에 저장

```python
# 메인 인터페이스
st.title("🤖 Strands Agents")
st.markdown("AWS Bedrock Claude 3를 활용한 멀티 에이전트 시스템")

# 사이드바 - 에이전트 관리
with st.sidebar:
    st.header("🔧 에이전트 관리")
    
    # 현재 에이전트 목록 표시
    agents = st.session_state.meta_agent.list_agents()
    if agents:
        st.subheader("활성 에이전트")
        for agent_name, agent_info in agents.items():
            with st.expander(f"📋 {agent_name}"):
                st.write(f"**설명:** {agent_info['description']}")
                if 'current_model' in agent_info:
                    st.write(f"**모델:** {agent_info['current_model']}")
```

**코드 설명:**
- `st.title()`: 페이지 제목 표시
- `st.sidebar`: 사이드바 영역 생성
- `st.expander()`: 접을 수 있는 섹션 생성

### 6. 테스트 스크립트 (test_model.py)

```python
#!/usr/bin/env python3
"""
Test script to verify Bedrock model invocation
"""
import sys
import os

# 프로젝트 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'strands-agents'))

from agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__("TestAgent", "Agent for testing model invocation")
    
    def process(self, input_data: str) -> str:
        return self.invoke_bedrock_model(input_data)

def main():
    print("Testing Bedrock model invocation...")
    
    try:
        agent = TestAgent()
        print(f"Agent info: {agent.get_info()}")
        
        # 간단한 테스트 프롬프트
        test_prompt = "Hello! Please respond with a simple greeting."
        print(f"\nSending test prompt: {test_prompt}")
        
        response = agent.process(test_prompt)
        print(f"\nModel response: {response}")
        
        if response.startswith("Error"):
            print("\n❌ Model invocation failed!")
            return 1
        else:
            print("\n✅ Model invocation successful!")
            return 0
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
```

**호출 방법:**
```bash
cd /home/ubuntu/strands-auto
python test_model.py
```

---

## 실행 방법

### 1. 기본 실행

```bash
# 프로젝트 디렉토리로 이동
cd /home/ubuntu/strands-auto

# Streamlit 애플리케이션 실행
streamlit run app.py
```

### 2. 스크립트를 통한 실행

```bash
# 실행 권한 부여
chmod +x run.sh

# 스크립트 실행
./run.sh
```

**run.sh 내용:**
```bash
#!/bin/bash
echo "Starting Strands Agents application..."
streamlit run app.py
```

### 3. 백그라운드 실행

```bash
# 백그라운드에서 실행
nohup streamlit run app.py &

# 프로세스 확인
ps aux | grep streamlit

# 종료
pkill -f streamlit
```

### 4. 포트 지정 실행

```bash
# 특정 포트에서 실행
streamlit run app.py --server.port 8502

# 헤드리스 모드 (브라우저 자동 열기 안함)
streamlit run app.py --server.headless true
```

---

## 문제 해결

### 1. 의존성 오류

**문제:** `ModuleNotFoundError` 또는 패키지 충돌

**해결방법:**
```bash
# 가상환경 생성 (권장)
python -m venv strands-env
source strands-env/bin/activate  # Linux/Mac
# 또는
strands-env\Scripts\activate     # Windows

# 의존성 재설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. AWS 인증 오류

**문제:** `NoCredentialsError` 또는 `AccessDenied`

**해결방법:**
```bash
# AWS 자격 증명 확인
aws sts get-caller-identity

# 자격 증명 재설정
aws configure

# 환경변수 설정 확인
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION
```

### 3. 모델 호출 오류

**문제:** `ValidationException` 또는 모델 접근 불가

**해결방법:**
```bash
# 테스트 스크립트 실행
python test_model.py

# AWS Bedrock 서비스 활성화 확인
# AWS 콘솔 > Bedrock > Model access 에서 모델 활성화
```

### 4. 포트 충돌

**문제:** `Port 8501 is already in use`

**해결방법:**
```bash
# 사용 중인 프로세스 확인
lsof -ti:8501

# 프로세스 종료
sudo kill -9 $(lsof -ti:8501)

# 다른 포트 사용
streamlit run app.py --server.port 8502
```

### 5. 메모리 부족

**문제:** 애플리케이션이 느리거나 멈춤

**해결방법:**
```bash
# 메모리 사용량 확인
free -h
top

# 불필요한 프로세스 종료
# 가상환경 사용으로 메모리 절약
```

---

## 추가 개발 가이드

### 1. 새로운 에이전트 추가

```python
# 새 에이전트 클래스 생성
class CustomAgent(BaseAgent):
    def __init__(self, specialty: str):
        super().__init__(
            name=f"{specialty} 전문가",
            description=f"{specialty} 분야 전문 에이전트"
        )
        self.specialty = specialty
    
    def process(self, input_data: str) -> str:
        prompt = f"당신은 {self.specialty} 전문가입니다. {input_data}"
        return self.invoke_bedrock_model(prompt)

# 사용 방법
custom_agent = CustomAgent("마케팅")
response = custom_agent.process("효과적인 마케팅 전략은?")
```

### 2. 설정 커스터마이징

```python
# aws_config.py 수정
class AWSConfig:
    def __init__(self, custom_region=None, custom_model=None):
        self.region = custom_region or "ap-northeast-2"
        self.bedrock_model_id = custom_model or "anthropic.claude-3-haiku-20240307-v1:0"
```

### 3. 로깅 추가

```python
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strands_agents.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 에이전트에서 사용
def invoke_bedrock_model(self, prompt: str, max_tokens: int = 1000) -> str:
    logger.info(f"Invoking model with prompt: {prompt[:50]}...")
    # ... 기존 코드
```

---

## 마무리

이 매뉴얼을 통해 Strands Agents 시스템의 전체 구조와 각 코드의 역할을 이해할 수 있습니다. 

**학습 순서 권장:**
1. AWS 설정 이해
2. BaseAgent 클래스 구조 파악
3. 구체적인 에이전트 구현 방법 학습
4. Streamlit 인터페이스 구조 이해
5. 실제 실행 및 테스트

**다음 단계:**
- 새로운 전문 분야 에이전트 추가
- 대화 기록 저장 기능 구현
- 에이전트 간 협업 기능 개발
- 성능 모니터링 및 로깅 시스템 구축

문제가 발생하면 테스트 스크립트(`test_model.py`)를 먼저 실행하여 기본 기능이 작동하는지 확인하세요.
