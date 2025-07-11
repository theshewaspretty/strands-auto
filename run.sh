#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# ## 실행 방법:
# conda strands-auto 로 함. 

# 1. AWS 자격 증명 설정:
# bash
# aws configure


# 2. 의존성 설치 및 실행:
# bash
# ./run.sh


# 3. 브라우저에서 접속:
# http://localhost:8501
