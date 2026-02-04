"""
Database Seed Script for OnTrackIA OJT V1
Creates initial admin user and default organization
"""
import os
import sys
from datetime import datetime
import hashlib

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.sms_models import RiskMatrix
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ontrackia_ojt:password@localhost:5432/ontrackia_ojt_db")

print(f"🔌 Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'database'}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_database():
    """Seed initial data for OnTrackIA OJT V1"""
    
    print("🌱 Starting database seed...")
    
    # Ensure tables exist
    print("📋 Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Seed ICAO 5x5 Risk Matrix
        print("\n📊 Seeding ICAO 5x5 Risk Matrix...")
        
        # Severity levels
        severity_levels = [
            (1, "Insignificante", "Sin efecto en seguridad"),
            (2, "Menor", "Incidencia menor"),
            (3, "Moderado", "Incidente significativo"),
            (4, "Mayor", "Daños graves"),
            (5, "Catastrófico", "Pérdida total / fatalidades")
        ]
        
        for value, label, description in severity_levels:
            existing = db.query(RiskMatrix).filter(
                RiskMatrix.dimension == "SEVERITY",
                RiskMatrix.value == value
            ).first()
            
            if not existing:
                matrix_entry = RiskMatrix(
                    matrix_type="ICAO_5x5",
                    dimension="SEVERITY",
                    value=value,
                    label=label,
                    description=description
                )
                db.add(matrix_entry)
                print(f"   ✅ Added SEVERITY level {value}: {label}")
        
        # Probability levels
        probability_levels = [
            (1, "Extremadamente Improbable", "Casi imposible que ocurra"),
            (2, "Improbable", "Poco probable"),
            (3, "Remoto", "Puede ocurrir ocasionalmente"),
            (4, "Probable", "Ocurrirá varias veces"),
            (5, "Frecuente", "Ocurrirá repetidamente")
        ]
        
        for value, label, description in probability_levels:
            existing = db.query(RiskMatrix).filter(
                RiskMatrix.dimension == "PROBABILITY",
                RiskMatrix.value == value
            ).first()
            
            if not existing:
                matrix_entry = RiskMatrix(
                    matrix_type="ICAO_5x5",
                    dimension="PROBABILITY",
                    value=value,
                    label=label,
                    description=description
                )
                db.add(matrix_entry)
                print(f"   ✅ Added PROBABILITY level {value}: {label}")
        
        db.commit()
        print("✅ Risk Matrix seeded successfully")
        
        # 2. Apply RLS functions (if not already applied)
        print("\n🔒 Applying Row-Level Security functions...")
        try:
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
            
            db.commit()
            print("✅ RLS functions created")
        except Exception as e:
            print(f"⚠️  RLS functions may already exist: {e}")
            db.rollback()
        
        print("\n✅ DATABASE SEED COMPLETED SUCCESSFULLY")
        print("\n📊 Summary:")
        print(f"   - Risk Matrix entries: {db.query(RiskMatrix).count()}")
        print(f"   - Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
        
    except Exception as e:
        print(f"\n❌ ERROR during seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
