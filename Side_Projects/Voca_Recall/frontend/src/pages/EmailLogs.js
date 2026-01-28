import React, { useState, useEffect } from 'react';
import apiService from '../utils/apiService';

const EmailLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState('all'); // 'all', 'sent', 'failed'

  useEffect(() => {
    fetchLogs();
  }, [currentPage]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/email/logs?page=${currentPage}&per_page=10`);
      setLogs(response.data.logs);
      setTotalPages(response.data.pages);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch email logs');
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    return log.status === filter;
  });

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const baseClasses = "px-3 py-1 rounded-full text-xs font-semibold";
    if (status === 'sent') {
      return (
        <span className={`${baseClasses} bg-green-100 text-green-800`}>
          ✓ Sent
        </span>
      );
    } else if (status === 'failed') {
      return (
        <span className={`${baseClasses} bg-red-100 text-red-800`}>
          ✗ Failed
        </span>
      );
    }
    return (
      <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
        {status}
      </span>
    );
  };

  if (loading && logs.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
          <h1 className="text-2xl font-bold text-white flex items-center">
            📧 Email Delivery Logs
          </h1>
          <p className="text-indigo-100 mt-1">Track all scheduled vocabulary email deliveries</p>
        </div>

        {/* Filter Tabs */}
        <div className="border-b border-gray-200 bg-gray-50 px-6 py-3">
          <div className="flex space-x-4">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              All ({logs.length})
            </button>
            <button
              onClick={() => setFilter('sent')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'sent'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Sent ({logs.filter(l => l.status === 'sent').length})
            </button>
            <button
              onClick={() => setFilter('failed')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === 'failed'
                  ? 'bg-red-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Failed ({logs.filter(l => l.status === 'failed').length})
            </button>
            <button
              onClick={fetchLogs}
              className="ml-auto px-4 py-2 bg-white text-gray-700 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors flex items-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-6 mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Email Logs Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sent At
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vocabulary Count
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Error
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                    No email logs found
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{log.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {formatDate(log.sent_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(log.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {log.vocabulary_items ? log.vocabulary_items.length : 0} items
                    </td>
                    <td className="px-6 py-4 text-sm text-red-600">
                      {log.error_message || '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  currentPage === 1
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  currentPage === totalPages
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Statistics Footer */}
        <div className="bg-indigo-50 px-6 py-4 border-t border-indigo-100">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-indigo-600">{logs.length}</div>
              <div className="text-xs text-gray-600 uppercase">Total Logs</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {logs.filter(l => l.status === 'sent').length}
              </div>
              <div className="text-xs text-gray-600 uppercase">Successful</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {logs.filter(l => l.status === 'failed').length}
              </div>
              <div className="text-xs text-gray-600 uppercase">Failed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg px-6 py-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 Email Monitoring Tips</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Logs are stored in UTC timezone</li>
          <li>Failed emails include error messages for troubleshooting</li>
          <li>Each log entry shows the vocabulary items that were sent</li>
          <li>Refresh regularly to see the latest email deliveries</li>
        </ul>
      </div>
    </div>
  );
};

export default EmailLogs;
