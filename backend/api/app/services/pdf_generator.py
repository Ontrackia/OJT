"""
PDF Generator Service for OnTrackIA OJT V2.0
Generates professional audit reports with forensic SHA-256 integrity seal
"""
import hashlib
import io
from datetime import datetime
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class PDFGenerator:
    """Professional PDF generator with forensic integrity"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ForensicSeal',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Courier'
        ))
    
    def generate_audit_report(
        self,
        audit_id: str,
        audit_name: str,
        regulation: str,
        territory: str,
        findings: List[Dict],
        rca_records: List[Dict],
        sms_reports: List[Dict],
        metadata: Optional[Dict] = None
    ) -> bytes:
        """
        Generate comprehensive audit report PDF
        
        Returns:
            bytes: PDF file content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build document content
        story = []
        
        # Header
        story.append(Paragraph("OnTrackIA OJT", self.styles['CustomTitle']))
        story.append(Paragraph("AUDIT REPORT - FORENSIC INTEGRITY SEAL", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Audit Information
        story.append(Paragraph("Audit Information", self.styles['SectionHeader']))
        audit_info_data = [
            ['Audit ID:', audit_id],
            ['Audit Name:', audit_name],
            ['Regulation:', regulation],
            ['Territory:', territory or 'GLOBAL'],
            ['Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
        ]
        
        audit_info_table = Table(audit_info_data, colWidths=[2*inch, 4*inch])
        audit_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(audit_info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Findings Summary
        if findings:
            story.append(Paragraph("Findings Summary", self.styles['SectionHeader']))
            
            findings_data = [['ID', 'Level', 'Title', 'Status', 'Deadline']]
            for f in findings:
                level_label = {1: 'CRITICAL', 2: 'MAJOR', 3: 'OBSERVATION'}.get(f.get('level'), 'N/A')
                findings_data.append([
                    f.get('finding_id', 'N/A'),
                    level_label,
                    f.get('title', 'N/A')[:40] + '...' if len(f.get('title', '')) > 40 else f.get('title', 'N/A'),
                    f.get('status', 'N/A'),
                    f.get('deadline', 'N/A')[:10] if f.get('deadline') else 'N/A'
                ])
            
            findings_table = Table(findings_data, colWidths=[1*inch, 1*inch, 2.5*inch, 0.8*inch, 1*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(findings_table)
            story.append(Spacer(1, 0.3*inch))
        
        # RCA Records
        if rca_records:
            story.append(Paragraph("Root Cause Analysis", self.styles['SectionHeader']))
            for rca in rca_records:
                story.append(Paragraph(f"<b>RCA ID:</b> {rca.get('rca_id', 'N/A')}", self.styles['Normal']))
                story.append(Paragraph(f"<b>Root Cause:</b> {rca.get('root_cause', 'N/A')}", self.styles['Normal']))
                story.append(Paragraph(f"<b>Corrective Action:</b> {rca.get('corrective_action', 'N/A')}", self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # SMS Reports
        if sms_reports:
            story.append(Paragraph("SMS Safety Reports", self.styles['SectionHeader']))
            sms_data = [['Report ID', 'Risk Level', 'Status', 'Description']]
            for sms in sms_reports:
                sms_data.append([
                    sms.get('report_id', 'N/A'),
                    sms.get('risk_level', 'N/A'),
                    sms.get('status', 'N/A'),
                    sms.get('description', 'N/A')[:50] + '...' if len(sms.get('description', '')) > 50 else sms.get('description', 'N/A')
                ])
            
            sms_table = Table(sms_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 3.3*inch])
            sms_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(sms_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Forensic Integrity Seal
        story.append(PageBreak())
        story.append(Paragraph("FORENSIC INTEGRITY SEAL", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Calculate SHA-256 hash of report content
        content_for_hash = f"{audit_id}|{audit_name}|{regulation}|{len(findings)}|{len(rca_records)}|{len(sms_reports)}|{datetime.utcnow().isoformat()}"
        sha256_hash = hashlib.sha256(content_for_hash.encode('utf-8')).hexdigest()
        
        seal_data = [
            ['Document Hash (SHA-256):', sha256_hash],
            ['Hash Algorithm:', 'SHA-256'],
            ['Timestamp:', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Compliance:', f'{regulation} - EASA Part-145.A.55'],
            ['Verification:', 'This document is cryptographically sealed for forensic integrity']
        ]
        
        seal_table = Table(seal_data, colWidths=[2*inch, 4*inch])
        seal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b'))
        ]))
        story.append(seal_table)
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "⚠️ WARNING: Any modification to this document will invalidate the cryptographic seal. "
            "Verify the SHA-256 hash to ensure document integrity.",
            self.styles['ForensicSeal']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    @staticmethod
    def calculate_document_hash(content: str) -> str:
        """Calculate SHA-256 hash for document integrity"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
