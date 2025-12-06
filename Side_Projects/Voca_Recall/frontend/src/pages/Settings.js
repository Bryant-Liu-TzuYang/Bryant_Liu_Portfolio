import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Settings as SettingsIcon, 
  User, 
  Mail, 
  Clock, 
  Save,
  Eye,
  EyeOff,
  Send,
  Activity
} from 'lucide-react';
import LoggingStatus from '../components/LoggingStatus';

const Settings = () => {
  const { user, updateProfile } = useAuth();
  const [emailSettings, setEmailSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get('/api/user/settings');
      setEmailSettings(response.data.email_settings);
      
      // Set form values
      if (response.data.email_settings) {
        setValue('vocabulary_count', response.data.email_settings.vocabulary_count);
        setValue('send_time', response.data.email_settings.send_time);
        setValue('timezone', response.data.email_settings.timezone);
        setValue('is_active', response.data.email_settings.is_active);
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const onProfileSubmit = async (data) => {
    try {
      const result = await updateProfile(data);
      if (result.success) {
        toast.success('Profile updated successfully!');
      }
    } catch (error) {
      console.error('Profile update error:', error);
    }
  };

  const onEmailSettingsSubmit = async (data) => {
    try {
      await axios.put('/api/user/settings', data);
      toast.success('Email settings updated successfully!');
      fetchSettings();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to update email settings';
      toast.error(message);
    }
  };

  const sendTestEmail = async () => {
    setSendingTest(true);
    try {
      const apiKey = prompt('Please enter your Notion API key:');
      if (!apiKey) return;

      const databaseId = prompt('Please enter your database ID:');
      if (!databaseId) return;

      const vocabularyCount = prompt('How many vocabulary items? (default: 5)', '5');

      await axios.post('/api/email/send-test', {
        notion_api_key: apiKey,
        database_id: databaseId,
        vocabulary_count: parseInt(vocabularyCount) || 5,
      });

      toast.success('Test email sent successfully!');
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to send test email';
      toast.error(message);
    } finally {
      setSendingTest(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'email', name: 'Email Settings', icon: Mail },
    { id: 'logging', name: 'Logging', icon: Activity },
  ];

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your profile and email preferences.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Information</h2>
          <form onSubmit={handleSubmit(onProfileSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="first_name" className="form-label">
                  First Name
                </label>
                <input
                  id="first_name"
                  type="text"
                  className={`input-field ${
                    errors.first_name ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                  }`}
                  defaultValue={user?.first_name}
                  {...register('first_name', {
                    required: 'First name is required',
                    minLength: {
                      value: 2,
                      message: 'First name must be at least 2 characters',
                    },
                  })}
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="form-label">
                  Last Name
                </label>
                <input
                  id="last_name"
                  type="text"
                  className={`input-field ${
                    errors.last_name ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                  }`}
                  defaultValue={user?.last_name}
                  {...register('last_name', {
                    required: 'Last name is required',
                    minLength: {
                      value: 2,
                      message: 'Last name must be at least 2 characters',
                    },
                  })}
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                className="input-field bg-gray-50"
                value={user?.email}
                disabled
              />
              <p className="mt-1 text-sm text-gray-500">
                Email address cannot be changed. Contact support if needed.
              </p>
            </div>

            <div className="flex justify-end">
              <button type="submit" className="btn-primary inline-flex items-center">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Email Settings Tab */}
      {activeTab === 'email' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Email Preferences</h2>
            <form onSubmit={handleSubmit(onEmailSettingsSubmit)} className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Email frequency is now configured per database. Go to the Databases page to set individual frequencies for each connected database.
                </p>
              </div>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="vocabulary_count" className="form-label">
                    Vocabulary Count
                  </label>
                  <input
                    id="vocabulary_count"
                    type="number"
                    min="1"
                    max="50"
                    className={`input-field ${
                      errors.vocabulary_count ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                    }`}
                    {...register('vocabulary_count', {
                      required: 'Vocabulary count is required',
                      min: { value: 1, message: 'Minimum 1 vocabulary item' },
                      max: { value: 50, message: 'Maximum 50 vocabulary items' },
                    })}
                  />
                  {errors.vocabulary_count && (
                    <p className="mt-1 text-sm text-red-600">{errors.vocabulary_count.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="send_time" className="form-label">
                    Send Time
                  </label>
                  <input
                    id="send_time"
                    type="time"
                    className="input-field"
                    {...register('send_time')}
                  />
                </div>

                <div>
                  <label htmlFor="timezone" className="form-label">
                    Timezone
                  </label>
                  <select
                    id="timezone"
                    className="input-field"
                    {...register('timezone')}
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  id="is_active"
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  {...register('is_active')}
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Enable email notifications
                </label>
              </div>

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={sendTestEmail}
                  disabled={sendingTest}
                  className="btn-secondary inline-flex items-center"
                >
                  {sendingTest ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                  ) : (
                    <Send className="h-4 w-4 mr-2" />
                  )}
                  Send Test Email
                </button>

                <button type="submit" className="btn-primary inline-flex items-center">
                  <Save className="h-4 w-4 mr-2" />
                  Save Settings
                </button>
              </div>
            </form>
          </div>

          {/* Email Logs */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Email Activity</h3>
            <EmailLogs />
          </div>
        </div>
      )}

      {/* Logging Tab */}
      {activeTab === 'logging' && (
        <div className="space-y-6">
          <LoggingStatus />
        </div>
      )}
    </div>
  );
};

// Email Logs Component
const EmailLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/api/email/logs?per_page=5');
      setLogs(response.data.logs);
    } catch (error) {
      console.error('Failed to fetch email logs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-4 bg-gray-200 rounded"></div>
      ))}
    </div>;
  }

  if (logs.length === 0) {
    return <p className="text-gray-500">No email activity yet.</p>;
  }

  return (
    <div className="space-y-3">
      {logs.map((log) => (
        <div key={log.id} className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-3">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              log.status === 'sent' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {log.status}
            </span>
            <span className="text-gray-600">
              {new Date(log.sent_at).toLocaleDateString()} at{' '}
              {new Date(log.sent_at).toLocaleTimeString()}
            </span>
          </div>
          <span className="text-gray-500">
            {log.vocabulary_items?.length || 0} items
          </span>
        </div>
      ))}
    </div>
  );
};

export default Settings; 