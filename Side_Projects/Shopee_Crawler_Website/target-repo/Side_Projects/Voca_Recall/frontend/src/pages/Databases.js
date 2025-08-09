import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Database, 
  Plus, 
  Trash2, 
  Edit, 
  ExternalLink, 
  TestTube,
  CheckCircle,
  XCircle
} from 'lucide-react';

const Databases = () => {
  const [databases, setDatabases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);
  const [editingDatabase, setEditingDatabase] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm();

  useEffect(() => {
    fetchDatabases();
  }, []);

  const fetchDatabases = async () => {
    try {
      const response = await axios.get('/api/databases');
      setDatabases(response.data.databases);
    } catch (error) {
      console.error('Failed to fetch databases:', error);
      toast.error('Failed to load databases');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      // Build payload expected by backend
      const payload = {
        notion_api_key: data.notion_api_key,
        database_url: data.database_url,
      };

      if (editingDatabase) {
        await axios.put(`/api/databases/${editingDatabase.id}`, payload);
        toast.success('Database updated successfully!');
        setEditingDatabase(null);
      } else {
        await axios.post('/api/databases', payload);
        toast.success('Database added successfully!');
      }
      fetchDatabases();
      reset();
      setShowAddForm(false);
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to save database';
      toast.error(message);
    }
  };

  const handleDelete = async (databaseId) => {
    if (!window.confirm('Are you sure you want to delete this database?')) {
      return;
    }

    try {
      await axios.delete(`/api/databases/${databaseId}`);
      toast.success('Database deleted successfully!');
      fetchDatabases();
    } catch (error) {
      toast.error('Failed to delete database');
    }
  };

  const handleTestConnection = async (databaseId) => {
    setTestingConnection(databaseId);
    try {
      const apiKey = prompt('Please enter your Notion API key:');
      if (!apiKey) return;

      const response = await axios.post(`/api/databases/${databaseId}/test`, {
        notion_api_key: apiKey,
      });

      toast.success('Connection successful!');
      console.log('Test results:', response.data);
    } catch (error) {
      const message = error.response?.data?.error || 'Connection test failed';
      toast.error(message);
    } finally {
      setTestingConnection(null);
    }
  };

  const handleEdit = (database) => {
    setEditingDatabase(database);
    setValue('database_url', database.database_url);
  setValue('notion_api_key', '');
    setShowAddForm(true);
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setEditingDatabase(null);
    reset();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notion Databases</h1>
          <p className="mt-2 text-gray-600">
            Manage your connected Notion databases for vocabulary learning.
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary inline-flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Database
        </button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editingDatabase ? 'Edit Database' : 'Add New Database'}
          </h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Integration Token */}
            <div>
              <label htmlFor="notion_api_key" className="form-label">
                Integration Token
              </label>
              <input
                id="notion_api_key"
                type="password"
                className={`input-field ${
                  errors.notion_api_key ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                }`}
                placeholder="secret_xxx from your Notion integration"
                {...register('notion_api_key', {
                  required: 'Integration Token is required',
                  minLength: { value: 10, message: 'Token looks too short' },
                })}
              />
              {errors.notion_api_key && (
                <p className="mt-1 text-sm text-red-600">{errors.notion_api_key.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                Create a Notion internal integration and copy its secret. We do not store your token.
              </p>
            </div>

            <div>
              <label htmlFor="database_url" className="form-label">
                Database URL or ID
              </label>
              <input
                id="database_url"
                type="text"
                className={`input-field ${
                  errors.database_url ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
                }`}
                placeholder="https://www.notion.so/... or a 32-char database ID"
                {...register('database_url', {
                  required: 'Database URL or ID is required',
                  validate: (value) => {
                    const urlRegex = /^https?:\/\/[^\s]+$/;
                    const idRegex = /^(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$/;
                    return urlRegex.test(value) || idRegex.test(value) || 'Enter a Notion URL or database ID';
                  },
                })}
              />
              {errors.database_url && (
                <p className="mt-1 text-sm text-red-600">{errors.database_url.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                Paste the Notion database page URL (the ID is embedded) or the 32-character database ID.
                Example: https://www.notion.so/workspace/<strong>xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</strong>
              </p>
            </div>

            <div className="flex space-x-4">
              <button type="submit" className="btn-primary">
                {editingDatabase ? 'Update Database' : 'Add Database'}
              </button>
              <button type="button" onClick={handleCancel} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Databases List */}
      <div className="space-y-4">
        {databases.length === 0 ? (
          <div className="card text-center py-12">
            <Database className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No databases connected</h3>
            <p className="text-gray-600 mb-6">
              Connect your first Notion database to start receiving vocabulary emails.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary inline-flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Database
            </button>
          </div>
        ) : (
          databases.map((database) => (
            <div key={database.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Database className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {database.database_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Added on {new Date(database.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    database.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {database.is_active ? (
                      <>
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Active
                      </>
                    ) : (
                      <>
                        <XCircle className="h-3 w-3 mr-1" />
                        Inactive
                      </>
                    )}
                  </span>

                  <button
                    onClick={() => handleTestConnection(database.id)}
                    disabled={testingConnection === database.id}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors duration-200"
                    title="Test connection"
                  >
                    {testingConnection === database.id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    ) : (
                      <TestTube className="h-4 w-4" />
                    )}
                  </button>

                  <a
                    href={database.database_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors duration-200"
                    title="Open in Notion"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                  <button
                    onClick={() => handleEdit(database)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors duration-200"
                    title="Edit database"
                  >
                    <Edit className="h-4 w-4" />
                  </button>

                  <button
                    onClick={() => handleDelete(database.id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors duration-200"
                    title="Delete database"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Databases; 