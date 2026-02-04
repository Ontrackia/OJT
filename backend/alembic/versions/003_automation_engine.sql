"""
Database Migration: Automation Engine Tables
Creates schema and tables for automation system
"""

-- ==========================================
-- SCHEMA AUTOMATION
-- ==========================================

CREATE SCHEMA IF NOT EXISTS automation;

-- ==========================================
-- AUTOMATION EVENTS (Transactional Outbox)
-- ==========================================

CREATE TABLE automation.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Event details
    type VARCHAR(100) NOT NULL,  -- 'finding.created', 'checkpoint.status_changed'
    entity_type VARCHAR(50) NOT NULL,  -- 'finding', 'audit', 'checkpoint'
    entity_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    
    -- Processing
    processed_at TIMESTAMP,
    trace_id VARCHAR(100),  -- Correlación logs
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_tenant_type_created ON automation.events(tenant_id, type, created_at);
CREATE INDEX idx_events_processed ON automation.events(processed_at) WHERE processed_at IS NULL;
CREATE INDEX idx_events_trace ON automation.events(trace_id);

-- ==========================================
-- AUTOMATION RULES
-- ==========================================

CREATE TABLE automation.rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Rule details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,  -- Mayor = más prioritario
    
    -- Trigger
    trigger_event VARCHAR(100) NOT NULL,  -- 'checkpoint.status_changed'
    
    -- Conditions (JSON logic)
    conditions JSONB NOT NULL,
    
    -- Actions (lista de pasos)
    actions JSONB NOT NULL,
    
    -- Metadata
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rules_tenant_trigger_enabled ON automation.rules(tenant_id, trigger_event, enabled);
CREATE INDEX idx_rules_priority ON automation.rules(priority DESC);

-- ==========================================
-- AUTOMATION JOBS
-- ==========================================

CREATE TABLE automation.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Job details
    job_type VARCHAR(100) NOT NULL,  -- 'send_email', 'create_calendar_event'
    payload JSONB NOT NULL,
    
    -- Scheduling
    run_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Status
    status VARCHAR(20) DEFAULT 'queued',  -- queued, running, done, failed, dead
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Idempotency
    idempotency_key VARCHAR(200) NOT NULL,
    
    -- Error handling
    last_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_jobs_tenant_status_run_at ON automation.jobs(tenant_id, status, run_at);
CREATE UNIQUE INDEX idx_jobs_idempotency ON automation.jobs(tenant_id, idempotency_key);
CREATE INDEX idx_jobs_status ON automation.jobs(status) WHERE status IN ('queued', 'failed');

-- ==========================================
-- AUTOMATION LOGS
-- ==========================================

CREATE TABLE automation.logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- References
    job_id UUID REFERENCES automation.jobs(id),
    event_id UUID REFERENCES automation.events(id),
    rule_id UUID REFERENCES automation.rules(id),
    
    -- Log details
    step VARCHAR(100),
    status VARCHAR(20),  -- success, error, warning
    message TEXT,
    duration_ms INTEGER,
    error TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_logs_tenant_created ON automation.logs(tenant_id, created_at);
CREATE INDEX idx_logs_job ON automation.logs(job_id);
CREATE INDEX idx_logs_status ON automation.logs(status) WHERE status = 'error';

-- ==========================================
-- AI PROVIDERS
-- ==========================================

CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Provider config
    provider_type VARCHAR(50) NOT NULL,  -- 'openai', 'anthropic', 'azure', 'ollama', 'custom'
    provider_name VARCHAR(100),
    
    -- Configuration (encrypted in production)
    config JSONB NOT NULL,
    
    -- Priority & defaults
    is_default BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 0,
    
    -- Limits
    max_requests_per_month INTEGER,
    max_tokens_per_request INTEGER,
    max_tokens_per_month INTEGER,
    
    -- Status
    enabled BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_ai_providers_tenant_default ON ai_providers(tenant_id, is_default);
