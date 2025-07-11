# Strands Agents 코드 리뷰 및 매뉴얼

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [코드 구조](#코드-구조)
3. [핵심 컴포넌트 분석](#핵심-컴포넌트-분석)
4. [API 및 메서드 매뉴얼](#api-및-메서드-매뉴얼)
5. [데이터 플로우](#데이터-플로우)
6. [설정 및 환경](#설정-및-환경)
7. [사용법 가이드](#사용법-가이드)
8. [확장 가이드](#확장-가이드)
9. [트러블슈팅](#트러블슈팅)

## 🎯 프로젝트 개요

Strands Agents는 AWS Bedrock Claude 3를 활용한 멀티 에이전트 시스템으로, 다음과 같은 핵심 기능을 제공합니다:

- **멀티 에이전트 아키텍처**: 각기 다른 전문 분야를 담당하는 에이전트들
- **메타 에이전트**: 작업을 분석하여 적절한 에이전트에게 위임
- **웹 인터페이스**: Streamlit 기반의 직관적인 사용자 인터페이스
- **AWS 통합**: Bedrock 서비스를 통한 고성능 AI 모델 활용

## 🏗️ 코드 구조

```
strands-auto/
├── app.py                          # Streamlit 메인 애플리케이션
├── requirements.txt                # Python 의존성 패키지
├── run.sh                         # 실행 스크립트
├── .env.example                   # 환경 변수 템플릿
├── README.md                      # 프로젝트 문서
├── code-review.md                 # 코드 리뷰 문서 (현재 파일)
└── strands-agents/                # 메인 패키지
    ├── __init__.py
    ├── agents/                    # 에이전트 모듈
    │   ├── __init__.py
    │   ├── base_agent.py         # 기본 에이전트 추상 클래스
    │   ├── strands_agent.py      # 전문 에이전트 구현
    │   └── meta_agent.py         # 메타 에이전트 구현
    ├── config/                   # 설정 모듈
    │   ├── __init__.py
    │   └── aws_config.py         # AWS 설정 관리
    └── utils/                    # 유틸리티 모듈 (확장 가능)
        └── __init__.py
```

## 🔍 핵심 컴포넌트 분석

### 1. BaseAgent (base_agent.py)

**역할**: 모든 에이전트의 기본 클래스로, 공통 기능을 제공

**주요 기능**:
- AWS Bedrock 모델 호출 추상화
- 에이전트 정보 관리
- 에러 처리

**핵심 메서드**:
```python
class BaseAgent(ABC):
    def __init__(self, name: str, description: str)
    def process(self, input_data: str) -> str  # 추상 메서드
    def invoke_bedrock_model(self, prompt: str, max_tokens: int = 1000) -> str
    def get_info(self) -> Dict[str, str]
```

**설계 패턴**: Template Method Pattern 사용

### 2. StrandsAgent (strands_agent.py)

**역할**: 특정 도메인에 특화된 에이전트 구현

**주요 기능**:
- 전문 분야별 프롬프트 생성
- 대화 기록 관리
- 맞춤형 응답 생성

**핵심 메서드**:
```python
class StrandsAgent(BaseAgent):
    def __init__(self, name: str, description: str, specialty: str)
    def process(self, input_data: str) -> str
    def _create_specialized_prompt(self, input_data: str) -> str
    def get_conversation_history(self) -> List[Dict[str, str]]
    def clear_history(self)
    def get_specialty_info(self) -> Dict[str, str]
```

**특징**:
- 전문성 기반 프롬프트 엔지니어링
- 상태 관리 (대화 기록)
- 확장 가능한 구조

### 3. MetaAgent (meta_agent.py)

**역할**: 다른 에이전트들을 관리하고 작업을 조율하는 상위 에이전트

**주요 기능**:
- 에이전트 등록/제거
- 작업 분석 및 에이전트 선택
- 작업 기록 관리
- 시스템 상태 모니터링

**핵심 메서드**:
```python
class MetaAgent(BaseAgent):
    def __init__(self)
    def add_agent(self, agent: StrandsAgent)
    def remove_agent(self, agent_name: str)
    def list_agents(self) -> List[Dict[str, str]]
    def process(self, input_data: str) -> str
    def _select_agent(self, input_data: str) -> Optional[StrandsAgent]
    def _handle_meta_task(self, input_data: str) -> str
    def get_task_history(self) -> List[Dict[str, Any]]
    def get_agent_status(self) -> Dict[str, Any]
```

**설계 패턴**: 
- Strategy Pattern (에이전트 선택)
- Observer Pattern (상태 모니터링)

### 4. AWSConfig (aws_config.py)

**역할**: AWS 서비스 설정 및 클라이언트 관리

**주요 기능**:
- Bedrock 클라이언트 초기화
- 모델 설정 관리
- 리전 설정

**핵심 메서드**:
```python
class AWSConfig:
    def __init__(self)
    def get_bedrock_runtime_client(self)
    def get_bedrock_agent_client(self)
    def get_model_config(self) -> Dict[str, Any]
```

**설계 패턴**: Singleton Pattern (글로벌 설정 인스턴스)

### 5. Streamlit App (app.py)

**역할**: 웹 기반 사용자 인터페이스 제공

**주요 기능**:
- 채팅 인터페이스
- 에이전트 관리 UI
- 상태 모니터링 대시보드
- 세션 상태 관리

**핵심 함수**:
```python
def create_default_agents()  # 기본 에이전트 생성
def main()                   # 메인 애플리케이션 로직
```

## 📚 API 및 메서드 매뉴얼

### BaseAgent API

#### `__init__(name: str, description: str)`
- **목적**: 에이전트 초기화
- **매개변수**: 
  - `name`: 에이전트 이름
  - `description`: 에이전트 설명
- **반환값**: None

#### `invoke_bedrock_model(prompt: str, max_tokens: int = 1000) -> str`
- **목적**: AWS Bedrock 모델 호출
- **매개변수**:
  - `prompt`: 입력 프롬프트
  - `max_tokens`: 최대 토큰 수 (기본값: 1000)
- **반환값**: 모델 응답 텍스트
- **예외**: 모델 호출 실패 시 에러 메시지 반환

### StrandsAgent API

#### `process(input_data: str) -> str`
- **목적**: 사용자 입력 처리 및 응답 생성
- **매개변수**: `input_data` - 사용자 입력
- **반환값**: 처리된 응답
- **부작용**: 대화 기록에 추가

#### `get_conversation_history() -> List[Dict[str, str]]`
- **목적**: 대화 기록 조회
- **반환값**: 입력-출력 쌍의 리스트
- **형식**: `[{"input": "...", "output": "..."}, ...]`

### MetaAgent API

#### `add_agent(agent: StrandsAgent)`
- **목적**: 새 에이전트 등록
- **매개변수**: `agent` - 등록할 StrandsAgent 인스턴스
- **부작용**: 내부 에이전트 딕셔너리에 추가

#### `_select_agent(input_data: str) -> Optional[StrandsAgent]`
- **목적**: 입력에 가장 적합한 에이전트 선택
- **매개변수**: `input_data` - 분석할 입력
- **반환값**: 선택된 에이전트 또는 None
- **알고리즘**: LLM 기반 에이전트 매칭

## 🔄 데이터 플로우

### 1. 사용자 요청 처리 플로우

```
사용자 입력 (Streamlit)
    ↓
MetaAgent.process()
    ↓
_select_agent() → 적절한 에이전트 선택
    ↓
선택된 에이전트 또는 MetaAgent 직접 처리
    ↓
BaseAgent.invoke_bedrock_model()
    ↓
AWS Bedrock Claude 3 호출
    ↓
응답 생성 및 기록 저장
    ↓
Streamlit UI 업데이트
```

### 2. 에이전트 선택 알고리즘

```python
def _select_agent(self, input_data: str) -> Optional[StrandsAgent]:
    # 1. 사용 가능한 에이전트 목록 생성
    agent_info = self._get_agents_summary()
    
    # 2. LLM을 통한 에이전트 매칭
    selection_prompt = f"작업: {input_data}\n에이전트: {agent_info}"
    response = self.invoke_bedrock_model(selection_prompt)
    
    # 3. 응답 파싱 및 에이전트 반환
    return self.agents.get(response.strip())
```

## ⚙️ 설정 및 환경

### 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 필수 환경 변수
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### AWS 권한 요구사항

필요한 IAM 권한:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### 의존성 패키지

```txt
streamlit==1.28.1      # 웹 UI 프레임워크
boto3==1.34.0          # AWS SDK
langchain==0.1.0       # LLM 체인 관리
langchain-aws==0.1.0   # AWS 통합
python-dotenv==1.0.0   # 환경 변수 관리
pydantic==2.5.0        # 데이터 검증
```

## 📖 사용법 가이드

### 1. 기본 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
./run.sh
# 또는
streamlit run app.py
```

### 2. 새 에이전트 추가

```python
# 프로그래밍 방식
new_agent = StrandsAgent(
    name="번역 전문가",
    description="다국어 번역 및 언어학 전문",
    specialty="번역 및 언어학"
)
meta_agent.add_agent(new_agent)
```

### 3. 직접 API 사용

```python
from strands_agents.agents.meta_agent import MetaAgent
from strands_agents.agents.strands_agent import StrandsAgent

# 메타 에이전트 생성
meta = MetaAgent()

# 전문 에이전트 추가
coding_agent = StrandsAgent(
    name="코딩 전문가",
    description="프로그래밍 전문",
    specialty="소프트웨어 개발"
)
meta.add_agent(coding_agent)

# 작업 처리
response = meta.process("Python으로 웹 크롤러를 만들어줘")
print(response)
```

## 🔧 확장 가이드

### 1. 새로운 에이전트 타입 추가

```python
class CustomAgent(BaseAgent):
    def __init__(self, name: str, description: str, custom_param: str):
        super().__init__(name, description)
        self.custom_param = custom_param
    
    def process(self, input_data: str) -> str:
        # 커스텀 로직 구현
        custom_prompt = f"Custom: {self.custom_param}\nInput: {input_data}"
        return self.invoke_bedrock_model(custom_prompt)
```

### 2. 새로운 모델 지원 추가

```python
# aws_config.py 수정
class AWSConfig:
    def __init__(self, model_type="claude-3"):
        if model_type == "claude-3":
            self.bedrock_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        elif model_type == "claude-3-haiku":
            self.bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
```

### 3. 플러그인 시스템 추가

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_class):
        self.plugins[name] = plugin_class
    
    def create_agent(self, plugin_name: str, **kwargs):
        if plugin_name in self.plugins:
            return self.plugins[plugin_name](**kwargs)
```

## 🐛 트러블슈팅

### 일반적인 문제들

#### 1. AWS 인증 오류
```
Error: Unable to locate credentials
```
**해결책**:
- AWS CLI 설정: `aws configure`
- 환경 변수 확인: `.env` 파일 설정
- IAM 권한 확인

#### 2. Bedrock 모델 접근 오류
```
Error: Access denied to model
```
**해결책**:
- Bedrock 콘솔에서 모델 액세스 요청
- 올바른 리전 설정 확인 (ap-northeast-2)
- IAM 권한 확인

#### 3. Streamlit 포트 충돌
```
Error: Port 8501 is already in use
```
**해결책**:
```bash
# 다른 포트 사용
streamlit run app.py --server.port 8502

# 또는 기존 프로세스 종료
lsof -ti:8501 | xargs kill -9
```

#### 4. 메모리 부족 오류
**해결책**:
- 대화 기록 정기적 삭제
- `max_tokens` 값 조정
- 에이전트 수 제한

### 디버깅 팁

#### 1. 로깅 활성화
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 응답 시간 모니터링
```python
import time

def timed_process(self, input_data: str) -> str:
    start_time = time.time()
    result = self.process(input_data)
    end_time = time.time()
    print(f"Processing time: {end_time - start_time:.2f}s")
    return result
```

#### 3. 에러 추적
```python
try:
    response = agent.process(input_data)
except Exception as e:
    print(f"Error in {agent.name}: {str(e)}")
    import traceback
    traceback.print_exc()
```

## 🚀 성능 최적화

### 1. 캐싱 구현
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_model_call(self, prompt: str) -> str:
    return self.invoke_bedrock_model(prompt)
```

### 2. 비동기 처리
```python
import asyncio
import aiohttp

async def async_process_multiple(self, inputs: List[str]) -> List[str]:
    tasks = [self.async_process(input_data) for input_data in inputs]
    return await asyncio.gather(*tasks)
```

### 3. 배치 처리
```python
def batch_process(self, inputs: List[str], batch_size: int = 5) -> List[str]:
    results = []
    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i + batch_size]
        batch_results = [self.process(input_data) for input_data in batch]
        results.extend(batch_results)
    return results
```

## 📊 모니터링 및 메트릭

### 주요 메트릭
- 응답 시간
- 에이전트 선택 정확도
- 토큰 사용량
- 에러율

### 모니터링 구현
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "avg_response_time": 0,
            "error_count": 0
        }
    
    def record_request(self, response_time: float, success: bool):
        self.metrics["total_requests"] += 1
        if not success:
            self.metrics["error_count"] += 1
        # 평균 응답 시간 업데이트 로직
```

이 문서는 Strands Agents 시스템의 완전한 이해와 효과적인 사용을 위한 종합 가이드입니다. 추가 질문이나 특정 부분에 대한 더 자세한 설명이 필요하시면 언제든 문의해 주세요.
