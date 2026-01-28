import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Key, 
  Plus, 
  Trash2, 
  Edit2, 
  Save, 
  X, 
  Eye, 
  EyeOff,
  Database,
  Calendar,
  AlertCircle
} from 'lucide-react';

const ManageTokens = () => {
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingToken, setEditingToken] = useState(null);
  const [newToken, setNewToken] = useState({ token: '', token_name: '' });
  const [showTokenValue, setShowTokenValue] = useState({});

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/tokens');
      setTokens(response.data.tokens);
    } catch (error) {
      console.error('Failed to fetch tokens:', error);
      toast.error('Failed to load tokens');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToken = async (e) => {
    e.preventDefault();
    
    if (!newToken.token.trim()) {
      toast.error('Token is required');
      return;
    }

    try {
      await axios.post('/api/tokens', {
        token: newToken.token.trim(),
        token_name: newToken.token_name.trim()
      });
      
      toast.success('Token added successfully');
      setShowAddModal(false);
      setNewToken({ token: '', token_name: '' });
      fetchTokens();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to add token';
      toast.error(message);
    }
  };

  const handleUpdateToken = async (e) => {
    e.preventDefault();
    
    if (!editingToken) return;

    try {
      await axios.put(`/api/tokens/${editingToken.id}`, {
        token_name: editingToken.token_name
      });
      
      toast.success('Token updated successfully');
      setShowEditModal(false);
      setEditingToken(null);
      fetchTokens();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to update token';
      toast.error(message);
    }
  };

  const handleDeleteToken = async (tokenId, tokenName) => {
    const confirmMessage = tokenName 
      ? `Are you sure you want to delete the token "${tokenName}"?`
      : 'Are you sure you want to delete this token?';
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      await axios.delete(`/api/tokens/${tokenId}`);
      toast.success('Token deleted successfully');
      fetchTokens();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to delete token';
      
      // If error includes databases list, show them
      if (error.response?.data?.databases) {
        const databases = error.response.data.databases.join(', ');
        toast.error(`Cannot delete: Token is used by databases: ${databases}`);
      } else {
        toast.error(message);
      }
    }
  };

  const toggleTokenVisibility = (tokenId) => {
    setShowTokenValue(prev => ({
      ...prev,
      [tokenId]: !prev[tokenId]
    }));
  };

  const maskToken = (token) => {
    if (!token) return '';
    const visibleChars = 8;
    if (token.length <= visibleChars) return token;
    return token.substring(0, visibleChars) + '•'.repeat(Math.min(token.length - visibleChars, 40));
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Manage Tokens</h1>
          <p className="mt-2 text-gray-600">
            Manage your Notion API integration tokens. Tokens are used to connect to your Notion databases.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary inline-flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Token
        </button>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">How to get your Notion API token:</p>
            <ol className="list-decimal list-inside space-y-1 ml-2">
              <li>Go to <a href="https://www.notion.so/my-integrations" target="_blank" rel="noopener noreferrer" className="underline font-medium">notion.so/my-integrations</a></li>
              <li>Click "New integration" or select an existing one</li>
              <li>Copy the "Internal Integration Token"</li>
              <li>Share your database with the integration</li>
            </ol>
          </div>
        </div>
      </div>

      {/* Tokens List */}
      {tokens.length === 0 ? (
        <div className="card text-center py-12">
          <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No tokens yet</h3>
          <p className="text-gray-600 mb-6">
            Add your first Notion API token to get started
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary inline-flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Your First Token
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {tokens.map((token) => (
            <div key={token.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-3">
                    <Key className="h-5 w-5 text-primary-600 flex-shrink-0" />
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {token.token_name || 'Unnamed Token'}
                    </h3>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      token.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {token.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Database className="h-4 w-4" />
                      <span>
                        {token.database_count === 0 && 'No databases using this token'}
                        {token.database_count === 1 && '1 database using this token'}
                        {token.database_count > 1 && `${token.database_count} databases using this token`}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>Added {new Date(token.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => {
                      setEditingToken({
                        id: token.id,
                        token_name: token.token_name || '',
                        database_count: token.database_count
                      });
                      setShowEditModal(true);
                    }}
                    className="p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Edit token name"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteToken(token.id, token.token_name)}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Delete token"
                    disabled={token.database_count > 0}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Token Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Add New Token</h2>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setNewToken({ token: '', token_name: '' });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleAddToken}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="token_name" className="form-label">
                    Token Name (Optional)
                  </label>
                  <input
                    id="token_name"
                    type="text"
                    className="input-field"
                    placeholder="e.g., My Notion Integration"
                    value={newToken.token_name}
                    onChange={(e) => setNewToken({ ...newToken, token_name: e.target.value })}
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Give this token a memorable name
                  </p>
                </div>
                
                <div>
                  <label htmlFor="token" className="form-label">
                    Notion API Token <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="token"
                    className="input-field font-mono text-sm"
                    placeholder="secret_..."
                    rows="3"
                    value={newToken.token}
                    onChange={(e) => setNewToken({ ...newToken, token: e.target.value })}
                    required
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Paste your Notion integration token here
                  </p>
                </div>
              </div>
              
              <div className="mt-6 flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setNewToken({ token: '', token_name: '' });
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary flex-1">
                  Add Token
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Token Modal */}
      {showEditModal && editingToken && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Edit Token Name</h2>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingToken(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleUpdateToken}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="edit_token_name" className="form-label">
                    Token Name
                  </label>
                  <input
                    id="edit_token_name"
                    type="text"
                    className="input-field"
                    placeholder="e.g., My Notion Integration"
                    value={editingToken.token_name}
                    onChange={(e) => setEditingToken({ ...editingToken, token_name: e.target.value })}
                  />
                </div>
              </div>
              
              <div className="mt-6 flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingToken(null);
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary flex-1">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageTokens;
