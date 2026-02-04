-- ==========================================
-- Master Audit Log Table - Aviation Compliance
-- Immutable black box for FAA/EASA/CASA traceability
-- ==========================================

CREATE TABLE IF NOT EXISTS system_audit_logs (
    id SERIAL PRIMARY KEY,
    
    -- Tenant Isolation (RLS)
    tenant_id INTEGER NOT NULL,
    
    -- User Information
    user_id INTEGER NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    
    -- Action Details
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    action_type VARCHAR(100) NOT NULL,  -- CREATE, UPDATE, DELETE, CLOSE, VALIDATE
    action_description TEXT NOT NULL,
    
    -- Entity Information
    entity_type VARCHAR(100) NOT NULL,  -- AUDIT, FINDING, RCA, SMS, CAPA
    entity_id VARCHAR(255) NOT NULL,
    
    -- Change Tracking
    previous_state JSONB,
    new_state JSONB,
    changes_summary TEXT,
    
    -- Forensic Information
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent TEXT,
    device_info JSONB,
    
    -- Request Context
    request_id VARCHAR(100),
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    
    -- Integrity Hash (SHA-256)
    entry_hash VARCHAR(64) NOT NULL UNIQUE,
    previous_hash VARCHAR(64),
    
    -- Metadata
    severity VARCHAR(20) DEFAULT 'INFO',
    tags JSONB
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

CREATE INDEX idx_audit_tenant_timestamp ON system_audit_logs(tenant_id, timestamp DESC);
CREATE INDEX idx_audit_user_action ON system_audit_logs(user_id, action_type);
CREATE INDEX idx_audit_entity ON system_audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_timestamp_desc ON system_audit_logs(timestamp DESC);
CREATE INDEX idx_audit_hash ON system_audit_logs(entry_hash);

-- ==========================================
-- ROW-LEVEL SECURITY (RLS)
-- ==========================================

ALTER TABLE system_audit_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see logs from their tenant
CREATE POLICY tenant_isolation_audit_logs ON system_audit_logs
    FOR ALL
    USING (tenant_id = get_current_organization_id())
    WITH CHECK (tenant_id = get_current_organization_id());

-- ==========================================
-- IMMUTABILITY PROTECTION
-- ==========================================

-- Prevent updates and deletes (audit log is append-only)
CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'Audit logs are immutable and cannot be updated';
    ELSIF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Audit logs are immutable and cannot be deleted';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER protect_audit_log_immutability
    BEFORE UPDATE OR DELETE ON system_audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_log_modification();

-- ==========================================
-- INTEGRITY VERIFICATION FUNCTION
-- ==========================================

CREATE OR REPLACE FUNCTION verify_audit_chain_integrity(
    p_tenant_id INTEGER,
    p_start_id INTEGER DEFAULT NULL,
    p_end_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    is_valid BOOLEAN,
    broken_at INTEGER,
    expected_hash VARCHAR(64),
    actual_hash VARCHAR(64)
) AS $$
DECLARE
    v_current_log RECORD;
    v_previous_hash VARCHAR(64);
BEGIN
    FOR v_current_log IN
        SELECT id, entry_hash, previous_hash
        FROM system_audit_logs
        WHERE tenant_id = p_tenant_id
            AND (p_start_id IS NULL OR id >= p_start_id)
            AND (p_end_id IS NULL OR id <= p_end_id)
        ORDER BY id
    LOOP
        IF v_previous_hash IS NOT NULL AND v_current_log.previous_hash != v_previous_hash THEN
            RETURN QUERY SELECT FALSE, v_current_log.id, v_previous_hash, v_current_log.previous_hash;
            RETURN;
        END IF;
        
        v_previous_hash := v_current_log.entry_hash;
    END LOOP;
    
    RETURN QUERY SELECT TRUE, NULL::INTEGER, NULL::VARCHAR(64), NULL::VARCHAR(64);
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- COMMENTS
-- ==========================================

COMMENT ON TABLE system_audit_logs IS 'Master Audit Log - Immutable black box for FAA/EASA/CASA compliance';
COMMENT ON COLUMN system_audit_logs.entry_hash IS 'SHA-256 hash of entry content for integrity verification';
COMMENT ON COLUMN system_audit_logs.previous_hash IS 'Hash of previous entry for blockchain-like chain verification';
COMMENT ON FUNCTION verify_audit_chain_integrity IS 'Verifies integrity of audit log chain';

-- ==========================================
-- GRANT PERMISSIONS
-- ==========================================

-- Only allow INSERT (append-only)
GRANT SELECT, INSERT ON system_audit_logs TO ontrackia_ojt;
GRANT USAGE, SELECT ON SEQUENCE system_audit_logs_id_seq TO ontrackia_ojt;
