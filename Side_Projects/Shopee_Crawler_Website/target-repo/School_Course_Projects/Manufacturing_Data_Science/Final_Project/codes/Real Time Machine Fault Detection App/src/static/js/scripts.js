document.addEventListener('DOMContentLoaded', function() {
    const alertBox = document.getElementById('alert-box');
    const recordsTableBody = document.querySelector('#records-table tbody');
    const filterCheckbox = document.getElementById('filter-anomalies');

    function fetchLatestResult() {
        fetch('/api/latest_result')
            .then(response => response.json())
            .then(data => {
                if (data.alert) {
                    alertBox.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                } else {
                    alertBox.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alertBox.innerHTML = `<div class="alert alert-danger">An error occurred while fetching the latest result.</div>`;
            });
    }

    function fetchPastRecords() {
        const filterAnomalies = filterCheckbox.checked ? 'true' : 'false';
        fetch(`/api/past_records?filter_anomalies=${filterAnomalies}`)
            .then(response => response.json())
            .then(records => {
                console.log('Fetched records:', records); // Log the records for debugging
                recordsTableBody.innerHTML = ''; // Clear existing rows
                records.forEach(record => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${record.timestamp}</td>
                        <td>${record.fault_types.join(', ')}</td>
                        <td>${record.probabilities}</td> <!-- Display max probability directly -->
                    `;
                    recordsTableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error fetching past records:', error);
            });
    }

    // Fetch the latest result every 5 seconds
    setInterval(fetchLatestResult, 5000);

    // Fetch past records every 10 seconds
    setInterval(fetchPastRecords, 5000);

    // Fetch records when filter changes
    filterCheckbox.addEventListener('change', fetchPastRecords);

    fetchPastRecords();
});

