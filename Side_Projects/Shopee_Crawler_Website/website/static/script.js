// ---- 1. 處理 Upload 點擊並自動 Submit ----
function handleFile() {
  console.log("handleFile called");
  const fileInput = document.getElementById("file-input");
  
  if (!fileInput) {
    console.error("file-input element not found");
    return;
  }
  
  // Check if at least one platform is selected
  const momoChecked = document.getElementById("momo-checkbox").checked;
  const coupangChecked = document.getElementById("coupang-checkbox").checked;
  
  if (!momoChecked && !coupangChecked) {
    alert("Please select at least one platform (Momo or Coupang) before uploading.");
    return;
  }
  
  // Save platform preferences to localStorage
  savePlatformPreferences();
  
  // Set the selected platforms in the hidden input
  const platformsInput = document.getElementById("platforms");
  const selectedPlatforms = [];
  if (momoChecked) selectedPlatforms.push("momo");
  if (coupangChecked) selectedPlatforms.push("coupang");
  platformsInput.value = selectedPlatforms.join(",");
  
  fileInput.click();

  // 使用 change event 監聽使用者選取檔案
  fileInput.addEventListener("change", () => {
    console.log("File selected:", fileInput.files.length);
    console.log("Selected platforms:", platformsInput.value);
    if (fileInput.files.length > 0) {
      const submitBtn = document.getElementById("file-submit");
      if (submitBtn) {
        submitBtn.click();
      } else {
        console.error("file-submit element not found");
      }
    }
  }, { once: true }); // 確保只執行一次
}

// ---- Platform Preference Cache Functions ----
function savePlatformPreferences() {
  const momoChecked = document.getElementById("momo-checkbox").checked;
  const coupangChecked = document.getElementById("coupang-checkbox").checked;
  
  const preferences = {
    momo: momoChecked,
    coupang: coupangChecked,
    timestamp: Date.now()
  };
  
  localStorage.setItem('platformPreferences', JSON.stringify(preferences));
  console.log("Platform preferences saved:", preferences);
  
  // Show preference saved indicator
  showPreferenceStatus();
}

function showPreferenceStatus() {
  const statusElement = document.getElementById('preference-status');
  if (statusElement) {
    statusElement.classList.add('show');
    setTimeout(() => {
      statusElement.classList.remove('show');
    }, 2000);
  }
}

function loadPlatformPreferences() {
  try {
    const stored = localStorage.getItem('platformPreferences');
    if (stored) {
      const preferences = JSON.parse(stored);
      
      // Check if preferences are not too old (optional: 30 days)
      const thirtyDaysInMs = 30 * 24 * 60 * 60 * 1000;
      if (Date.now() - preferences.timestamp < thirtyDaysInMs) {
        
        // Apply saved preferences
        const momoCheckbox = document.getElementById("momo-checkbox");
        const coupangCheckbox = document.getElementById("coupang-checkbox");
        
        if (momoCheckbox && coupangCheckbox) {
          momoCheckbox.checked = preferences.momo;
          coupangCheckbox.checked = preferences.coupang;
          
          // Ensure at least one platform is selected
          if (!preferences.momo && !preferences.coupang) {
            // If no platforms were saved as selected, default to coupang
            coupangCheckbox.checked = true;
          }
          
          // Add visual feedback
          const labels = document.querySelectorAll('.checkbox-label');
          labels.forEach(label => label.classList.add('preference-loaded'));
          setTimeout(() => {
            labels.forEach(label => label.classList.remove('preference-loaded'));
          }, 500);
          
          console.log("Platform preferences loaded:", preferences);
          return true;
        }
      } else {
        // Remove old preferences
        localStorage.removeItem('platformPreferences');
        console.log("Old platform preferences removed");
      }
    }
  } catch (error) {
    console.error("Error loading platform preferences:", error);
    localStorage.removeItem('platformPreferences');
  }
  return false;
}

function clearPlatformPreferences() {
  localStorage.removeItem('platformPreferences');
  console.log("Platform preferences cleared");
}

