/**
 * OnTrackIA OJT V2.0 - useGeolocation Hook
 * ==========================================
 * Hook de React para capturar la geolocalización del dispositivo
 * con validación de permisos y manejo de errores.
 * 
 * Features:
 * - Solicita permisos de geolocalización
 * - Captura coordenadas GPS en tiempo real
 * - Precisión del GPS (accuracy)
 * - Manejo de errores y permisos denegados
 * - Compatible con PWA y dispositivos móviles
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 * @compliance Protocolo Búnker + Geolocalización Forense
 */

import { useState, useEffect } from 'react';

/**
 * Hook para obtener la geolocalización del dispositivo
 * 
 * @param {Object} options - Opciones de geolocalización
 * @param {boolean} options.enableHighAccuracy - Usar GPS de alta precisión
 * @param {number} options.timeout - Timeout en ms
 * @param {number} options.maximumAge - Edad máxima del cache en ms
 * @param {boolean} options.watchPosition - Si true, escucha cambios de posición
 * 
 * @returns {Object} Estado de geolocalización
 * @returns {Object|null} location - Coordenadas GPS
 * @returns {number} location.latitude - Latitud
 * @returns {number} location.longitude - Longitud
 * @returns {number} location.accuracy - Precisión en metros
 * @returns {number} location.timestamp - Timestamp de captura
 * @returns {boolean} loading - Si está cargando
 * @returns {Object|null} error - Error si lo hay
 * @returns {Function} requestLocation - Función para solicitar ubicación manualmente
 */
export const useGeolocation = (options = {}) => {
    const {
        enableHighAccuracy = true,
        timeout = 10000,
        maximumAge = 0,
        watchPosition = false
    } = options;

    const [location, setLocation] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [permissionStatus, setPermissionStatus] = useState('prompt'); // 'granted', 'denied', 'prompt'

    /**
     * Verifica si el navegador soporta geolocalización
     */
    const isGeolocationSupported = () => {
        return 'geolocation' in navigator;
    };

    /**
     * Verifica permisos de geolocalización
     */
    const checkPermission = async () => {
        if ('permissions' in navigator) {
            try {
                const result = await navigator.permissions.query({ name: 'geolocation' });
                setPermissionStatus(result.state);

                // Escuchar cambios en permisos
                result.addEventListener('change', () => {
                    setPermissionStatus(result.state);
                });
            } catch (err) {
                console.warn('⚠️ No se pueden verificar permisos de geolocalización:', err);
            }
        }
    };

    /**
     * Maneja el éxito de la captura de ubicación
     */
    const handleSuccess = (position) => {
        const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            altitudeAccuracy: position.coords.altitudeAccuracy,
            heading: position.coords.heading,
            speed: position.coords.speed,
            timestamp: position.timestamp
        };

        setLocation(locationData);
        setLoading(false);
        setError(null);

        console.log('✅ Ubicación capturada:', {
            coords: `${locationData.latitude.toFixed(6)}, ${locationData.longitude.toFixed(6)}`,
            accuracy: `${locationData.accuracy.toFixed(2)}m`
        });
    };

    /**
     * Maneja errores de geolocalización
     */
    const handleError = (err) => {
        setLoading(false);

        let errorMessage;
        let errorType;

        switch (err.code) {
            case err.PERMISSION_DENIED:
                errorType = 'PERMISSION_DENIED';
                errorMessage = 'Permiso de ubicación denegado. Habilite la geolocalización para continuar.';
                setPermissionStatus('denied');
                break;

            case err.POSITION_UNAVAILABLE:
                errorType = 'POSITION_UNAVAILABLE';
                errorMessage = 'Ubicación no disponible. Verifique su conexión GPS.';
                break;

            case err.TIMEOUT:
                errorType = 'TIMEOUT';
                errorMessage = 'Tiempo de espera agotado. Intente nuevamente.';
                break;

            default:
                errorType = 'UNKNOWN_ERROR';
                errorMessage = 'Error desconocido al obtener ubicación.';
        }

        const errorObj = {
            type: errorType,
            message: errorMessage,
            code: err.code,
            originalError: err
        };

        setError(errorObj);
        console.error('❌ Error de geolocalización:', errorObj);
    };

    /**
     * Solicita la ubicación del dispositivo
     */
    const requestLocation = () => {
        if (!isGeolocationSupported()) {
            setError({
                type: 'NOT_SUPPORTED',
                message: 'Geolocalización no soportada en este navegador.',
                code: -1
            });
            return;
        }

        setLoading(true);
        setError(null);

        const geoOptions = {
            enableHighAccuracy,
            timeout,
            maximumAge
        };

        if (watchPosition) {
            // Escuchar cambios de posición continuamente
            const watchId = navigator.geolocation.watchPosition(
                handleSuccess,
                handleError,
                geoOptions
            );

            // Retornar función de limpieza
            return () => navigator.geolocation.clearWatch(watchId);
        } else {
            // Obtener posición una sola vez
            navigator.geolocation.getCurrentPosition(
                handleSuccess,
                handleError,
                geoOptions
            );
        }
    };

    // Verificar permisos al montar
    useEffect(() => {
        checkPermission();
    }, []);

    return {
        location,
        loading,
        error,
        permissionStatus,
        requestLocation,
        isSupported: isGeolocationSupported()
    };
};

/**
 * Hook simplificado para captura única de ubicación
 * 
 * @returns {Object} Estado y función de captura
 */
export const useQuickLocation = () => {
    const { location, loading, error, requestLocation } = useGeolocation({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000 // Cache de 1 minuto
    });

    return {
        gps: location,
        isLoadingGPS: loading,
        gpsError: error,
        captureLocation: requestLocation
    };
};

export default useGeolocation;
