-- ==========================================
-- Row-Level Security (RLS) for OnTrackIA OJT
-- Organization-level data isolation
-- ==========================================

-- ==========================================
-- ENABLE RLS ON ALL TABLES
-- ==========================================

ALTER TABLE sms_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE rca_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- CREATE RLS FUNCTIONS
-- ==========================================

-- Function to get organization_id from session
CREATE OR REPLACE FUNCTION get_current_organization_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.organization_id', TRUE), '')::INTEGER;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to set organization_id for session
CREATE OR REPLACE FUNCTION set_organization_id(p_organization_id INTEGER)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.organization_id', p_organization_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- CREATE RLS POLICIES
-- ==========================================

-- Note: For V1 with single tenant (Travis), these policies will allow all data
-- In V2 with multi-tenant, they will enforce strict isolation

-- SMS Reports - Future: filter by organization
CREATE POLICY org_isolation_sms_reports ON sms_reports
    FOR ALL
    USING (true)  -- V1: Allow all, V2: organization_id = get_current_organization_id()
    WITH CHECK (true);

-- Audit Contexts
CREATE POLICY org_isolation_audit_contexts ON audit_contexts
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Findings
CREATE POLICY org_isolation_findings ON findings
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- RCA Records
CREATE POLICY org_isolation_rca_records ON rca_records
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Security Events
CREATE POLICY org_isolation_security_events ON security_events
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ==========================================
-- COMMENTS
-- ==========================================

COMMENT ON FUNCTION get_current_organization_id() IS 'Gets organization_id from current session';
COMMENT ON FUNCTION set_organization_id(INTEGER) IS 'Sets organization_id for current session';

-- ==========================================
-- USAGE EXAMPLE
-- ==========================================

/*
-- In Python (FastAPI):

from sqlalchemy import text

# At the start of each request
db.execute(text("SELECT set_organization_id(:org_id)"), {"org_id": current_user['organization_id']})

# Now all queries are automatically filtered by organization_id
reports = db.query(SMSReport).all()  # Only from current organization

# At the end of request (optional, clears automatically)
db.execute(text("SELECT set_organization_id(NULL)"))
*/
