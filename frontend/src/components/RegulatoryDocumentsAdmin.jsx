/**
 * OnTrackIA OJT V2.0 - Regulatory Documents Admin Panel
 * ======================================================
 * Panel de administración para carga y procesamiento de normativas PDF
 * 
 * Features:
 * - Drag & Drop de PDFs
 * - Conversión automática PDF→Markdown
 * - Chunking e indexación RAG
 * - Visualización de documentos indexados
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useCallback, useEffect } from 'react';
import { FileUp, RefreshCw, FileText, Database, CheckCircle, XCircle, Loader } from 'lucide-react';
import { useLanguage } from './LanguageSelector';

const RegulatoryDocumentsAdmin = () => {
    const { t, language } = useLanguage();
    const [isDragging, setIsDragging] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [indexedDocuments, setIndexedDocuments] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [currentStep, setCurrentStep] = useState('');

    useEffect(() => {
        loadIndexedDocuments();
    }, []);

    const loadIndexedDocuments = async () => {
        try {
            const response = await fetch('/api/rag/documents');
            if (response.ok) {
                const data = await response.json();
                setIndexedDocuments(data.documents || []);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    const handleDragEnter = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback(async (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files).filter(
            file => file.type === 'application/pdf'
        );

        if (files.length > 0) {
            await processFiles(files);
        }
    }, []);

    const handleFileInput = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            await processFiles(files);
        }
    };

    const processFiles = async (files) => {
        setProcessing(true);
        const results = [];

        for (const file of files) {
            try {
                setCurrentStep(language === 'es'
                    ? `Procesando ${file.name}...`
                    : `Processing ${file.name}...`
                );

                // 1. Upload PDF
                const formData = new FormData();
                formData.append('file', file);

                const uploadResponse = await fetch('/api/rag/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!uploadResponse.ok) throw new Error('Upload failed');

                // 2. Convertir a Markdown
                setCurrentStep(language === 'es'
                    ? 'Convirtiendo a Markdown...'
                    : 'Converting to Markdown...'
                );

                const convertResponse = await fetch('/api/rag/convert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: file.name })
                });

                if (!convertResponse.ok) throw new Error('Conversion failed');

                // 3. Indexar chunks
                setCurrentStep(language === 'es'
                    ? 'Indexando chunks en ChromaDB...'
                    : 'Indexing chunks in ChromaDB...'
                );

                const indexResponse = await fetch('/api/rag/index', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: file.name.replace('.pdf', '.md') })
                });

                if (!indexResponse.ok) throw new Error('Indexing failed');

                const indexData = await indexResponse.json();

                results.push({
                    filename: file.name,
                    status: 'success',
                    chunks: indexData.chunk_count,
                    hash: indexData.file_hash
                });

            } catch (error) {
                results.push({
                    filename: file.name,
                    status: 'error',
                    error: error.message
                });
            }
        }

        setUploadedFiles(prev => [...prev, ...results]);
        setProcessing(false);
        setCurrentStep('');

        // Recargar documentos indexados
        await loadIndexedDocuments();
    };

    return (
        <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                marginBottom: '32px'
            }}>
                <Database size={32} color="var(--primary)" />
                <div>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        marginBottom: '4px'
                    }}>
                        {language === 'es' ? 'Refinería de Datos Normativos' : 'Regulatory Data Refinery'}
                    </h1>
                    <p style={{
                        fontSize: '14px',
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es'
                            ? 'Pipeline automatizado RAG para normativas aeronáuticamente actualizadas'
                            : 'Automated RAG pipeline for up-to-date aeronautical regulations'
                        }
                    </p>
                </div>
            </div>

            {/* Upload Zone */}
            <div className="glass-card" style={{ marginBottom: '32px' }}>
                <h2 style={{
                    fontSize: '20px',
                    fontWeight: 600,
                    marginBottom: '24px',
                    color: 'var(--text-primary)'
                }}>
                    {language === 'es' ? 'Cargar Normativa' : 'Upload Regulation'}
                </h2>

                <div
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    style={{
                        border: isDragging
                            ? '2px dashed var(--primary)'
                            : '2px dashed var(--glass-border)',
                        borderRadius: '12px',
                        padding: '48px',
                        textAlign: 'center',
                        background: isDragging
                            ? 'rgba(124, 58, 237, 0.05)'
                            : 'var(--glass-bg)',
                        transition: 'all 0.2s',
                        cursor: 'pointer'
                    }}
                    onClick={() => document.getElementById('file-input').click()}
                >
                    <FileUp
                        size={48}
                        color={isDragging ? 'var(--primary)' : 'var(--text-secondary)'}
                        style={{ marginBottom: '16px' }}
                    />

                    <div style={{
                        fontSize: '16px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginBottom: '8px'
                    }}>
                        {language === 'es'
                            ? 'Arrastra archivos PDF aquí o haz clic para seleccionar'
                            : 'Drag PDF files here or click to select'
                        }
                    </div>

                    <div style={{
                        fontSize: '13px',
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es'
                            ? 'Soportado: EASA Part-66/145, RAC LPTA 66, UK CAA CAP 741, FAA Order 8900.1'
                            : 'Supported: EASA Part-66/145, RAC LPTA 66, UK CAA CAP 741, FAA Order 8900.1'
                        }
                    </div>

                    <input
                        id="file-input"
                        type="file"
                        accept="application/pdf"
                        multiple
                        onChange={handleFileInput}
                        style={{ display: 'none' }}
                    />
                </div>

                {processing && (
                    <div style={{
                        marginTop: '24px',
                        padding: '16px',
                        background: 'rgba(124, 58, 237, 0.05)',
                        border: '1px solid rgba(124, 58, 237, 0.2)',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                    }}>
                        <Loader size={20} color="var(--primary)" className="spin" />
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                                {currentStep}
                            </div>
                            <div className="progress-bar" style={{ marginTop: '8px', height: '4px' }}>
                                <div className="progress-fill" style={{ animation: 'progress 2s infinite' }} />
                            </div>
                        </div>
                    </div>
                )}

                {uploadedFiles.length > 0 && (
                    <div style={{ marginTop: '24px' }}>
                        {uploadedFiles.map((file, idx) => (
                            <div
                                key={idx}
                                style={{
                                    padding: '12px',
                                    background: 'var(--bg-card)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    marginBottom: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px'
                                }}
                            >
                                {file.status === 'success' ? (
                                    <CheckCircle size={20} color="var(--success)" />
                                ) : (
                                    <XCircle size={20} color="var(--error)" />
                                )}

                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                                        {file.filename}
                                    </div>
                                    {file.status === 'success' && (
                                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                            {file.chunks} chunks indexed | Hash: {file.hash?.substring(0, 16)}...
                                        </div>
                                    )}
                                    {file.status === 'error' && (
                                        <div style={{ fontSize: '12px', color: 'var(--error)' }}>
                                            {file.error}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Indexed Documents */}
            <div className="glass-card">
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '24px'
                }}>
                    <h2 style={{
                        fontSize: '20px',
                        fontWeight: 600,
                        color: 'var(--text-primary)'
                    }}>
                        {language === 'es' ? 'Documentos Indexados' : 'Indexed Documents'}
                    </h2>

                    <button
                        onClick={loadIndexedDocuments}
                        className="icon-button"
                        style={{ width: '44px', height: '44px' }}
                    >
                        <RefreshCw size={20} />
                    </button>
                </div>

                {indexedDocuments.length === 0 ? (
                    <div style={{
                        padding: '48px',
                        textAlign: 'center',
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es'
                            ? 'No hay documentos indexados. Carga tu primera normativa arriba.'
                            : 'No indexed documents. Upload your first regulation above.'
                        }
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>{language === 'es' ? 'Documento' : 'Document'}</th>
                                <th>{language === 'es' ? 'Autoridad' : 'Authority'}</th>
                                <th>{language === 'es' ? 'Chunks' : 'Chunks'}</th>
                                <th>{language === 'es' ? 'Idioma' : 'Language'}</th>
                                <th>{language === 'es' ? 'Actualizado' : 'Updated'}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {indexedDocuments.map((doc, idx) => (
                                <tr key={idx}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <FileText size={16} color="var(--primary)" />
                                            <span style={{ fontWeight: 600 }}>{doc.document_code}</span>
                                        </div>
                                    </td>
                                    <td>{doc.authority}</td>
                                    <td>{doc.chunk_count}</td>
                                    <td>{doc.language.toUpperCase()}</td>
                                    <td>{doc.update_date}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default RegulatoryDocumentsAdmin;
