# Strands Agents

AWS Bedrock Claude 3를 활용한 멀티 에이전트 시스템입니다.

## 기능

1. **Strands Agent**: 특정 도메인에 특화된 에이전트
2. **Meta Agent**: 다른 에이전트들을 관리하고 조율하는 메타 에이전트
3. **Streamlit UI**: 웹 기반 사용자 인터페이스

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. AWS 자격 증명 설정
AWS CLI를 통해 자격 증명을 설정하거나 `.env` 파일을 생성하세요:

```bash
# AWS CLI 설정
aws configure

# 또는 .env 파일 생성
cp .env.example .env
# .env 파일을 편집하여 AWS 자격 증명 입력
```

### 3. 애플리케이션 실행
```bash
# 스크립트를 통한 실행
./run.sh

# 또는 직접 실행
streamlit run app.py
```

## 구조

```
strands-auto/
├── strands-agents/
│   ├── agents/
│   │   ├── base_agent.py      # 기본 에이전트 클래스
│   │   ├── strands_agent.py   # Strands 에이전트
│   │   └── meta_agent.py      # 메타 에이전트
│   ├── config/
│   │   └── aws_config.py      # AWS 설정
│   └── utils/                 # 유틸리티 함수들
├── app.py                     # Streamlit 애플리케이션
├── requirements.txt           # Python 의존성
├── run.sh                     # 실행 스크립트
└── README.md                  # 문서
```

## 사용법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 사이드바에서 에이전트 관리
3. 채팅 인터페이스를 통해 에이전트와 상호작용

## 주요 특징

- **AWS Bedrock Claude 3 Sonnet** 모델 사용
- **ap-northeast-2** 리전 설정
- 동적 에이전트 추가/제거
- 대화 기록 관리
- 작업 기록 추적

## 기본 에이전트

- **코딩 전문가**: 프로그래밍 및 소프트웨어 개발
- **데이터 분석가**: 데이터 분석 및 머신러닝
- **AWS 전문가**: AWS 클라우드 서비스