CREATE INDEX idx_ai_providers_tenant_enabled ON ai_providers(tenant_id, enabled);

-- ==========================================
-- AI INTERACTION LOGS (AI Act Compliance)
-- ==========================================

CREATE TABLE ai_interaction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Context
    audit_id VARCHAR(100),
    module VARCHAR(50),  -- 'audit', 'moe', 'ojt', 'license'
    user_id INTEGER NOT NULL,
    
    -- Provider
    provider_type VARCHAR(50),
    model VARCHAR(100),
    
    -- Request/Response (hashed for privacy)
    prompt_hash VARCHAR(64),  -- SHA256
    response_hash VARCHAR(64),
    
    -- Full text (encrypted, for audit)
    prompt_encrypted TEXT,
    response_encrypted TEXT,
    
    -- Metadata
    tokens_used INTEGER,
    duration_ms INTEGER,
    confidence_score FLOAT,
    
    -- Human validation (OBLIGATORIO)
    human_validated BOOLEAN DEFAULT false,
    validated_by INTEGER,
    validated_at TIMESTAMP,
    validation_notes TEXT,
    
    -- Retention (AI Act)
    retention_until TIMESTAMP,  -- 5 años
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_ai_logs_tenant_module ON ai_interaction_logs(tenant_id, module, created_at);
CREATE INDEX idx_ai_logs_audit ON ai_interaction_logs(audit_id);
CREATE INDEX idx_ai_logs_validation ON ai_interaction_logs(human_validated, validated_at);
CREATE INDEX idx_ai_logs_retention ON ai_interaction_logs(retention_until);

-- ==========================================
-- INTEGRATION CONNECTORS
-- ==========================================

CREATE TABLE integration_connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    
    -- Connector details
    connector_type VARCHAR(50) NOT NULL,  -- 'amos', 'sharepoint', 'sap_sf'
    connector_name VARCHAR(100),
    
    -- Configuration (encrypted)
    config JSONB NOT NULL,
    
    -- Status
    enabled BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    last_error TEXT,
    
    -- Feature flags
    read_enabled BOOLEAN DEFAULT true,
    write_enabled BOOLEAN DEFAULT false,  -- Empezar solo lectura
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_connectors_tenant_type ON integration_connectors(tenant_id, connector_type);
CREATE INDEX idx_connectors_enabled ON integration_connectors(enabled);

-- ==========================================
-- INTEGRATION LOGS
-- ==========================================

CREATE TABLE integration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER NOT NULL,
    connector_id UUID REFERENCES integration_connectors(id),
    
    -- Action details
    action VARCHAR(100),  -- 'sync_work_orders', 'create_meeting'
    status VARCHAR(20),   -- 'success', 'error', 'warning'
    
    -- Metadata
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    duration_ms INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_integration_logs_tenant_created ON integration_logs(tenant_id, created_at);
CREATE INDEX idx_integration_logs_connector ON integration_logs(connector_id);
CREATE INDEX idx_integration_logs_status ON integration_logs(status) WHERE status = 'error';

-- ==========================================
-- COMMENTS
-- ==========================================

COMMENT ON SCHEMA automation IS 'Automation Engine: events, rules, jobs, logs';
COMMENT ON TABLE automation.events IS 'Transactional outbox for event-driven architecture';
COMMENT ON TABLE automation.rules IS 'Automation rules with JSON conditions and actions';
COMMENT ON TABLE automation.jobs IS 'Job queue for async execution';
COMMENT ON TABLE automation.logs IS 'Audit trail of automation executions';
COMMENT ON TABLE ai_providers IS 'AI provider configuration per tenant (OpenAI, Ollama, custom)';
COMMENT ON TABLE ai_interaction_logs IS 'AI Act compliant logging with 5-year retention';
COMMENT ON TABLE integration_connectors IS 'External system connectors (AMOS, SharePoint, SAP, etc.)';
COMMENT ON TABLE integration_logs IS 'Integration execution logs';
