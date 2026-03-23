// Multi-agent management types

export interface AgentSummary {
  id: string;
  name: string;
  description: string;
  workspace_dir: string;
}

export interface AgentListResponse {
  agents: AgentSummary[];
}

export interface AgentProfileConfig {
  id: string;
  name: string;
  description?: string;
  workspace_dir?: string;
  channels?: unknown;
  mcp?: unknown;
  heartbeat?: unknown;
  running?: unknown;
  llm_routing?: unknown;
  system_prompt_files?: string[];
  tools?: unknown;
  security?: unknown;
}

export interface CreateAgentRequest {
  name: string;
  description?: string;
  workspace_dir?: string;
  language?: string;
}

export interface AgentProfileRef {
  id: string;
  workspace_dir: string;
}

// Natural language agent creation types
export interface CreateAgentFromTextRequest {
  description: string;
  language?: string;
}

export interface GeneratedConfig {
  name: string;
  description: string;
  identity: string;
  style: string;
  capabilities: string[];
}

export interface CreateAgentFromTextResponse {
  agent_id: string;
  name: string;
  description: string;
  workspace_dir: string;
  generated_config: GeneratedConfig;
  message: string;
}
