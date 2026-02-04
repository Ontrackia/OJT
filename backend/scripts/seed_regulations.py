"""
OnTrackIA V1-Core - Regulatory Seed Data
EU Fisheries Control Regulation 2023/2842 + EU AI Act 2024/1689
"""

from sqlalchemy.orm import Session
from datetime import datetime
import json

# EU Fisheries Control Regulation 2023/2842 - Article 58
FISHERIES_REGULATION = {
    "regulation_id": "EU_2023_2842",
    "title": "Fisheries Control Regulation",
    "jurisdiction": "European Union",
    "effective_date": "2026-01-10",
    "article_58": {
        "title": "Digital Traceability Requirements",
        "mandatory_digital": True,
        "retention_period_years": 3,
        "standards": ["GS1 GTIN", "EPCIS"],
        "mandatory_data_points": [
            {
                "field": "lot_id",
                "description": "Unique identifier for the lot",
                "required": True,
                "type": "string"
            },
            {
                "field": "capture_date",
                "description": "Date of fishing trip or aquaculture harvest",
                "required": True,
                "type": "date"
            },
            {
                "field": "producer_id",
                "description": "Producer name and registration (aquaculture)",
                "required": True,
                "type": "string"
            },
            {
                "field": "vessel_id",
                "description": "IMO number or vessel ID",
                "required": True,
                "type": "string"
            },
            {
                "field": "catch_certificate",
                "description": "Associated catch certificate number",
                "required": True,
                "type": "string"
            },
            {
                "field": "species",
                "description": "FAO code + scientific name",
                "required": True,
                "type": "string",
                "format": "FAO_CODE - Scientific Name"
            },
            {
                "field": "geographic_origin",
                "description": "Catch zone or country of origin",
                "required": True,
                "type": "string"
            },
            {
                "field": "fishing_gear",
                "description": "Type of fishing gear used",
                "required": True,
                "type": "string"
            },
            {
                "field": "quantity",
                "description": "Weight in kg or number of pieces",
                "required": True,
                "type": "number",
                "unit": "kg or pieces"
            }
        ],
        "compliance_checkpoints": [
            "Interoperability check between supply chain partners",
            "Verifiability on demand by competent authorities",
            "Digital lot management for fresh food counters"
        ]
    },
    "implementation_milestones": [
        {
            "date": "2026-01-10",
            "phase": "Phase 1",
            "scope": "Unprocessed or minimally processed products",
            "cn_codes": ["03"],
            "description": "Fresh, frozen, smoked fish, crustaceans, and mollusks"
        },
        {
            "date": "2029-01-10",
            "phase": "Phase 2",
            "scope": "Processed products",
            "cn_codes": ["1604", "1605"],
            "description": "Canned fish, prepared fish, caviar, ready meals with >20% fish"
        }
    ]
}

