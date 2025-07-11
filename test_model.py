#!/usr/bin/env python3
"""
Test script to verify Bedrock model invocation
"""
import sys
import os

# Add the project root to Python path
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
        
        # Simple test prompt
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