// Add event listeners for platform checkboxes to save preferences when changed
function initializePlatformPreferences() {
  const momoCheckbox = document.getElementById("momo-checkbox");
  const coupangCheckbox = document.getElementById("coupang-checkbox");
  
  if (momoCheckbox && coupangCheckbox) {
    // Load saved preferences first
    const preferencesLoaded = loadPlatformPreferences();
    
    // If no preferences were loaded, set default to coupang
    if (!preferencesLoaded) {
      coupangCheckbox.checked = true;
      momoCheckbox.checked = false;
    }
    
    // Add change event listeners to save preferences when user changes selection
    momoCheckbox.addEventListener('change', savePlatformPreferences);
    coupangCheckbox.addEventListener('change', savePlatformPreferences);
    
    console.log("Platform preference system initialized");
  }
}

// ---- 2. 處理 Stop 按鈕點擊事件 ----
function handleStop() {
  console.log("handleStop called");
  const stopButton = document.getElementById("stop-btn");
  if (stopButton) {
    stopButton.addEventListener("click", () => {
      // 這裡可以添加停止爬蟲的邏輯
      alert("停止爬蟲功能尚未實作！");
    });
  } else {
    console.warn("stop-btn element not found");
  }
}

// ---- 3. 初始化 DataTables 表格排序與搜尋 ----
function initializeDataTables() {
  console.log("Attempting to initialize DataTables");
  
  // Check if jQuery is available
  if (typeof $ === 'undefined' || typeof jQuery === 'undefined') {
    console.error("jQuery is not available, cannot initialize DataTables");
    return;
  }
  
  // Check if table exists
  if ($('#sortableTable').length === 0) {
    console.error("sortableTable element not found");
    return;
  }

  try {
    $('#sortableTable').DataTable({
      order: [],
      columnDefs: [
        { orderable: false, targets: [5, 6] }
      ],
      language: {
        search: "搜尋：",
        lengthMenu: "每頁顯示 _MENU_ 筆",
        info: "顯示第 _START_ 至 _END_ 筆，共 _TOTAL_ 筆",
        paginate: {
          first: "第一頁",
          last: "最後一頁",
          next: "下一頁",
          previous: "上一頁"
        },
        zeroRecords: "查無資料",
      }
    });
    console.log("DataTables initialized successfully");
  } catch (error) {
    console.error("Error initializing DataTables:", error);
  }
}

// Wait for jQuery to be available, then initialize
function waitForJQuery() {
  if (typeof $ !== 'undefined' && typeof jQuery !== 'undefined') {
    $(document).ready(function () {
      console.log("jQuery ready, initializing DataTables");
      initializeDataTables();
    });
  } else {
    console.log("Waiting for jQuery to load...");
    setTimeout(waitForJQuery, 100);
  }
}

// Start waiting for jQuery
waitForJQuery();

// ---- 6. Initialize when DOM is loaded ----
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM Content Loaded");
  handleStop(); // Initialize stop button if it exists
  initializeDeleteButtons(); // Initialize delete buttons
  initializePlatformPreferences(); // Initialize platform preference cache system
});

// ---- 4. 處理刪除按鈕功能 ----
function deleteFile(filename, stamp, buttonElement) {
  // Confirm deletion
  if (!confirm(`確定要刪除檔案 "${filename}" 嗎？此操作無法復原。`)) {
    return;
  }

  // Disable button and show loading state
  const originalText = buttonElement.innerHTML;
  buttonElement.innerHTML = "刪除中...";
  buttonElement.disabled = true;

  // Make AJAX request to delete the file
  fetch(`/delete/${stamp}/${filename}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      // Remove the row from the table
      const row = buttonElement.closest('tr');
      if (row) {
        // If using DataTables, remove the row properly
        if ($.fn.DataTable.isDataTable('#sortableTable')) {
          $('#sortableTable').DataTable().row(row).remove().draw();
        } else {
          // Fallback: remove row directly
          row.remove();
        }
      }
      
      // Show success message
      alert('檔案已成功刪除！');
    } else {
      // Show error message
      alert(`刪除失敗: ${data.message}`);
      // Restore button
      buttonElement.innerHTML = originalText;
      buttonElement.disabled = false;
    }
  })
  .catch(error => {
    console.error('Error deleting file:', error);
    alert('刪除時發生錯誤，請稍後再試。');
    // Restore button
    buttonElement.innerHTML = originalText;
    buttonElement.disabled = false;
  });
}

// ---- 5. 初始化刪除按鈕事件監聽器 ----
function initializeDeleteButtons() {
  document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
      const filename = this.getAttribute('data-filename');
      const stamp = this.getAttribute('data-stamp');
      deleteFile(filename, stamp, this);
    });
  });
}

// ...existing code...
