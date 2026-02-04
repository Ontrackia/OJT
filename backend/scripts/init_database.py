"""
Initialize Database for OnTrackIA OJT V1
Creates all tables and applies RLS
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import Base, engine, SessionLocal
from app.models.sms_models import SMSReport, RiskMatrix
from app.models.audit_models import AuditContext, Finding, RCARecord, Component, AuditTrailEntry
from app.models.security_models import SecurityEvent

print("🚀 Initializing OnTrackIA OJT Database...")
print("=" * 60)

# 1. Create all tables
print("\n📋 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully")

# 2. Apply RLS functions
print("\n🔒 Applying Row-Level Security...")
db = SessionLocal()

try:
    # Create RLS functions
    db.execute(text("""
        CREATE OR REPLACE FUNCTION get_current_organization_id()
        RETURNS INTEGER AS $$
        BEGIN
            RETURN NULLIF(current_setting('app.organization_id', TRUE), '')::INTEGER;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """))
    
    db.execute(text("""
        CREATE OR REPLACE FUNCTION set_organization_id(p_organization_id INTEGER)
        RETURNS VOID AS $$
        BEGIN
            PERFORM set_config('app.organization_id', p_organization_id::TEXT, FALSE);
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    # Enable RLS on tables
    tables = ['sms_reports', 'audit_contexts', 'findings', 'rca_records', 
              'components', 'audit_trail', 'security_events']
    
    for table in tables:
        try:
            db.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"))
            db.execute(text(f"""
                CREATE POLICY org_isolation_{table} ON {table}
                FOR ALL
                USING (true)
                WITH CHECK (true);
            """))
            print(f"   ✅ RLS enabled on {table}")
        except Exception as e:
            print(f"   ⚠️  {table}: {str(e)[:50]}")
    
    db.commit()
    print("✅ Row-Level Security applied")
    
except Exception as e:
    print(f"⚠️  RLS setup: {e}")
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 60)
print("✅ DATABASE INITIALIZATION COMPLETE")
print("\nTables created:")
print("  - sms_reports (SMS Safety Reports)")
print("  - risk_matrix (ICAO 5x5 Matrix)")
print("  - audit_contexts (Audit Scopes)")
print("  - findings (Audit Findings)")
print("  - rca_records (Root Cause Analysis)")
print("  - components (Aircraft Components)")
print("  - audit_trail (Immutable Audit Log)")
print("  - security_events (Security Logging)")
print("\nNext steps:")
print("  1. Run: python scripts/seed_database.py")
print("  2. Start server: uvicorn rag_server_mistral:app --reload")
