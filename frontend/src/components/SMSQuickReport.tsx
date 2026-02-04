import React, { useState } from 'react';
import { Upload, AlertCircle, Send, X } from 'lucide-react';

interface SMSQuickReportProps {
    onClose: () => void;
    language: 'es' | 'en';
}

const SMSQuickReport: React.FC<SMSQuickReportProps> = ({ onClose, language }) => {
    const [formData, setFormData] = useState({
        description: '',
        notifierName: '',
        notifierContact: '',
        location: '',
        severity: 'MEDIUM',
    });
    const [evidences, setEvidences] = useState<File[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);

    const translations = {
        es: {
            title: 'Reporte Voluntario Confidencial - SMS',
            generalInfo: 'Generalidades',
            date: 'Fecha / Date',
            notifier: 'Notificador / Notifier',
            notifierPlaceholder: 'Seleccione Notificador (Opcional)',
            anonymous: 'Anónimo',
            description: 'Describe con el mayor detalle posible el peligro, evento o situación. Puedes incluir tus recomendaciones de cómo resolver el peligro o situación.',
            feedbackNote: 'NOTA: Si deseas recibir retroalimentación del seguimiento de tu reporte puedes incluir tu correo-e o teléfono.',
            evidenceTitle: 'Si tienes algún documento o foto que pueda ser usado como evidencia para apoyar tu reporte, por favor agrégalo aquí.',
            location: 'Ubicación (Opcional)',
            locationPlaceholder: 'Ej: Hangar 3, Pista Principal',
            severity: 'Severidad',
            severityLow: 'Baja',
            severityMedium: 'Media',
            severityHigh: 'Alta',
            severityCritical: 'Crítica',
            submit: 'Enviar Reporte',
            cancel: 'Cancelar',
            successTitle: '✅ Reporte Recibido',
            successMessage: 'Gracias por contribuir a la seguridad. Tu reporte ha sido registrado.',
            reportId: 'ID de Reporte',
        },
        en: {
            title: 'Confidential Voluntary Report - SMS',
            generalInfo: 'General Information',
            date: 'Date',
            notifier: 'Notifier',
            notifierPlaceholder: 'Select Notifier (Optional)',
            anonymous: 'Anonymous',
            description: 'Describe in as much detail as possible the hazard, event or situation. You can include your recommendations on how to resolve the hazard or situation.',
            feedbackNote: 'NOTE: If you wish to receive feedback on the follow-up of your report, you can include your email or phone.',
            evidenceTitle: 'If you have any document or photo that can be used as evidence to support your report, please add it here.',
            location: 'Location (Optional)',
            locationPlaceholder: 'E.g: Hangar 3, Main Runway',
            severity: 'Severity',
            severityLow: 'Low',
            severityMedium: 'Medium',
            severityHigh: 'High',
            severityCritical: 'Critical',
            submit: 'Submit Report',
            cancel: 'Cancel',
            successTitle: '✅ Report Received',
            successMessage: 'Thank you for contributing to safety. Your report has been registered.',
            reportId: 'Report ID',
        },
    };

    const t = translations[language];

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setEvidences(Array.from(e.target.files));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const formDataToSend = new FormData();
            formDataToSend.append('description', formData.description);
            formDataToSend.append('notifier_name', formData.notifierName);
            formDataToSend.append('notifier_contact', formData.notifierContact);
            formDataToSend.append('location', formData.location);
            formDataToSend.append('severity', formData.severity);
            formDataToSend.append('ip_address', 'client_ip'); // Will be replaced by backend

            evidences.forEach((file) => {
                formDataToSend.append('evidences', file);
            });

            const response = await fetch('/api/v2/sms-quick/report', {
                method: 'POST',
                body: formDataToSend,
            });

            if (response.ok) {
                setShowSuccess(true);
                setTimeout(() => {
                    onClose();
                }, 3000);
            }
        } catch (error) {
            console.error('Error submitting report:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (showSuccess) {
        return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full text-center">
                    <div className="text-6xl mb-4">✅</div>
                    <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                        {t.successTitle}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-300 mb-6">
                        {t.successMessage}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full my-8">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
                    <div className="flex justify-between items-center">
                        <h2 className="text-2xl font-bold">{t.title}</h2>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-white/20 rounded-full p-2 transition"
                        >
                            <X size={24} />
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Generalidades */}
                    <div className="bg-blue-50 dark:bg-gray-700 p-4 rounded-lg">
                        <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
                            {t.generalInfo}
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Date */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    {t.date}
                                </label>
                                <input
                                    type="text"
                                    value={new Date().toLocaleDateString()}
                                    disabled
                                    className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg"
                                />
                            </div>

                            {/* Notifier (Optional) */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    {t.notifier}
                                </label>
                                <input
                                    type="text"
                                    value={formData.notifierName}
                                    onChange={(e) => setFormData({ ...formData, notifierName: e.target.value })}
                                    placeholder={t.notifierPlaceholder}
                                    className="w-full px-4 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    {t.anonymous}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="bg-blue-50 dark:bg-gray-700 p-4 rounded-lg">
                        <label className="block text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                            {t.description}
                        </label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            required
                            rows={6}
                            className="w-full px-4 py-3 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                            placeholder={language === 'es' ? 'Describe el evento, peligro o situación...' : 'Describe the event, hazard or situation...'}
                        />
                        <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded">
                            <p className="text-sm text-red-700 dark:text-red-300">
                                {t.feedbackNote}
                            </p>
                        </div>
                        <input
                            type="text"
                            value={formData.notifierContact}
                            onChange={(e) => setFormData({ ...formData, notifierContact: e.target.value })}
                            placeholder="correo@ejemplo.com o +123456789"
                            className="w-full mt-3 px-4 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {/* Location & Severity */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                {t.location}
                            </label>
                            <input
                                type="text"
                                value={formData.location}
                                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                placeholder={t.locationPlaceholder}
                                className="w-full px-4 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                {t.severity}
                            </label>
                            <select
                                value={formData.severity}
                                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                                className="w-full px-4 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="LOW">{t.severityLow}</option>
                                <option value="MEDIUM">{t.severityMedium}</option>
                                <option value="HIGH">{t.severityHigh}</option>
                                <option value="CRITICAL">{t.severityCritical}</option>
                            </select>
                        </div>
                    </div>

                    {/* Evidence Upload */}
                    <div className="bg-blue-50 dark:bg-gray-700 p-4 rounded-lg">
                        <label className="block text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                            {t.evidenceTitle}
                        </label>
                        <div className="flex items-center justify-center w-full">
                            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 dark:border-gray-500 border-dashed rounded-lg cursor-pointer bg-white dark:bg-gray-600 hover:bg-gray-50 dark:hover:bg-gray-500 transition">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <Upload className="w-10 h-10 mb-3 text-gray-400" />
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                        <span className="font-semibold">
                                            {language === 'es' ? 'Clic para subir' : 'Click to upload'}
                                        </span>
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        PNG, JPG, PDF (MAX. 10MB)
                                    </p>
                                </div>
                                <input
                                    type="file"
                                    multiple
                                    onChange={handleFileChange}
                                    className="hidden"
                                    accept="image/*,.pdf"
                                />
                            </label>
                        </div>
                        {evidences.length > 0 && (
                            <div className="mt-3">
                                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                                    {evidences.length} {language === 'es' ? 'archivo(s) seleccionado(s)' : 'file(s) selected'}
                                </p>
                                <ul className="text-xs text-gray-500 dark:text-gray-400">
                                    {evidences.map((file, index) => (
                                        <li key={index}>• {file.name}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-4 pt-4">
                        <button
                            type="submit"
                            disabled={isSubmitting || !formData.description}
                            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2"
                        >
                            <Send size={20} />
                            {isSubmitting ? (language === 'es' ? 'Enviando...' : 'Sending...') : t.submit}
                        </button>
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2"
                        >
                            <X size={20} />
                            {t.cancel}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SMSQuickReport;