# EU AI Act 2024/1689 - Risk Classification & Governance
EU_AI_ACT = {
    "regulation_id": "EU_2024_1689",
    "title": "EU Artificial Intelligence Act",
    "jurisdiction": "European Union",
    "effective_date": "2024-08-01",
    "risk_classifications": [
        {
            "level": "prohibited",
            "articles": ["5"],
            "description": "Systems that manipulate human behavior or social scoring",
            "examples": [
                "Subliminal manipulation",
                "Social scoring by governments",
                "Real-time biometric identification in public spaces"
            ],
            "compliance_action": "MUST NOT DEPLOY"
        },
        {
            "level": "high_risk",
            "articles": ["6", "7", "8", "9"],
            "description": "Systems used in critical infrastructure or worker management",
            "examples": [
                "Aviation safety systems",
                "Worker performance evaluation",
                "Critical infrastructure management"
            ],
            "requirements": [
                "Mandatory human oversight (HITL)",
                "Risk management system",
                "Data governance and quality",
                "Technical documentation",
                "Record-keeping (logging)",
                "Transparency and user information",
                "Human oversight mechanisms",
                "Accuracy, robustness, cybersecurity"
            ],
            "compliance_action": "REQUIRES FULL GOVERNANCE"
        },
        {
            "level": "limited_risk",
            "articles": ["52"],
            "description": "Systems requiring transparency obligations",
            "examples": [
                "Chatbots",
                "Emotion recognition systems",
                "Biometric categorization"
            ],
            "requirements": [
                "Inform users they are interacting with AI",
                "Transparency about AI-generated content"
            ],
            "compliance_action": "TRANSPARENCY REQUIRED"
        },
        {
            "level": "minimal_risk",
            "articles": [],
            "description": "All other AI systems",
            "examples": [
                "AI-enabled video games",
                "Spam filters"
            ],
            "requirements": [],
            "compliance_action": "NO SPECIFIC OBLIGATIONS"
        }
    ],
    "transparency_requirements": {
        "article_12": {
            "title": "Record-keeping (Logging)",
            "requirements": [
                "Automatic generation of logs during system lifetime",
                "Logs must enable traceability of system functioning",
                "Retention period appropriate to intended purpose"
            ]
        },
        "article_13": {
            "title": "Transparency and User Information",
            "requirements": [
                "Instructions for use must be clear and comprehensive",
                "Information about system capabilities and limitations",
                "Information about human oversight measures"
            ]
        },
        "article_14": {
            "title": "Human Oversight",
            "requirements": [
                "Interface designed for human supervision",
                "Ability to override AI decisions",
                "Ability to interrupt system operation",
                "Measures to prevent over-reliance on AI output"
            ]
        },
        "article_15": {
            "title": "Accuracy, Robustness, Cybersecurity",
            "requirements": [
                "Appropriate level of accuracy",
                "Robustness against errors and faults",
                "Resilience against attempts to alter use or performance"
            ]
        }
    },
    "ontrackia_classification": {
        "risk_level": "high_risk",
        "justification": "Aviation safety system used for audit findings and root cause analysis",
        "applicable_articles": ["6", "7", "8", "9", "12", "13", "14", "15"],
        "compliance_measures": [
            "Human-in-the-Loop (HITL) for all AI-generated suggestions",
            "Master Audit Log for complete traceability",
            "Technical documentation maintained",
            "User transparency (AI suggestions clearly marked)",
            "Override capability (human can reject AI suggestions)",
            "Accuracy monitoring and validation",
            "Cybersecurity measures (AES-256 encryption)"
        ]
    }
}

def seed_regulatory_data(db: Session):
    """
    Seed regulatory data into Knowledge Vault
    """
    from app.models.evidence_vault import KnowledgeDocument
    from app.services.knowledge_ingestion import KnowledgeIngestionService
    
    knowledge_service = KnowledgeIngestionService(db)
    
    # Seed Fisheries Regulation
    fisheries_doc = KnowledgeDocument(
        title="EU Fisheries Control Regulation 2023/2842 - Article 58",
        document_type="REGULATION",
        content=json.dumps(FISHERIES_REGULATION, indent=2),
        file_hash=hashlib.sha256(
            json.dumps(FISHERIES_REGULATION).encode()
        ).hexdigest(),
        organization_id=1,  # System-wide
        uploaded_by=1,  # Admin
        priority=90,  # High priority for regulations
        metadata={
            "regulation_id": "EU_2023_2842",
            "jurisdiction": "EU",
            "effective_date": "2026-01-10",
            "article": "58"
        }
    )
    db.add(fisheries_doc)
    
    # Seed EU AI Act
    ai_act_doc = KnowledgeDocument(
        title="EU Artificial Intelligence Act 2024/1689",
        document_type="REGULATION",
        content=json.dumps(EU_AI_ACT, indent=2),
        file_hash=hashlib.sha256(
            json.dumps(EU_AI_ACT).encode()
        ).hexdigest(),
        organization_id=1,
        uploaded_by=1,
        priority=95,  # Highest priority for AI governance
        metadata={
            "regulation_id": "EU_2024_1689",
            "jurisdiction": "EU",
            "effective_date": "2024-08-01",
            "ontrackia_risk_level": "high_risk"
        }
    )
    db.add(ai_act_doc)
    
    db.commit()
    
    # Index in ChromaDB
    knowledge_service.index_document(fisheries_doc.id)
    knowledge_service.index_document(ai_act_doc.id)
    
    print("✅ Regulatory data seeded successfully")
    print(f"   - EU Fisheries Regulation 2023/2842")
    print(f"   - EU AI Act 2024/1689")

if __name__ == "__main__":
    from app.database import SessionLocal
    import hashlib
    
    db = SessionLocal()
    try:
        seed_regulatory_data(db)
    finally:
        db.close()
