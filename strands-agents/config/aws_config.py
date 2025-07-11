"""
AWS Configuration for Strands Agents
"""
import boto3
from typing import Dict, Any

class AWSConfig:
    def __init__(self):
        self.region = "ap-northeast-2"
        # Use Claude 3 Haiku as primary model (confirmed working)
        self.bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        self.bedrock_runtime_client = None
        self.bedrock_agent_client = None
    
    def get_bedrock_runtime_client(self):
        """Get Bedrock Runtime client"""
        if not self.bedrock_runtime_client:
            self.bedrock_runtime_client = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
        return self.bedrock_runtime_client
    
    def get_bedrock_agent_client(self):
        """Get Bedrock Agent client"""
        if not self.bedrock_agent_client:
            self.bedrock_agent_client = boto3.client(
                'bedrock-agent',
                region_name=self.region
            )
        return self.bedrock_agent_client
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            "modelId": self.bedrock_model_id,
            "contentType": "application/json",
            "accept": "application/json"
        }
    
    def try_alternative_models(self):
        """Get list of alternative model IDs to try"""
        return [
            "anthropic.claude-3-haiku-20240307-v1:0",  # Claude 3 Haiku (confirmed working)
            "us.anthropic.claude-3-haiku-20240307-v1:0",  # Claude 3 Haiku inference profile
            "us.anthropic.claude-3-sonnet-20240229-v1:0",  # Cross-region inference profile
            "us.anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet
        ]

# Global configuration instance
aws_config = AWSConfig()
