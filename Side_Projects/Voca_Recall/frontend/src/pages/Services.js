import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Mail, 
  Plus, 
  Edit, 
  Trash2, 
  Clock, 
  Database,
  Filter,
  Calendar,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import EmailServiceModal from '../components/EmailServiceModal';

const Services = () => {
  // List of email services (read in UI; updated by fetch and saves)
  const [services, setServices] = useState([]);
  // Map of databases by id (read in UI; updated by fetch)
  const [databases, setDatabases] = useState({});
  // Page loading indicator (read in UI; updated after initial fetch)
  const [loading, setLoading] = useState(true);
  // Controls EmailServiceModal visibility (read by modal; updated on open/close)
  const [showModal, setShowModal] = useState(false);
  // Service currently being edited; null when creating (read by modal; updated on edit/open/close)
  const [editingService, setEditingService] = useState(null);
  // Selected DB context for add/edit (read by modal; updated on open/close)
  const [selectedDatabase, setSelectedDatabase] = useState(null);
  // Router navigation helper
  const navigate = useNavigate();

  useEffect(() => {
    fetchServices();
    fetchDatabases();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await axios.get('/api/email-services');
      setServices(response.data.services || []); // update `services`
    } catch (error) {
      console.error('Failed to fetch services:', error);
      toast.error('Failed to load email services');
    } finally {
      setLoading(false); // update `loading`
    }
  };

  const fetchDatabases = async () => {
    try {
      const response = await axios.get('/api/databases');
      const dbMap = {};
      response.data.databases.forEach(db => {
        dbMap[db.id] = db;
      });
      setDatabases(dbMap); // update `databases`
    } catch (error) {
      console.error('Failed to fetch databases:', error);
    }
  };

  const handleAddService = () => {
    if (Object.keys(databases).length === 0) {
      toast.error('Please add a database first');
      navigate('/databases');
      return;
    }
    
    // Use the first database as default
    const firstDb = Object.values(databases)[0];
    setSelectedDatabase(firstDb); // update `selectedDatabase`
    setEditingService(null); // reset `editingService` for create flow
    setShowModal(true); // open modal
  };

  const handleEditService = (service) => {
    const db = databases[service.database_id];
    if (!db) {
      toast.error('Database not found');
      return;
    }
    setSelectedDatabase(db); // update `selectedDatabase`
    setEditingService(service); // set `editingService` for edit flow
    setShowModal(true); // open modal
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Are you sure you want to delete this email service?')) {
      return;
    }

    try {
      await axios.delete(`/api/email-services/${serviceId}`);
      toast.success('Email service deleted successfully');
      fetchServices();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to delete email service';
      toast.error(message);
    }
  };

  const handleServiceSave = () => {
    fetchServices(); // refresh `services`
    setShowModal(false); // close modal
  };

  const getSelectionMethodBadge = (method) => {
    const badges = {
      random: { color: 'bg-blue-100 text-blue-800', icon: Filter },
      latest: { color: 'bg-green-100 text-green-800', icon: Clock },
      date_range: { color: 'bg-purple-100 text-purple-800', icon: Calendar }
    };
    const badge = badges[method] || badges.random;
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {method.replace('_', ' ')}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Email Services</h1>
            <p className="mt-2 text-gray-600">
              Manage your email services and vocabulary delivery schedules.
            </p>
          </div>
          <button
            onClick={handleAddService}
            className="btn-primary inline-flex items-center cursor-pointer relative z-10"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Service
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Mail className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Total Services</p>
              <p className="text-2xl font-semibold text-gray-900">{services.length}</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Active</p>
              <p className="text-2xl font-semibold text-gray-900">
                {services.filter(s => s.is_active).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-gray-100 rounded-lg">
              <XCircle className="h-6 w-6 text-gray-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Inactive</p>
              <p className="text-2xl font-semibold text-gray-900">
                {services.filter(s => !s.is_active).length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">Databases</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Object.keys(databases).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Services List */}
      {services.length === 0 ? (
        <div className="card text-center py-12">
          <Mail className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Email Services</h3>
          <p className="text-gray-500 mb-6">
            Create your first email service to start receiving vocabulary emails
          </p>
          <button
            onClick={handleAddService}
            className="btn-primary inline-flex items-center cursor-pointer"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create First Service
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {services.map((service) => {
            const db = databases[service.database_id];
            return (
              <div key={service.id} className="card relative">
                <div className="flex items-start justify-between">
                  <div className="flex-grow">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {service.service_name}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        service.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {service.is_active ? (
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
                      {getSelectionMethodBadge(service.selection_method)}
                    </div>

                    {service.description && (
                      <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                    )}

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="flex items-center text-gray-500 mb-1">
                          <Database className="h-3 w-3 mr-1" />
                          Database
                        </div>
                        <p className="font-medium text-gray-900">
                          {db ? db.database_name : 'Unknown'}
                        </p>
                      </div>

                      <div>
                        <div className="flex items-center text-gray-500 mb-1">
                          <Clock className="h-3 w-3 mr-1" />
                          Schedule
                        </div>
                        <p className="font-medium text-gray-900">
                          {service.send_time} ({service.timezone})
                        </p>
                        <p className="text-xs text-gray-500">{service.frequency}</p>
                      </div>

                      <div>
                        <div className="flex items-center text-gray-500 mb-1">
                          <Filter className="h-3 w-3 mr-1" />
                          Vocabulary
                        </div>
                        <p className="font-medium text-gray-900">
                          {service.vocabulary_count} items
                        </p>
                      </div>

                      <div>
                        <div className="text-gray-500 mb-1">Last Sent</div>
                        <p className="font-medium text-gray-900">
                          {service.last_sent_at 
                            ? new Date(service.last_sent_at).toLocaleDateString()
                            : 'Never'}
                        </p>
                      </div>
                    </div>

                    {service.selection_method === 'date_range' && (service.date_range_start || service.date_range_end) && (
                      <div className="mt-3 text-sm bg-purple-50 p-3 rounded-lg">
                        <div className="flex items-center text-purple-700">
                          <Calendar className="h-4 w-4 mr-2" />
                          <span className="font-medium">Date Range: </span>
                          <span className="ml-2">
                            {service.date_range_start && new Date(service.date_range_start).toLocaleDateString()}
                            {service.date_range_start && service.date_range_end && ' - '}
                            {service.date_range_end && new Date(service.date_range_end).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2 ml-4 relative z-10 flex-shrink-0">
                    <button
                      onClick={() => handleEditService(service)}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors cursor-pointer"
                      title="Edit service"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteService(service.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors cursor-pointer"
                      title="Delete service"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Email Service Modal */}
      <EmailServiceModal
        isOpen={showModal} // read `showModal`
        onClose={() => {
          setShowModal(false); // update `showModal`
          setSelectedDatabase(null); // reset `selectedDatabase`
          setEditingService(null); // reset `editingService`
        }}
        database={selectedDatabase} // read `selectedDatabase`
        service={editingService} // read `editingService`
        onSave={handleServiceSave} // updates `services`, closes modal
      />
    </div>
  );
};

export default Services;
