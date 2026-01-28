import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Users, 
  UserPlus, 
  Search, 
  Shield, 
  ShieldAlert,
  User as UserIcon,
  Mail,
  Save,
  X,
  Eye,
  EyeOff
} from 'lucide-react';

const ManageUsers = () => {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    // Redirect if not admin
    if (!isAdmin()) {
      navigate('/dashboard');
      toast.error('Admin access required');
      return;
    }
    fetchUsers();
  }, [currentPage, searchTerm]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        per_page: 15,
        ...(searchTerm && { search: searchTerm })
      };
      
      const response = await axios.get('/api/admin/users', { params });
      setUsers(response.data.users);
      setTotalPages(response.data.pages);
      setTotalUsers(response.data.total);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await axios.put(`/api/admin/users/${userId}/role`, { role: newRole });
      toast.success('User role updated successfully');
      fetchUsers();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to update user role';
      toast.error(message);
    }
  };

  const handleToggleActive = async (userId, isActive) => {
    try {
      await axios.put(`/api/admin/users/${userId}/activate`, { is_active: !isActive });
      toast.success(`User ${!isActive ? 'activated' : 'deactivated'} successfully`);
      fetchUsers();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to update user status';
      toast.error(message);
    }
  };

  const getRoleBadge = (role) => {
    const styles = {
      admin: 'bg-red-100 text-red-800 border-red-200',
      developer: 'bg-blue-100 text-blue-800 border-blue-200',
      user: 'bg-gray-100 text-gray-800 border-gray-200'
    };

    const icons = {
      admin: <ShieldAlert className="h-3 w-3 mr-1" />,
      developer: <Shield className="h-3 w-3 mr-1" />,
      user: <UserIcon className="h-3 w-3 mr-1" />
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[role]}`}>
        {icons[role]}
        {role}
      </span>
    );
  };

  if (loading && users.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Users className="h-8 w-8 mr-3" />
          Manage Users
        </h1>
        <p className="mt-2 text-gray-600">
          Manage user roles and create new accounts. Total users: {totalUsers}
        </p>
      </div>

      {/* Search and Create */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="input-field pl-10"
              />
            </div>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center justify-center"
          >
            <UserPlus className="h-5 w-5 mr-2" />
            Create User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-700 font-medium">
                          {user.first_name[0]}{user.last_name[0]}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {user.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="user">User</option>
                      <option value="developer">Developer</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleToggleActive(user.id, user.is_active)}
                      className={`inline-flex items-center px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        user.is_active
                          ? 'bg-green-100 text-green-800 hover:bg-green-200'
                          : 'bg-red-100 text-red-800 hover:bg-red-200'
                      }`}
                    >
                      {user.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {getRoleBadge(user.role)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Page <span className="font-medium">{currentPage}</span> of{' '}
                  <span className="font-medium">{totalPages}</span>
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="btn-secondary rounded-l-md disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="btn-secondary rounded-r-md disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <CreateUserModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchUsers();
          }}
        />
      )}
    </div>
  );
};

// Create User Modal Component
const CreateUserModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'user'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await axios.post('/api/admin/users', formData);
      toast.success('User created successfully');
      onSuccess();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to create user';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 flex items-center">
            <UserPlus className="h-6 w-6 mr-2" />
            Create New User
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">First Name</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
            <div>
              <label className="form-label">Last Name</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="input-field"
            />
          </div>

          <div>
            <label className="form-label">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="input-field pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            <p className="mt-1 text-xs text-gray-500">Minimum 8 characters</p>
          </div>

          <div>
            <label className="form-label">Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="input-field"
            >
              <option value="user">User</option>
              <option value="developer">Developer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary inline-flex items-center"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Create User
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ManageUsers;
