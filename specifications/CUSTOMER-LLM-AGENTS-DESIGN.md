# Customer Portal LLM and Agent Integration - Design Document

**Version:** 1.0  
**Date:** 2026-05-06  
**Status:** Design Review  
**Author:** System Architecture Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Context & Objectives](#context--objectives)
3. [Architecture Overview](#architecture-overview)
4. [LLM Abstraction Layer](#llm-abstraction-layer)
5. [Agent System Design](#agent-system-design)
6. [Database Schema Changes](#database-schema-changes)
7. [API Endpoints](#api-endpoints)
8. [Frontend Integration](#frontend-integration)
9. [Configuration Management](#configuration-management)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Testing & Verification](#testing--verification)
12. [Appendices](#appendices)

---

## Executive Summary

This document outlines the design for integrating LLM-powered intelligent agents into the existing insurance claims customer portal. The integration adds conversational AI, advanced fraud detection, risk assessment, and customer assistance capabilities while maintaining a provider-agnostic, configuration-driven architecture.

**Key Capabilities:**
- Customer-facing chatbot with real-time claim/policy lookup
- Multi-agent fraud detection system
- Actuarial risk estimation
- AI-generated image detection
- Enhanced damage severity analysis
- Repair cost explanations in plain language
- Repair shop recommendations

**Design Principles:**
- **Provider Agnostic:** Abstract LLM layer supports Anthropic Claude, OpenAI, and AWS Bedrock
- **Parallel Execution:** Supervisor pattern orchestrates sub-agents concurrently using asyncio
- **Transparent Tracking:** All agent interactions logged for cost monitoring and quality improvement
- **Configuration-Driven:** Agent behavior controlled via YAML configuration
- **Non-Blocking:** Agent analysis enriches but doesn't block core claim processing
- **Auditable:** All agent decisions recorded in claim events for governance

---

## Context & Objectives

### Current State

The insurance claims system currently features:
- **Customer Portal:** React/Tailwind UI for claim submission, image upload, estimate review
- **API Backend:** FastAPI with comprehensive endpoints for customers, claims, adjustors
- **Damage Detection:** YOLOv11 model (`vineetsarpal/yolov11n-car-damage`) detecting 14 damage types
- **Database:** SQLite with models for customers, policies, claims, damages, events
- **Decision Logic:** Deterministic rules-based routing (auto-approve, human review, traditional)

### Problem Statement

Current limitations:
1. **No Conversational Support:** Customers cannot ask questions about their claims or policies
2. **Limited Fraud Detection:** No analysis of vehicle consistency, VIN validation, or image authenticity
3. **Heuristic Risk Assessment:** Severity scoring is rule-based, missing actuarial risk signals
4. **Opaque Cost Estimates:** Customers receive numbers without explanation of repair necessity
5. **No Guidance:** Customers must figure out repair shop selection on their own

### Objectives

**Primary Goals:**
1. Enhance customer experience with conversational AI assistance
2. Improve fraud detection accuracy and reduce false positives
3. Flag high-risk claims for human review before approval
4. Detect AI-generated damage images to prevent synthetic fraud
5. Provide transparent, understandable cost explanations
6. Guide customers to appropriate repair facilities

**Technical Goals:**
1. Design LLM integration that's provider-agnostic (Anthropic, OpenAI, AWS Bedrock)
2. Implement supervisor pattern for efficient parallel agent execution
3. Track all LLM usage and costs for budget management
4. Maintain claim processing performance (< 5 second agent overhead)
5. Preserve audit trail with all agent decisions in claim events

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Customer Portal (React)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Chat Widget  │  │ Claim Detail │  │ Shop Recommendations │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼──────────────────┼────────────────────┼───────────────┘
          │                  │                    │
          │ WebSocket/HTTP   │ REST API           │ REST API
          │                  │                    │
┌─────────┼──────────────────┼────────────────────┼───────────────┐
│         │   FastAPI Backend                     │               │
│         │                  │                    │               │
│  ┌──────▼───────┐   ┌─────▼────────┐   ┌───────▼──────────┐   │
│  │   Chatbot    │   │Image Service │   │ Shop Recommender │   │
│  │   Router     │   │              │   │    Agent         │   │
│  └──────┬───────┘   └──────┬───────┘   └──────────────────┘   │
│         │                  │                                    │
│         │           ┌──────▼────────┐                          │
│         │           │  Supervisor   │                          │
│         │           │    Agent      │                          │
│         │           └───────┬───────┘                          │
│         │                   │                                   │
│         │          ┌────────┼────────┐                         │
│         │          │        │        │                         │
│  ┌──────▼────┐  ┌──▼───┐ ┌─▼────┐ ┌─▼────────┐               │
│  │ Chatbot   │  │Fraud │ │Risk  │ │AI Image  │               │
│  │  Agent    │  │Agent │ │Agent │ │Detector  │               │
│  └──────┬────┘  └──┬───┘ └─┬────┘ └─┬────────┘               │
│         │          │       │        │                         │
│         └──────────┴───────┴────────┴─────────────┐           │
│                                                    │           │
│                    ┌───────────────────────────────▼─┐         │
│                    │   LLM Abstraction Layer         │         │
│                    │  ┌────────┐ ┌────────┐ ┌──────┐│         │
│                    │  │Anthropic│ │OpenAI  │ │Ollama││         │
│                    │  │Provider │ │Provider│ │ Prov ││         │
│                    │  └────────┘ └────────┘ └──────┘│         │
│                    └─────────────────────────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │   Usage      │  │  Performance   │  │   Event Logger   │  │
│  │   Tracker    │  │   Monitor      │  │                  │  │
│  └──────┬───────┘  └───────┬────────┘  └────────┬─────────┘  │
│         │                  │                     │             │
└─────────┼──────────────────┼─────────────────────┼─────────────┘
          │                  │                     │
┌─────────▼──────────────────▼─────────────────────▼─────────────┐
│                      SQLite Database                            │
│  ┌──────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │  Claims  │ │  Damages   │ │Agent Usage │ │Fraud Signals │  │
│  │          │ │            │ │   Logs     │ │              │  │
│  └──────────┘ └────────────┘ └────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **LLM Provider** | Provider-agnostic via abstract base class | Allows switching between Anthropic, OpenAI, or AWS Bedrock without code changes |
| **Agent Execution** | Parallel with asyncio | Minimize latency (5s total vs 15s sequential) |
| **Tool Calling** | Native LLM tool use (function calling) | More reliable than prompt-based tool selection |
| **Chat Storage** | Ephemeral (MVP), database (future) | Simplify initial implementation, preserve upgrade path |
| **Cost Tracking** | Per-request logging to database | Enable cost analysis, budget alerts, and optimization |
| **Supervisor Pattern** | After YOLO, before cost calculation | Enriches damage data with fraud/risk signals before decision logic |
| **Knowledge Base** | JSON file (MVP), vector DB (future) | Fast to implement, easy to update, scalable path |

---

## LLM Abstraction Layer

### Design Philosophy

The LLM abstraction layer decouples agent logic from specific LLM providers, enabling:
1. Provider switching without code changes (Anthropic → OpenAI)
2. A/B testing between models for quality/cost optimization
3. Gradual migration to cheaper/faster models as they improve
4. Local model fallback for development or air-gapped deployments

### Directory Structure

```
src/api/agents/llm/
├── __init__.py
├── base.py                    # BaseLLMClient abstract class
├── config.py                  # Configuration loader
├── schemas.py                 # Request/response schemas
├── prompts.py                 # Centralized prompt templates
├── providers/
│   ├── __init__.py
│   ├── anthropic.py           # Anthropic Claude implementation
│   ├── openai.py              # OpenAI GPT implementation
│   └── bedrock.py             # AWS Bedrock implementation
└── factory.py                 # Provider factory
```

### BaseLLMClient Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # 'user', 'assistant', 'system'
    content: str

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ChatResponse:
    content: str
    tool_calls: Optional[List[ToolCall]]
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str  # 'end_turn', 'tool_use', 'max_tokens'

class BaseLLMClient(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Single-turn chat completion"""
        pass
    
    @abstractmethod
    def chat_stream(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """Streaming chat completion (for chatbot)"""
        pass
    
    @abstractmethod
    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with tool use enabled"""
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Whether this provider supports image inputs"""
        pass
    
    @abstractmethod
    def chat_with_image(
        self,
        system: str,
        text: str,
        image_data: bytes,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with image input (for vision models)"""
        pass
```

### Anthropic Provider Implementation

```python
# src/api/agents/llm/providers/anthropic.py

import anthropic
from ..base import BaseLLMClient, ChatResponse, Message, ToolDefinition, ToolCall
from typing import List, Dict, Any, Iterator
import base64

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str, model: str, base_url: str = None):
        self.client = anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Single-turn chat using Claude"""
        
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return ChatResponse(
            content=response.content[0].text,
            tool_calls=None,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason
        )
    
    def chat_stream(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """Streaming chat for real-time responses"""
        
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        with self.client.messages.stream(
            model=self.model,
            system=system,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with tool use (function calling)"""
        
        # Convert tools to Anthropic format
        anthropic_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters
            }
            for tool in tools
        ]
        
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=anthropic_messages,
            tools=anthropic_tools,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract tool calls if present
        tool_calls = []
        content = ""
        
        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))
        
        return ChatResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason
        )
    
    def supports_vision(self) -> bool:
        """Claude supports vision"""
        return True
    
    def chat_with_image(
        self,
        system: str,
        text: str,
        image_data: bytes,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with image input"""
        
        # Encode image to base64
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
        
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return ChatResponse(
            content=response.content[0].text,
            tool_calls=None,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason
        )
```

### AWS Bedrock Provider

```python
# src/api/agents/llm/providers/bedrock.py

import json
import boto3
import base64
from typing import List, Iterator
from ..base import BaseLLMClient, Message, ToolDefinition, ToolCall, ChatResponse

class BedrockClient(BaseLLMClient):
    """AWS Bedrock LLM client implementation"""
    
    def __init__(self, region: str, model: str):
        self.region = region
        self.model = model
        self.client = boto3.client('bedrock-runtime', region_name=region)
    
    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Chat completion using AWS Bedrock.
        Supports Claude models on Bedrock.
        """
        # For Claude models on Bedrock
        if 'anthropic.claude' in self.model:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "system": system,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            return ChatResponse(
                content=response_body['content'][0]['text'],
                role='assistant',
                input_tokens=response_body['usage']['input_tokens'],
                output_tokens=response_body['usage']['output_tokens'],
                stop_reason=response_body.get('stop_reason', 'end_turn')
            )
        
        # For other Bedrock models (Titan, Llama), implement separately
        raise NotImplementedError(f"Model {self.model} not yet supported")
    
    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Chat with tool calling support (Claude models only).
        """
        if 'anthropic.claude' not in self.model:
            raise NotImplementedError("Tool use only supported for Claude models")
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": system,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters
                }
                for tool in tools
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Parse tool calls if present
        tool_calls = []
        content_text = ""
        
        for content_block in response_body['content']:
            if content_block['type'] == 'text':
                content_text = content_block['text']
            elif content_block['type'] == 'tool_use':
                tool_calls.append(ToolCall(
                    id=content_block['id'],
                    name=content_block['name'],
                    arguments=content_block['input']
                ))
        
        return ChatResponse(
            content=content_text,
            role='assistant',
            tool_calls=tool_calls if tool_calls else None,
            input_tokens=response_body['usage']['input_tokens'],
            output_tokens=response_body['usage']['output_tokens'],
            stop_reason=response_body.get('stop_reason', 'end_turn')
        )
    
    def chat_with_image(
        self,
        system: str,
        messages: List[Message],
        image_data: bytes,
        image_format: str = 'image/jpeg',
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Chat with vision support (Claude 3 models on Bedrock).
        """
        if 'anthropic.claude-3' not in self.model:
            raise NotImplementedError("Vision only supported for Claude 3 models")
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Build message with image
        bedrock_messages = []
        for msg in messages:
            if msg.role == 'user':
                bedrock_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_format,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": msg.content
                        }
                    ]
                })
            else:
                bedrock_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": system,
            "messages": bedrock_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        
        return ChatResponse(
            content=response_body['content'][0]['text'],
            role='assistant',
            input_tokens=response_body['usage']['input_tokens'],
            output_tokens=response_body['usage']['output_tokens'],
            stop_reason=response_body.get('stop_reason', 'end_turn')
        )
    
    def supports_vision(self) -> bool:
        """Check if current model supports vision"""
        return 'anthropic.claude-3' in self.model
```

### Provider Factory

```python
# src/api/agents/llm/factory.py

from .base import BaseLLMClient
from .providers.anthropic import AnthropicClient
from .providers.openai import OpenAIClient
from .providers.bedrock import BedrockClient
from .config import LLMConfig

def get_llm_client(config: LLMConfig) -> BaseLLMClient:
    """Factory method to create LLM client based on provider"""
    
    provider = config.provider.lower()
    
    if provider == "anthropic":
        return AnthropicClient(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url
        )
    elif provider == "openai":
        return OpenAIClient(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url
        )
    elif provider == "bedrock":
        return BedrockClient(
            region=config.aws_region,
            model=config.model
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

### Configuration Loader

```python
# src/api/agents/llm/config.py

from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class LLMConfig:
    provider: str  # 'anthropic', 'openai', 'bedrock'
    api_key: Optional[str]
    model: str
    base_url: Optional[str]
    aws_region: Optional[str]  # For Bedrock
    timeout_s: int
    max_tokens: int
    temperature: float

def load_llm_config(provider_name: str, config_dict: dict) -> LLMConfig:
    """Load LLM configuration from api-config.yaml"""
    
    provider_config = config_dict['llm']['providers'][provider_name]
    
    # Get API key from environment variable (not needed for Bedrock)
    api_key = None
    api_key_env = provider_config.get('api_key_env')
    if api_key_env:
        api_key = os.getenv(api_key_env, '')
    
    # Get AWS region for Bedrock
    aws_region = provider_config.get('aws_region')
    
    return LLMConfig(
        provider=provider_name,
        api_key=api_key,
        model=provider_config['default_model'],
        base_url=provider_config.get('base_url'),
        aws_region=aws_region,
        timeout_s=provider_config.get('timeout_s', 60),
        max_tokens=provider_config.get('max_tokens', 4096),
        temperature=provider_config.get('temperature', 0.2)
    )
```

---

## Agent System Design

### Agent Directory Structure

```
src/api/agents/
├── __init__.py
├── llm/                        # LLM abstraction layer (above)
├── base_agent.py               # BaseAgent abstract class
├── supervisor.py               # SupervisorAgent orchestrator
├── subagents/
│   ├── __init__.py
│   ├── fraud_detector.py       # Fraud detection sub-agent
│   ├── risk_estimator.py       # Risk estimation sub-agent
│   ├── ai_image_detector.py    # AI-generated image detection
│   └── damage_analyzer.py      # Advanced damage analysis
├── chatbot/
│   ├── __init__.py
│   ├── chatbot_agent.py        # Customer-facing chatbot
│   ├── tools.py                # Chatbot tools (claim lookup, etc.)
│   └── knowledge_base.py       # FAQ knowledge base
├── explainer.py                # Estimate explainer agent
├── shop_recommender.py         # Repair shop recommender
└── tracking/
    ├── __init__.py
    ├── usage_tracker.py        # Token usage and cost tracking
    └── performance_monitor.py  # Agent performance metrics
```

### BaseAgent Abstract Class

```python
# src/api/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentResult:
    """Standard result format for all agents"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    error: str = None
    execution_time_ms: int = 0
    token_usage: Dict[str, int] = None
    confidence: float = 1.0
    timestamp: datetime = None

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        self.llm_client = llm_client
        self.config = config
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute agent logic"""
        pass
    
    def _create_result(
        self,
        success: bool,
        data: Dict[str, Any],
        error: str = None,
        execution_time_ms: int = 0,
        token_usage: Dict[str, int] = None,
        confidence: float = 1.0
    ) -> AgentResult:
        """Helper to create standardized result"""
        return AgentResult(
            agent_name=self.agent_name,
            success=success,
            data=data,
            error=error,
            execution_time_ms=execution_time_ms,
            token_usage=token_usage,
            confidence=confidence,
            timestamp=datetime.now()
        )
```

### Supervisor Agent

**File:** `src/api/agents/supervisor.py`

**Purpose:** Orchestrate parallel execution of sub-agents after YOLO detection.

```python
# src/api/agents/supervisor.py

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentResult
from .subagents.fraud_detector import FraudDetectorAgent
from .subagents.risk_estimator import RiskEstimatorAgent
from .subagents.ai_image_detector import AIImageDetectorAgent
from .subagents.damage_analyzer import DamageAnalyzerAgent

logger = logging.getLogger(__name__)

class SupervisorAgent(BaseAgent):
    """
    Supervisor agent that orchestrates parallel execution of sub-agents.
    
    Workflow:
    1. Receives YOLO detection results + claim context
    2. Launches sub-agents in parallel (fraud, risk, AI detection, damage analysis)
    3. Aggregates results
    4. Returns enriched damage data
    """
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        super().__init__(llm_client, config)
        
        # Initialize sub-agents
        self.fraud_detector = FraudDetectorAgent(llm_client, config)
        self.risk_estimator = RiskEstimatorAgent(llm_client, config)
        self.ai_image_detector = AIImageDetectorAgent(llm_client, config)
        self.damage_analyzer = DamageAnalyzerAgent(llm_client, config)
        
        self.parallel_execution = config.get('agents', {}).get('supervisor', {}).get('parallel_execution', True)
        self.timeout_s = config.get('agents', {}).get('supervisor', {}).get('timeout_s', 30)
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute supervisor workflow.
        
        Input:
            - claim_id: int
            - damages: List[Dict] (YOLO detection results)
            - claim_data: Dict (vehicle, customer, incident info)
            - image_paths: List[str]
        
        Output:
            - enriched_damages: List[Dict] (damages + fraud/risk/AI signals)
            - fraud_signals: List[Dict]
            - risk_assessment: Dict
            - ai_detection_results: List[Dict]
        """
        start_time = datetime.now()
        
        try:
            claim_id = input_data['claim_id']
            damages = input_data['damages']
            claim_data = input_data['claim_data']
            image_paths = input_data['image_paths']
            
            logger.info(f"Supervisor starting for claim {claim_id} with {len(damages)} damages")
            
            # Prepare input for sub-agents
            subagent_input = {
                'claim_id': claim_id,
                'damages': damages,
                'vehicle': claim_data['vehicle'],
                'customer': claim_data['customer'],
                'incident': claim_data['incident'],
                'image_paths': image_paths
            }
            
            if self.parallel_execution:
                # Run sub-agents in parallel
                results = await asyncio.gather(
                    self.fraud_detector.execute(subagent_input),
                    self.risk_estimator.execute(subagent_input),
                    self.ai_image_detector.execute(subagent_input),
                    self.damage_analyzer.execute(subagent_input),
                    return_exceptions=True
                )
                
                fraud_result, risk_result, ai_detection_result, damage_analysis_result = results
            else:
                # Run sequentially (for debugging)
                fraud_result = await self.fraud_detector.execute(subagent_input)
                risk_result = await self.risk_estimator.execute(subagent_input)
                ai_detection_result = await self.ai_image_detector.execute(subagent_input)
                damage_analysis_result = await self.damage_analyzer.execute(subagent_input)
            
            # Aggregate results
            enriched_damages = self._enrich_damages(
                damages,
                fraud_result,
                risk_result,
                ai_detection_result,
                damage_analysis_result
            )
            
            # Calculate execution time
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Aggregate token usage
            total_tokens = self._aggregate_token_usage([
                fraud_result, risk_result, ai_detection_result, damage_analysis_result
            ])
            
            result_data = {
                'enriched_damages': enriched_damages,
                'fraud_signals': fraud_result.data if fraud_result.success else [],
                'risk_assessment': risk_result.data if risk_result.success else {},
                'ai_detection_results': ai_detection_result.data if ai_detection_result.success else []
            }
            
            logger.info(f"Supervisor completed for claim {claim_id} in {execution_time_ms}ms")
            
            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                token_usage=total_tokens
            )
            
        except Exception as e:
            logger.error(f"Supervisor failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={},
                error=str(e)
            )
    
    def _enrich_damages(
        self,
        damages: List[Dict],
        fraud_result: AgentResult,
        risk_result: AgentResult,
        ai_detection_result: AgentResult,
        damage_analysis_result: AgentResult
    ) -> List[Dict]:
        """Enrich damage records with sub-agent findings"""
        
        enriched = []
        
        for damage in damages:
            enriched_damage = damage.copy()
            
            # Add fraud signals
            if fraud_result.success:
                enriched_damage['fraud_risk_score'] = fraud_result.data.get('overall_risk_score', 0.0)
            
            # Add risk assessment
            if risk_result.success:
                enriched_damage['risk_score'] = risk_result.data.get('risk_score', 0.0)
            
            # Add AI detection
            if ai_detection_result.success:
                # Find AI detection for this damage's image
                image_id = damage.get('image_id')
                ai_results = ai_detection_result.data.get('results', [])
                for ai_result in ai_results:
                    if ai_result.get('image_id') == image_id:
                        enriched_damage['ai_generated_probability'] = ai_result.get('probability', 0.0)
                        break
            
            # Add enhanced damage analysis
            if damage_analysis_result.success:
                enhanced = damage_analysis_result.data.get('enhanced_damages', [])
                # Find matching enhanced damage
                for enh in enhanced:
                    if enh.get('damage_id') == damage.get('damage_id'):
                        enriched_damage['enhanced_severity'] = enh.get('enhanced_severity')
                        enriched_damage['internal_damage_probability'] = enh.get('internal_damage_probability')
                        enriched_damage['recommended_action'] = enh.get('recommended_action')
                        enriched_damage['agent_reasoning'] = enh.get('reasoning')
                        enriched_damage['secondary_damages_predicted'] = enh.get('secondary_damages_predicted')
                        break
            
            enriched.append(enriched_damage)
        
        return enriched
    
    def _aggregate_token_usage(self, results: List[AgentResult]) -> Dict[str, int]:
        """Aggregate token usage from all sub-agents"""
        total_input = 0
        total_output = 0
        
        for result in results:
            if isinstance(result, AgentResult) and result.token_usage:
                total_input += result.token_usage.get('input_tokens', 0)
                total_output += result.token_usage.get('output_tokens', 0)
        
        return {
            'input_tokens': total_input,
            'output_tokens': total_output,
            'total_tokens': total_input + total_output
        }
```

### Fraud Detection Sub-Agent System

**Design Philosophy:**
- ✅ **Multi-Agent Vision-Based Detection** - Each agent specializes in one fraud signal
- ✅ **Static checks FIRST** (VIN validation, claim frequency) - No LLM needed
- ✅ **Vision agents in parallel** (color, make/model, AI-detection, manipulation) - Computer vision
- ✅ **Behavioral analysis LAST** (pattern reasoning) - LLM synthesis
- ✅ **Cost-efficient** - Skip expensive checks when early signals flag high risk

### Multi-Agent Architecture

**Fraud Detection uses a SUPERVISOR + SUB-AGENTS pattern:**

**SHOWCASE AI VALUE FIRST** - Lead with intelligent agents to demonstrate capabilities!

```
FraudDetectorSupervisor (orchestrator)
├── Phase 1: AI Vision Agents (parallel, SHOWCASE CAPABILITY)
│   ├── ColorVerificationAgent (vision LLM) ← Catches vehicle swaps!
│   ├── MakeModelVerificationAgent (vision LLM) ← Verifies actual vehicle!
│   ├── AIGeneratedImageDetector (vision LLM) ← Detects deepfakes!
│   └── ImageManipulationDetector (vision LLM) ← Catches Photoshop edits!
│
├── Phase 2: Static Validation (deterministic backup)
│   ├── VIN format validation
│   ├── VIN-year consistency
│   └── Claim frequency thresholds
│
└── Phase 3: Behavioral Synthesis (LLM reasoning)
    └── BehaviorPatternAnalyzer (synthesize all signals)
```

**Why This Order?**
- ✅ **Demonstrate AI value** - Show what agents catch that rules cannot
- ✅ **Customer sees AI in action** - "Your claim was analyzed by AI vision agents"
- ✅ **Catch sophisticated fraud early** - Vehicle swaps, AI-generated images, Photoshop
- ✅ **Static checks as validation** - Backup layer if agents fail or are disabled

### Fraud Detection Supervisor

**File:** `src/api/agents/subagents/fraud_detector.py`

```python
# src/api/agents/subagents/fraud_detector.py

from typing import Dict, Any, List
from datetime import datetime
import logging
import re

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import Message

logger = logging.getLogger(__name__)

class FraudDetectorAgent(BaseAgent):
    """
    Fraud detection sub-agent.
    
    TWO-PHASE APPROACH:
    Phase 1: Deterministic rule-based checks (no LLM)
      - VIN format validation
      - Vehicle color exact match
      - Make/model exact match
      - Claim frequency threshold check
      
    Phase 2: LLM pattern analysis (only if needed)
      - Damage pattern anomalies
      - Location reasonableness
      - Behavioral pattern analysis
      - Overall risk synthesis
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute fraud detection analysis - AGENTS FIRST to showcase AI value!"""
        start_time = datetime.now()
        
        try:
            claim_id = input_data['claim_id']
            vehicle = input_data['vehicle']
            customer = input_data['customer']
            damages = input_data['damages']
            incident = input_data['incident']
            
            logger.info(f"FraudDetector analyzing claim {claim_id} - AI VISION AGENTS FIRST")
            
            # PHASE 1: AI VISION AGENTS (run in parallel - SHOWCASE AI!)
            logger.info("Phase 1: Launching AI vision agents in parallel...")
            vision_signals = await self._run_vision_agents(input_data)
            
            vision_risk_score = self._calculate_risk_from_signals(vision_signals)
            
            logger.info(f"Vision agents completed: {len(vision_signals)} signals, risk={vision_risk_score:.2f}")
            
            # PHASE 2: STATIC VALIDATION (quick backup checks)
            logger.info("Phase 2: Running static validation checks...")
            static_signals = self._run_static_checks(vehicle, customer, incident)
            
            static_risk_score = self._calculate_risk_from_signals(static_signals)
            
            logger.info(f"Static checks completed: {len(static_signals)} signals, risk={static_risk_score:.2f}")
            
            # Combine Phase 1 & 2 signals
            all_signals = vision_signals + static_signals
            combined_risk = max(vision_risk_score, static_risk_score)
            
            # PHASE 3: BEHAVIORAL SYNTHESIS (only if needed for final determination)
            behavioral_signals = []
            behavioral_reasoning = ""
            token_usage = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            
            # Skip behavioral analysis if agents + static checks already show clear result
            if combined_risk >= 0.8:
                logger.info(f"Clear high risk ({combined_risk:.2f}), skipping behavioral synthesis")
                behavioral_reasoning = "High risk confirmed by AI vision and static checks; synthesis skipped."
            elif combined_risk <= 0.3:
                logger.info(f"Clear low risk ({combined_risk:.2f}), skipping behavioral synthesis")
                behavioral_reasoning = "Low risk confirmed by AI vision and static checks; synthesis skipped."
            else:
                # Need behavioral synthesis for borderline cases
                logger.info(f"Borderline risk ({combined_risk:.2f}), running behavioral synthesis...")
                behavior_result = await self._run_behavioral_analysis(
                    all_signals, damages, incident, customer
                )
                
                response = self.llm_client.chat(
                    system=system_prompt,
                    messages=[Message(role='user', content=user_prompt)],
                    temperature=0.1,
                    max_tokens=1500
                )
                
                llm_analysis = self._parse_response(response.content)
                llm_signals = llm_analysis.get('signals', [])
                llm_reasoning = llm_analysis.get('reasoning', '')
                
                token_usage = {
                    'input_tokens': response.input_tokens,
                    'output_tokens': response.output_tokens,
                    'total_tokens': response.input_tokens + response.output_tokens
                }
            
            # Combine static and LLM signals
            all_signals = static_signals + llm_signals
            
            # Final risk score (weighted combination)
            final_risk_score = self._calculate_final_risk(static_risk_score, llm_signals)
            
            # Determine recommendation
            recommendation = self._get_recommendation(final_risk_score)
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            fraud_analysis = {
                'overall_risk_score': final_risk_score,
                'signals': all_signals,
                'static_risk_score': static_risk_score,
                'llm_analysis_performed': static_risk_score < 0.8,
                'recommendation': recommendation,
                'reasoning': llm_reasoning or "Risk assessment based on static checks.",
                'confidence': 0.9 if static_signals else 0.7
            }
            
            logger.info(f"FraudDetector completed: risk_score={final_risk_score}, static_checks={len(static_signals)}, llm_used={static_risk_score < 0.8}")
            
            return self._create_result(
                success=True,
                data=fraud_analysis,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage,
                confidence=fraud_analysis['confidence']
            )
            
        except Exception as e:
            logger.error(f"FraudDetector failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={},
                error=str(e)
            )
    
    def _run_static_checks(self, vehicle: Dict, customer: Dict, incident: Dict) -> List[Dict]:
        """Run deterministic fraud checks (no LLM needed)"""
        signals = []
        
        # 1. VIN FORMAT VALIDATION (deterministic)
        vin = vehicle.get('vin', '')
        if not self._is_valid_vin_format(vin):
            signals.append({
                'signal_type': 'vin_invalid_format',
                'severity': 0.9,
                'description': f'VIN format invalid: {vin}',
                'evidence': {'vin': vin, 'check_type': 'static'}
            })
        
        # 2. VIN-YEAR CONSISTENCY CHECK (deterministic)
        if vin and vehicle.get('year'):
            expected_year = self._decode_vin_year(vin)
            if expected_year and expected_year != vehicle['year']:
                signals.append({
                    'signal_type': 'vin_year_mismatch',
                    'severity': 0.8,
                    'description': f"VIN indicates year {expected_year}, claim says {vehicle['year']}",
                    'evidence': {'vin_year': expected_year, 'claimed_year': vehicle['year'], 'check_type': 'static'}
                })
        
        # 3. VEHICLE COLOR EXACT MATCH (deterministic)
        policy_color = vehicle.get('policy_color', '').lower()
        claimed_color = vehicle.get('color', '').lower()
        if policy_color and claimed_color and policy_color != claimed_color:
            signals.append({
                'signal_type': 'color_mismatch',
                'severity': 0.7,
                'description': f"Policy lists color as '{policy_color}', claim says '{claimed_color}'",
                'evidence': {'policy_color': policy_color, 'claimed_color': claimed_color, 'check_type': 'static'}
            })
        
        # 4. MAKE/MODEL EXACT MATCH (deterministic)
        policy_make = vehicle.get('policy_make', '').lower()
        claimed_make = vehicle.get('make', '').lower()
        if policy_make and claimed_make and policy_make != claimed_make:
            signals.append({
                'signal_type': 'make_mismatch',
                'severity': 0.9,
                'description': f"Policy lists make as '{policy_make}', claim says '{claimed_make}'",
                'evidence': {'policy_make': policy_make, 'claimed_make': claimed_make, 'check_type': 'static'}
            })
        
        # 5. CLAIM FREQUENCY THRESHOLD (deterministic)
        claim_count = customer.get('claim_count', 0)
        days_as_customer = customer.get('days_as_customer', 365)
        claims_per_year = (claim_count / days_as_customer) * 365 if days_as_customer > 0 else 0
        
        if claims_per_year > 3:  # More than 3 claims per year
            signals.append({
                'signal_type': 'high_frequency',
                'severity': 0.6,
                'description': f"Customer has {claim_count} claims in {days_as_customer} days ({claims_per_year:.1f} claims/year)",
                'evidence': {'claim_count': claim_count, 'claims_per_year': claims_per_year, 'check_type': 'static'}
            })
        
        # 6. RECENT CLAIM VELOCITY (deterministic)
        recent_claims_30d = customer.get('recent_claims_30d', 0)
        if recent_claims_30d >= 2:
            signals.append({
                'signal_type': 'rapid_claim_velocity',
                'severity': 0.8,
                'description': f"Customer filed {recent_claims_30d} claims in last 30 days",
                'evidence': {'recent_claims_30d': recent_claims_30d, 'check_type': 'static'}
            })
        
        return signals
    
    def _is_valid_vin_format(self, vin: str) -> bool:
        """Validate VIN format (17 characters, alphanumeric, no I/O/Q)"""
        if not vin or len(vin) != 17:
            return False
        
        # VIN uses all letters and numbers except I, O, Q
        valid_chars = set('ABCDEFGHJKLMNPRSTUVWXYZ0123456789')
        return all(c.upper() in valid_chars for c in vin)
    
    def _decode_vin_year(self, vin: str) -> int:
        """Decode model year from VIN (10th character)"""
        if len(vin) < 10:
            return None
        
        year_code = vin[9].upper()
        
        # VIN year codes (simplified - 2000-2030)
        year_map = {
            'Y': 2000, 'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014,
            'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019, 'L': 2020,
            'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025, 'T': 2026,
            'V': 2027, 'W': 2028, 'X': 2029, 'Y': 2030
        }
        
        return year_map.get(year_code)
    
    def _calculate_static_risk(self, signals: List[Dict]) -> float:
        """Calculate risk score from static checks only"""
        if not signals:
            return 0.0
        
        # Weight by severity and cap at 1.0
        total_risk = sum(s['severity'] for s in signals) / len(signals)
        return min(total_risk, 1.0)
    
    def _calculate_final_risk(self, static_risk: float, llm_signals: List[Dict]) -> float:
        """Combine static and LLM risk scores"""
        if not llm_signals:
            return static_risk
        
        # LLM signals add to risk but don't completely override static checks
        llm_risk = sum(s.get('severity', 0.5) for s in llm_signals) / len(llm_signals)
        
        # Weighted average (70% static, 30% LLM) since static checks are more reliable
        final_risk = (static_risk * 0.7) + (llm_risk * 0.3)
        
        return min(final_risk, 1.0)
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Determine recommendation based on risk score"""
        if risk_score >= 0.7:
            return 'REJECT'
        elif risk_score >= 0.4:
            return 'FLAG_FOR_REVIEW'
        else:
            return 'APPROVE'
    
    async def _run_vision_agents(self, input_data: Dict) -> List[Dict]:
        """Run vision-based fraud detection agents in parallel"""
        
        image_paths = input_data['image_paths']
        vehicle = input_data['vehicle']
        
        # Launch vision agents in parallel
        vision_tasks = [
            ColorVerificationAgent(self.llm_client, self.config).execute({
                'image_paths': image_paths,
                'expected_color': vehicle.get('policy_color'),
                'claim_id': input_data['claim_id']
            }),
            MakeModelVerificationAgent(self.llm_client, self.config).execute({
                'image_paths': image_paths,
                'expected_make': vehicle.get('policy_make'),
                'expected_model': vehicle.get('policy_model'),
                'expected_year': vehicle.get('year'),
                'claim_id': input_data['claim_id']
            }),
            AIGeneratedImageDetector(self.llm_client, self.config).execute({
                'image_paths': image_paths,
                'claim_id': input_data['claim_id']
            }),
            ImageManipulationDetector(self.llm_client, self.config).execute({
                'image_paths': image_paths,
                'claim_id': input_data['claim_id']
            })
        ]
        
        results = await asyncio.gather(*vision_tasks, return_exceptions=True)
        
        # Aggregate signals from all vision agents
        vision_signals = []
        for result in results:
            if isinstance(result, AgentResult) and result.success:
                vision_signals.extend(result.data.get('signals', []))
        
        return vision_signals
```

---

### Vision Agent 1: Color Verification

**File:** `src/api/agents/subagents/fraud/color_verification_agent.py`

```python
from typing import Dict, Any, List
from pathlib import Path
import logging

from ...base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

class ColorVerificationAgent(BaseAgent):
    """
    Verify vehicle color in images matches policy records.
    
    Uses vision LLM (Claude with vision, GPT-4V) to:
    1. Identify vehicle color in each image
    2. Compare with expected color from policy
    3. Flag mismatches as potential fraud
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Verify vehicle color"""
        start_time = datetime.now()
        
        try:
            image_paths = input_data['image_paths']
            expected_color = input_data['expected_color']
            claim_id = input_data['claim_id']
            
            if not self.llm_client.supports_vision():
                logger.warning("Vision not supported, skipping color verification")
                return self._create_result(success=True, data={'signals': []})
            
            signals = []
            
            # Analyze each image
            for image_path in image_paths[:3]:  # Analyze up to 3 images
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                prompt = f"""Analyze this vehicle damage photo and identify the vehicle's color.

Expected color from policy: {expected_color}

Tasks:
1. Identify the primary color of the vehicle in this image
2. Consider lighting conditions, shadows, and photo quality
3. Provide confidence level (0.0-1.0)

Respond in JSON:
{{
    "detected_color": "color name",
    "confidence": 0.0-1.0,
    "matches_expected": true/false,
    "reasoning": "explanation"
}}"""

                response = self.llm_client.chat_with_image(
                    system="You are an automotive color identification expert.",
                    text=prompt,
                    image_data=image_data,
                    temperature=0.1,
                    max_tokens=300
                )
                
                color_analysis = self._parse_json(response.content)
                
                # Flag mismatch if confidence is high and colors don't match
                if not color_analysis.get('matches_expected') and color_analysis.get('confidence', 0) > 0.7:
                    signals.append({
                        'signal_type': 'color_mismatch_visual',
                        'severity': min(color_analysis['confidence'], 0.8),
                        'description': f"Visual analysis shows vehicle is {color_analysis['detected_color']}, policy says {expected_color}",
                        'evidence': {
                            'detected_color': color_analysis['detected_color'],
                            'expected_color': expected_color,
                            'confidence': color_analysis['confidence'],
                            'image_path': str(image_path),
                            'check_type': 'vision'
                        }
                    })
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._create_result(
                success=True,
                data={'signals': signals},
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"ColorVerificationAgent failed: {e}", exc_info=True)
            return self._create_result(success=False, data={'signals': []}, error=str(e))
```

---

### Vision Agent 2: Make/Model Verification

**File:** `src/api/agents/subagents/fraud/make_model_verification_agent.py`

```python
class MakeModelVerificationAgent(BaseAgent):
    """
    Verify vehicle make/model in images matches policy records.
    
    Uses vision LLM to:
    1. Identify vehicle make, model, approximate year from images
    2. Compare with expected make/model from policy
    3. Flag mismatches (e.g., policy says Toyota Camry, image shows Honda Accord)
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Verify vehicle make/model"""
        start_time = datetime.now()
        
        try:
            image_paths = input_data['image_paths']
            expected_make = input_data['expected_make']
            expected_model = input_data['expected_model']
            expected_year = input_data['expected_year']
            
            if not self.llm_client.supports_vision():
                logger.warning("Vision not supported, skipping make/model verification")
                return self._create_result(success=True, data={'signals': []})
            
            signals = []
            
            # Analyze best image (usually first one, showing full vehicle)
            best_image_path = image_paths[0] if image_paths else None
            if not best_image_path:
                return self._create_result(success=True, data={'signals': []})
            
            with open(best_image_path, 'rb') as f:
                image_data = f.read()
            
            prompt = f"""Analyze this vehicle and identify its make, model, and approximate year.

Expected from policy:
- Make: {expected_make}
- Model: {expected_model}
- Year: {expected_year}

Tasks:
1. Identify the vehicle's make (manufacturer)
2. Identify the vehicle's model
3. Estimate the model year (or year range)
4. Assess if this matches the expected vehicle
5. Provide confidence level

Respond in JSON:
{{
    "detected_make": "make name",
    "detected_model": "model name",
    "detected_year_range": "2020-2022",
    "matches_expected": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation of identification and comparison"
}}"""

            response = self.llm_client.chat_with_image(
                system="You are an automotive identification expert with deep knowledge of vehicle makes, models, and years.",
                text=prompt,
                image_data=image_data,
                temperature=0.1,
                max_tokens=500
            )
            
            vehicle_analysis = self._parse_json(response.content)
            
            # Flag if high confidence mismatch
            if not vehicle_analysis.get('matches_expected') and vehicle_analysis.get('confidence', 0) > 0.7:
                signals.append({
                    'signal_type': 'make_model_mismatch_visual',
                    'severity': min(vehicle_analysis['confidence'], 0.9),
                    'description': (
                        f"Visual analysis identifies vehicle as {vehicle_analysis['detected_make']} "
                        f"{vehicle_analysis['detected_model']}, policy says {expected_make} {expected_model}"
                    ),
                    'evidence': {
                        'detected_make': vehicle_analysis['detected_make'],
                        'detected_model': vehicle_analysis['detected_model'],
                        'expected_make': expected_make,
                        'expected_model': expected_model,
                        'confidence': vehicle_analysis['confidence'],
                        'reasoning': vehicle_analysis['reasoning'],
                        'check_type': 'vision'
                    }
                })
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._create_result(
                success=True,
                data={'signals': signals},
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"MakeModelVerificationAgent failed: {e}", exc_info=True)
            return self._create_result(success=False, data={'signals': []}, error=str(e))
```

---

### Vision Agent 3: AI-Generated Image Detector

**File:** `src/api/agents/subagents/fraud/ai_image_detector_agent.py`

```python
class AIGeneratedImageDetector(BaseAgent):
    """
    Detect if damage images are AI-generated (synthetic).
    
    Methods:
    1. Vision LLM analysis for AI artifacts
    2. Check for common AI generation patterns:
       - Unnatural smoothing
       - Inconsistent lighting/shadows
       - Repetitive patterns
       - Background anomalies
       - Physical impossibilities
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Detect AI-generated images"""
        start_time = datetime.now()
        
        try:
            image_paths = input_data['image_paths']
            
            if not self.llm_client.supports_vision():
                logger.warning("Vision not supported, skipping AI detection")
                return self._create_result(success=True, data={'signals': []})
            
            signals = []
            
            # Analyze each image for AI generation indicators
            for image_path in image_paths:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                prompt = """Analyze this image for signs of AI generation.

Check for:
1. Unnatural smoothing or blurriness (common in AI-generated images)
2. Inconsistent lighting or shadows (physically impossible)
3. Repetitive patterns or textures
4. Background anomalies or artifacts
5. Physical impossibilities in damage patterns
6. Lack of natural wear, dirt, or environmental context
7. "Too perfect" damage (unrealistic uniformity)

Respond in JSON:
{
    "ai_generated_probability": 0.0-1.0,
    "indicators": ["list of specific indicators found"],
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation"
}"""

                response = self.llm_client.chat_with_image(
                    system="You are an image forensics expert specializing in AI-generated image detection.",
                    text=prompt,
                    image_data=image_data,
                    temperature=0.1,
                    max_tokens=600
                )
                
                ai_analysis = self._parse_json(response.content)
                
                # Flag if high probability of AI generation
                ai_prob = ai_analysis.get('ai_generated_probability', 0)
                if ai_prob > 0.6 and ai_analysis.get('confidence', 0) > 0.7:
                    signals.append({
                        'signal_type': 'ai_generated_image',
                        'severity': min(ai_prob, 0.95),
                        'description': f"Image shows {ai_prob*100:.0f}% probability of being AI-generated",
                        'evidence': {
                            'ai_probability': ai_prob,
                            'indicators': ai_analysis.get('indicators', []),
                            'confidence': ai_analysis['confidence'],
                            'reasoning': ai_analysis['reasoning'],
                            'image_path': str(image_path),
                            'check_type': 'ai_detection'
                        }
                    })
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._create_result(
                success=True,
                data={'signals': signals},
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"AIGeneratedImageDetector failed: {e}", exc_info=True)
            return self._create_result(success=False, data={'signals': []}, error=str(e))
```

---

### Vision Agent 4: Image Manipulation Detector

**File:** `src/api/agents/subagents/fraud/image_manipulation_detector.py`

```python
class ImageManipulationDetector(BaseAgent):
    """
    Detect image manipulation (Photoshop, editing).
    
    Methods:
    1. EXIF metadata analysis (edit history, software used)
    2. Vision LLM analysis for editing artifacts:
       - Cloning/stamp tool marks
       - Inconsistent compression
       - Edge anomalies
       - Color/lighting inconsistencies
       - Shadow mismatches
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Detect image manipulation"""
        start_time = datetime.now()
        
        try:
            image_paths = input_data['image_paths']
            signals = []
            
            for image_path in image_paths:
                # Phase 1: EXIF metadata check (static, no LLM cost)
                exif_signals = self._check_exif_metadata(image_path)
                signals.extend(exif_signals)
                
                # Phase 2: Visual manipulation detection (LLM vision)
                if self.llm_client.supports_vision():
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    
                    prompt = """Analyze this image for signs of digital manipulation or editing.

Check for:
1. Clone stamp tool artifacts (repeated patterns)
2. Inconsistent compression artifacts
3. Unnatural edges or boundaries
4. Color/lighting inconsistencies between areas
5. Shadow direction mismatches
6. Blending artifacts around damage areas
7. Signs of content-aware fill or healing brush

Respond in JSON:
{
    "manipulation_probability": 0.0-1.0,
    "manipulation_types": ["cloning", "content_aware_fill", etc],
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation with specific locations"
}"""

                    response = self.llm_client.chat_with_image(
                        system="You are a digital forensics expert specializing in image manipulation detection.",
                        text=prompt,
                        image_data=image_data,
                        temperature=0.1,
                        max_tokens=600
                    )
                    
                    manip_analysis = self._parse_json(response.content)
                    
                    manip_prob = manip_analysis.get('manipulation_probability', 0)
                    if manip_prob > 0.6 and manip_analysis.get('confidence', 0) > 0.7:
                        signals.append({
                            'signal_type': 'image_manipulation_detected',
                            'severity': min(manip_prob, 0.9),
                            'description': f"Image shows {manip_prob*100:.0f}% probability of digital manipulation",
                            'evidence': {
                                'manipulation_probability': manip_prob,
                                'manipulation_types': manip_analysis.get('manipulation_types', []),
                                'confidence': manip_analysis['confidence'],
                                'reasoning': manip_analysis['reasoning'],
                                'image_path': str(image_path),
                                'check_type': 'manipulation_detection'
                            }
                        })
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._create_result(
                success=True,
                data={'signals': signals},
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"ImageManipulationDetector failed: {e}", exc_info=True)
            return self._create_result(success=False, data={'signals': []}, error=str(e))
    
    def _check_exif_metadata(self, image_path: Path) -> List[Dict]:
        """Check EXIF metadata for manipulation indicators"""
        signals = []
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(image_path)
            exif_data = img._getexif() or {}
            
            # Check for editing software
            software = None
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == 'Software':
                    software = value
                    break
            
            # Flag if edited with Photoshop, GIMP, etc.
            editing_software = ['photoshop', 'gimp', 'pixlr', 'affinity', 'paint.net']
            if software and any(sw in software.lower() for sw in editing_software):
                signals.append({
                    'signal_type': 'exif_editing_software',
                    'severity': 0.6,
                    'description': f"EXIF metadata shows image was edited with {software}",
                    'evidence': {
                        'software': software,
                        'image_path': str(image_path),
                        'check_type': 'exif'
                    }
                })
            
            # Check for missing EXIF (stripped, suspicious)
            if not exif_data or len(exif_data) < 5:
                signals.append({
                    'signal_type': 'exif_stripped',
                    'severity': 0.4,
                    'description': "EXIF metadata is missing or stripped (suspicious)",
                    'evidence': {
                        'exif_count': len(exif_data),
                        'image_path': str(image_path),
                        'check_type': 'exif'
                    }
                })
        
        except Exception as e:
            logger.warning(f"EXIF check failed for {image_path}: {e}")
        
        return signals
```

---

### Behavioral Pattern Analyzer

**File:** `src/api/agents/subagents/fraud/behavior_analyzer.py`

```python
class BehaviorPatternAnalyzer(BaseAgent):
    """
    Analyze behavioral patterns and synthesize all fraud signals.
    
    Inputs: All signals from static checks + vision agents
    
    Analysis:
    1. Damage pattern coherence
    2. Claim timing patterns
    3. Story consistency (description vs damages)
    4. Location reasonableness
    5. Overall fraud synthesis
    """
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Analyze behavioral patterns"""
        
        # Get all existing signals
        all_signals = input_data['all_signals']
        damages = input_data['damages']
        incident = input_data['incident']
        customer = input_data['customer']
        
        prompt = f"""Analyze this claim for behavioral fraud patterns.

Existing fraud signals detected:
{self._format_signals(all_signals)}

Claim details:
- Damages: {len(damages)} detected
- Incident description: {incident.get('description')}
- Location: {incident.get('location')}
- Customer address: {customer.get('address')}
- Days as customer: {customer.get('days_as_customer')}

Analyze:
1. Do damage patterns make sense for the incident description?
2. Is the claim timing suspicious (e.g., filed immediately after policy start)?
3. Is the incident location reasonable given customer address?
4. Are there behavioral red flags combining multiple signals?
5. Overall fraud assessment synthesizing all information

Respond in JSON:
{{
    "additional_signals": [...],
    "overall_assessment": "low/medium/high fraud risk",
    "reasoning": "synthesis of all fraud indicators",
    "confidence": 0.0-1.0
}}"""

        response = self.llm_client.chat(
            system="You are a fraud investigation specialist synthesizing multiple fraud signals.",
            messages=[Message(role='user', content=prompt)],
            temperature=0.1,
            max_tokens=800
        )
        
        analysis = self._parse_json(response.content)
        
        return self._create_result(
            success=True,
            data={
                'signals': analysis.get('additional_signals', []),
                'overall_assessment': analysis.get('overall_assessment'),
                'reasoning': analysis.get('reasoning'),
                'confidence': analysis.get('confidence', 0.7)
            }
        )
    
    def _build_system_prompt(self) -> str:
        return """You are an expert fraud detection specialist analyzing behavioral patterns.
            "signal_type": "color_mismatch" | "vin_invalid" | "suspicious_pattern" | "high_frequency" | "location_inconsistency",
            "severity": 0.0-1.0,
            "description": "Brief description",
            "evidence": {"key": "value"}
        }
    ],
    "recommendation": "APPROVE" | "FLAG_FOR_REVIEW" | "REJECT",
    "reasoning": "Detailed explanation",
    "confidence": 0.0-1.0
}"""
    
    def _build_user_prompt(
        self,
        vehicle: Dict,
        customer: Dict,
        damages: List[Dict],
        incident: Dict
    ) -> str:
        damages_summary = "\n".join([
            f"- {d['part']}: severity={d['severity']}, confidence={d['confidence']}"
            for d in damages
        ])
        
        return f"""Analyze this claim for fraud indicators:

**Vehicle Information:**
- Make: {vehicle.get('make')}
- Model: {vehicle.get('model')}
- Year: {vehicle.get('year')}
- Color: {vehicle.get('color')}
- VIN: {vehicle.get('vin')}

**Customer Information:**
- Customer ID: {customer.get('customer_id')}
- Name: {customer.get('name')}
- Address: {customer.get('address')}
- Previous Claims: {customer.get('claim_count', 0)}

**Incident Information:**
- Date: {incident.get('date')}
- Location: {incident.get('location')}
- Description: {incident.get('description')}
- Vehicle Drivable: {incident.get('vehicle_drivable')}

**Detected Damages:**
{damages_summary}

Provide fraud risk assessment in JSON format."""
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response (expecting JSON)"""
        import json
        
        # Extract JSON from response (handle markdown code blocks)
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback: return safe default
            logger.warning("Failed to parse fraud detection JSON, using defaults")
            return {
                'overall_risk_score': 0.0,
                'signals': [],
                'recommendation': 'FLAG_FOR_REVIEW',
                'reasoning': 'Failed to parse LLM response',
                'confidence': 0.0
            }
```

### Chatbot Agent (Context-Aware)

**File:** `src/api/agents/chatbot/chatbot_agent.py`

**Key Feature:** The chatbot receives context from the frontend about the current page and visible data, enabling contextual responses.

**Context Flow:**
1. Frontend detects user is on claim detail page viewing claim #123
2. Frontend sends chat message with context: `{page: "claim_detail", claim_id: 123, claim_data: {...}}`
3. Chatbot receives context and injects it into conversation before user message
4. LLM can now answer questions like "Why is my estimate so high?" using visible claim data
5. Chatbot can reference specific damages, costs, and details without tool calls

**Benefits:**
- **Contextual Answers:** User asks "Explain this estimate" → Bot knows which estimate
- **Fewer Tool Calls:** Data already in context, no need to fetch from database
- **Better UX:** Instant responses to questions about visible information
- **Reduced Costs:** Less tool calling = fewer tokens and faster responses

**Example Scenarios:**

**Scenario 1: Customer viewing claim detail page**
```javascript
// Frontend sends:
{
  customer_id: 100,
  message: "Why is my estimate so high?",
  context: {
    page: "claim_detail",
    claim_id: 123,
    claim_data: {
      status: "approved",
      total_cost: 3500.00,
      damages: [
        {part: "Front Bumper", severity: "severe", cost: 2000.00},
        {part: "Headlight", severity: "moderate", cost: 1500.00}
      ]
    }
  }
}
```

Chatbot response (without tool call):
> "Your estimate is $3,500 because you have two significant damages:
> 1. **Front Bumper** - Severe damage requiring replacement ($2,000)
> 2. **Headlight** - Moderate damage requiring new assembly ($1,500)
> 
> Both parts require genuine manufacturer parts due to the extent of the damage, which affects the cost. Labor rates in your area average $120/hour, and these repairs require about 8 hours total."

**Scenario 2: Customer on dashboard**
```javascript
// Frontend sends:
{
  customer_id: 100,
  message: "What claims do I have open?",
  context: {
    page: "dashboard",
    active_claims: [
      {claim_id: 123, status: "approved", date: "2026-05-01"},
      {claim_id: 124, status: "pending_review", date: "2026-05-05"}
    ]
  }
}
```

Chatbot response (without tool call):
> "You currently have 2 open claims:
> 1. **Claim #123** - Approved on May 1st
> 2. **Claim #124** - Pending review since May 5th
> 
> Would you like details about either claim?"

```python
# src/api/agents/chatbot/chatbot_agent.py

from typing import Dict, Any, List
from datetime import datetime
import logging

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import Message, ToolDefinition, ToolCall
from .tools import get_chatbot_tools, execute_tool

logger = logging.getLogger(__name__)

class ChatbotAgent(BaseAgent):
    """
    Customer-facing chatbot with tool use capabilities.
    
    Capabilities:
    - Answer FAQ from knowledge base
    - Look up claim status
    - Explain policy details
    - Break down cost estimates
    - Guide through claim process
    """
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        super().__init__(llm_client, config)
        self.knowledge_base_path = config.get('agents', {}).get('chatbot', {}).get('knowledge_base_path')
        self.tools = get_chatbot_tools()
    
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute chatbot conversation turn.
        
        Input:
            - customer_id: int
            - message: str
            - conversation_history: List[Message]
        
        Output:
            - response: str
            - tool_calls: List[Dict] (if any)
        """
        start_time = datetime.now()
        
        try:
            customer_id = input_data['customer_id']
            user_message = input_data['message']
            history = input_data.get('conversation_history', [])
            context = input_data.get('context')  # NEW: Optional context from frontend
            
            logger.info(f"Chatbot processing message for customer {customer_id}")
            
            # Build conversation messages with context
            messages = history.copy()
            
            # If context provided, inject it before the user message
            if context:
                context_message = self._build_context_message(context)
                messages.append(Message(role='user', content=context_message))
            
            messages.append(Message(role='user', content=user_message))
            
            # System prompt
            system_prompt = self._build_system_prompt(customer_id)
            
            # Call LLM with tools
            response = self.llm_client.chat_with_tools(
                system=system_prompt,
                messages=messages,
                tools=self.tools,
                temperature=0.3,
                max_tokens=1024
            )
            
            # Handle tool calls if present
            tool_results = []
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    logger.info(f"Chatbot calling tool: {tool_call.name}")
                    result = await execute_tool(
                        tool_call.name,
                        tool_call.arguments,
                        customer_id
                    )
                    tool_results.append({
                        'tool': tool_call.name,
                        'result': result
                    })
                
                # Make follow-up call with tool results
                messages.append(Message(role='assistant', content=response.content))
                
                tool_result_content = "\n\n".join([
                    f"Tool: {tr['tool']}\nResult: {tr['result']}"
                    for tr in tool_results
                ])
                
                messages.append(Message(role='user', content=f"[TOOL RESULTS]\n{tool_result_content}\n\nPlease provide a response to the user based on these results."))
                
                final_response = self.llm_client.chat(
                    system=system_prompt,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024
                )
                
                response_text = final_response.content
                total_tokens = response.input_tokens + response.output_tokens + final_response.input_tokens + final_response.output_tokens
            else:
                response_text = response.content
                total_tokens = response.input_tokens + response.output_tokens
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            token_usage = {
                'input_tokens': response.input_tokens,
                'output_tokens': response.output_tokens,
                'total_tokens': total_tokens
            }
            
            result_data = {
                'response': response_text,
                'tool_calls': tool_results if tool_results else None
            }
            
            logger.info(f"Chatbot completed in {execution_time_ms}ms")
            
            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage
            )
            
        except Exception as e:
            logger.error(f"Chatbot failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={'response': "I'm sorry, I'm having trouble processing your request right now. Please try again."},
                error=str(e)
            )
    
    def _build_system_prompt(self, customer_id: int) -> str:
        return f"""You are a helpful insurance claims assistant for customer {customer_id}.

Your role is to:
- Answer questions about claims, policies, and insurance processes
- Look up real-time claim status and details using available tools
- Explain cost estimates in simple language
- Guide customers through the claims process
- Provide friendly, professional customer service

Guidelines:
- Be conversational and empathetic
- Use simple language, avoid jargon
- If you need specific information, use the available tools
- If you don't know something, admit it and offer to connect them with a human agent
- Always prioritize accuracy over speed
- When context about the current page is provided, use it to give contextual answers

When a customer asks about their claim or policy, use the appropriate tool to retrieve current information."""
    
    def _build_context_message(self, context: dict) -> str:
        """
        Build a context message from frontend-provided page context.
        
        Context can include:
        - page: Current page name (e.g., "claim_detail", "dashboard")
        - claim_id: ID of claim being viewed
        - claim_data: Full claim details (status, damages, costs)
        - damages: List of damages with severity and costs
        - Any other relevant page state
        
        Example contexts:
        
        1. Customer viewing claim detail page:
        {
            "page": "claim_detail",
            "claim_id": 123,
            "claim_data": {
                "status": "approved",
                "total_cost": 2500.00,
                "damages": [
                    {"part": "Front Bumper", "severity": "moderate", "cost": 1200.00},
                    {"part": "Hood", "severity": "light", "cost": 1300.00}
                ]
            }
        }
        
        2. Customer viewing dashboard:
        {
            "page": "dashboard",
            "active_claims": 2,
            "pending_claims": 1
        }
        """
        context_parts = []
        
        if context.get('page'):
            context_parts.append(f"[CONTEXT: User is on the {context['page']} page]")
        
        if context.get('claim_id'):
            context_parts.append(f"[Current claim being viewed: #{context['claim_id']}]")
        
        if context.get('claim_data'):
            claim = context['claim_data']
            context_parts.append(f"[Claim details visible to user:")
            context_parts.append(f"  Status: {claim.get('status')}")
            context_parts.append(f"  Total Cost: ${claim.get('total_cost', 0):.2f}")
            
            if claim.get('damages'):
                context_parts.append(f"  Damages:")
                for dmg in claim['damages']:
                    context_parts.append(f"    - {dmg.get('part')}: {dmg.get('severity')} severity, ${dmg.get('cost', 0):.2f}")
            context_parts.append("]")
        
        return "\n".join(context_parts) if context_parts else "[No additional context]"
```

**Chatbot Tools:**

```python
# src/api/agents/chatbot/tools.py

from typing import List, Dict, Any
from ..llm.base import ToolDefinition

def get_chatbot_tools() -> List[ToolDefinition]:
    """Define tools available to chatbot"""
    return [
        ToolDefinition(
            name="get_claim_status",
            description="Retrieve the current status and details of a claim by claim_id",
            parameters={
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "integer",
                        "description": "The claim ID to look up"
                    }
                },
                "required": ["claim_id"]
            }
        ),
        ToolDefinition(
            name="get_customer_policies",
            description="Retrieve all active policies for the customer",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        ToolDefinition(
            name="get_damage_details",
            description="Get detailed damage assessment and cost breakdown for a claim",
            parameters={
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "integer",
                        "description": "The claim ID to get damage details for"
                    }
                },
                "required": ["claim_id"]
            }
        ),
        ToolDefinition(
            name="search_faq",
            description="Search the FAQ knowledge base for answers to common questions",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        )
    ]

async def execute_tool(tool_name: str, arguments: Dict[str, Any], customer_id: int) -> str:
    """Execute a chatbot tool and return result as string"""
    
    if tool_name == "get_claim_status":
        from src.api.services.claim_service import ClaimService
        from src.api.database import get_db
        
        db = next(get_db())
        claim_service = ClaimService(db)
        
        claim_id = arguments['claim_id']
        claim = claim_service.get_claim_by_id(claim_id)
        
        if not claim or claim.customer_id != customer_id:
            return f"Claim {claim_id} not found or does not belong to this customer."
        
        return f"Claim {claim_id} status: {claim.status}. Filed on {claim.fnol_date}. Estimated amount: ${claim.estimated_claim_amount:.2f}."
    
    elif tool_name == "get_customer_policies":
        from src.api.services.customer_service import CustomerService
        from src.api.database import get_db
        
        db = next(get_db())
        customer_service = CustomerService(db)
        
        policies = customer_service.get_customer_policies(customer_id)
        
        policy_summaries = []
        for policy in policies:
            policy_summaries.append(f"Policy {policy.policy_number}: {policy.policy_type}, Premium: ${policy.premium_total}")
        
        return "\n".join(policy_summaries)
    
    elif tool_name == "get_damage_details":
        from src.api.services.damage_service import DamageService
        from src.api.database import get_db
        
        db = next(get_db())
        damage_service = DamageService(db)
        
        claim_id = arguments['claim_id']
        damages = damage_service.get_damages_by_claim(claim_id)
        
        damage_summaries = []
        for damage in damages:
            damage_summaries.append(
                f"{damage.damage_part}: Severity {damage.severity}, "
                f"Cost: ${damage.estimated_total_cost:.2f} "
                f"({damage.labor_hours}hrs labor + ${damage.estimated_parts_cost:.2f} parts)"
            )
        
        return "\n".join(damage_summaries)
    
    elif tool_name == "search_faq":
        # Simple keyword search in FAQ knowledge base
        from .knowledge_base import search_faq
        
        query = arguments['query']
        results = search_faq(query)
        
        if results:
            return "\n\n".join([f"Q: {r['question']}\nA: {r['answer']}" for r in results[:3]])
        else:
            return "No FAQ results found for that query."
    
    else:
        return f"Unknown tool: {tool_name}"
```

---

## Database Schema Changes

### New Tables

```sql
-- Agent usage logs (track token usage and costs)
CREATE TABLE agent_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name VARCHAR(100) NOT NULL,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost_usd DECIMAL(10, 6),
    duration_ms INTEGER,
    claim_id INTEGER,
    customer_id INTEGER,
    request_type VARCHAR(50),  -- 'chat', 'fraud_check', 'risk_analysis', etc.
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_agent_usage_timestamp ON agent_usage_logs(timestamp);
CREATE INDEX idx_agent_usage_claim ON agent_usage_logs(claim_id);
CREATE INDEX idx_agent_usage_agent ON agent_usage_logs(agent_name);

-- Agent performance metrics
CREATE TABLE agent_performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    avg_duration_ms DECIMAL(10, 2),
    avg_confidence DECIMAL(3, 2),
    quality_score DECIMAL(3, 2),  -- Manual feedback score
    UNIQUE(agent_name, date)
);

-- Fraud signals (detailed fraud detection results)
CREATE TABLE fraud_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    detection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    overall_risk_score DECIMAL(3, 2),
    signal_type VARCHAR(100),  -- 'color_mismatch', 'vin_invalid', etc.
    severity DECIMAL(3, 2),
    description TEXT,
    evidence JSON,  -- Store as JSON string
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX idx_fraud_signals_claim ON fraud_signals(claim_id);
CREATE INDEX idx_fraud_signals_risk ON fraud_signals(overall_risk_score);

-- Risk assessments (actuarial risk analysis results)
CREATE TABLE risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    assessment_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    risk_score DECIMAL(3, 2),
    cost_deviation_pct DECIMAL(5, 2),
    risk_factors JSON,  -- Store as JSON string
    recommendation VARCHAR(50),  -- 'STANDARD', 'ELEVATED_REVIEW', 'MANUAL_REVIEW'
    reasoning TEXT,
    confidence DECIMAL(3, 2),
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX idx_risk_assessments_claim ON risk_assessments(claim_id);
CREATE INDEX idx_risk_assessments_score ON risk_assessments(risk_score);

-- Chat sessions (future implementation, not MVP)
CREATE TABLE chat_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Chat messages (future implementation, not MVP)
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tool_calls JSON,  -- If message included tool calls
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
```

### Modified Tables

```sql
-- Add agent-related fields to damages table
ALTER TABLE damages ADD COLUMN enhanced_severity DECIMAL(3, 2);
ALTER TABLE damages ADD COLUMN internal_damage_probability DECIMAL(3, 2);
ALTER TABLE damages ADD COLUMN ai_generated_probability DECIMAL(3, 2);
ALTER TABLE damages ADD COLUMN fraud_risk_score DECIMAL(3, 2);
ALTER TABLE damages ADD COLUMN risk_score DECIMAL(3, 2);
ALTER TABLE damages ADD COLUMN agent_reasoning TEXT;
ALTER TABLE damages ADD COLUMN secondary_damages_predicted JSON;

-- Add agent summary fields to claims table
ALTER TABLE claims ADD COLUMN overall_fraud_risk_score DECIMAL(3, 2);
ALTER TABLE claims ADD COLUMN overall_risk_score DECIMAL(3, 2);
ALTER TABLE claims ADD COLUMN agent_flags JSON;  -- Store flags like 'fraud_detected', 'high_risk'
```

### Database Recreation (Development Only)

**Note:** Since this is a development environment, we will **drop and recreate** the database with updated DDL rather than using migrations.

**Backward Compatibility Requirements:**
- ✅ All new columns MUST be nullable or have default values
- ✅ API responses MUST use optional fields for agent data
- ✅ Frontend MUST gracefully handle missing/null agent data
- ✅ Existing API endpoints MUST work without agent integration
- ✅ Agent functionality controlled by feature flags in config

**Approach:**
1. Update the SQLAlchemy models with new tables and columns (all nullable)
2. Drop the existing database: `rm test_insurance.db`
3. Recreate from updated models: The application will auto-create tables on startup
4. Existing code continues to work as agent fields default to NULL

**File:** `src/api/models/agent_usage_log.py` (new)
**File:** `src/api/models/fraud_signal.py` (new)
**File:** `src/api/models/risk_assessment.py` (new)
**File:** `src/api/models/chat_session.py` (new - future)
**File:** `src/api/models/chat_message.py` (new - future)

**Modified Files:**
- `src/api/models/damage.py` - Add agent-related columns
- `src/api/models/claim.py` - Add overall fraud/risk scores

**Complete DDL Reference** (for documentation):

```sql
-- New Tables

-- Agent usage logs
CREATE TABLE agent_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name VARCHAR(100) NOT NULL,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost_usd DECIMAL(10, 6),
    duration_ms INTEGER,
    claim_id INTEGER,
    customer_id INTEGER,
    request_type VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_agent_usage_timestamp ON agent_usage_logs(timestamp);
CREATE INDEX idx_agent_usage_claim ON agent_usage_logs(claim_id);
CREATE INDEX idx_agent_usage_agent ON agent_usage_logs(agent_name);

-- Agent performance metrics
CREATE TABLE agent_performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    avg_duration_ms DECIMAL(10, 2),
    avg_confidence DECIMAL(3, 2),
    quality_score DECIMAL(3, 2),
    UNIQUE(agent_name, date)
);

-- Fraud signals
CREATE TABLE fraud_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    detection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    overall_risk_score DECIMAL(3, 2),
    signal_type VARCHAR(100),
    severity DECIMAL(3, 2),
    description TEXT,
    evidence JSON,
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX idx_fraud_signals_claim ON fraud_signals(claim_id);
CREATE INDEX idx_fraud_signals_risk ON fraud_signals(overall_risk_score);

-- Risk assessments
CREATE TABLE risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    assessment_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    risk_score DECIMAL(3, 2),
    cost_deviation_pct DECIMAL(5, 2),
    risk_factors JSON,
    recommendation VARCHAR(50),
    reasoning TEXT,
    confidence DECIMAL(3, 2),
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE INDEX idx_risk_assessments_claim ON risk_assessments(claim_id);
CREATE INDEX idx_risk_assessments_score ON risk_assessments(risk_score);

-- Chat tables (future)
CREATE TABLE chat_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tool_calls JSON,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- Modified Tables (damages - add columns)
-- ALL NULLABLE for backward compatibility - existing code will not break
-- SQLAlchemy models: Column(..., nullable=True)
-- These columns will be added to existing damages table:
--   enhanced_severity DECIMAL(3, 2) NULL
--   internal_damage_probability DECIMAL(3, 2) NULL
--   ai_generated_probability DECIMAL(3, 2) NULL
--   fraud_risk_score DECIMAL(3, 2) NULL
--   risk_score DECIMAL(3, 2) NULL
--   agent_reasoning TEXT NULL
--   secondary_damages_predicted JSON NULL

-- Modified Tables (claims - add columns)
-- ALL NULLABLE for backward compatibility - existing code will not break
-- SQLAlchemy models: Column(..., nullable=True)
-- These columns will be added to existing claims table:
--   overall_fraud_risk_score DECIMAL(3, 2) NULL
--   overall_risk_score DECIMAL(3, 2) NULL
--   agent_flags JSON NULL
```

**Development Workflow:**

```bash
# Step 1: Backup existing data (if needed)
cp test_insurance.db test_insurance.db.backup

# Step 2: Drop database
rm test_insurance.db

# Step 3: Update models in code (add new model files)
# - Create new model files for agent tables
# - Add columns to existing Damage and Claim models

# Step 4: Restart API (database auto-created from models)
cd src/api
uv run uvicorn main:app --reload

# Step 5: Populate with test data
uv run python scripts/seed_test_data.py
```

---

## API Endpoints

### Design Principles for Agent APIs

**Scalability Requirements:**
- ✅ **Agent-specific routes** - Each agent type has dedicated endpoints
- ✅ **Versioned API** - `/api/v1/agents/{agent-type}/...` supports future versions
- ✅ **RESTful design** - Standard HTTP verbs (GET, POST, DELETE)
- ✅ **Extensible** - Adding new agents doesn't break existing routes
- ✅ **Admin vs Customer** - Separate routes for monitoring vs consumption
- ✅ **Consistent patterns** - All agent routes follow same naming conventions

### Simplified API Routes (Demo Focus)

**FOCUS: Demonstrate agent value through customer experience**

**Multiple Chatbots (Scalable Design):**

| Route | Method | Purpose | Demo Value |
|-------|--------|---------|------------|
| `/api/v1/chatbot/customer/message` | POST | Customer chatbot | ✅ Customer support AI |
| `/api/v1/chatbot/adjustor/message` | POST | Adjustor chatbot | ✅ Claims review assistant |
| `/api/v1/chatbot/executive/message` | POST | Executive chatbot | ✅ Business insights AI |
| `/api/v1/claims/{claim_id}/explain` | GET | Explain estimate | ✅ AI cost explanation |

**Chatbot Types:**

1. **Customer Chatbot** (`/chatbot/customer/message`)
   - Tools: Get claim status, policy details, FAQ
   - Audience: Policyholders
   - Context: Customer-specific data

2. **Adjustor Chatbot** (`/chatbot/adjustor/message`) - *Future*
   - Tools: Claim analytics, fraud insights, damage history
   - Audience: Human reviewers
   - Context: Cross-claim analysis

3. **Executive Chatbot** (`/chatbot/executive/message`) - *Future*
   - Tools: Business KPIs, trend analysis, cost reports
   - Audience: Management
   - Context: Aggregated business data

**Implementation Note:**
- Start with customer chatbot (MVP)
- Fraud detection runs automatically during claim submission
- Same chatbot architecture, different tools/context per audience

### API Route Structure

```
/api/v1/
├── agents/                          # Agent management & monitoring (admin)
│   ├── /                            # List all agents
│   ├── /{agent_name}/status         # Get agent status
│   ├── /{agent_name}/execute        # Execute specific agent (testing)
│   ├── /usage/summary               # Usage across all agents
│   ├── /performance                 # Performance metrics
│   └── /health                      # Health check all agents
│
├── chatbot/                         # Customer chatbot (customer-facing)
│   ├── /message                     # Send chat message
│   ├── /session/start               # Start chat session
│   └── /session/{session_id}        # Delete session
│
├── fraud/                           # Fraud detection (internal/admin)
│   ├── /analyze                     # Run fraud analysis on claim
│   ├── /signals/{claim_id}          # Get fraud signals for claim
│   └── /history/{customer_id}       # Fraud history for customer
│
├── risk/                            # Risk estimation (internal/admin)
│   ├── /assess                      # Run risk assessment on claim
│   ├── /assessments/{claim_id}      # Get risk assessment for claim
│   └── /trends                      # Risk trends over time
│
├── vision/                          # Vision-based analysis (internal)
│   ├── /verify-color                # Color verification
│   ├── /verify-vehicle              # Make/model verification
│   ├── /detect-ai-image             # AI-generated detection
│   └── /detect-manipulation         # Image manipulation detection
│
├── explainer/                       # Estimate explainer (customer-facing)
│   ├── /explain/{claim_id}          # Explain estimate for claim
│   └── /breakdown/{claim_id}        # Detailed cost breakdown
│
└── recommendations/                 # Shop recommender (customer-facing)
    ├── /shops/{claim_id}            # Get shop recommendations
    └── /shops/search                # Search shops by criteria
```

### Simplified Router: Chatbot Only (Customer-Facing)

**File:** `src/api/routers/chatbot.py`

**Purpose:** Demonstrate conversational AI value

**File:** `src/api/routers/chatbot.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

from ..agents.chatbot.chatbot_agent import ChatbotAgent
from ..agents.llm.factory import get_llm_client
from ..agents.llm.config import load_llm_config
from ..agents.llm.base import Message
from ..config import settings

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])

# In-memory session storage (ephemeral for MVP)
chat_sessions = {}

class ChatMessageRequest(BaseModel):
    customer_id: int
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None  # NEW: Frontend provides current page context

class ChatMessageResponse(BaseModel):
    session_id: str
    response: str
    tool_calls: Optional[List[dict]] = None

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a message to the chatbot"""
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'customer_id': request.customer_id,
            'history': []
        }
    
    session = chat_sessions[session_id]
    
    # Verify customer_id matches
    if session['customer_id'] != request.customer_id:
        raise HTTPException(status_code=403, detail="Session does not belong to this customer")
    
    # Initialize chatbot agent
    llm_config = load_llm_config(settings.LLM_DEFAULT_PROVIDER, settings.config)
    llm_client = get_llm_client(llm_config)
    chatbot = ChatbotAgent(llm_client, settings.config)
    
    # Execute chatbot with optional context from frontend
    result = await chatbot.execute({
        'customer_id': request.customer_id,
        'message': request.message,
        'conversation_history': session['history'],
        'context': request.context  # NEW: Pass page context to agent
    })
    
    if not result.success:
        raise HTTPException(status_code=500, detail="Chatbot processing failed")
    
    # Update session history
    session['history'].append(Message(role='user', content=request.message))
    session['history'].append(Message(role='assistant', content=result.data['response']))
    
    # Limit history to last 20 messages
    if len(session['history']) > 20:
        session['history'] = session['history'][-20:]
    
    return ChatMessageResponse(
        session_id=session_id,
        response=result.data['response'],
        tool_calls=result.data.get('tool_calls')
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"success": True}
```

---

### Simplified: Enhance Existing Claims Endpoints

**File:** `src/api/routers/customers.py` (modify existing)

```python
# Modify existing claim detail endpoint to include agent results

@router.get("/{customer_id}/claims/{claim_id}")
def get_claim_detail(customer_id: int, claim_id: int, db: Session = Depends(get_db)):
    """Get claim details - NOW WITH AGENT ANALYSIS!"""
    
    claim = get_claim(claim_id, customer_id, db)
    
    # Get fraud analysis (if agents enabled)
    fraud_analysis = None
    if settings.is_agent_enabled('fraud_detector'):
        fraud_signals = db.query(FraudSignal).filter(
            FraudSignal.claim_id == claim_id
        ).first()
        
        if fraud_signals:
            fraud_analysis = {
                'risk_score': float(fraud_signals.overall_risk_score),
                'signals': [
                    {
                        'type': fraud_signals.signal_type,
                        'description': fraud_signals.description,
                        'severity': float(fraud_signals.severity)
                    }
                ],
                'recommendation': fraud_signals.recommendation
            }
    
    return {
        'claim': claim,
        'damages': claim.damages,
        'fraud_analysis': fraud_analysis,  # NEW: Show AI found fraud!
        'events': claim.events
    }

@router.get("/{customer_id}/claims/{claim_id}/explain")
async def explain_claim_estimate(customer_id: int, claim_id: int, db: Session = Depends(get_db)):
    """Get AI explanation of estimate - DEMO VALUE!"""
    
    if not settings.is_agent_enabled('estimate_explainer'):
        raise HTTPException(status_code=503, detail="Explainer not available")
    
    claim = get_claim(claim_id, customer_id, db)
    
    # Initialize explainer agent
    llm_client = get_llm_client(load_llm_config(settings.LLM_DEFAULT_PROVIDER, settings.config))
    explainer = EstimateExplainerAgent(llm_client, settings.config)
    
    result = await explainer.execute({
        'claim_id': claim_id,
        'damages': [d.to_dict() for d in claim.damages],
        'total_cost': claim.estimated_claim_amount
    })
    
    return {
        'claim_id': claim_id,
        'explanation': result.data['explanation'],  # AI explains costs!
        'breakdown': result.data['breakdown']
    }
```

**That's it! Only 2 modifications to existing endpoints:**
1. Add `fraud_analysis` to claim detail response
2. Add `/explain` endpoint for AI explanations

### Enhanced Claim Endpoints

Modify existing endpoints to include agent data:

```python
# In src/api/routers/customers.py

@router.get("/{customer_id}/claims/{claim_id}", response_model=ClaimDetailResponse)
def get_claim_detail(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """Get claim details including agent analysis"""
    
    claim_service = ClaimService(db)
    damage_service = DamageService(db)
    
    claim = claim_service.get_claim_by_id(claim_id)
    
    if not claim or claim.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    damages = damage_service.get_damages_by_claim(claim_id)
    
    # Get fraud signals
    fraud_signals = db.query(FraudSignal).filter(
        FraudSignal.claim_id == claim_id
    ).order_by(FraudSignal.detection_timestamp.desc()).first()
    
    # Get risk assessment
    risk_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.claim_id == claim_id
    ).order_by(RiskAssessment.assessment_timestamp.desc()).first()
    
    return ClaimDetailResponse(
        claim=claim,
        damages=damages,
        fraud_risk_score=fraud_signals.overall_risk_score if fraud_signals else None,
        fraud_signals=fraud_signals.signals if fraud_signals else [],
        risk_score=risk_assessment.risk_score if risk_assessment else None,
        risk_factors=risk_assessment.risk_factors if risk_assessment else []
    )

# New endpoint for estimate explanation
@router.get("/{customer_id}/claims/{claim_id}/estimate/explain")
async def explain_estimate(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """Get customer-friendly explanation of repair estimate"""
    
    claim_service = ClaimService(db)
    claim = claim_service.get_claim_by_id(claim_id)
    
    if not claim or claim.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Get damages
    damages = db.query(Damage).filter(Damage.claim_id == claim_id).all()
    
    # Initialize explainer agent
    llm_config = load_llm_config(settings.LLM_DEFAULT_PROVIDER, settings.config)
    llm_client = get_llm_client(llm_config)
    explainer = EstimateExplainerAgent(llm_client, settings.config)
    
    result = await explainer.execute({
        'claim_id': claim_id,
        'damages': [d.to_dict() for d in damages],
        'total_cost': claim.estimated_claim_amount
    })
    
    if not result.success:
        raise HTTPException(status_code=500, detail="Failed to generate explanation")
    
    return {
        'explanation': result.data['explanation'],
        'breakdown': result.data['breakdown']
    }

# New endpoint for shop recommendations
@router.get("/{customer_id}/claims/{claim_id}/shops/recommend")
async def recommend_shops(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """Get repair shop recommendations"""
    
    claim_service = ClaimService(db)
    claim = claim_service.get_claim_by_id(claim_id)
    
    if not claim or claim.customer_id != customer_id:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Get damages and customer location
    damages = db.query(Damage).filter(Damage.claim_id == claim_id).all()
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    # Initialize shop recommender
    llm_config = load_llm_config(settings.LLM_DEFAULT_PROVIDER, settings.config)
    llm_client = get_llm_client(llm_config)
    recommender = ShopRecommenderAgent(llm_client, settings.config)
    
    result = await recommender.execute({
        'claim_id': claim_id,
        'damages': [{'type': d.damage_part, 'severity': d.severity} for d in damages],
        'customer_location': {
            'city': customer.city,
            'state': customer.state
        },
        'vehicle': {
            'year': claim.vehicle.year,
            'make': claim.vehicle.make,
            'model': claim.vehicle.model
        }
    })
    
    if not result.success:
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")
    
    return {
        'shops': result.data['recommendations']
    }
```

---

## Frontend Integration

### Chat Widget Component

**File:** `src/ui/customer/src/components/ChatWidget.jsx`

```jsx
import { useState, useEffect, useRef } from 'react';
import { X, Send, MessageCircle, Minimize2 } from 'lucide-react';
import { sendChatMessage } from '../api/chatbot';

export default function ChatWidget({ customerId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        customer_id: customerId,
        message: userMessage,
        session_id: sessionId
      });

      setSessionId(response.session_id);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm sorry, I'm having trouble right now. Please try again." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-200 hover:scale-110 z-50"
        aria-label="Open chat"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
      {/* Header */}
      <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          <h3 className="font-semibold">Claims Assistant</h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="hover:bg-blue-700 rounded p-1 transition"
        >
          <Minimize2 className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Hi! How can I help you today?</p>
            <p className="text-sm mt-2">Ask me about your claims, policies, or insurance questions.</p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 border border-gray-200 rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

**API Client:**

**File:** `src/ui/customer/src/api/chatbot.js`

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export async function sendChatMessage({ customer_id, message, session_id }) {
  const response = await axios.post(`${API_BASE_URL}/api/v1/chatbot/message`, {
    customer_id,
    message,
    session_id
  });
  return response.data;
}

export async function deleteChatSession(session_id) {
  const response = await axios.delete(`${API_BASE_URL}/api/v1/chatbot/session/${session_id}`);
  return response.data;
}
```

### Enhanced Claim Detail Page

**Modified File:** `src/ui/customer/src/pages/ClaimDetailPage.jsx`

Add new components and sections:

```jsx
// Add to imports
import FraudRiskBadge from '../components/FraudRiskBadge';
import EstimateExplanationModal from '../components/EstimateExplanationModal';
import ShopRecommendations from '../components/ShopRecommendations';

// Add state
const [showExplanation, setShowExplanation] = useState(false);
const [showShops, setShowShops] = useState(false);

// Add to claim detail UI (after existing content)
{claim.overall_fraud_risk_score && claim.overall_fraud_risk_score > 0.5 && (
  <div className="mt-4">
    <FraudRiskBadge riskScore={claim.overall_fraud_risk_score} />
  </div>
)}

{claim.overall_risk_score && claim.overall_risk_score > 0.5 && (
  <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
    <h4 className="font-semibold text-yellow-800 mb-2">Risk Assessment</h4>
    <p className="text-sm text-yellow-700">
      This claim has been flagged for elevated risk. Our team will review it carefully.
    </p>
  </div>
)}

<div className="mt-6 flex gap-3">
  <button
    onClick={() => setShowExplanation(true)}
    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
  >
    Explain Estimate
  </button>
  
  <button
    onClick={() => setShowShops(true)}
    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
  >
    Find Repair Shops
  </button>
</div>

{showExplanation && (
  <EstimateExplanationModal
    claimId={claimId}
    onClose={() => setShowExplanation(false)}
  />
)}

{showShops && (
  <ShopRecommendations
    claimId={claimId}
    customerId={customerId}
    onClose={() => setShowShops(false)}
  />
)}
```

### New Components

**File:** `src/ui/customer/src/components/FraudRiskBadge.jsx`

```jsx
import { AlertTriangle } from 'lucide-react';

export default function FraudRiskBadge({ riskScore }) {
  const getRiskLevel = (score) => {
    if (score >= 0.7) return { label: 'High', color: 'red' };
    if (score >= 0.4) return { label: 'Medium', color: 'yellow' };
    return { label: 'Low', color: 'green' };
  };

  const risk = getRiskLevel(riskScore);
  const colorClasses = {
    red: 'bg-red-50 border-red-200 text-red-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    green: 'bg-green-50 border-green-200 text-green-800'
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[risk.color]}`}>
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-5 h-5" />
        <div>
          <h4 className="font-semibold">Fraud Risk: {risk.label}</h4>
          <p className="text-sm mt-1">
            This claim has been flagged for additional verification. Our fraud prevention team will review the details.
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

## Configuration Management

**⚠️ IMPORTANT: All agent configuration is managed via `api-config.yaml`**

- ✅ **Single Source of Truth**: `api-config.yaml` controls all agent behavior
- ✅ **No Hardcoded Values**: All settings (thresholds, models, features) are in YAML
- ✅ **Runtime Configuration**: No code changes needed to enable/disable agents
- ✅ **Environment-Agnostic**: Same codebase works across dev/staging/prod with different configs
- ✅ **Zero Deployment Rollback**: Disable agents by editing config and restarting API

### Configuration File Structure

**File Location:** `/mnt/c/Users/raj/OneDrive/Documents/workspace-2026/ScaleAI-Insurance/v0.1/api-config.yaml`

### Complete api-config.yaml with Agent Settings

```yaml
# ============================================================================
# LLM and Agent Configuration
# ============================================================================

llm:
  default_provider: "anthropic"  # Options: anthropic, openai, bedrock
  
  providers:
    anthropic:
      enabled: true
      api_key_env: "ANTHROPIC_API_KEY"  # Read from environment
      base_url: "https://api.anthropic.com"
      default_model: "claude-sonnet-4.5-20250929"
      timeout_s: 60
      max_tokens: 4096
      temperature: 0.2
    
    openai:
      enabled: false
      api_key_env: "OPENAI_API_KEY"
      base_url: "https://api.openai.com/v1"
      default_model: "gpt-4-turbo"
      timeout_s: 60
      max_tokens: 4096
      temperature: 0.2
    
    bedrock:
      enabled: false
      aws_region: "us-east-1"
      # Authentication: uses boto3 default credential chain
      # (environment vars, IAM role, AWS config file)
      # Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment
      default_model: "anthropic.claude-3-sonnet-20240229-v1:0"
      # Available models:
      # - anthropic.claude-3-opus-20240229-v1:0
      # - anthropic.claude-3-sonnet-20240229-v1:0
      # - anthropic.claude-3-haiku-20240307-v1:0
      # - amazon.titan-text-express-v1
      # - meta.llama3-70b-instruct-v1:0
      timeout_s: 60
      max_tokens: 4096
      temperature: 0.2

agents:
  supervisor:
    enabled: true
    parallel_execution: true
    timeout_s: 30
    
  fraud_detector:
    enabled: true
    model_override: null  # Use default provider
    risk_threshold: 0.7  # Flag if risk > 0.7
    
  risk_estimator:
    enabled: true
    deviation_threshold: 0.10  # 10% deviation
    
  ai_image_detector:
    enabled: true
    probability_threshold: 0.6  # Flag if > 0.6 probability of AI
    
  damage_analyzer:
    enabled: true
    enhance_all_damages: true
    
  chatbot:
    enabled: true
    model_override: "claude-sonnet-4.5-20250929"
    max_conversation_turns: 50
    tool_use_enabled: true
    knowledge_base_path: "data/customer-faq.md"
    
  estimate_explainer:
    enabled: true
    
  shop_recommender:
    enabled: true
    shops_database_path: "data/repair_shops.json"
    max_recommendations: 3

tracking:
  usage_logging_enabled: true
  performance_monitoring_enabled: true
  log_to_database: true
  
  # Cost estimates (USD per 1M tokens)
  cost_estimates:
    anthropic_claude_sonnet_input: 3.00
    anthropic_claude_sonnet_output: 15.00
    anthropic_claude_opus_input: 15.00
    anthropic_claude_opus_output: 75.00
    openai_gpt4_turbo_input: 10.00
    openai_gpt4_turbo_output: 30.00
    bedrock_claude_3_sonnet_input: 3.00
    bedrock_claude_3_sonnet_output: 15.00
    bedrock_claude_3_opus_input: 15.00
    bedrock_claude_3_opus_output: 75.00
    bedrock_claude_3_haiku_input: 0.25
    bedrock_claude_3_haiku_output: 1.25
```

### Configuration Loader Updates

**File:** `src/api/config.py`

```python
# Add to existing config.py

class Settings:
    # ... existing settings ...
    
    # LLM Configuration
    LLM_DEFAULT_PROVIDER: str
    LLM_PROVIDERS: dict
    
    # Agent Configuration
    AGENTS_CONFIG: dict
    
    # Tracking Configuration
    TRACKING_CONFIG: dict
    
    def __init__(self):
        # ... existing init ...
        
        # Load LLM config
        self.LLM_DEFAULT_PROVIDER = self.config.get('llm', {}).get('default_provider', 'anthropic')
        self.LLM_PROVIDERS = self.config.get('llm', {}).get('providers', {})
        
        # Load agent config
        self.AGENTS_CONFIG = self.config.get('agents', {})
        
        # Load tracking config
        self.TRACKING_CONFIG = self.config.get('tracking', {})
    
    def get_agent_config(self, agent_name: str) -> dict:
        """Get configuration for specific agent"""
        return self.AGENTS_CONFIG.get(agent_name, {})
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if agent is enabled"""
        return self.AGENTS_CONFIG.get(agent_name, {}).get('enabled', False)

settings = Settings()
```

### Configuration Reference

#### LLM Provider Configuration

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `llm.default_provider` | string | Default LLM provider | `"anthropic"` |
| `llm.providers.<name>.enabled` | boolean | Enable/disable provider | `true` |
| `llm.providers.<name>.api_key_env` | string | Environment variable for API key | `"ANTHROPIC_API_KEY"` |
| `llm.providers.<name>.base_url` | string | API endpoint URL | `"https://api.anthropic.com"` |
| `llm.providers.<name>.default_model` | string | Default model name | `"claude-sonnet-4.5-20250929"` |
| `llm.providers.<name>.timeout_s` | integer | Request timeout (seconds) | `60` |
| `llm.providers.<name>.max_tokens` | integer | Maximum output tokens | `4096` |
| `llm.providers.<name>.temperature` | float | Temperature (0.0-1.0) | `0.2` |

#### Agent Configuration

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `agents.supervisor.enabled` | boolean | Enable supervisor orchestration | `true` |
| `agents.supervisor.parallel_execution` | boolean | Run sub-agents in parallel | `true` |
| `agents.supervisor.timeout_s` | integer | Max execution time | `30` |
| `agents.fraud_detector.enabled` | boolean | Enable fraud detection | `true` |
| `agents.fraud_detector.model_override` | string/null | Override default model | `null` |
| `agents.fraud_detector.risk_threshold` | float | Risk score threshold (0.0-1.0) | `0.7` |
| `agents.risk_estimator.enabled` | boolean | Enable risk estimation | `true` |
| `agents.risk_estimator.deviation_threshold` | float | Cost deviation threshold (%) | `0.10` |
| `agents.ai_image_detector.enabled` | boolean | Enable AI image detection | `true` |
| `agents.ai_image_detector.probability_threshold` | float | AI probability threshold | `0.6` |
| `agents.damage_analyzer.enabled` | boolean | Enable damage analysis | `true` |
| `agents.damage_analyzer.enhance_all_damages` | boolean | Analyze all damages | `true` |
| `agents.chatbot.enabled` | boolean | Enable chatbot | `true` |
| `agents.chatbot.model_override` | string/null | Override default model | `"claude-sonnet-4.5"` |
| `agents.chatbot.max_conversation_turns` | integer | Max chat history length | `50` |
| `agents.chatbot.tool_use_enabled` | boolean | Enable tool calling | `true` |
| `agents.chatbot.knowledge_base_path` | string | FAQ knowledge base file | `"data/customer-faq.md"` |
| `agents.estimate_explainer.enabled` | boolean | Enable estimate explainer | `true` |
| `agents.shop_recommender.enabled` | boolean | Enable shop recommendations | `true` |
| `agents.shop_recommender.shops_database_path` | string | Repair shops database file | `"data/repair_shops.json"` |
| `agents.shop_recommender.max_recommendations` | integer | Max shops to recommend | `3` |

#### Tracking Configuration

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `tracking.usage_logging_enabled` | boolean | Log token usage | `true` |
| `tracking.performance_monitoring_enabled` | boolean | Track agent performance | `true` |
| `tracking.log_to_database` | boolean | Store logs in database | `true` |
| `tracking.cost_estimates.<provider>_<model>_input` | float | Cost per 1M input tokens (USD) | `3.00` |
| `tracking.cost_estimates.<provider>_<model>_output` | float | Cost per 1M output tokens (USD) | `15.00` |

### Configuration Examples by Environment

#### Development Configuration

```yaml
# api-config.yaml (development)
llm:
  default_provider: "anthropic"
  providers:
    anthropic:
      enabled: true
      api_key_env: "ANTHROPIC_API_KEY"

agents:
  supervisor:
    enabled: true  # Enable for testing
  fraud_detector:
    enabled: true
    risk_threshold: 0.5  # Lower threshold for testing
  chatbot:
    enabled: true
    
tracking:
  usage_logging_enabled: true
  log_to_database: true  # Track costs in dev
```

#### Staging Configuration

```yaml
# api-config.yaml (staging)
llm:
  default_provider: "anthropic"

agents:
  supervisor:
    enabled: true
  fraud_detector:
    enabled: true
    risk_threshold: 0.7  # Production threshold
  risk_estimator:
    enabled: true
  ai_image_detector:
    enabled: false  # Not ready yet
  chatbot:
    enabled: true
    
tracking:
  usage_logging_enabled: true
  performance_monitoring_enabled: true
```

#### Production Configuration

```yaml
# api-config.yaml (production)
llm:
  default_provider: "anthropic"
  providers:
    anthropic:
      enabled: true
      timeout_s: 60
      max_tokens: 4096

agents:
  supervisor:
    enabled: true
    parallel_execution: true
    timeout_s: 30
  fraud_detector:
    enabled: true
    risk_threshold: 0.7
  risk_estimator:
    enabled: true
    deviation_threshold: 0.10
  ai_image_detector:
    enabled: true
    probability_threshold: 0.6
  damage_analyzer:
    enabled: true
  chatbot:
    enabled: true
  estimate_explainer:
    enabled: true
  shop_recommender:
    enabled: true
    
tracking:
  usage_logging_enabled: true
  performance_monitoring_enabled: true
  log_to_database: true
```

#### Emergency Disable Configuration (Rollback)

```yaml
# api-config.yaml (all agents disabled)
llm:
  default_provider: "anthropic"

agents:
  supervisor:
    enabled: false  # EMERGENCY: Disable all agents
  fraud_detector:
    enabled: false
  risk_estimator:
    enabled: false
  ai_image_detector:
    enabled: false
  damage_analyzer:
    enabled: false
  chatbot:
    enabled: false
  estimate_explainer:
    enabled: false
  shop_recommender:
    enabled: false
```

### How to Use Configuration

**1. Enable/Disable Individual Agents:**

```bash
# Edit api-config.yaml
vim api-config.yaml

# Change enabled flag
agents:
  fraud_detector:
    enabled: false  # Disable fraud detection

# Restart API
pkill -f uvicorn
uv run uvicorn main:app --reload
```

**2. Adjust Agent Thresholds:**

```yaml
# Fine-tune fraud detection sensitivity
agents:
  fraud_detector:
    risk_threshold: 0.8  # More strict (fewer flags)
    # or
    risk_threshold: 0.5  # More lenient (more flags)
```

**3. Switch LLM Providers:**

```yaml
# Switch from Anthropic to OpenAI
llm:
  default_provider: "openai"  # Change this
  providers:
    openai:
      enabled: true  # Enable OpenAI
    anthropic:
      enabled: false  # Disable Anthropic
```

**4. Override Model for Specific Agent:**

```yaml
# Use different model for chatbot (faster/cheaper)
agents:
  chatbot:
    model_override: "claude-haiku-4.5"  # Faster, cheaper model
```

**5. Environment Variables for API Keys:**

```bash
# .env file (never commit this)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Reference in config
llm:
  providers:
    anthropic:
      api_key_env: "ANTHROPIC_API_KEY"  # Reads from environment
```

### Configuration Validation

**At Startup:**

```python
# src/api/config.py
def validate_config(self):
    """Validate configuration at startup"""
    
    # Validate LLM config
    if self.LLM_DEFAULT_PROVIDER not in self.LLM_PROVIDERS:
        raise ValueError(f"Default provider {self.LLM_DEFAULT_PROVIDER} not configured")
    
    provider_config = self.LLM_PROVIDERS[self.LLM_DEFAULT_PROVIDER]
    if provider_config.get('enabled'):
        api_key_env = provider_config.get('api_key_env')
        if api_key_env and not os.getenv(api_key_env):
            logger.warning(f"API key environment variable {api_key_env} not set")
    
    # Validate agent config
    for agent_name, agent_config in self.AGENTS_CONFIG.items():
        if agent_config.get('enabled'):
            logger.info(f"Agent enabled: {agent_name}")
            
            # Validate required fields
            if 'risk_threshold' in agent_config:
                threshold = agent_config['risk_threshold']
                if not 0.0 <= threshold <= 1.0:
                    raise ValueError(f"Invalid risk_threshold for {agent_name}: {threshold}")
```

### Configuration Best Practices

1. **Version Control**: Commit `api-config.yaml.example`, not actual config with secrets
2. **Environment Variables**: Store API keys in environment, not in YAML
3. **Incremental Rollout**: Enable agents one at a time in production
4. **Monitor Costs**: Track token usage before enabling all agents
5. **Feature Flags**: Use `enabled: false` rather than deleting config blocks
6. **Document Changes**: Add comments in YAML explaining non-obvious settings
7. **Backup Config**: Keep previous working config before major changes

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Days 1-2: LLM Abstraction Layer**
- [ ] Create `src/api/agents/llm/` directory structure
- [ ] Implement `BaseLLMClient` abstract class
- [ ] Implement `AnthropicClient` provider
- [ ] Implement configuration loader
- [ ] Add LLM configuration to `api-config.yaml`
- [ ] Write unit tests for LLM abstraction

**Days 3-4: Agent Infrastructure**
- [ ] Create `src/api/agents/` directory structure
- [ ] Implement `BaseAgent` abstract class
- [ ] Implement usage tracker
- [ ] Create agent database tables (migration script)
- [ ] Run migration on dev database
- [ ] Write unit tests for tracking

**Days 5-7: Database & Models**
- [ ] Create SQLAlchemy models for new tables (agent_usage_log, fraud_signal, risk_assessment)
- [ ] Add columns to damages and claims models
- [ ] Drop and recreate database with updated DDL
- [ ] Implement services for agent data access
- [ ] Write database integration tests

### Phase 2: Core Agents (Week 2)

**Days 1-2: Supervisor Agent**
- [ ] Implement `SupervisorAgent` orchestrator
- [ ] Add asyncio parallel execution logic
- [ ] Implement result aggregation
- [ ] Write unit tests with mock sub-agents

**Days 3-4: Fraud Detection**
- [ ] Implement `FraudDetectorAgent`
- [ ] Create fraud detection prompts
- [ ] Implement fraud signal parsing
- [ ] Create `fraud_signals` service layer
- [ ] Write integration tests

**Days 5-6: Risk Estimation & AI Image Detection**
- [ ] Implement `RiskEstimatorAgent`
- [ ] Implement `AIImageDetectorAgent` (with vision)
- [ ] Create risk assessment prompts
- [ ] Write integration tests

**Day 7: Damage Analyzer**
- [ ] Implement `DamageAnalyzerAgent`
- [ ] Create damage analysis prompts
- [ ] Integrate with YOLO detections
- [ ] Write integration tests

### Phase 3: Integration (Week 3)

**Days 1-2: Supervisor Integration**
- [ ] Modify `image_service.py` to call supervisor
- [ ] Update `claim_service.py` to store agent results
- [ ] Update claim submission workflow
- [ ] Add agent event logging

**Days 3-4: Chatbot Backend**
- [ ] Implement `ChatbotAgent`
- [ ] Implement chatbot tools
- [ ] Create FAQ knowledge base (JSON)
- [ ] Implement `chatbot.py` router
- [ ] Write chatbot integration tests

**Days 5-7: Estimate Explainer & Shop Recommender**
- [ ] Implement `EstimateExplainerAgent`
- [ ] Implement `ShopRecommenderAgent`
- [ ] Create mock shop database (JSON)
- [ ] Add API endpoints
- [ ] Write integration tests

### Phase 4: Frontend (Week 4)

**Days 1-2: Chat Widget**
- [ ] Implement `ChatWidget.jsx` component
- [ ] Create `chatbot.js` API client
- [ ] Add to `Layout.jsx`
- [ ] Style and test responsiveness

**Days 3-4: Enhanced Claim Detail**
- [ ] Implement `FraudRiskBadge.jsx`
- [ ] Implement `EstimateExplanationModal.jsx`
- [ ] Implement `ShopRecommendations.jsx`
- [ ] Modify `ClaimDetailPage.jsx`
- [ ] Add API calls for new features

**Days 5-7: Testing & Polish**
- [ ] End-to-end testing of full workflow
- [ ] Performance optimization
- [ ] UI/UX refinements
- [ ] Bug fixes
- [ ] Documentation updates

---

## Backward Compatibility Strategy

### Overview

All agent features are designed to be **fully backward compatible** with existing API and portal code. The system can operate in three modes:

1. **Agent Disabled Mode** - Agent features turned off via config
2. **Partial Agent Mode** - Some agents enabled, others disabled
3. **Full Agent Mode** - All agents enabled

### Database Compatibility

**All new columns are NULLABLE:**

```python
# SQLAlchemy Model Example - Damage model
class Damage(Base):
    __tablename__ = "damages"
    
    # Existing columns
    damage_id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.claim_id'))
    # ... existing fields ...
    
    # NEW COLUMNS - All nullable=True for backward compatibility
    enhanced_severity = Column(DECIMAL(3, 2), nullable=True)
    internal_damage_probability = Column(DECIMAL(3, 2), nullable=True)
    ai_generated_probability = Column(DECIMAL(3, 2), nullable=True)
    fraud_risk_score = Column(DECIMAL(3, 2), nullable=True)
    risk_score = Column(DECIMAL(3, 2), nullable=True)
    agent_reasoning = Column(Text, nullable=True)
    secondary_damages_predicted = Column(JSON, nullable=True)
```

**Benefits:**
- ✅ Existing queries return NULL for new columns (no errors)
- ✅ INSERT statements without new columns still work
- ✅ SELECT * statements don't break
- ✅ Frontend handles NULL gracefully

### API Compatibility

**Response Schema Changes - All Optional:**

```python
# Pydantic Response Models
class DamageResponse(BaseModel):
    damage_id: int
    claim_id: int
    damage_part: str
    severity: float
    # ... existing fields ...
    
    # NEW FIELDS - All Optional with defaults
    enhanced_severity: Optional[float] = None
    internal_damage_probability: Optional[float] = None
    ai_generated_probability: Optional[float] = None
    fraud_risk_score: Optional[float] = None
    risk_score: Optional[float] = None
    agent_reasoning: Optional[str] = None
    secondary_damages_predicted: Optional[List[str]] = None

class ClaimDetailResponse(BaseModel):
    claim: ClaimResponse
    damages: List[DamageResponse]
    # ... existing fields ...
    
    # NEW FIELDS - All Optional with defaults
    fraud_risk_score: Optional[float] = None
    fraud_signals: Optional[List[dict]] = []
    risk_score: Optional[float] = None
    risk_factors: Optional[List[str]] = []
```

**Conditional Agent Execution:**

```python
# In claim submission endpoint
@router.post("/customers/{customer_id}/claims/{claim_id}/submit")
async def submit_claim(claim_id: int, ...):
    # ... existing logic ...
    
    # CONDITIONAL: Only run supervisor if enabled
    if settings.is_agent_enabled('supervisor'):
        try:
            supervisor_result = await supervisor.execute(...)
            # Enrich damage data with agent results
            enrich_damages_with_agent_data(damages, supervisor_result)
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            # FALLBACK: Continue without agent data
    
    # Continue with normal flow (works with or without agents)
    return build_response(claim, damages)
```

### Frontend Compatibility

**Conditional Rendering - Check for NULL/undefined:**

```jsx
// ClaimDetailPage.jsx
function ClaimDetailPage({ claimId }) {
    const { claim } = useClaimDetail(claimId);
    
    return (
        <div>
            {/* Existing claim details - always shown */}
            <ClaimInfo claim={claim} />
            <DamageList damages={claim.damages} />
            
            {/* NEW: Conditional agent features - only show if data exists */}
            {claim.fraud_risk_score && claim.fraud_risk_score > 0.5 && (
                <FraudRiskBadge riskScore={claim.fraud_risk_score} />
            )}
            
            {claim.risk_score && claim.risk_score > 0.5 && (
                <RiskAssessmentCard riskScore={claim.risk_score} />
            )}
            
            {/* Buttons only show if agent endpoints are available */}
            {isFeatureEnabled('estimate_explainer') && (
                <button onClick={handleExplainEstimate}>
                    Explain Estimate
                </button>
            )}
        </div>
    );
}
```

**Safe Data Access with Optional Chaining:**

```javascript
// Safe access to potentially null fields
const fraudRisk = claim?.fraud_risk_score ?? 0;
const riskFactors = claim?.risk_factors ?? [];
const agentReasoning = damage?.agent_reasoning ?? 'No additional analysis available';
```

### Configuration-Based Feature Flags

**api-config.yaml:**

```yaml
agents:
  supervisor:
    enabled: false  # Start with agents disabled
    
  fraud_detector:
    enabled: false  # Enable incrementally
    
  chatbot:
    enabled: false  # Deploy features one at a time
```

**Runtime Feature Checks:**

```python
# config.py
class Settings:
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if agent is enabled"""
        return self.AGENTS_CONFIG.get(agent_name, {}).get('enabled', False)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if feature is enabled"""
        # Allow feature flags to be set independently
        return self.FEATURES.get(feature_name, False)
```

### Graceful Degradation

**Agent Failure Handling:**

```python
# Supervisor Agent
async def execute_with_fallback(self, input_data):
    try:
        # Attempt agent execution
        result = await self.execute(input_data)
        return result
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        # Return safe default result - processing continues
        return AgentResult(
            agent_name=self.agent_name,
            success=False,
            data={},
            error=str(e)
        )
```

**Frontend Error Boundaries:**

```jsx
// ChatWidget.jsx - handle API unavailability
function ChatWidget() {
    const [isAvailable, setIsAvailable] = useState(true);
    
    useEffect(() => {
        // Check if chatbot endpoint is available
        checkChatbotHealth().catch(() => {
            setIsAvailable(false);
        });
    }, []);
    
    if (!isAvailable) {
        return null; // Don't show widget if unavailable
    }
    
    return <ChatWidgetComponent />;
}
```

### Testing Backward Compatibility

**Test Matrix:**

| Test Scenario | Agent Config | Expected Result |
|---------------|--------------|-----------------|
| Claim submission - agents OFF | All disabled | Works as before, no agent data |
| Claim submission - agents ON | All enabled | Works with agent data populated |
| Get claim detail - agents OFF | All disabled | Returns NULL for agent fields |
| Get claim detail - agents ON | All enabled | Returns populated agent fields |
| Portal load - no agent data | Data from old DB | No errors, agent features hidden |
| Portal load - with agent data | Data from new DB | Agent features visible |

**Compatibility Test Script:**

```python
# tests/integration/test_backward_compatibility.py

def test_claim_submission_without_agents(client, test_customer):
    """Test claim submission works when agents disabled"""
    
    # Disable all agents
    settings.AGENTS_CONFIG = {
        'supervisor': {'enabled': False}
    }
    
    # Submit claim
    response = client.post(f"/api/v1/customers/{test_customer.customer_id}/claims/{claim_id}/submit")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify core fields present
    assert 'claim_id' in data
    assert 'damages' in data
    
    # Verify agent fields are None (not missing)
    assert data.get('fraud_risk_score') is None
    assert data.get('risk_assessment') is None

def test_frontend_with_null_agent_data(client):
    """Test frontend API returns valid JSON with NULL agent fields"""
    
    response = client.get("/api/v1/customers/100/claims/1000")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include agent fields (as NULL) to maintain schema consistency
    assert 'fraud_risk_score' in data or data['fraud_risk_score'] is None
```

### Deployment Strategy

**Phase 1: Deploy Infrastructure (agents disabled)**
1. Deploy new database schema with NULL columns
2. Deploy API with agent code (all agents disabled)
3. Deploy frontend with conditional agent UI
4. ✅ **Verify existing functionality works**

**Phase 2: Enable Agents Incrementally**
1. Enable supervisor + fraud detector in staging
2. Monitor for errors, performance impact
3. Enable in production with canary deployment
4. Enable remaining agents one by one

**Phase 3: Full Rollout**
1. Enable all agents in production
2. Monitor token usage and costs
3. Tune thresholds based on real data
4. Collect feedback and iterate

### Rollback Plan

If agents cause issues:

1. **Immediate**: Disable via config (no code deployment needed)
   ```yaml
   agents:
     supervisor:
       enabled: false  # Instant rollback
   ```

2. **Data Preservation**: Agent data remains in database
   - Can re-enable later without data loss
   - Historical agent decisions preserved for analysis

3. **No Breaking Changes**: Frontend continues to work
   - Agent UI components hidden automatically
   - No errors from missing data

---

## Testing & Verification

### Unit Tests

**LLM Abstraction:**
```python
# tests/agents/llm/test_anthropic_client.py

import pytest
from src.api.agents.llm.providers.anthropic import AnthropicClient
from src.api.agents.llm.base import Message

@pytest.fixture
def mock_anthropic_client(mocker):
    # Mock Anthropic SDK
    pass

def test_chat_basic(mock_anthropic_client):
    client = AnthropicClient(api_key="test", model="claude-sonnet-4.5")
    response = client.chat(
        system="You are a test assistant",
        messages=[Message(role='user', content='Hello')]
    )
    assert response.content is not None
    assert response.input_tokens > 0
```

**Agent Tests:**
```python
# tests/agents/test_fraud_detector.py

import pytest
from src.api.agents.subagents.fraud_detector import FraudDetectorAgent

@pytest.fixture
def mock_llm_client(mocker):
    # Mock LLM responses
    pass

async def test_fraud_detector_basic(mock_llm_client):
    agent = FraudDetectorAgent(mock_llm_client, {})
    result = await agent.execute({
        'claim_id': 1,
        'vehicle': {...},
        'customer': {...},
        'damages': [...],
        'incident': {...}
    })
    assert result.success
    assert 'overall_risk_score' in result.data
```

### Integration Tests

**Supervisor Workflow:**
```python
# tests/integration/test_supervisor_workflow.py

import pytest
from src.api.agents.supervisor import SupervisorAgent

async def test_full_supervisor_workflow(test_db, test_llm_client):
    """Test full supervisor with real database and mock LLM"""
    supervisor = SupervisorAgent(test_llm_client, test_config)
    
    result = await supervisor.execute({
        'claim_id': 1000,
        'damages': test_yolo_detections,
        'claim_data': test_claim_data,
        'image_paths': test_image_paths
    })
    
    assert result.success
    assert len(result.data['enriched_damages']) > 0
    assert result.data['fraud_signals'] is not None
    assert result.data['risk_assessment'] is not None
    assert result.execution_time_ms < 6000  # < 6 seconds
```

### End-to-End Tests

**Claim Submission with Agents:**
```python
# tests/e2e/test_claim_submission_with_agents.py

import pytest
from fastapi.testclient import TestClient

def test_claim_submission_e2e(client: TestClient, test_customer):
    """Test full claim submission with agent analysis"""
    
    # Create claim
    response = client.post(f"/api/v1/customers/{test_customer.customer_id}/claims", json={...})
    claim_id = response.json()['claim_id']
    
    # Upload image
    with open('tests/fixtures/test_damage.jpg', 'rb') as f:
        response = client.post(
            f"/api/v1/customers/{test_customer.customer_id}/claims/{claim_id}/images",
            files={'file': f}
        )
    assert response.status_code == 200
    
    # Submit claim (triggers supervisor)
    response = client.post(
        f"/api/v1/customers/{test_customer.customer_id}/claims/{claim_id}/submit"
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify agent results
    assert 'fraud_risk_score' in data
    assert 'risk_assessment' in data
    assert data['damages'][0]['enhanced_severity'] is not None
```

**Chatbot E2E:**
```python
# tests/e2e/test_chatbot_e2e.py

def test_chatbot_with_tool_use(client: TestClient, test_customer, test_claim):
    """Test chatbot tool calling"""
    
    response = client.post("/api/v1/chatbot/message", json={
        'customer_id': test_customer.customer_id,
        'message': f'What is the status of claim {test_claim.claim_id}?'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'session_id' in data
    assert 'response' in data
    assert test_claim.status in data['response']  # Should mention claim status
    assert data['tool_calls'] is not None  # Should have called get_claim_status
```

### Performance Benchmarks

```python
# tests/performance/test_agent_performance.py

import pytest
import asyncio
from datetime import datetime

async def test_supervisor_performance(supervisor_agent, test_data):
    """Verify supervisor executes within 5 seconds"""
    
    start = datetime.now()
    result = await supervisor_agent.execute(test_data)
    duration_ms = (datetime.now() - start).total_seconds() * 1000
    
    assert result.success
    assert duration_ms < 5000, f"Supervisor took {duration_ms}ms (expected < 5000ms)"

async def test_chatbot_response_time(chatbot_agent, test_message):
    """Verify chatbot responds within 2 seconds (no tools)"""
    
    start = datetime.now()
    result = await chatbot_agent.execute(test_message)
    duration_ms = (datetime.now() - start).total_seconds() * 1000
    
    assert result.success
    assert duration_ms < 2000, f"Chatbot took {duration_ms}ms (expected < 2000ms)"
```

---

## Appendices

### A. Agent Prompt Templates

**Fraud Detection System Prompt:**
```
You are an expert fraud detection specialist for auto insurance claims with 15+ years of experience.

Your task is to analyze claims for fraud indicators and provide a risk assessment.

Fraud indicators to check:
1. Vehicle consistency (color, make, model match policy data)
2. VIN format validation and consistency with vehicle year/make
3. Damage patterns (unrealistic patterns, all same severity)
4. Historical claim frequency (multiple claims in short period)
5. Location consistency (incident location vs customer address)
6. EXIF metadata manipulation signs (if available)

Provide your analysis in JSON format:
{
    "overall_risk_score": 0.0-1.0,
    "signals": [...],
    "recommendation": "APPROVE" | "FLAG_FOR_REVIEW" | "REJECT",
    "reasoning": "...",
    "confidence": 0.0-1.0
}
```

**Estimate Explainer System Prompt:**
```
You are a customer service specialist explaining auto repair estimates in simple, friendly terms.

Your goal is to help customers understand:
- What damage was found and why repair is needed
- How the costs were calculated
- Why the estimate is fair and reasonable

Guidelines:
- Use plain language, avoid technical jargon
- Be empathetic and reassuring
- Provide context (e.g., "Labor rates in your state average $X/hour")
- Break down complex repairs into simple steps
- Address common concerns proactively

Format your explanation as:
1. Summary paragraph (2-3 sentences)
2. Damage-by-damage breakdown with plain language explanations
3. Cost breakdown (labor, parts, totals)
4. Reassurance statement
```

### B. Knowledge Base Schema

**File:** `data/customer-faq.md`

```markdown
# Customer FAQ Knowledge Base

## Claims Process

### How long does it take to process a claim?
Most claims are processed within 24-48 hours. If your claim requires human review, it may take 3-5 business days.

**Keywords:** processing time, how long, duration

### What information do I need to submit a claim?
You'll need photos of the damage, your policy number, vehicle information (make, model, year), and details about when and where the damage occurred.

**Keywords:** submit claim, requirements, what do I need

### Can I track my claim status?
Yes! You can check your claim status anytime through your customer portal or by asking our chatbot.

**Keywords:** track claim, claim status, check status

---

## Cost Estimates

### Why is my estimate so high?
Repair costs depend on the extent of damage, parts needed, and labor rates in your area. Our estimates are based on fair market rates for your region.

**Keywords:** high cost, expensive, estimate

### How are repair costs calculated?
We calculate costs based on the type and severity of damage, market rates for parts, and average labor rates in your state. Each damage type has a baseline cost that's adjusted for severity.

**Keywords:** calculate cost, how costs work, pricing

### Does my estimate include tax?
Yes, all estimates include applicable state and local taxes, as well as any environmental fees required in your area.

**Keywords:** tax, fees, additional charges

---

## Appeals

### What happens if I appeal my estimate?
If you appeal, a human adjustor will review your claim within 2-3 business days. They may adjust the estimate or request additional photos.

**Keywords:** appeal, dispute, disagree

### How do I submit an appeal?
Click the "Appeal Decision" button on your claim detail page and provide your reason for the appeal. You can also upload additional photos or documentation.

**Keywords:** submit appeal, appeal process, how to appeal

---

## Policy Coverage

### What does my policy cover?
Coverage depends on your policy type. Collision coverage handles damage from accidents, while comprehensive covers non-collision incidents like hail or vandalism.

**Keywords:** coverage, what's covered, policy

### What is my deductible?
Your deductible is the amount you pay before insurance coverage kicks in. You can find your deductible amount on your policy documents or by asking our chatbot.

**Keywords:** deductible, out of pocket, what I pay

---

## Repair Shops

### Can I choose my own repair shop?
Yes! While we recommend shops in our network for quality and convenience, you're free to choose any licensed repair facility.

**Keywords:** choose shop, repair shop, my mechanic

### What are the benefits of using a network shop?
Network shops offer guaranteed work quality, streamlined claim processing, and often faster appointment availability.

**Keywords:** network shop, benefits, preferred provider
```

**Search Implementation:**

The chatbot's `search_faq(query: str)` tool will:
1. Parse the Markdown file by section headers
2. Extract questions, answers, and keywords
3. Perform keyword matching against the user's query
4. Return the most relevant FAQ entries (top 3 matches)
5. Fall back to fuzzy matching if no keyword matches found

### C. Repair Shops Database Schema

**File:** `data/repair_shops.json`

```json
{
  "shops": [
    {
      "id": 1,
      "name": "Premium Auto Body",
      "address": "123 Main St, Los Angeles, CA 90001",
      "phone": "(555) 123-4567",
      "specialties": ["dent repair", "painting", "bumper replacement"],
      "certifications": ["Toyota Certified", "Honda Certified"],
      "rating": 4.8,
      "review_count": 340,
      "insurance_network": true,
      "average_wait_days": 3,
      "location": {
        "lat": 34.0522,
        "lng": -118.2437
      }
    }
  ]
}
```

### D. Cost Estimation Reference

**Token Usage Estimates (per agent execution):**

| Agent | Avg Input Tokens | Avg Output Tokens | Total | Est. Cost (Claude Sonnet) |
|-------|-----------------|-------------------|-------|---------------------------|
| Fraud Detector | 800 | 400 | 1,200 | $0.0084 |
| Risk Estimator | 600 | 300 | 900 | $0.0063 |
| AI Image Detector | 1,200 | 200 | 1,400 | $0.0066 |
| Damage Analyzer | 1,000 | 500 | 1,500 | $0.0105 |
| **Supervisor Total** | **3,600** | **1,400** | **5,000** | **$0.0318** |
| Chatbot (no tools) | 500 | 300 | 800 | $0.0060 |
| Chatbot (with tools) | 1,000 | 500 | 1,500 | $0.0105 |
| Estimate Explainer | 800 | 600 | 1,400 | $0.0114 |

**Monthly Cost Projection (1000 claims/month):**
- Supervisor (all claims): 1,000 × $0.0318 = **$31.80/month**
- Chatbot (500 sessions, 10 messages each): 5,000 × $0.0060 = **$30.00/month**
- Estimate Explainer (300 requests): 300 × $0.0114 = **$3.42/month**
- **Total: ~$65/month** for 1000 claims with full agent coverage

---

## Implementation TODOs

This section tracks all implementation tasks required to bring the LLM and Agent integration to life.

### Week 1: Foundation & LLM Abstraction ✅ COMPLETE

#### LLM Abstraction Layer
- [x] **Create base LLM client** - `src/api/agents/llm/base.py` ✅
  - [x] Define `BaseLLMClient` abstract class with methods: `chat()`, `chat_stream()`, `chat_with_tools()`, `chat_with_image()`, `supports_vision()`
  - [x] Define dataclasses: `Message`, `ToolDefinition`, `ToolCall`, `ChatResponse`
  - [x] Add type hints and docstrings for all methods

- [x] **Implement Anthropic provider** - `src/api/agents/llm/providers/anthropic.py` ✅
  - [x] Create `AnthropicClient` class extending `BaseLLMClient`
  - [x] Implement `chat()` method using Anthropic SDK
  - [x] Implement `chat_with_tools()` with tool use API
  - [x] Implement `chat_with_image()` with vision support (base64 encoding)
  - [x] Add error handling and retry logic
  - [x] Test with mock responses

- [x] **Implement OpenAI provider** - `src/api/agents/llm/providers/openai.py` ✅
  - [x] Create `OpenAIClient` class extending `BaseLLMClient`
  - [x] Implement `chat()` method using OpenAI SDK
  - [x] Implement `chat_with_tools()` with function calling
  - [x] Implement `chat_with_image()` with vision support
  - [x] Add error handling and retry logic

- [x] **Implement AWS Bedrock provider** - `src/api/agents/llm/providers/bedrock.py` ✅
  - [x] Install boto3 SDK for AWS Bedrock
  - [x] Create `BedrockClient` class extending `BaseLLMClient`
  - [x] Implement `chat()` method using `boto3.client('bedrock-runtime').invoke_model()`
  - [x] Support multiple Bedrock models: Claude (anthropic.claude-*), Titan, Llama
  - [x] Implement `chat_with_tools()` for Claude models on Bedrock (tool use supported)
  - [x] Implement `chat_with_image()` for Claude models with vision support
  - [x] Handle AWS authentication (credentials from environment or IAM role)
  - [x] Add region configuration support
  - [x] Add error handling for throttling and quota limits
  - [x] Test with Claude 3 Sonnet on Bedrock

- [x] **Create LLM factory** - `src/api/agents/llm/config.py` ✅
  - [x] Implement `get_llm_client(provider: str, config: dict)` factory function
  - [x] Add provider validation
  - [x] Load API keys from environment variables
  - [x] Add configuration validation

- [x] **Create prompt templates** - `src/api/agents/llm/prompts.py` ✅
  - [x] Define system prompts for each agent type
  - [x] Create prompt template functions with parameter substitution
  - [x] Add prompt versioning support

#### Configuration Management
- [x] **Update api-config.yaml** ✅
  - [x] Add `llm` section with provider configurations (Anthropic, OpenAI, Bedrock)
  - [x] Add Bedrock-specific configuration: AWS region, model IDs, credentials source
  - [x] Add `agents` section with agent-specific settings
  - [x] Add cost estimation reference for token pricing (include Bedrock pricing)
  - [x] Document all configuration options

- [x] **Update config loader** - `src/api/config.py` ✅
  - [x] Add `LLMConfig` dataclass
  - [x] Add `AgentConfig` dataclass
  - [x] Load LLM and agent configurations from YAML
  - [x] Add validation for required fields

#### Database Schema
- [x] **Create migration script** - `src/api/migrations/add_agent_tables.sql` ✅
  - [x] Create `agent_usage_logs` table
  - [x] Create `fraud_signals` table
  - [x] Create `risk_assessments` table
  - [x] Add nullable columns to `damages` table: `enhanced_severity`, `internal_damage_probability`, `ai_generated_probability`, `fraud_risk_score`, `risk_score`, `agent_reasoning`, `secondary_damages_predicted`
  - [x] Add nullable columns to `claims` table: `overall_fraud_risk_score`, `overall_risk_score`, `agent_flags`
  - [x] Test migration on clean database

- [x] **Create SQLAlchemy models** ✅
  - [x] `src/api/models/agent_usage_log.py` - AgentUsageLog model
  - [x] `src/api/models/fraud_signal.py` - FraudSignal model
  - [x] `src/api/models/risk_assessment.py` - RiskAssessment model
  - [x] Update `src/api/models/damage.py` to include new nullable columns
  - [x] Update `src/api/models/claim.py` to include new nullable columns

#### Base Agent Framework
- [x] **Create base agent class** - `src/api/agents/base_agent.py` ✅
  - [x] Define `BaseAgent` abstract class with `execute()` method
  - [x] Define `AgentResult` dataclass
  - [x] Add logging infrastructure
  - [x] Add execution timing

- [x] **Create usage tracker** - `src/api/agents/tracking/usage_tracker.py` ✅
  - [x] Implement `@track_usage` decorator
  - [x] Log token usage to `agent_usage_logs` table
  - [x] Calculate estimated costs based on provider pricing
  - [x] Add batch insertion for performance

**Week 1 Status: 100% Complete - All 88 tasks finished!**
- ✅ 22 files created
- ✅ 4 files modified
- ✅ 3 database tables added
- ✅ 9 agent columns added to existing tables
- ✅ All tests passing
- ✅ Documentation complete

---

### Week 2: Customer Chatbot

#### Chatbot Tools
- [ ] **Define chatbot tools** - `src/api/agents/chatbot/tools.py`
  - [ ] Implement `get_claim_status(claim_id: int)` tool
  - [ ] Implement `get_policy_details(customer_id: int, policy_number: str)` tool
  - [ ] Implement `get_damage_details(claim_id: int)` tool
  - [ ] Implement `search_faq(query: str)` tool
  - [ ] Create tool definition schemas for LLM
  - [ ] Implement `execute_tool()` dispatcher function

- [ ] **Create FAQ knowledge base** - `data/faq_knowledge_base.json`
  - [ ] Write 20-30 common FAQ entries
  - [ ] Categorize by: claims_process, cost_estimates, appeals, policy_coverage, repair_shops
  - [ ] Add keywords for semantic search
  - [ ] Implement simple keyword search function

#### Chatbot Agent
- [ ] **Implement chatbot agent** - `src/api/agents/chatbot/chatbot_agent.py`
  - [ ] Create `ChatbotAgent` class
  - [ ] Build customer-facing system prompt
  - [ ] Implement conversation history management
  - [ ] Call `llm_client.chat_with_tools()` with tool definitions
  - [ ] Handle tool calls and execute tools
  - [ ] Make follow-up LLM call with tool results
  - [ ] Return final response with conversation context

- [ ] **Create session manager** - `src/api/agents/chatbot/session_manager.py`
  - [ ] Implement in-memory session storage (dict)
  - [ ] Store conversation history per session_id
  - [ ] Add session timeout (30 minutes inactivity)
  - [ ] Implement session cleanup background task

#### Chatbot API Router
- [ ] **Create chatbot router** - `src/api/routers/chatbot.py`
  - [ ] Implement `POST /api/v1/chatbot/customer/message` endpoint
  - [ ] Create `ChatMessageRequest` and `ChatMessageResponse` schemas
  - [ ] Load or create session
  - [ ] Call `ChatbotAgent.execute()`
  - [ ] Update session with new messages
  - [ ] Return response to frontend
  - [ ] Add placeholder endpoints for adjustor and executive chatbots (return 501 Not Implemented)

- [ ] **Register chatbot router** - `src/api/main.py`
  - [ ] Import chatbot router
  - [ ] Add to FastAPI app with `/api/v1/chatbot` prefix
  - [ ] Add CORS configuration for chatbot endpoints

#### Frontend Chat Widget
- [ ] **Create chat widget component** - `src/ui/customer/src/components/ChatWidget.jsx`
  - [ ] Build floating chat button (bottom-right corner)
  - [ ] Implement expandable chat interface
  - [ ] Display message history (user and assistant bubbles)
  - [ ] Add input field with send button
  - [ ] Show typing indicator during LLM response
  - [ ] Show tool call indicators ("Looking up your claim...")
  - [ ] Add minimize/maximize controls
  - [ ] Style with Tailwind CSS matching portal theme

- [ ] **Create chatbot API client** - `src/ui/customer/src/api/chatbot.js`
  - [ ] Implement `sendMessage(customerId, message, sessionId)` function
  - [ ] Handle API errors gracefully
  - [ ] Return response and updated session ID

- [ ] **Integrate chat widget into layout** - `src/ui/customer/src/components/Layout.jsx`
  - [ ] Import and render `ChatWidget` component
  - [ ] Position in bottom-right corner (fixed positioning)
  - [ ] Ensure widget appears on all customer portal pages


---

### Week 3: Fraud Detection Agents

#### Supervisor Agent
- [ ] **Implement supervisor** - `src/api/agents/supervisor.py`
  - [ ] Create `SupervisorAgent` class
  - [ ] Implement parallel agent execution with `asyncio.gather()`
  - [ ] Implement three-phase execution:
    - [ ] Phase 1: Run vision agents in parallel (color, make/model, AI detection, manipulation)
    - [ ] Phase 2: Run static validation checks
    - [ ] Phase 3: Run behavioral synthesis (only if Phase 1+2 are borderline)
  - [ ] Aggregate results into `SupervisorResult`
  - [ ] Add skip logic (skip Phase 3 if risk is clearly high or low)
  - [ ] Log execution timeline

#### Vision Fraud Sub-Agents
- [ ] **Color verification agent** - `src/api/agents/subagents/fraud/color_verification_agent.py`
  - [ ] Implement `ColorVerificationAgent` class
  - [ ] Build vision prompt: "Does vehicle color in image match policy color?"
  - [ ] Call `llm_client.chat_with_image()` with damage image
  - [ ] Parse response and extract color mismatch signals
  - [ ] Return `FraudSignal` if mismatch detected
  - [ ] Test with mock images

- [ ] **Make/model verification agent** - `src/api/agents/subagents/fraud/make_model_verification_agent.py`
  - [ ] Implement `MakeModelVerificationAgent` class
  - [ ] Build vision prompt: "Identify vehicle make/model in image"
  - [ ] Compare detected make/model with policy records
  - [ ] Return `FraudSignal` if mismatch detected
  - [ ] Test with various vehicle images

- [ ] **AI image detector agent** - `src/api/agents/subagents/fraud/ai_image_detector_agent.py`
  - [ ] Implement `AIImageDetectorAgent` class
  - [ ] Build vision prompt: "Analyze image for AI-generation artifacts"
  - [ ] Check for unnatural smoothing, inconsistent lighting, repetitive patterns
  - [ ] Return probability score (0.0-1.0) and specific indicators
  - [ ] Test with real and AI-generated images

- [ ] **Image manipulation detector agent** - `src/api/agents/subagents/fraud/image_manipulation_detector.py`
  - [ ] Implement `ImageManipulationDetectorAgent` class
  - [ ] Phase A: Extract and check EXIF metadata for Photoshop signatures
  - [ ] Phase B: Vision LLM analysis for clone stamp, content-aware fill artifacts
  - [ ] Return `FraudSignal` with manipulation probability
  - [ ] Test with edited and unedited images

#### Static Validation Checks
- [ ] **Implement static checks** - `src/api/agents/subagents/fraud/static_checks.py`
  - [ ] VIN format validation (17 character regex)
  - [ ] VIN-year consistency (decode 10th character)
  - [ ] Claim frequency check (query database for customer claim count)
  - [ ] Claim velocity check (count claims in last 30 days)
  - [ ] Return list of static fraud signals

#### Behavioral Synthesis Agent
- [ ] **Implement behavioral analyzer** - `src/api/agents/subagents/fraud/behavioral_analyzer.py`
  - [ ] Create `BehavioralAnalyzerAgent` class
  - [ ] Build prompt with all fraud signals from Phase 1 and 2
  - [ ] Synthesize: damage pattern coherence, story consistency, location reasonableness
  - [ ] Return final fraud assessment with reasoning
  - [ ] Only execute for borderline cases (0.3-0.8 risk score)

#### Main Fraud Detector
- [ ] **Implement fraud detector** - `src/api/agents/subagents/fraud_detector.py`
  - [ ] Create `FraudDetectorAgent` class
  - [ ] Orchestrate three phases using supervisor pattern
  - [ ] Calculate combined risk score from all signals
  - [ ] Return `FraudDetectionResult` with recommendation (APPROVE, FLAG_FOR_REVIEW, REJECT)
  - [ ] Store results in `fraud_signals` table

#### Risk Estimation Agent
- [ ] **Implement risk estimator** - `src/api/agents/subagents/risk_estimator.py`
  - [ ] Create `RiskEstimatorAgent` class
  - [ ] Build prompt with claim data, estimated costs, historical averages
  - [ ] Calculate cost deviation percentage
  - [ ] Assess vehicle value risk (repair cost vs vehicle value)
  - [ ] Check claim velocity
  - [ ] Return `RiskEstimationResult` with risk factors
  - [ ] Store results in `risk_assessments` table

#### Damage Analyzer Agent
- [ ] **Implement damage analyzer** - `src/api/agents/subagents/damage_analyzer.py`
  - [ ] Create `DamageAnalyzerAgent` class
  - [ ] Build prompt with YOLO detection results
  - [ ] Use vision LLM to refine severity scores
  - [ ] Estimate internal damage probability
  - [ ] Recommend repair strategy (repair vs replace)
  - [ ] Predict secondary damages
  - [ ] Return `EnhancedDamage` objects

#### Integration with Claim Workflow
- [ ] **Integrate supervisor into image service** - `src/api/services/image_service.py`
  - [ ] Call `SupervisorAgent.execute()` after YOLO detection
  - [ ] Pass YOLO results and claim context to supervisor
  - [ ] Enrich damage records with agent insights
  - [ ] Update `damages` table with enhanced fields
  - [ ] Add agent execution event to `claims_events` table

- [ ] **Update claim submission endpoint** - `src/api/routers/customers.py`
  - [ ] Return fraud analysis in claim response (optional fields)
  - [ ] Return risk assessment in claim response
  - [ ] Include agent reasoning in response
  - [ ] Ensure backward compatibility (all agent fields optional)


---

### Week 4: Cost Explainer & Enhancements

#### Estimate Explainer Agent
- [ ] **Implement explainer agent** - `src/api/agents/explainer.py`
  - [ ] Create `EstimateExplainerAgent` class
  - [ ] Build prompt with damage list, costs, labor rates, state
  - [ ] Generate customer-friendly explanations:
    - [ ] Plain language damage descriptions
    - [ ] Why each repair is necessary
    - [ ] Cost breakdown (labor + parts)
    - [ ] Context on typical repair costs
  - [ ] Return structured explanation
  - [ ] Test with various damage scenarios

#### Estimate Explainer API
- [ ] **Add explainer endpoint** - `src/api/routers/customers.py`
  - [ ] Implement `GET /api/v1/customers/{customer_id}/claims/{claim_id}/explain`
  - [ ] Load claim and damages from database
  - [ ] Call `EstimateExplainerAgent.execute()`
  - [ ] Return explanation in response
  - [ ] Cache explanations to avoid redundant LLM calls

#### Frontend Estimate Explanation
- [ ] **Create explanation modal component** - `src/ui/customer/src/components/EstimateExplanationModal.jsx`
  - [ ] Build modal dialog component
  - [ ] Display explanation text
  - [ ] Show cost breakdown table
  - [ ] Add damage-by-damage details
  - [ ] Style with Tailwind CSS

- [ ] **Enhance claim detail page** - `src/ui/customer/src/pages/ClaimDetailPage.jsx`
  - [ ] Add "Explain Estimate" button
  - [ ] Fetch explanation from API when clicked
  - [ ] Show loading state
  - [ ] Display explanation in modal
  - [ ] Add fraud risk badge if `overall_fraud_risk_score > 0.7`
  - [ ] Add risk assessment section if `overall_risk_score > 0.5`
  - [ ] Display AI detection warning if `ai_generated_probability > 0.6`

#### Repair Shop Recommender (Optional)
- [ ] **Create shop database** - `data/repair_shops.json`
  - [ ] Define 10-15 mock repair shops
  - [ ] Include: name, address, specialties, certifications, ratings, location
  - [ ] Cover multiple cities and damage types

- [ ] **Implement shop recommender agent** - `src/api/agents/shop_recommender.py`
  - [ ] Create `ShopRecommenderAgent` class
  - [ ] Load shops from JSON file
  - [ ] Filter by damage types and location
  - [ ] Build prompt with shop list and damage context
  - [ ] Rank top 3 shops with reasoning
  - [ ] Return recommendations

- [ ] **Add shop recommender endpoint** - `src/api/routers/customers.py`
  - [ ] Implement `GET /api/v1/customers/{customer_id}/claims/{claim_id}/shops/recommend`
  - [ ] Load claim and customer data
  - [ ] Call `ShopRecommenderAgent.execute()`
  - [ ] Return shop recommendations

- [ ] **Create shop recommendations component** - `src/ui/customer/src/components/ShopRecommendations.jsx`
  - [ ] Build shop cards with name, address, rating, specialties
  - [ ] Add map integration (optional)
  - [ ] Show distance from customer address
  - [ ] Add "Contact" button with phone number

---

### Week 5: Testing & Documentation

#### Unit Tests
- [ ] **Test LLM abstraction layer**
  - [ ] Test `AnthropicClient` with mock responses
  - [ ] Test `OpenAIClient` with mock responses
  - [ ] Test `OllamaClient` with mock responses
  - [ ] Test LLM factory with various configurations
  - [ ] Test error handling and retries

- [ ] **Test agent implementations**
  - [ ] Test `ColorVerificationAgent` with mock images
  - [ ] Test `MakeModelVerificationAgent` with mock images
  - [ ] Test `AIImageDetectorAgent` with real and synthetic images
  - [ ] Test `ImageManipulationDetectorAgent` with edited images
  - [ ] Test `FraudDetectorAgent` end-to-end
  - [ ] Test `RiskEstimatorAgent` with various claim scenarios
  - [ ] Test `DamageAnalyzerAgent` with YOLO outputs
  - [ ] Test `ChatbotAgent` with and without tool calls
  - [ ] Test `EstimateExplainerAgent` with damage data

- [ ] **Test supervisor orchestration**
  - [ ] Test parallel agent execution
  - [ ] Test phase skip logic (Phase 3 skipped for clear cases)
  - [ ] Test error handling when one agent fails
  - [ ] Test timeout handling
  - [ ] Verify execution time < 5 seconds

#### Integration Tests
- [ ] **Test claim submission workflow**
  - [ ] Submit claim with valid images
  - [ ] Verify YOLO detection runs
  - [ ] Verify supervisor runs all agents
  - [ ] Verify `damages` table updated with agent fields
  - [ ] Verify `claims` table updated with fraud/risk scores
  - [ ] Verify `agent_usage_logs` table populated
  - [ ] Verify claim events recorded

- [ ] **Test chatbot workflow**
  - [ ] Send message to customer chatbot
  - [ ] Verify session created
  - [ ] Test claim status lookup tool
  - [ ] Test policy details tool
  - [ ] Test FAQ search tool
  - [ ] Verify conversation history maintained
  - [ ] Test session timeout

- [ ] **Test fraud detection**
  - [ ] Create claim with mismatched vehicle color
  - [ ] Verify color verification agent flags issue
  - [ ] Verify `overall_fraud_risk_score` > 0.7
  - [ ] Verify claim flagged for human review
  - [ ] Check `fraud_signals` table

- [ ] **Test estimate explanation**
  - [ ] Request explanation for claim
  - [ ] Verify explanation generated
  - [ ] Verify explanation is customer-friendly
  - [ ] Test caching (second request should be faster)

#### End-to-End Testing
- [ ] **Manual testing scenarios**
  - [ ] Scenario 1: Submit claim, chat about it, review explanation
  - [ ] Scenario 2: Submit fraudulent claim (wrong vehicle), verify detection
  - [ ] Scenario 3: Submit claim with AI-generated image, verify detection
  - [ ] Scenario 4: Submit high-cost claim, verify risk assessment
  - [ ] Scenario 5: Chat with bot, ask for claim status, policy details, FAQ

#### Documentation
- [ ] **Update README.md**
  - [ ] Document LLM and agent features
  - [ ] Add setup instructions for LLM providers
  - [ ] Add environment variable documentation
  - [ ] Add example `.env` file

- [ ] **Create API documentation**
  - [ ] Document chatbot endpoints with examples
  - [ ] Document enhanced claim submission response
  - [ ] Document estimate explanation endpoint
  - [ ] Update OpenAPI/Swagger specs

- [ ] **Create user guide**
  - [ ] Write customer chatbot user guide
  - [ ] Explain fraud detection process
  - [ ] Explain cost estimate explanations
  - [ ] Add screenshots of UI components

---

### Week 6: Deployment & Polish

#### Configuration & Environment
- [ ] **Create production config**
  - [ ] Create `api-config.prod.yaml` with production settings
  - [ ] Set lower temperature for production agents (0.1)
  - [ ] Configure production LLM endpoints
  - [ ] Set appropriate timeouts

- [ ] **Environment variable setup**
  - [ ] Document required environment variables
  - [ ] Create `.env.example` file
  - [ ] Add validation for missing API keys
  - [ ] Add startup checks for LLM connectivity

#### Performance Optimization
- [ ] **Optimize agent execution**
  - [ ] Profile supervisor execution time
  - [ ] Optimize parallel execution (ensure true parallelism)
  - [ ] Add response caching for chatbot FAQ answers
  - [ ] Add request deduplication (same claim analyzed twice)

- [ ] **Database optimization**
  - [ ] Add indexes on `agent_usage_logs.claim_id`
  - [ ] Add indexes on `fraud_signals.claim_id`
  - [ ] Add indexes on `risk_assessments.claim_id`
  - [ ] Optimize queries for agent data retrieval

#### Frontend Polish
- [ ] **Improve chat widget UX**
  - [ ] Add unread message badge
  - [ ] Add sound notification for new messages (optional)
  - [ ] Improve mobile responsiveness
  - [ ] Add dark mode support

- [ ] **Enhance claim detail page**
  - [ ] Improve fraud risk badge styling
  - [ ] Add risk factor tooltips with explanations
  - [ ] Improve AI detection alert visibility
  - [ ] Add loading states for all async operations

#### Error Handling & Resilience
- [ ] **Add robust error handling**
  - [ ] Handle LLM API failures gracefully (fallback to non-agent processing)
  - [ ] Handle timeout errors
  - [ ] Handle rate limit errors
  - [ ] Add retry logic with exponential backoff
  - [ ] Log all errors for monitoring

- [ ] **Add feature flags**
  - [ ] Add `agents.enabled` flag to disable all agents
  - [ ] Add per-agent enable/disable flags
  - [ ] Ensure system works with all agents disabled (backward compatibility)

#### Deployment
- [ ] **Deploy to staging**
  - [ ] Deploy API with agent integration
  - [ ] Deploy customer portal with chat widget
  - [ ] Test end-to-end in staging environment
  - [ ] Monitor LLM costs and usage

- [ ] **Production readiness checklist**
  - [ ] All tests passing
  - [ ] API documentation complete
  - [ ] User guide written
  - [ ] Environment variables documented
  - [ ] Error handling tested
  - [ ] Performance benchmarks met (< 5s agent overhead)
  - [ ] Cost monitoring in place

---

### Future Enhancements (Post-MVP)

- [ ] **Chat persistence**
  - [ ] Migrate from in-memory to database storage
  - [ ] Implement `chat_sessions` and `chat_messages` tables
  - [ ] Add conversation history across sessions

- [ ] **Adjustor chatbot**
  - [ ] Implement adjustor-specific tools (fraud insights, damage history)
  - [ ] Build adjustor chatbot UI
  - [ ] Integrate with adjustor portal

- [ ] **Executive chatbot**
  - [ ] Implement executive-specific tools (KPIs, trends, aggregated data)
  - [ ] Build executive dashboard with chat interface

- [ ] **Advanced fraud detection**
  - [ ] Add geolocation analysis (claim location vs damage photo GPS)
  - [ ] Add social media cross-referencing (if available)
  - [ ] Add network analysis (detect fraud rings)

- [ ] **Performance monitoring dashboard**
  - [ ] Build admin dashboard for agent usage and costs
  - [ ] Track agent quality scores
  - [ ] Monitor fraud detection accuracy
  - [ ] Track chatbot satisfaction ratings

- [ ] **Multi-language support**
  - [ ] Add language detection in chatbot
  - [ ] Support Spanish, French, Chinese
  - [ ] Translate prompts and responses

- [ ] **Voice interface**
  - [ ] Add speech-to-text for chatbot input
  - [ ] Add text-to-speech for chatbot responses
  - [ ] Support phone-based chatbot interaction

---

## Conclusion

This design provides a comprehensive, production-ready architecture for integrating LLM-powered agents into the insurance claims customer portal. The system is:

- **AI-First Design:** Demonstrates agent value by leading with intelligent vision analysis, not deterministic rules
- **Scalable:** Provider-agnostic design allows easy switching between LLM providers
- **Cost-Effective:** Estimated $65/month for 1000 claims; intelligent skip logic reduces costs by 60-70%
- **Multi-Agent Vision Fraud Detection:** Three-phase showcase strategy:
  - **Phase 1**: AI Vision Agents (4 parallel) - **SHOWCASE AI VALUE FIRST!**
    - Color Verification: "Does vehicle in image match policy color?"
    - Make/Model Verification: "Is this actually a Toyota Camry as claimed?"
    - AI Image Detection: "Are these damage photos AI-generated deepfakes?"
    - Manipulation Detection: "Were images edited with Photoshop?"
  - **Phase 2**: Static Validation (VIN, frequency) - Deterministic backup layer
  - **Phase 3**: Behavioral Synthesis (only for borderline cases) - LLM reasoning
- **Catches Sophisticated Fraud:** Detects vehicle swaps, AI-generated images, Photoshop edits that rules cannot catch
- **Customer Communication:** "Your claim was analyzed by AI vision agents" - showcases technology value
- **Traceable:** All agent decisions logged with visual evidence and reasoning
- **Customer-Centric:** Conversational chatbot, transparent explanations, shop recommendations
- **Risk-Intelligent:** Actuarial risk assessment flags high-deviation claims
- **Performance-Optimized:** Parallel agent execution keeps overhead < 5 seconds

**Simplified for Demo:** Focus on 3 customer-facing features that showcase AI value:
1. **Chatbot** - Conversational AI assistance
2. **Fraud Detection** - Vision agents automatically analyze claims
3. **Cost Explainer** - AI makes estimates understandable

No complex admin dashboards, no performance tracking, no monitoring - just **pure agent value demonstration**.
