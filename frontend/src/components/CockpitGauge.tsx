import React from 'react';

interface CockpitGaugeProps {
    value: number;
    max: number;
    label: string;
    unit?: string;
    status?: 'safe' | 'warning' | 'critical';
}

const CockpitGauge: React.FC<CockpitGaugeProps> = ({
    value,
    max,
    label,
    unit = '%',
    status = 'safe',
}) => {
    const percentage = (value / max) * 100;
    const circumference = 2 * Math.PI * 50; // radius = 50
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    const colors = {
        safe: '#10b981',
        warning: '#f59e0b',
        critical: '#ef4444',
    };

    return (
        <div className="cockpit-gauge">
            {/* SVG Circle Progress */}
            <svg
                className="absolute inset-0 w-full h-full -rotate-90"
                viewBox="0 0 120 120"
            >
                {/* Background Circle */}
                <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="var(--bg-tertiary)"
                    strokeWidth="8"
                />
                {/* Progress Circle */}
                <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke={colors[status]}
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    style={{
                        transition: 'stroke-dashoffset 0.5s ease-in-out',
                        filter: `drop-shadow(0 0 6px ${colors[status]}40)`,
                    }}
                />
            </svg>

            {/* Value Display */}
            <div className="cockpit-gauge-value">
                {value}
                <span className="text-sm">{unit}</span>
            </div>

            {/* Label */}
            <div className="cockpit-gauge-label">{label}</div>
        </div>
    );
};

export default CockpitGauge;
