import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Lock } from 'lucide-react';

interface CockpitPanelProps {
    title: string;
    children: React.ReactNode;
    defaultExpanded?: boolean;
    hasIntegrity?: boolean;
    integrityHash?: string;
    className?: string;
}

const CockpitPanel: React.FC<CockpitPanelProps> = ({
    title,
    children,
    defaultExpanded = true,
    hasIntegrity = false,
    integrityHash,
    className = '',
}) => {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className={`cockpit-panel-collapsible ${className}`}>
            <div
                className="cockpit-panel-header"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-primary">{title}</h3>
                    {hasIntegrity && (
                        <div
                            className="integrity-badge"
                            title={`SHA-256: ${integrityHash}`}
                            onClick={(e) => e.stopPropagation()}
                        >
                            <Lock className="integrity-badge-icon" />
                            <span>VERIFIED</span>
                        </div>
                    )}
                </div>
                {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
            <div className={`cockpit-panel-content ${isExpanded ? 'expanded' : ''}`}>
                {children}
            </div>
        </div>
    );
};

export default CockpitPanel;
