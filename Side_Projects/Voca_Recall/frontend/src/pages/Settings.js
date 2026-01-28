import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
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
  Activity,
  Key,
  Database,
  Filter
} from 'lucide-react';
import LoggingStatus from '../components/LoggingStatus';

const Settings = () => {
  const { user, updateProfile, isDeveloper } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [databases, setDatabases] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [emailSettings, setEmailSettings] = useState(null);
  const [savingSettings, setSavingSettings] = useState(false);
  const [emailServices, setEmailServices] = useState([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  useEffect(() => {
    fetchDatabases();
    fetchEmailSettings();
    fetchEmailServices();
    setLoading(false);
  }, []);

  const fetchDatabases = async () => {
    try {
      const response = await axios.get('/api/databases');
      setDatabases(response.data.databases);
      if (response.data.databases.length > 0) {
        setSelectedDatabase(response.data.databases[0].id.toString());
      }
    } catch (error) {
      console.error('Failed to fetch databases:', error);
    }
  };

  const fetchEmailSettings = async () => {
    try {
      const response = await axios.get('/api/user/email-settings');
      setEmailSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch email settings:', error);
    }
  };

  const fetchEmailServices = async () => {
    try {
      const response = await axios.get('/api/email-services');
      setEmailServices(response.data.services || []);
    } catch (error) {
      console.error('Failed to fetch email services:', error);
    }
  };

  const saveEmailSettings = async (updatedSettings) => {
    setSavingSettings(true);
    try {
      const response = await axios.put('/api/user/email-settings', updatedSettings);
      setEmailSettings(response.data.email_settings);
      toast.success('Email settings updated successfully!');
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to update email settings';
      toast.error(message);
    } finally {
      setSavingSettings(false);
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

  const sendTestEmail = async () => {
    if (!selectedDatabase) {
      toast.error('Please select a database first or add one on the Databases page');
      return;
    }

    const vocabularyCount = prompt('How many vocabulary items? (default: 5)', '5');
    if (vocabularyCount === null) return;

    setSendingTest(true);
    try {
      await axios.post('/api/email/send-test', {
        database_pk: parseInt(selectedDatabase),
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
    { id: 'services', name: 'Email Services', icon: Database },
    ...(isDeveloper() ? [{ id: 'logging', name: 'Logging', icon: Activity }] : []),
    { id: 'tokens', name: 'Tokens', icon: Key },
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
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Test Email</h2>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Email frequency and vocabulary count are configured per email service. 
                Go to the <a href="/databases" className="underline font-semibold">Databases page</a> to configure individual email services.
              </p>
            </div>

            <div className="space-y-4">
              {databases.length > 0 ? (
                <>
                  <div>
                    <label htmlFor="test-database" className="form-label">
                      Select Database for Test Email
                    </label>
                    <select
                      id="test-database"
                      value={selectedDatabase}
                      onChange={(e) => setSelectedDatabase(e.target.value)}
                      className="input-field"
                    >
                      {databases.map((db) => (
                        <option key={db.id} value={db.id}>
                          {db.database_name}
                        </option>
                      ))}
                    </select>
                  </div>
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
                </>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    No databases found. Please add a database on the{' '}
                    <a href="/databases" className="underline font-semibold">
                      Databases page
                    </a>{' '}
                    to send test emails.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Email Logs */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Email Activity</h3>
            <EmailLogs />
          </div>
        </div>
      )}

      {/* Email Services Tab */}
      {activeTab === 'services' && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Database className="h-5 w-5 mr-2" />
                Email Services Overview
              </h2>
              <button
                onClick={() => navigate('/services')}
                className="btn-primary text-sm inline-flex items-center"
              >
                Manage Services
              </button>
            </div>

            {emailServices.length === 0 ? (
              <div className="text-center py-12">
                <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Email Services</h3>
                <p className="text-gray-500 mb-6">
                  Create email services to receive vocabulary emails from your databases
                </p>
                <button
                  onClick={() => navigate('/services')}
                  className="btn-primary inline-flex items-center"
                >
                  Create Service
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {emailServices.map((service) => (
                  <div
                    key={service.id}
                    className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-grow">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-medium text-gray-900">
                            {service.service_name}
                          </h3>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            service.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {service.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>

                        {service.description && (
                          <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                        )}

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Database:</span>
                            <p className="font-medium text-gray-900">{service.database_name || 'N/A'}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              Send Time:
                            </span>
                            <p className="font-medium text-gray-900">
                              {service.send_time} ({service.timezone})
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-500 flex items-center">
                              <Filter className="h-3 w-3 mr-1" />
                              Selection:
                            </span>
                            <p className="font-medium text-gray-900 capitalize">
                              {service.selection_method.replace('_', ' ')}
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-500">Vocabulary:</span>
                            <p className="font-medium text-gray-900">
                              {service.vocabulary_count} items, {service.frequency}
                            </p>
                          </div>
                        </div>

                        {service.selection_method === 'date_range' && (service.date_range_start || service.date_range_end) && (
                          <div className="mt-3 text-sm text-gray-600 bg-blue-50 p-2 rounded">
                            <span className="font-medium">Date Range: </span>
                            {service.date_range_start && `From ${new Date(service.date_range_start).toLocaleDateString()}`}
                            {service.date_range_start && service.date_range_end && ' '}
                            {service.date_range_end && `to ${new Date(service.date_range_end).toLocaleDateString()}`}
                          </div>
                        )}

                        {service.last_sent_at && (
                          <div className="mt-2 text-xs text-gray-500">
                            Last sent: {new Date(service.last_sent_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                <div className="pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600 mb-3">
                    <strong>Summary:</strong> You have {emailServices.length} email service{emailServices.length !== 1 ? 's' : ''} configured.
                    {emailServices.filter(s => s.is_active).length} active, {emailServices.filter(s => !s.is_active).length} inactive.
                  </p>
                  <button
                    onClick={() => navigate('/databases')}
                    className="btn-secondary inline-flex items-center"
                  >
                    <Database className="h-4 w-4 mr-2" />
                    Manage All Services
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Logging Tab */}
      {activeTab === 'logging' && (
        <div className="space-y-6">
          <LoggingStatus />
        </div>
      )}

      {/* Tokens Tab */}
      {activeTab === 'tokens' && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Manage Tokens</h2>
          <p className="text-gray-600 mb-6">
            Manage your Notion API integration tokens. Tokens are used to connect to your Notion databases.
          </p>
          <button
            onClick={() => navigate('/settings/tokens')}
            className="btn-primary inline-flex items-center"
          >
            <Key className="h-4 w-4 mr-2" />
            Go to Token Management
          </button>
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