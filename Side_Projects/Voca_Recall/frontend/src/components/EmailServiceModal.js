import React, { useState, useEffect } from 'react';
import { X, Save, Clock, Hash, Filter, Calendar } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const EmailServiceModal = ({ isOpen, onClose, database, service = null, onSave }) => {
  const [formData, setFormData] = useState({
    service_name: '',
    description: '',
    send_time: '09:00',
    timezone: 'UTC',
    frequency: 'daily',
    vocabulary_count: 10,
    selection_method: 'random',
    date_range_start: '',
    date_range_end: '',
    is_active: true,
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (service) {
      // Edit mode: populate form with service data
      setFormData({
        service_name: service.service_name || '',
        description: service.description || '',
        send_time: service.send_time || '09:00',
        timezone: service.timezone || 'UTC',
        frequency: service.frequency || 'daily',
        vocabulary_count: service.vocabulary_count || 10,
        selection_method: service.selection_method || 'random',
        date_range_start: service.date_range_start || '',
        date_range_end: service.date_range_end || '',
        is_active: service.is_active !== undefined ? service.is_active : true,
      });
    } else if (database) {
      // Create mode: set default name based on database
      setFormData(prev => ({
        ...prev,
        service_name: `${database.database_name} - Email Service`,
      }));
    }
  }, [service, database]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const payload = {
        ...formData,
        database_id: database.id,
      };

      let response;
      if (service) {
        // Update existing service
        response = await axios.put(`/api/email-services/${service.id}`, payload);
      } else {
        // Create new service
        response = await axios.post('/api/email-services', payload);
      }

      toast.success(service ? 'Service updated successfully!' : 'Service created successfully!');
      onSave(response.data.service);
      onClose();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to save service';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            {service ? 'Edit Email Service' : 'Create Email Service'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Service Name */}
          <div>
            <label className="form-label">Service Name *</label>
            <input
              type="text"
              value={formData.service_name}
              onChange={(e) => setFormData({ ...formData, service_name: e.target.value })}
              className="input-field"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="form-label">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input-field"
              rows="3"
              placeholder="Optional description for this email service"
            />
          </div>

          {/* Schedule Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Schedule
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="form-label">Send Time *</label>
                <input
                  type="time"
                  value={formData.send_time}
                  onChange={(e) => setFormData({ ...formData, send_time: e.target.value })}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="form-label">Timezone *</label>
                <select
                  value={formData.timezone}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                  className="input-field"
                  required
                >
                  <option value="UTC">UTC +0</option>
                  <option value="America/New_York">Eastern Time (US & Canada) -5/-4</option>
                  <option value="America/Chicago">Central Time (US & Canada) -6/-5</option>
                  <option value="America/Denver">Mountain Time (US & Canada) -7/-6</option>
                  <option value="America/Los_Angeles">Pacific Time (US & Canada) -8/-7</option>
                  <option value="Europe/London">London +0/+1</option>
                  <option value="Europe/Paris">Paris +1/+2</option>
                  <option value="Europe/Berlin">Berlin +1/+2</option>
                  <option value="Asia/Tokyo">Tokyo +9</option>
                  <option value="Asia/Shanghai">Shanghai +8</option>
                  <option value="Asia/Taipei">Taiwan +8</option>
                  <option value="Asia/Hong_Kong">Hong Kong +8</option>
                  <option value="Asia/Singapore">Singapore +8</option>
                  <option value="Australia/Sydney">Sydney +10/+11</option>
                </select>
              </div>

              <div>
                <label className="form-label">Frequency *</label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                  className="input-field"
                  required
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
            </div>
          </div>

          {/* Vocabulary Settings Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Hash className="h-5 w-5 mr-2" />
              Vocabulary Settings
            </h3>

            <div className="space-y-4">
              <div>
                <label className="form-label">Vocabulary Count *</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={formData.vocabulary_count}
                  onChange={(e) => setFormData({ ...formData, vocabulary_count: parseInt(e.target.value) })}
                  className="input-field"
                  required
                />
                <p className="mt-1 text-sm text-gray-500">
                  Number of vocabulary items per email (1-50)
                </p>
              </div>

              <div>
                <label className="form-label flex items-center">
                  <Filter className="h-4 w-4 mr-2" />
                  Selection Method *
                </label>
                <select
                  value={formData.selection_method}
                  onChange={(e) => setFormData({ ...formData, selection_method: e.target.value })}
                  className="input-field"
                  required
                >
                  <option value="random">Random Selection</option>
                  <option value="latest">Latest Items</option>
                  <option value="date_range">Date Range Selection</option>
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  {formData.selection_method === 'random' && 'Randomly select items from the entire database'}
                  {formData.selection_method === 'latest' && 'Select the most recently created items'}
                  {formData.selection_method === 'date_range' && 'Select items created within a specific date range'}
                </p>
              </div>

              {/* Date Range Fields - Only show for date_range selection method */}
              {formData.selection_method === 'date_range' && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <label className="form-label flex items-center mb-3">
                    <Calendar className="h-4 w-4 mr-2" />
                    Date Range
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-gray-600 mb-1 block">Start Date</label>
                      <input
                        type="date"
                        value={formData.date_range_start}
                        onChange={(e) => setFormData({ ...formData, date_range_start: e.target.value })}
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-gray-600 mb-1 block">End Date</label>
                      <input
                        type="date"
                        value={formData.date_range_end}
                        onChange={(e) => setFormData({ ...formData, date_range_end: e.target.value })}
                        className="input-field"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Active Status */}
          <div className="border-t pt-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                Active (send emails automatically)
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="border-t pt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary inline-flex items-center"
              disabled={saving}
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {service ? 'Update Service' : 'Create Service'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmailServiceModal;
