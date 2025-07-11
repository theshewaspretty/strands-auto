"""
Streamlit Application for Strands Agents
"""
import streamlit as st
import sys
import os

# Add the strands-agents directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'strands-agents'))

from agents.strands_agent import StrandsAgent
from agents.meta_agent import MetaAgent

# Page configuration
st.set_page_config(
    page_title="Strands Agents",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'meta_agent' not in st.session_state:
    st.session_state.meta_agent = MetaAgent()

if 'agents_created' not in st.session_state:
    st.session_state.agents_created = False

def create_default_agents():
    """Create default agents"""
    if not st.session_state.agents_created:
        # 기본 에이전트들 생성
        agents_config = [
            {
                "name": "코딩 전문가",
                "description": "프로그래밍, 소프트웨어 개발, 코드 리뷰 전문",
                "specialty": "프로그래밍 및 소프트웨어 개발"
            },
            {
                "name": "데이터 분석가",
                "description": "데이터 분석, 통계, 머신러닝 전문",
                "specialty": "데이터 분석 및 머신러닝"
            },
            {
                "name": "AWS 전문가",
                "description": "AWS 클라우드 서비스, 인프라 설계 전문",
                "specialty": "AWS 클라우드 서비스"
            }
        ]
        
        for config in agents_config:
            agent = StrandsAgent(
                name=config["name"],
                description=config["description"],
                specialty=config["specialty"]
            )
            st.session_state.meta_agent.add_agent(agent)
        
        st.session_state.agents_created = True

def main():
    st.title("🤖 Strands Agents")
    st.markdown("AWS Bedrock Claude 3를 활용한 멀티 에이전트 시스템")
    
    # Create default agents
    create_default_agents()
    
    # Sidebar for agent management
    with st.sidebar:
        st.header("에이전트 관리")
        
        # Display current agents
        agents = st.session_state.meta_agent.list_agents()
        if agents:
            st.subheader("현재 에이전트들")
            for agent in agents:
                st.write(f"**{agent['name']}**")
                st.write(f"전문분야: {agent['specialty']}")
                st.write(f"설명: {agent['description']}")
                st.write("---")
        
        # Add new agent
        st.subheader("새 에이전트 추가")
        with st.form("add_agent_form"):
            new_name = st.text_input("에이전트 이름")
            new_specialty = st.text_input("전문 분야")
            new_description = st.text_area("설명")
            
            if st.form_submit_button("에이전트 추가"):
                if new_name and new_specialty and new_description:
                    new_agent = StrandsAgent(
                        name=new_name,
                        description=new_description,
                        specialty=new_specialty
                    )
                    st.session_state.meta_agent.add_agent(new_agent)
                    st.success(f"'{new_name}' 에이전트가 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("모든 필드를 입력해주세요.")
    
    # Main chat interface
    st.header("💬 채팅 인터페이스")
    
    # Display chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with chat_container:
            st.chat_message("user").write(prompt)
        
        # Get response from meta agent
        with st.spinner("응답 생성 중..."):
            try:
                response = st.session_state.meta_agent.process(prompt)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Display assistant response
                with chat_container:
                    st.chat_message("assistant").write(response)
                    
            except Exception as e:
                error_message = f"오류가 발생했습니다: {str(e)}"
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
                with chat_container:
                    st.chat_message("assistant").write(error_message)
    
    # Additional features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("채팅 기록 지우기"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("작업 기록 보기"):
            task_history = st.session_state.meta_agent.get_task_history()
            if task_history:
                st.subheader("작업 기록")
                for i, task in enumerate(task_history[-5:], 1):  # Show last 5 tasks
                    st.write(f"**작업 {i}:**")
                    st.write(f"입력: {task['input']}")
                    st.write(f"처리 에이전트: {task['selected_agent']}")
                    st.write(f"출력: {task['output'][:100]}...")
                    st.write("---")
            else:
                st.info("작업 기록이 없습니다.")
    
    with col3:
        if st.button("에이전트 상태"):
            status = st.session_state.meta_agent.get_agent_status()
            st.subheader("에이전트 상태")
            st.write(f"총 에이전트 수: {status['total_agents']}")
            st.write(f"총 작업 수: {status['total_tasks']}")

if __name__ == "__main__":
    main()
