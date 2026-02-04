/**
 * OnTrackIA OJT V2.0 - Global Compliance Map
 * ===========================================
 * Mapa interactivo de cobertura normativa global con sistema de vigilancia
 * 
 * Features:
 * - Mapa vectorial con react-simple-maps
 * - Países iluminados según normativas cargadas
 * - Alertas visuales de actualizaciones (parpadeo)
 * - Panel de detalles por región
 * - Filtros por autoridad
 * - Compatible PWA offline
 * 
 * @author OnTrackia Dev Team
 * @date 2026-02-04
 */

import { useState, useEffect } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { Globe, FileSearch, Layers, BellRing, History, CheckCircle } from 'lucide-react';
import { useLanguage } from './LanguageSelector';

const GlobalComplianceMap = () => {
    const { t, language } = useLanguage();
    const [coverage, setCoverage] = useState({});
    const [pendingUpdates, setPendingUpdates] = useState([]);
    const [selectedRegion, setSelectedRegion] = useState(null);
    const [filterAuthority, setFilterAuthority] = useState('all');
    const [loading, setLoading] = useState(true);

    // Mapeo de códigos ISO a países
    const COUNTRY_MAPPING = {
        'EU': ['DEU', 'FRA', 'ESP', 'ITA', 'POL'], // EASA covers EU
        'US': ['USA'],
        'GB': ['GBR'],
        'CO': ['COL'],
        'MX': ['MEX'],
        'PA': ['PAN'],
        'AE': ['ARE'], // UAE
        'SA': ['SAU'], // Saudi Arabia
        'ICAO': 'global' // Internacional
    };

    // Autoridades disponibles
    const AUTHORITIES = [
        { id: 'all', name: { es: 'Todas', en: 'All' } },
        { id: 'EASA', name: { es: 'EASA (Europa)', en: 'EASA (Europe)' } },
        { id: 'FAA', name: { es: 'FAA (USA)', en: 'FAA (USA)' } },
        { id: 'UK CAA', name: { es: 'UK CAA (Reino Unido)', en: 'UK CAA (UK)' } },
        { id: 'RAC Colombia', name: { es: 'RAC (Colombia)', en: 'RAC (Colombia)' } },
        { id: 'ICAO', name: { es: 'ICAO (Internacional)', en: 'ICAO (International)' } }
    ];

    useEffect(() => {
        loadCoverageData();
        loadPendingUpdates();

        // Actualizar cada 5 minutos
        const interval = setInterval(() => {
            loadPendingUpdates();
        }, 5 * 60 * 1000);

        return () => clearInterval(interval);
    }, []);

    const loadCoverageData = async () => {
        try {
            const response = await fetch('/api/rag/coverage');
            if (response.ok) {
                const data = await response.json();
                setCoverage(data.coverage);
            }
        } catch (error) {
            console.error('Error loading coverage:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadPendingUpdates = async () => {
        try {
            const response = await fetch('/api/rag/pending-updates');
            if (response.ok) {
                const data = await response.json();
                setPendingUpdates(data.updates || []);
            }
        } catch (error) {
            console.error('Error loading updates:', error);
        }
    };

    const getCountryColor = (geo) => {
        const countryCode = geo.id;

        // Verificar si este país tiene normativas
        for (const [region, countries] of Object.entries(COUNTRY_MAPPING)) {
            if (Array.isArray(countries) && countries.includes(countryCode)) {
                const regionData = coverage[region];

                if (regionData && regionData.documents > 0) {
                    // Filtrar por autoridad si está seleccionado
                    if (filterAuthority !== 'all') {
                        if (regionData.authority === filterAuthority) {
                            return 'var(--primary)'; // #7c3aed
                        } else {
                            return 'var(--bg-card)';
                        }
                    }
                    return 'var(--primary)'; // #7c3aed
                }
            }
        }

        return 'var(--bg-card)';
    };

    const isCountryUpdating = (geo) => {
        const countryCode = geo.id;

        return pendingUpdates.some(update => {
            const updateCountries = COUNTRY_MAPPING[update.region] || [];
            return updateCountries.includes(countryCode);
        });
    };

    const handleCountryClick = (geo) => {
        const countryCode = geo.id;

        // Encontrar región
        for (const [region, countries] of Object.entries(COUNTRY_MAPPING)) {
            if (Array.isArray(countries) && countries.includes(countryCode)) {
                const regionData = coverage[region];
                if (regionData) {
                    setSelectedRegion({
                        ...regionData,
                        region: region,
                        countryName: geo.properties.name
                    });
                }
                break;
            }
        }
    };

    const handleApproveUpdate = async (updateId) => {
        try {
            const response = await fetch(`/api/rag/approve-update/${updateId}`, {
                method: 'POST'
            });

            if (response.ok) {
                // Reload data
                await loadCoverageData();
                await loadPendingUpdates();
            }
        } catch (error) {
            console.error('Error approving update:', error);
        }
    };

    return (
        <div style={{ padding: '32px', maxWidth: '1600px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                marginBottom: '32px'
            }}>
                <Globe size={32} color="var(--primary)" />
                <div>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        marginBottom: '4px'
                    }}>
                        {language === 'es' ? 'Cobertura Normativa Global' : 'Global Regulatory Coverage'}
                    </h1>
                    <p style={{
                        fontSize: '14px',
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es'
                            ? 'Mapa de vigilancia activa de normativas OJT en tiempo real'
                            : 'Active surveillance map of OJT regulations in real-time'
                        }
                    </p>
                </div>
            </div>

            {/* Filters */}
            <div className="glass-card" style={{ marginBottom: '24px' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    flexWrap: 'wrap'
                }}>
                    <Layers size={20} color="var(--text-secondary)" />
                    <span style={{
                        fontSize: '14px',
                        fontWeight: 600,
                        color: 'var(--text-secondary)'
                    }}>
                        {language === 'es' ? 'Filtrar por autoridad:' : 'Filter by authority:'}
                    </span>

                    {AUTHORITIES.map(auth => (
                        <button
                            key={auth.id}
                            onClick={() => setFilterAuthority(auth.id)}
                            className="btn"
                            style={{
                                height: '36px',
                                padding: '0 16px',
                                fontSize: '13px',
                                background: filterAuthority === auth.id
                                    ? 'var(--primary)'
                                    : 'var(--bg-card)',
                                border: filterAuthority === auth.id
                                    ? 'none'
                                    : '1px solid var(--glass-border)'
                            }}
                        >
                            {auth.name[language]}
                        </button>
                    ))}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '24px' }}>
                {/* Map */}
                <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
                    {loading ? (
                        <div style={{
                            height: '600px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'var(--text-secondary)'
                        }}>
                            {language === 'es' ? 'Cargando mapa...' : 'Loading map...'}
                        </div>
                    ) : (
                        <ComposableMap
                            projection="geoMercator"
                            projectionConfig={{
                                scale: 120,
                                center: [0, 20]
                            }}
                            style={{ width: '100%', height: '600px' }}
                        >
                            <Geographies geography="/world-110m.json">
                                {({ geographies }) =>
                                    geographies.map((geo) => {
                                        const isUpdating = isCountryUpdating(geo);

                                        return (
                                            <Geography
                                                key={geo.rsmKey}
                                                geography={geo}
                                                fill={getCountryColor(geo)}
                                                stroke="var(--glass-border)"
                                                strokeWidth={0.5}
                                                style={{
                                                    default: { outline: 'none' },
                                                    hover: {
                                                        fill: 'var(--primary-hover)',
                                                        outline: 'none',
                                                        cursor: 'pointer'
                                                    },
                                                    pressed: { outline: 'none' }
                                                }}
                                                onClick={() => handleCountryClick(geo)}
                                                className={isUpdating ? 'country-updating' : ''}
                                            />
                                        );
                                    })
                                }
                            </Geographies>
                        </ComposableMap>
                    )}
                </div>

                {/* Side Panel */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {/* Pending Updates */}
                    {pendingUpdates.length > 0 && (
                        <div className="glass-card">
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                marginBottom: '16px'
                            }}>
                                <BellRing size={20} color="var(--warning)" className="pulse" />
                                <h3 style={{
                                    fontSize: '16px',
                                    fontWeight: 600,
                                    color: 'var(--text-primary)'
                                }}>
                                    {language === 'es' ? 'Actualizaciones Pendientes' : 'Pending Updates'}
                                </h3>
                            </div>

                            {pendingUpdates.map((update, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        padding: '12px',
                                        background: 'var(--bg-card)',
                                        border: '1px solid rgba(245, 158, 11, 0.3)',
                                        borderRadius: '8px',
                                        marginBottom: '12px'
                                    }}
                                >
                                    <div style={{
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        color: 'var(--text-primary)',
                                        marginBottom: '6px'
                                    }}>
                                        {update.document_code} ({update.authority})
                                    </div>

                                    <div style={{
                                        fontSize: '12px',
                                        color: 'var(--text-secondary)',
                                        marginBottom: '8px'
                                    }}>
                                        {update.change_summary}
                                    </div>

                                    <button
                                        onClick={() => handleApproveUpdate(update.id)}
                                        className="btn"
                                        style={{
                                            width: '100%',
                                            height: '36px',
                                            fontSize: '13px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px'
                                        }}
                                    >
                                        <CheckCircle size={16} />
                                        {language === 'es' ? 'Aprobar e Indexar' : 'Approve & Index'}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Region Details */}
                    <div className="glass-card">
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            marginBottom: '16px'
                        }}>
                            <FileSearch size={20} color="var(--primary)" />
                            <h3 style={{
                                fontSize: '16px',
                                fontWeight: 600,
                                color: 'var(--text-primary)'
                            }}>
                                {language === 'es' ? 'Detalles de Región' : 'Region Details'}
                            </h3>
                        </div>

                        {selectedRegion ? (
                            <>
                                <div style={{
                                    padding: '12px',
                                    background: 'var(--bg-card)',
                                    borderRadius: '8px',
                                    marginBottom: '16px'
                                }}>
                                    <div style={{
                                        fontSize: '18px',
                                        fontWeight: 600,
                                        color: 'var(--primary)',
                                        marginBottom: '8px'
                                    }}>
                                        {selectedRegion.countryName}
                                    </div>

                                    <div style={{
                                        fontSize: '13px',
                                        color: 'var(--text-secondary)',
                                        marginBottom: '4px'
                                    }}>
                                        <strong>{language === 'es' ? 'Autoridad:' : 'Authority:'}</strong> {selectedRegion.authority}
                                    </div>

                                    <div style={{
                                        fontSize: '13px',
                                        color: 'var(--text-secondary)'
                                    }}>
                                        <strong>{language === 'es' ? 'Documentos:' : 'Documents:'}</strong> {selectedRegion.documents}
                                    </div>
                                </div>

                                {selectedRegion.regulations && selectedRegion.regulations.map((reg, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            padding: '10px 12px',
                                            background: 'var(--bg-deep)',
                                            border: '1px solid var(--glass-border)',
                                            borderRadius: '6px',
                                            marginBottom: '8px'
                                        }}
                                    >
                                        <div style={{
                                            fontSize: '13px',
                                            fontWeight: 600,
                                            color: 'var(--text-primary)',
                                            marginBottom: '4px'
                                        }}>
                                            {reg.document_code}
                                        </div>
                                        <div style={{
                                            fontSize: '11px',
                                            color: 'var(--text-muted)'
                                        }}>
                                            {language === 'es' ? 'Actualizado:' : 'Updated:'} {reg.update_date}
                                        </div>
                                    </div>
                                ))}
                            </>
                        ) : (
                            <div style={{
                                padding: '48px 24px',
                                textAlign: 'center',
                                color: 'var(--text-muted)',
                                fontSize: '13px'
                            }}>
                                {language === 'es'
                                    ? 'Haz clic en un país para ver detalles'
                                    : 'Click on a country to see details'
                                }
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* CSS for pulsing animation */}
            <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        .pulse {
          animation: pulse 2s infinite;
        }
        
        @keyframes blink-border {
          0%, 100% { stroke: var(--warning); stroke-width: 2; }
          50% { stroke: transparent; stroke-width: 2; }
        }
        
        .country-updating {
          animation: blink-border 2s infinite;
        }
      `}</style>
        </div>
    );
};

export default GlobalComplianceMap;
