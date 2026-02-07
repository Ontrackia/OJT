import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Plane, Battery, MapPin, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import CockpitGauge from '../CockpitGauge';
import './UASCockpit.css';

interface Aircraft {
    aircraft_id: string;
    registration: string;
    manufacturer: string;
    model: string;
    mtow_kg: number;
    category: string;
    status: string;
    total_flight_hours: number;
}

interface BatteryHealth {
    battery_serial: string;
    cycle_count: number;
    health_percentage: number;
    voltage: number;
    temperature: number;
    last_charge_date: string;
}

interface Mission {
    mission_id: string;
    mission_type: string;
    description: string;
    location: string;
    sail_level: string;
    ground_risk_class: string;
    air_risk_class: string;
    status: string;
    created_at: string;
}

export const UASCockpit: React.FC = () => {
    const { t } = useTranslation();
    const [selectedAircraft, setSelectedAircraft] = useState<Aircraft | null>(null);
    const [batteryHealth, setBatteryHealth] = useState<BatteryHealth | null>(null);
    const [activeMissions, setActiveMissions] = useState<Mission[]>([]);
    const [loading, setLoading] = useState(true);

    const [showMap, setShowMap] = useState(false);

    useEffect(() => {
        loadUASData();
    }, []);

    const loadUASData = async () => {
        try {
            // Mock data for now
            setSelectedAircraft({
                aircraft_id: '123',
                registration: 'EC-ABC',
                manufacturer: 'DJI',
                model: 'Matrice 300 RTK',
                mtow_kg: 9.0,
                category: 'Specific',
                status: 'Active',
                total_flight_hours: 145.5
            });

            setBatteryHealth({
                battery_serial: 'BAT-001',
                cycle_count: 87,
                health_percentage: 92,
                voltage: 22.8,
                temperature: 24.5,
                last_charge_date: new Date().toISOString()
            });

            setActiveMissions([
                {
                    mission_id: 'M001',
                    mission_type: 'Photogrammetry',
                    description: 'Aerial survey of construction site',
                    location: 'Madrid, Spain',
                    sail_level: 'III',
                    ground_risk_class: '4',
                    air_risk_class: 'B',
                    status: 'Planned',
                    created_at: new Date().toISOString()
                }
            ]);

            setLoading(false);
        } catch (error) {
            console.error('Error loading UAS data:', error);
            setLoading(false);
        }
    };

    const getSAILColor = (sail: string): string => {
        const colors: Record<string, string> = {
            'I': '#00ff00',
            'II': '#7fff00',
            'III': '#ffff00',
            'IV': '#ffa500',
            'V': '#ff4500',
            'VI': '#ff0000'
        };
        return colors[sail] || '#888';
    };

    const getStatusColor = (status: string): string => {
        const colors: Record<string, string> = {
            'Active': '#00ff00',
            'Maintenance': '#ffa500',
            'Grounded': '#ff0000',
            'Planned': '#00bfff',
            'Approved': '#7fff00',
            'InProgress': '#ffa500',
            'Completed': '#00ff00',
            'Cancelled': '#ff0000'
        };
        return colors[status] || '#888';
    };

    if (loading) {
        return (
            <div className="uas-cockpit-loading">
                <div className="loading-spinner"></div>
                <p>{t('uas.loading')}</p>
            </div>
        );
    }

    // Dynamic import to avoid SSR issues if any, but standard import is fine for CRA
    const UASGlassMap = require('../common/UASGlassMap').default;

    return (
        <div className="uas-cockpit glass-cockpit">
            {/* Header */}
            <div className="uas-cockpit-header">
                <div className="header-left">
                    <Plane className="header-icon" />
                    <h1>{t('uas.cockpit.title')}</h1>
                </div>
                <div className="header-right">
                    <button
                        className={`action-button ${showMap ? 'primary' : 'secondary'}`}
                        onClick={() => setShowMap(!showMap)}
                    >
                        <MapPin size={16} />
                        {showMap ? 'Dashboard' : 'Map View'}
                    </button>
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(selectedAircraft?.status || 'Active') }}>
                        {selectedAircraft?.status}
                    </div>
                </div>
            </div>

            {showMap ? (
                <div style={{ height: '600px', padding: '0 20px 20px 20px' }}>
                    <UASGlassMap
                        center={[40.4168, -3.7038]}
                        zoom={14}
                        zones={[
                            { center: [40.4168, -3.7038], radius: 500, color: 'red', type: 'No-Fly Zone' },
                            { center: [40.4200, -3.7100], radius: 300, color: 'green', type: 'VLOS Limit' }
                        ]}
                        markers={activeMissions.map(m => ({
                            position: [40.4180, -3.7050], // Mock position
                            title: m.mission_id,
                            description: m.description
                        }))}
                    />
                </div>
            ) : (
                <>
                    {/* Aircraft Info Panel */}
                    {selectedAircraft && (
                        <div className="aircraft-info-panel glass-panel">
                            <h2>{t('uas.aircraft.info')}</h2>
                            <div className="aircraft-details">
                                <div className="detail-row">
                                    <span className="label">{t('uas.aircraft.registration')}:</span>
                                    <span className="value">{selectedAircraft.registration}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.aircraft.model')}:</span>
                                    <span className="value">{selectedAircraft.manufacturer} {selectedAircraft.model}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.aircraft.mtow')}:</span>
                                    <span className="value">{selectedAircraft.mtow_kg} kg</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.aircraft.category')}:</span>
                                    <span className="value">{selectedAircraft.category}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Gauges Row */}
                    <div className="gauges-row">
                        {/* Battery Health Gauge */}
                        {batteryHealth && (
                            <CockpitGauge
                                label={t('uas.battery.health')}
                                value={batteryHealth.health_percentage}
                                max={100}
                                unit="%"
                                thresholds={{ warning: 30, critical: 15 }}
                                icon={<Battery />}
                            />
                        )}

                        {/* Flight Hours Gauge */}
                        {selectedAircraft && (
                            <CockpitGauge
                                label={t('uas.aircraft.flightHours')}
                                value={selectedAircraft.total_flight_hours}
                                max={500}
                                unit="hrs"
                                thresholds={{ warning: 400, critical: 450 }}
                                icon={<Clock />}
                            />
                        )}

                        {/* Battery Cycles Gauge */}
                        {batteryHealth && (
                            <CockpitGauge
                                label={t('uas.battery.cycles')}
                                value={batteryHealth.cycle_count}
                                max={200}
                                unit="cycles"
                                thresholds={{ warning: 150, critical: 180 }}
                                icon={<Battery />}
                            />
                        )}
                    </div>

                    {/* Battery Details Panel */}
                    {batteryHealth && (
                        <div className="battery-panel glass-panel">
                            <h2>
                                <Battery className="panel-icon" />
                                {t('uas.battery.details')}
                            </h2>
                            <div className="battery-details">
                                <div className="detail-row">
                                    <span className="label">{t('uas.battery.serial')}:</span>
                                    <span className="value">{batteryHealth.battery_serial}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.battery.voltage')}:</span>
                                    <span className="value">{batteryHealth.voltage} V</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.battery.temperature')}:</span>
                                    <span className="value">{batteryHealth.temperature} °C</span>
                                </div>
                                <div className="detail-row">
                                    <span className="label">{t('uas.battery.lastCharge')}:</span>
                                    <span className="value">{new Date(batteryHealth.last_charge_date).toLocaleString()}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Active Missions Panel */}
                    <div className="missions-panel glass-panel">
                        <h2>
                            <MapPin className="panel-icon" />
                            {t('uas.missions.active')}
                        </h2>
                        {activeMissions.length === 0 ? (
                            <p className="no-missions">{t('uas.missions.none')}</p>
                        ) : (
                            <div className="missions-list">
                                {activeMissions.map((mission) => (
                                    <div key={mission.mission_id} className="mission-card">
                                        <div className="mission-header">
                                            <span className="mission-type">{mission.mission_type}</span>
                                            <span
                                                className="mission-status"
                                                style={{ backgroundColor: getStatusColor(mission.status) }}
                                            >
                                                {mission.status}
                                            </span>
                                        </div>
                                        <p className="mission-description">{mission.description}</p>
                                        <div className="mission-details">
                                            <div className="detail-item">
                                                <MapPin size={14} />
                                                <span>{mission.location}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="sail-badge" style={{ backgroundColor: getSAILColor(mission.sail_level) }}>
                                                    SAIL {mission.sail_level}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="risk-indicators">
                                            <span className="risk-item">
                                                <AlertTriangle size={14} />
                                                Ground Risk: {mission.ground_risk_class}
                                            </span>
                                            <span className="risk-item">
                                                <AlertTriangle size={14} />
                                                Air Risk: {mission.air_risk_class}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Quick Actions */}
                    <div className="quick-actions">
                        <button className="action-button primary">
                            <Plane size={18} />
                            {t('uas.actions.newMission')}
                        </button>
                        <button className="action-button secondary">
                            <CheckCircle size={18} />
                            {t('uas.actions.preFlightCheck')}
                        </button>
                        <button
                            className="action-button secondary"
                            onClick={() => setShowMap(true)}
                        >
                            <MapPin size={18} />
                            {t('uas.actions.viewMap')}
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

