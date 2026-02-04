/**
 * OnTrackIA OJT V2.0 - Visual Scan Capture Component
 * ===================================================
 * Módulo de evidencia visual con hard-stop para tareas críticas
 * 
 * Features:
 * - Hard-stop obligatorio para tareas críticas
 * - Captura de foto con GPS + timestamp inmutable
 * - Validación de metadata forense
 * - Prevención de fotos antiguas
 * - Integración con audit_archive
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useRef, useEffect } from 'react';
import { Camera, MapPin, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useLanguage } from './LanguageSelector';
import { useGeolocation } from '../hooks/useGeolocation';

const VisualScanCapture = ({
    taskId,
    isCritical,
    onCaptureComplete,
    onSkip
}) => {
    const { t, language } = useLanguage();
    const { latitude, longitude, accuracy, error: gpsError } = useGeolocation();

    const [capturedPhoto, setCapturedPhoto] = useState(null);
    const [photoMetadata, setPhotoMetadata] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [validationError, setValidationError] = useState('');

    const fileInputRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [cameraActive, setCameraActive] = useState(false);

    useEffect(() => {
        return () => {
            // Cleanup camera stream
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [stream]);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' },
                audio: false
            });

            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
            setCameraActive(true);
        } catch (error) {
            console.error('Camera error:', error);
            setValidationError(
                language === 'es'
                    ? 'No se pudo acceder a la cámara. Usa el selector de archivo.'
                    : 'Could not access camera. Use file selector.'
            );
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
        setCameraActive(false);
    };

    const captureFromCamera = () => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        // Set canvas size to video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to blob
        canvas.toBlob((blob) => {
            processPhoto(blob);
            stopCamera();
        }, 'image/jpeg', 0.9);
    };

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            processPhoto(file);
        }
    };

    const processPhoto = async (photoBlob) => {
        setValidationError('');

        // Validar GPS
        if (!latitude || !longitude) {
            setValidationError(
                language === 'es'
                    ? 'GPS no disponible. Activa la ubicación para continuar.'
                    : 'GPS not available. Enable location to continue.'
            );
            return;
        }

        if (gpsError) {
            setValidationError(
                language === 'es'
                    ? `Error de GPS: ${gpsError}`
                    : `GPS Error: ${gpsError}`
            );
            return;
        }

        // Crear metadata forense
        const now = new Date();
        const metadata = {
            task_id: taskId,
            capture_timestamp: now.toISOString(),
            capture_timestamp_unix: now.getTime(),
            gps_latitude: latitude,
            gps_longitude: longitude,
            gps_accuracy: accuracy,
            device_info: {
                user_agent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language
            }
        };

        // Calcular hash de la foto
        const arrayBuffer = await photoBlob.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        metadata.photo_hash = hashHex;

        // Crear URL de preview
        const photoUrl = URL.createObjectURL(photoBlob);

        setCapturedPhoto(photoUrl);
        setPhotoMetadata({
            blob: photoBlob,
            metadata: metadata
        });
    };

    const validateAndUpload = async () => {
        if (!photoMetadata) return;

        setUploading(true);
        setValidationError('');

        try {
            const formData = new FormData();
            formData.append('photo', photoMetadata.blob, 'visual_scan.jpg');
            formData.append('metadata', JSON.stringify(photoMetadata.metadata));

            const response = await fetch('/api/visual-scan/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                onCaptureComplete?.(data);
            } else {
                const error = await response.json();
                setValidationError(
                    error.detail || (language === 'es'
                        ? 'Error al subir la foto'
                        : 'Error uploading photo')
                );
            }
        } catch (error) {
            console.error('Upload error:', error);
            setValidationError(
                language === 'es'
                    ? 'Error de conexión. Intenta de nuevo.'
                    : 'Connection error. Try again.'
            );
        } finally {
            setUploading(false);
        }
    };

    const handleRetake = () => {
        setCapturedPhoto(null);
        setPhotoMetadata(null);
        setValidationError('');
    };

    return (
        <div className="glass-card">
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '24px'
            }}>
                <Camera size={24} color={isCritical ? 'var(--error)' : 'var(--primary)'} />
                <div>
                    <h3 style={{
                        fontSize: '18px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginBottom: '4px'
                    }}>
                        {language === 'es' ? 'Escaneo Visual' : 'Visual Scan'}
                        {isCritical && (
                            <span style={{
                                marginLeft: '12px',
                                padding: '4px 8px',
                                background: 'rgba(239, 68, 68, 0.1)',
                                border: '1px solid var(--error)',
                                borderRadius: '4px',
                                fontSize: '12px',
                                fontWeight: 700,
                                color: 'var(--error)'
                            }}>
                                {language === 'es' ? 'CRÍTICO' : 'CRITICAL'}
                            </span>
                        )}
                    </h3>
                    <p style={{
                        fontSize: '13px',
                        color: 'var(--text-secondary)'
                    }}>
                        {isCritical
                            ? (language === 'es'
                                ? 'Fotografía obligatoria con GPS para continuar'
                                : 'Mandatory photo with GPS to continue')
                            : (language === 'es'
                                ? 'Captura evidencia visual de la inspección'
                                : 'Capture visual evidence of inspection')
                        }
                    </p>
                </div>
            </div>

            {/* GPS Status */}
            <div style={{
                padding: '12px',
                background: latitude && longitude ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                border: `1px solid ${latitude && longitude ? 'var(--success)' : 'var(--warning)'}`,
                borderRadius: '8px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
            }}>
                <MapPin size={20} color={latitude && longitude ? 'var(--success)' : 'var(--warning)'} />
                <div style={{ flex: 1 }}>
                    <div style={{
                        fontSize: '13px',
                        fontWeight: 600,
                        color: latitude && longitude ? 'var(--success)' : 'var(--warning)'
                    }}>
                        {latitude && longitude
                            ? (language === 'es' ? 'GPS Activo' : 'GPS Active')
                            : (language === 'es' ? 'Esperando GPS...' : 'Waiting for GPS...')
                        }
                    </div>
                    {latitude && longitude && (
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                            {latitude.toFixed(6)}, {longitude.toFixed(6)} (±{accuracy?.toFixed(0)}m)
                        </div>
                    )}
                </div>
            </div>

            {/* Validation Error */}
            {validationError && (
                <div style={{
                    padding: '12px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid var(--error)',
                    borderRadius: '8px',
                    marginBottom: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <AlertTriangle size={20} color="var(--error)" />
                    <span style={{ fontSize: '13px', color: 'var(--error)' }}>
                        {validationError}
                    </span>
                </div>
            )}

            {/* Camera View or Photo Preview */}
            {!capturedPhoto ? (
                <div style={{ marginBottom: '16px' }}>
                    {cameraActive ? (
                        <div style={{ position: 'relative' }}>
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                style={{
                                    width: '100%',
                                    borderRadius: '8px',
                                    background: 'var(--bg-deep)'
                                }}
                            />
                            <button
                                onClick={captureFromCamera}
                                disabled={!latitude || !longitude}
                                className="btn"
                                style={{
                                    position: 'absolute',
                                    bottom: '16px',
                                    left: '50%',
                                    transform: 'translateX(-50%)',
                                    width: '64px',
                                    height: '64px',
                                    borderRadius: '50%',
                                    padding: 0
                                }}
                            >
                                <Camera size={28} />
                            </button>
                        </div>
                    ) : (
                        <div style={{
                            border: '2px dashed var(--glass-border)',
                            borderRadius: '8px',
                            padding: '48px 24px',
                            textAlign: 'center',
                            background: 'var(--bg-card)'
                        }}>
                            <Camera size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
                            <p style={{
                                fontSize: '14px',
                                color: 'var(--text-secondary)',
                                marginBottom: '16px'
                            }}>
                                {language === 'es'
                                    ? 'Captura una fotografía de la inspección'
                                    : 'Capture a photo of the inspection'}
                            </p>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                                <button
                                    onClick={startCamera}
                                    disabled={!latitude || !longitude}
                                    className="btn"
                                    style={{ height: '44px' }}
                                >
                                    <Camera size={20} />
                                    <span>{language === 'es' ? 'Usar Cámara' : 'Use Camera'}</span>
                                </button>
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={!latitude || !longitude}
                                    className="btn"
                                    style={{
                                        height: '44px',
                                        background: 'var(--bg-card)',
                                        border: '1px solid var(--glass-border)'
                                    }}
                                >
                                    {language === 'es' ? 'Seleccionar Archivo' : 'Select File'}
                                </button>
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                capture="environment"
                                onChange={handleFileSelect}
                                style={{ display: 'none' }}
                            />
                        </div>
                    )}
                    <canvas ref={canvasRef} style={{ display: 'none' }} />
                </div>
            ) : (
                <div style={{ marginBottom: '16px' }}>
                    <img
                        src={capturedPhoto}
                        alt="Visual scan"
                        style={{
                            width: '100%',
                            borderRadius: '8px',
                            marginBottom: '12px'
                        }}
                    />

                    {/* Metadata Display */}
                    {photoMetadata?.metadata && (
                        <div style={{
                            padding: '12px',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--glass-border)',
                            borderRadius: '8px',
                            fontSize: '12px',
                            color: 'var(--text-secondary)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                                <Clock size={14} />
                                <strong>{language === 'es' ? 'Capturado:' : 'Captured:'}</strong>
                                <span>{new Date(photoMetadata.metadata.capture_timestamp).toLocaleString()}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                                <MapPin size={14} />
                                <strong>GPS:</strong>
                                <span>{photoMetadata.metadata.gps_latitude.toFixed(6)}, {photoMetadata.metadata.gps_longitude.toFixed(6)}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <CheckCircle size={14} />
                                <strong>Hash:</strong>
                                <span style={{ fontFamily: 'monospace', fontSize: '10px' }}>
                                    {photoMetadata.metadata.photo_hash.substring(0, 16)}...
                                </span>
                            </div>
                        </div>
                    )}

                    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                        <button
                            onClick={handleRetake}
                            disabled={uploading}
                            className="btn"
                            style={{
                                flex: 1,
                                height: '44px',
                                background: 'var(--bg-card)',
                                border: '1px solid var(--glass-border)'
                            }}
                        >
                            {language === 'es' ? 'Volver a Capturar' : 'Retake'}
                        </button>
                        <button
                            onClick={validateAndUpload}
                            disabled={uploading}
                            className="btn"
                            style={{ flex: 1, height: '44px' }}
                        >
                            {uploading
                                ? (language === 'es' ? 'Subiendo...' : 'Uploading...')
                                : (language === 'es' ? 'Confirmar' : 'Confirm')
                            }
                        </button>
                    </div>
                </div>
            )}

            {/* Skip Button (only if not critical) */}
            {!isCritical && !capturedPhoto && (
                <button
                    onClick={onSkip}
                    style={{
                        width: '100%',
                        height: '44px',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-muted)',
                        fontSize: '13px',
                        cursor: 'pointer'
                    }}
                >
                    {language === 'es' ? 'Omitir (opcional)' : 'Skip (optional)'}
                </button>
            )}
        </div>
    );
};

export default VisualScanCapture;
