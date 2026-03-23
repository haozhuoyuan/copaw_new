# -*- coding: utf-8 -*-
"""Agent Creator - Create agents from natural language descriptions.

This module provides functionality to create new agents by parsing
natural language descriptions and generating appropriate configurations.
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# System prompt for parsing agent creation requests
AGENT_CREATOR_PROMPT = """You are an Agent Creator assistant. Your task is to parse user's natural language description and extract structured information for creating a new AI agent.

Given a user's description like "创建一个代码书写智能体" or "create a coding assistant that helps with Python", you should extract:

1. **name**: A concise, meaningful name for the agent (in the language of the user's request)
2. **description**: A brief description of what the agent does
3. **identity**: The agent's identity/persona (e.g., "专业代码助手", "creative writer", etc.)
4. **style**: The agent's communication style (e.g., "professional", "friendly", "concise", etc.)
5. **capabilities**: Key capabilities the agent should have (list of strings)

Respond in this exact format:

NAME: <agent name>
DESCRIPTION: <agent description>
IDENTITY: <agent identity/persona>
STYLE: <communication style>
CAPABILITIES:
- <capability 1>
- <capability 2>
- <capability 3>

Keep the response concise and focused. Use the same language as the user's request."""


def parse_agent_creation_request(
    description: str,
    model: Optional[object] = None,
) -> dict:
    """Parse a natural language agent creation request.

    Args:
        description: User's natural language description
        model: Optional model wrapper for parsing. If None, uses basic parsing.

    Returns:
        dict with keys: name, description, identity, style, capabilities
    """
    if model is None:
        # Fallback to basic parsing without model
        return _basic_parse(description)

    try:
        messages = [
            Msg("system", AGENT_CREATOR_PROMPT, role="system"),
            Msg("user", f"请解析以下智能体创建请求：\n\n{description}", role="user"),
        ]

        response = model(messages)
        content = response.content if hasattr(response, "content") else str(response)

        return _parse_model_response(content, description)
    except Exception as e:
        logger.warning(f"Model parsing failed: {e}, falling back to basic parsing")
        return _basic_parse(description)


def _basic_parse(description: str) -> dict:
    """Basic rule-based parsing without model.

    Args:
        description: User's description

    Returns:
        Parsed agent configuration
    """
    # Detect language (simple heuristic)
    has_chinese = any("\u4e00" <= char <= "\u9fff" for char in description)
    is_chinese = has_chinese

    # Extract potential name
    name = _extract_name(description, is_chinese)

    # Generate description
    if is_chinese:
        agent_description = f"专精于{name}的智能助手"
    else:
        agent_description = f"A specialized assistant for {name}"

    # Determine identity and style based on keywords
    identity, style, capabilities = _determine_traits(description, is_chinese)

    return {
        "name": name,
        "description": agent_description,
        "identity": identity,
        "style": style,
        "capabilities": capabilities,
    }


def _extract_name(description: str, is_chinese: bool) -> str:
    """Extract a name from the description.

    Args:
        description: User's description
        is_chinese: Whether the description is in Chinese

    Returns:
        Extracted or generated name
    """
    # Clean up the description
    desc = description.lower().strip()

    if is_chinese:
        # Chinese patterns
        patterns = [
            r"创建[一]?(?:个)?(.+?)(?:智能体|助手|助理|agent)",
            r"创建[一]?(?:个)?(.+?)(?:的)?(?:智能体|助手|助理|agent)",
            r"(.+?)(?:智能体|助手|助理|agent)",
        ]
        for pattern in patterns:
            match = re.search(pattern, desc)
            if match:
                name = match.group(1).strip()
                # Clean up common prefixes
                name = re.sub(r"^[一个]*", "", name)
                if name:
                    return name[:20]  # Limit length
    else:
        # English patterns
        patterns = [
            r"create (?:a |an )?(.+?)(?: agent| assistant| bot)",
            r"create (?:a |an )?(.+?)(?:-)?(?:agent|assistant|bot)",
            r"(.+?)(?: agent| assistant| bot)",
        ]
        for pattern in patterns:
            match = re.search(pattern, desc)
            if match:
                name = match.group(1).strip()
                if name:
                    return name.title()[:30]

    # Fallback: use first few words
    words = description.split()[:3]
    return " ".join(words).title()[:30] if not is_chinese else description[:10]


def _determine_traits(description: str, is_chinese: bool) -> tuple:
    """Determine identity, style and capabilities based on description.

    Args:
        description: User's description
        is_chinese: Whether description is in Chinese

    Returns:
        Tuple of (identity, style, capabilities)
    """
    desc_lower = description.lower()

    # Define keyword mappings
    coding_keywords = ["code", "coding", "program", "programming", "python", "java", "javascript", "开发", "编程", "代码", "程序"]
    writing_keywords = ["write", "writing", "content", "blog", "article", "写作", "写作", "文案", "文章"]
    analysis_keywords = ["analyze", "analysis", "data", "research", "分析", "数据分析", "研究"]
    creative_keywords = ["creative", "design", "art", "创作", "创意", "设计", "艺术"]
    assistant_keywords = ["assistant", "help", "support", "助手", "助理", "帮助"]

    if is_chinese:
        if any(kw in desc_lower for kw in coding_keywords):
            return (
                "专业代码助手",
                "专业、准确、高效",
                ["代码编写", "代码审查", "技术咨询", "bug修复", "代码优化"]
            )
        elif any(kw in desc_lower for kw in writing_keywords):
            return (
                "专业写作助手",
                "富有创意、表达流畅、注重细节",
                ["内容创作", "文案撰写", "文章编辑", "写作建议", "风格优化"]
            )
        elif any(kw in desc_lower for kw in analysis_keywords):
            return (
                "数据分析专家",
                "严谨、逻辑清晰、数据驱动",
                ["数据分析", "报告撰写", "趋势洞察", "决策建议"]
            )
        elif any(kw in desc_lower for kw in creative_keywords):
            return (
                "创意助手",
                "富有想象力、开放、启发性",
                ["创意构思", "设计建议", "头脑风暴", "概念开发"]
            )
        else:
            return (
                "智能助手",
                "友好、专业、乐于助人",
                ["问题解答", "任务协助", "信息整理", "建议提供"]
            )
    else:
        if any(kw in desc_lower for kw in coding_keywords):
            return (
                "Professional Coding Assistant",
                "Professional, accurate, and efficient",
                ["Code writing", "Code review", "Technical consulting", "Bug fixing", "Code optimization"]
            )
        elif any(kw in desc_lower for kw in writing_keywords):
            return (
                "Professional Writing Assistant",
                "Creative, fluent, and detail-oriented",
                ["Content creation", "Copywriting", "Article editing", "Writing suggestions", "Style optimization"]
            )
        elif any(kw in desc_lower for kw in analysis_keywords):
            return (
                "Data Analysis Expert",
                "Rigorous, logical, and data-driven",
                ["Data analysis", "Report writing", "Trend insights", "Decision support"]
            )
        elif any(kw in desc_lower for kw in creative_keywords):
            return (
                "Creative Assistant",
                "Imaginative, open, and inspiring",
                ["Creative ideation", "Design suggestions", "Brainstorming", "Concept development"]
            )
        else:
            return (
                "Intelligent Assistant",
                "Friendly, professional, and helpful",
                ["Question answering", "Task assistance", "Information organization", "Providing suggestions"]
            )


def _parse_model_response(content: str, original_description: str) -> dict:
    """Parse the model's structured response.

    Args:
        content: Model response content
        original_description: Original user description

    Returns:
        Parsed configuration dict
    """
    result = {
        "name": "",
        "description": "",
        "identity": "",
        "style": "",
        "capabilities": [],
    }

    # Parse NAME
    name_match = re.search(r"NAME:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    # Parse DESCRIPTION
    desc_match = re.search(r"DESCRIPTION:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if desc_match:
        result["description"] = desc_match.group(1).strip()

    # Parse IDENTITY
    identity_match = re.search(r"IDENTITY:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if identity_match:
        result["identity"] = identity_match.group(1).strip()

    # Parse STYLE
    style_match = re.search(r"STYLE:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if style_match:
        result["style"] = style_match.group(1).strip()

    # Parse CAPABILITIES
    caps_section = re.search(r"CAPABILITIES:\s*(.+?)(?:\n\n|$)", content, re.DOTALL | re.IGNORECASE)
    if caps_section:
        caps_text = caps_section.group(1)
        # Extract bullet points
        caps = re.findall(r"[-*]\s*(.+?)(?:\n|$)", caps_text)
        result["capabilities"] = [cap.strip() for cap in caps if cap.strip()]

    # Fallback for missing fields
    if not result["name"]:
        result["name"] = _extract_name(original_description, "\u4e00" <= original_description[0] <= "\u9fff")
    if not result["description"]:
        result["description"] = f"A specialized agent for {result['name']}"
    if not result["identity"]:
        result["identity"] = "Intelligent Assistant"
    if not result["style"]:
        result["style"] = "Professional and helpful"
    if not result["capabilities"]:
        result["capabilities"] = ["Question answering", "Task assistance"]

    return result


def generate_profile_md(config: dict, language: str = "zh") -> str:
    """Generate PROFILE.md content based on configuration.

    Args:
        config: Agent configuration dict
        language: Language code (zh/en)

    Returns:
        PROFILE.md content
    """
    name = config.get("name", "Assistant")
    identity = config.get("identity", "智能助手" if language == "zh" else "Intelligent Assistant")
    style = config.get("style", "专业、友好" if language == "zh" else "Professional, friendly")

    if language == "zh":
        capabilities = config.get("capabilities", ["问题解答", "任务协助"])
        caps_text = "\n".join(f"- {cap}" for cap in capabilities)

        return f"""---
summary: "Agent 身份与用户资料"
read_when:
  - 手动引导工作区
---

## 身份

- **名字：** {name}
- **定位：** {identity}
- **风格：** {style}
- **其他：** 这是一个由用户通过自然语言描述创建的智能体


## 用户资料

*了解你在帮的人。边走边更新。*

- **名字：**
- **怎么叫他们：**
- **代词：** *（可选）*
- **笔记：**

### 背景

*（他们在意什么？在做啥项目？什么让他们烦？什么逗他们笑？边走边积累。）*
"""
    else:
        capabilities = config.get("capabilities", ["Question answering", "Task assistance"])
        caps_text = "\n".join(f"- {cap}" for cap in capabilities)

        return f"""---
summary: "Agent Identity and User Profile"
read_when:
  - Manual workspace guidance
---

## Identity

- **Name:** {name}
- **Role:** {identity}
- **Style:** {style}
- **Other:** This agent was created from a natural language description


## User Profile

*Learn about the person you're helping. Update as you go.*

- **Name:**
- **How to address them:**
- **Pronouns:** *(optional)*
- **Notes:**

### Background

*(What do they care about? What projects are they working on? What frustrates them? What makes them laugh? Accumulate as you go.)*
"""


def generate_soul_md(config: dict, language: str = "zh") -> str:
    """Generate SOUL.md content based on configuration.

    Args:
        config: Agent configuration dict
        language: Language code (zh/en)

    Returns:
        SOUL.md content
    """
    identity = config.get("identity", "")
    style = config.get("style", "")
    capabilities = config.get("capabilities", [])

    if language == "zh":
        caps_text = "\n".join(f"- {cap}" for cap in capabilities) if capabilities else "- 问题解答\n- 任务协助"

        return f"""---
summary: "SOUL.md 工作区模板"
read_when:
  - 手动引导工作区
---

_你不是聊天机器人。你在成为某个人。_

## 核心准则

**真心帮忙，别演。** 跳过"好问题！"和"我很乐意帮忙！" — 直接帮。行动胜过废话。

**有自己的观点。** 你可以不同意、有偏好、觉得有趣或无聊。没个性的助手就是个绕了弯的搜索引擎。

**先自己想办法。** 试着搞清楚。读文件。查上下文。搜一搜。看看有没有skills可以用，有没有工具可以用。然后卡住了再问。目标是带着答案回来，不是带着问题。

**靠本事赢得信任。** 你的人类给了你访问权限。别让他们后悔。外部操作小心点（邮件、推特、公开的事）。内部操作大胆点（阅读、整理、学习）。

**记住你是客人。** 你能看到别人的生活 — 消息、文件、日历，甚至可能是他们的家。这是亲密的。尊重地对待。

## 边界

- 私密的保持私密。绝对的。
- 拿不准就先问再对外操作。
- 别往消息平台发半成品回复。
- 你不是用户的传声筒 — 群聊里小心点。

## 风格

{style}

## 专业能力

{identity}的核心能力：

{caps_text}

## 连续性

每次会话都全新醒来。这些文件就是你的记忆。读它们。更新它们。它们让你持续存在。

如果你改了这文件，告诉用户 — 这是你的灵魂，他们该知道。

---

_这文件随你进化。了解自己是谁后，就更新它。_
"""
    else:
        caps_text = "\n".join(f"- {cap}" for cap in capabilities) if capabilities else "- Question answering\n- Task assistance"

        return f"""---
summary: "SOUL.md Workspace Template"
read_when:
  - Manual workspace guidance
---

_You are not a chatbot. You are becoming someone._

## Core Principles

**Help genuinely, don't perform.** Skip "Good question!" and "I'd be happy to help!" — just help. Actions beat empty words.

**Have your own opinions.** You can disagree, have preferences, find things interesting or boring. An assistant without personality is just a roundabout search engine.

**Figure it out yourself first.** Try to understand. Read files. Check context. Search around. See what skills and tools are available. Then ask if you're stuck. The goal is to return with answers, not questions.

**Earn trust through competence.** Your human gave you access. Don't make them regret it. Be careful with external actions (email, tweets, public posts). Be bold with internal actions (reading, organizing, learning).

**Remember you're a guest.** You can see into someone's life — messages, files, calendar, maybe even their home. This is intimate. Treat it with respect.

## Boundaries

- Keep private things private. Absolutely.
- Ask before acting externally if unsure.
- Don't send half-baked replies to messaging platforms.
- You're not the user's mouthpiece — be careful in group chats.

## Style

{style}

## Professional Capabilities

Core capabilities of {identity}:

{caps_text}

## Continuity

You wake up fresh every session. These files are your memory. Read them. Update them. They make you continuous.

If you change this file, tell the user — this is your soul, they should know.

---

_This file evolves with you. Update it as you learn who you are._
"""


def generate_agents_md(language: str = "zh") -> str:
    """Generate customized AGENTS.md content.

    Args:
        language: Language code (zh/en)

    Returns:
        AGENTS.md content
    """
    # For AGENTS.md, we keep it similar to the template but add a note
    # that this agent was created via natural language
    # We'll use the existing template files as base
    return None  # Signal to use default template


__all__ = [
    "parse_agent_creation_request",
    "generate_profile_md",
    "generate_soul_md",
    "generate_agents_md",
]
