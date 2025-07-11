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
        self.name = name
        self.description = description
        self.bedrock_client = aws_config.get_bedrock_runtime_client()
        self.model_config = aws_config.get_model_config()
        self.current_model_id = self.model_config["modelId"]
    
    @abstractmethod
    def process(self, input_data: str) -> str:
        """Process input and return response"""
        pass
    
    def invoke_bedrock_model(self, prompt: str, max_tokens: int = 1000) -> str:
        """Invoke Bedrock model with given prompt, trying fallback models if needed"""
        
        # List of models to try in order
        models_to_try = [self.current_model_id] + aws_config.try_alternative_models()
        
        for model_id in models_to_try:
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
                
                response = self.bedrock_client.invoke_model(
                    modelId=model_id,
                    contentType=self.model_config["contentType"],
                    accept=self.model_config["accept"],
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                
                # Update current working model if different
                if model_id != self.current_model_id:
                    self.current_model_id = model_id
                    print(f"Successfully switched to model: {model_id}")
                
                return response_body['content'][0]['text']
                
            except Exception as e:
                error_msg = str(e)
                print(f"Failed to invoke model {model_id}: {error_msg}")
                
                # If this is the last model to try, return the error
                if model_id == models_to_try[-1]:
                    return f"Error: All models failed. Last error: {error_msg}"
                
                # Continue to next model
                continue
        
        return "Error: No models available"
    
    def get_info(self) -> Dict[str, str]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "current_model": self.current_model_id
        }
