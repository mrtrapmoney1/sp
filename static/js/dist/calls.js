"use strict";
/**
 * Calls Management TypeScript Module
 * Handles fetching, displaying, and managing service calls
 */
// =============================================================================
// State Management
// =============================================================================
const state = {
    allCalls: [],
    filteredCalls: [],
    selectedCallIndices: new Set(),
    currentStatusFilter: '',
};
// =============================================================================
// Date Range Management
// =============================================================================
function setDateRange(days) {
    var _a;
    const today = new Date();
    const fromDate = new Date(today);
    if (days > 0) {
        fromDate.setDate(today.getDate() - days);
    }
    const fromInput = document.getElementById('from-date');
    const toInput = document.getElementById('to-date');
    if (fromInput)
        fromInput.value = window.ServiceDispatch.DateUtils.toISODate(fromDate);
    if (toInput)
        toInput.value = window.ServiceDispatch.DateUtils.toISODate(today);
    // Update button active states
    document.querySelectorAll('.btn-group .btn').forEach((btn, index) => {
        btn.classList.remove('active');
    });
    const quickButtons = [0, 2, 7, 14, 30];
    const buttonIndex = quickButtons.indexOf(days);
    if (buttonIndex >= 0) {
        (_a = document.querySelectorAll('.btn-group .btn')[buttonIndex]) === null || _a === void 0 ? void 0 : _a.classList.add('active');
    }
}
// =============================================================================
// Fetch Calls from API
// =============================================================================
async function fetchCalls() {
    const fromDateInput = document.getElementById('from-date');
    const toDateInput = document.getElementById('to-date');
    const statusFilterInput = document.getElementById('status-filter');
    const fromDate = fromDateInput === null || fromDateInput === void 0 ? void 0 : fromDateInput.value;
    const toDate = toDateInput === null || toDateInput === void 0 ? void 0 : toDateInput.value;
    const statusFilter = statusFilterInput === null || statusFilterInput === void 0 ? void 0 : statusFilterInput.value;
    if (!fromDate || !toDate) {
        window.ServiceDispatch.ToastManager.error('Please select a date range');
        return;
    }
    window.ServiceDispatch.LoadingManager.show();
    window.ServiceDispatch.ToastManager.info('Fetching calls from ServicePower...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/calls', {
            from_date: fromDate,
            to_date: toDate,
            status: statusFilter || undefined,
        });
        window.ServiceDispatch.LoadingManager.hide();
        if (response.success) {
            state.allCalls = response.calls || [];
            state.filteredCalls = [...state.allCalls];
            renderCallsTable(state.filteredCalls);
            updateStats(state.allCalls);
            updateChartsDisplay();
            window.ServiceDispatch.ToastManager.success(`Loaded ${state.allCalls.length} calls`);
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Failed to fetch calls');
        }
    }
    catch (error) {
        window.ServiceDispatch.LoadingManager.hide();
        console.error('Fetch error:', error);
        window.ServiceDispatch.ToastManager.error('Error fetching calls: ' + error.message);
    }
}
function refreshCalls() {
    fetchCalls();
}
// =============================================================================
// Phone Number Cleaning
// =============================================================================
function cleanPhoneNumber(phone) {
    if (!phone || phone === '0')
        return '';
    // Remove all non-digit characters
    let digits = phone.replace(/\D/g, '');
    // Remove excessive trailing zeros (keep only valid 10-digit US numbers)
    // Example: 402499465500000 -> 4024994655
    if (digits.length > 10) {
        // Check if extra digits are all zeros
        const extraDigits = digits.slice(10);
        if (/^0+$/.test(extraDigits)) {
            digits = digits.slice(0, 10);
        }
    }
    // Format as (XXX) XXX-XXXX if 10 digits
    if (digits.length === 10) {
        return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }
    // Format as XXX-XXXX if 7 digits
    if (digits.length === 7) {
        return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    }
    return digits || phone;
}
// =============================================================================
// SMS Functionality
// =============================================================================
function sendSMS(phone) {
    const cleanPhone = cleanPhoneNumber(phone).replace(/\D/g, '');
    if (!cleanPhone || cleanPhone.length < 10) {
        window.ServiceDispatch.ToastManager.error('Invalid phone number');
        return;
    }
    // Metro TV pre-filled SMS template (ticket 70590)
    const message = `This is Metro TV and Appliance. To schedule your service, we need 4 items to start your ticket. 70590

Please reply to this text with:

1. PHOTO of the Model/Serial Tag (Must be a clear picture directly on the appliance, not from paperwork)

2. PHOTO of the Problem (If the problem isn't visible, please send a photo of the appliance's location/environment)

3. Problem Description (Please be as descriptive as possible)

4. Your Address (Full street address and zip code)

IMPORTANT: Your Appointment
Your warranty company provides an initial request date, but this is NOT a confirmed appointment.

Your warranty company requires that your ticket first go through our tech review. We use this review to pre-order parts through your warranty company. This process is required by them to reduce turnaround times for claims and attempt a one-visit repair.

We will contact you directly to schedule your CONFIRMED appointment date.`;
    // Encode message for URL
    const encodedMessage = encodeURIComponent(message);
    // Google Voice URL format with +1 country code
    const googleVoiceUrl = `https://voice.google.com/u/0/messages?itemId=t.%2B1${cleanPhone}`;
    // Open in new tab
    window.open(googleVoiceUrl, '_blank');
    window.ServiceDispatch.ToastManager.success('Opening Google Voice with SMS template');
}
// =============================================================================
// Client-Side Filtering
// =============================================================================
function filterByStatus(status) {
    state.currentStatusFilter = status;
    if (!status || status === '' || status === 'all') {
        // Show all calls
        state.filteredCalls = [...state.allCalls];
    }
    else {
        // Filter by status (case-insensitive)
        state.filteredCalls = state.allCalls.filter(call => {
            const callStatus = (call.CallStatus || call.call_status || '').toUpperCase();
            const filterStatus = status.toUpperCase();
            // Match based on status keywords
            if (filterStatus.includes('COMPLET'))
                return callStatus.includes('COMPLET');
            if (filterStatus.includes('ACCEPT'))
                return callStatus.includes('ACCEPT');
            if (filterStatus.includes('CANCEL') || filterStatus.includes('REJECT')) {
                return callStatus.includes('CANCEL') || callStatus.includes('REJECT');
            }
            if (filterStatus.includes('PEND') || filterStatus.includes('NEW')) {
                return callStatus.includes('NEW') || callStatus.includes('PEND');
            }
            if (filterStatus === 'PARTS') {
                const problem = (call.ProbelmDesc || call.problem_desc || '').toLowerCase();
                return problem.includes('part');
            }
            return callStatus.includes(filterStatus);
        });
    }
    // Clear selections when filtering
    state.selectedCallIndices.clear();
    // Re-render table and update UI
    renderCallsTable(state.filteredCalls);
    updateBulkActionsBar();
    updateFilterTags();
    window.ServiceDispatch.ToastManager.info(`Showing ${state.filteredCalls.length} of ${state.allCalls.length} calls`);
}
function updateFilterTags() {
    // Update any filter tag displays if they exist
    const filterTagsContainer = document.getElementById('filter-tags');
    if (filterTagsContainer && state.currentStatusFilter) {
        filterTagsContainer.innerHTML = `
            <span class="badge bg-primary me-2">
                Filter: ${state.currentStatusFilter}
                <button class="btn-close btn-close-white ms-2" onclick="clearFilter()" style="font-size: 0.7rem;"></button>
            </span>
        `;
    }
    else if (filterTagsContainer) {
        filterTagsContainer.innerHTML = '';
    }
}
function clearFilter() {
    state.currentStatusFilter = '';
    state.filteredCalls = [...state.allCalls];
    renderCallsTable(state.filteredCalls);
    updateFilterTags();
}
// =============================================================================
// Render Calls Table
// =============================================================================
function renderCallsTable(calls) {
    const tbody = document.getElementById('calls-tbody');
    const callsCount = document.getElementById('calls-count');
    const tableInfo = document.getElementById('table-info');
    const lastUpdated = document.getElementById('last-updated');
    if (!tbody)
        return;
    if (!calls || calls.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-5">
                    <i class="bi bi-inbox text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-2">No calls found matching your filters.</p>
                </td>
            </tr>
        `;
        if (callsCount)
            callsCount.textContent = '0 calls';
        if (tableInfo)
            tableInfo.textContent = 'Showing 0 of 0 calls';
        return;
    }
    let html = '';
    calls.forEach((call, index) => {
        const callNumber = call.CallNumber || call.call_number || '';
        const lastName = call.ConsumerInfo_ConsumerLastName || call.lastname || '';
        const firstName = call.ConsumerInfo_ConsumerFirstName || call.firstname || '';
        const phone = call.ConsumerInfo_Phone1 || call.phone || '';
        const brand = call.ProductInfo_SPBrandDesc || call.brand || '';
        const product = call.ProductInfo_SPProductDesc || call.product || '';
        const model = call.ProductInfo_MobelNo || call.ProductInfo_ModelNo || call.model || '';
        const status = call.CallStatus || call.call_status || 'NEW';
        const warranty = call.WarrantyType || call.warranty_type || '';
        const scheduleDate = call.ScheduleDate || call.schedule_date || '';
        const problemDesc = call.ProbelmDesc || call.problem_desc || '';
        const statusBadge = getStatusBadge(status);
        const isSelected = state.selectedCallIndices.has(index);
        html += `
            <tr class="${isSelected ? 'table-active' : ''}">
                <td>
                    <input class="form-check-input" type="checkbox"
                           ${isSelected ? 'checked' : ''}
                           onchange="toggleCallSelection(${index})"
                           onclick="event.stopPropagation()">
                </td>
                <td>
                    <a href="#" class="text-decoration-none fw-bold" onclick="showCallDetail(${index}); return false;">
                        ${callNumber}
                    </a>
                </td>
                <td>
                    <strong>${lastName}</strong>${firstName ? ', ' + firstName : ''}
                </td>
                <td>${cleanPhoneNumber(phone)}</td>
                <td>
                    <strong>${brand}</strong><br>
                    <small class="text-muted">${product}</small>
                    ${model ? '<br><small class="text-muted">Model: ' + model + '</small>' : ''}
                </td>
                <td>
                    <small>${window.ServiceDispatch.StringUtils.truncate(problemDesc, 50)}</small>
                </td>
                <td>${statusBadge}</td>
                <td>
                    ${warranty ? `<span class="badge bg-secondary">${warranty}</span>` : '-'}
                </td>
                <td>
                    <small>${window.formatDate ? window.formatDate(scheduleDate) : scheduleDate}</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="showCallDetail(${index})">
                        <i class="bi bi-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
    // Update counters
    if (callsCount)
        callsCount.textContent = `${calls.length} calls`;
    if (tableInfo)
        tableInfo.textContent = `Showing ${calls.length} of ${state.allCalls.length} calls`;
    if (lastUpdated)
        lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}
// =============================================================================
// Status Badge Helper
// =============================================================================
function getStatusBadge(status) {
    const statusUpper = (status || '').toUpperCase();
    let badgeClass = 'bg-secondary';
    if (statusUpper.includes('COMPLET'))
        badgeClass = 'bg-success';
    else if (statusUpper.includes('ACCEPT'))
        badgeClass = 'bg-info';
    else if (statusUpper.includes('CANCEL') || statusUpper.includes('REJECT'))
        badgeClass = 'bg-danger';
    else if (statusUpper.includes('SCHEDUL'))
        badgeClass = 'bg-primary';
    else if (statusUpper.includes('NEW') || statusUpper.includes('PEND'))
        badgeClass = 'bg-warning';
    return `<span class="badge ${badgeClass}">${status}</span>`;
}
// =============================================================================
// Helper Functions
// =============================================================================
// Note: escapeHtml, formatDate, and formatPhone are defined in main.ts
// We access them via window object when needed
// For phone formatting in this module, we use cleanPhoneNumber directly
// =============================================================================
// Update Statistics
// =============================================================================
function updateStats(calls) {
    const stats = {
        total: calls.length,
        pending: 0,
        completed: 0,
        accepted: 0,
        cancelled: 0,
        parts: 0,
    };
    calls.forEach(call => {
        const status = (call.CallStatus || call.call_status || '').toUpperCase();
        if (status.includes('COMPLET'))
            stats.completed++;
        else if (status.includes('ACCEPT'))
            stats.accepted++;
        else if (status.includes('CANCEL') || status.includes('REJECT'))
            stats.cancelled++;
        else if (status.includes('NEW') || status.includes('PEND'))
            stats.pending++;
        const problem = (call.ProbelmDesc || call.problem_desc || '').toLowerCase();
        if (problem.includes('part'))
            stats.parts++;
    });
    document.getElementById('stat-total').textContent = stats.total.toString();
    document.getElementById('stat-pending').textContent = stats.pending.toString();
    document.getElementById('stat-completed').textContent = stats.completed.toString();
    document.getElementById('stat-accepted').textContent = stats.accepted.toString();
    document.getElementById('stat-cancelled').textContent = stats.cancelled.toString();
    document.getElementById('stat-parts').textContent = stats.parts.toString();
}
// =============================================================================
// Selection Management
// =============================================================================
function toggleCallSelection(index) {
    if (state.selectedCallIndices.has(index)) {
        state.selectedCallIndices.delete(index);
    }
    else {
        state.selectedCallIndices.add(index);
    }
    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox === null || selectAllCheckbox === void 0 ? void 0 : selectAllCheckbox.checked) {
        state.filteredCalls.forEach((_, index) => {
            state.selectedCallIndices.add(index);
        });
    }
    else {
        state.selectedCallIndices.clear();
    }
    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}
function clearSelection() {
    state.selectedCallIndices.clear();
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox)
        selectAllCheckbox.checked = false;
    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}
function updateBulkActionsBar() {
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');
    if (selectedCount) {
        selectedCount.textContent = state.selectedCallIndices.size.toString();
    }
    if (bulkActions) {
        if (state.selectedCallIndices.size > 0) {
            bulkActions.classList.remove('d-none');
        }
        else {
            bulkActions.classList.add('d-none');
        }
    }
}
// =============================================================================
// Call Detail Modal
// =============================================================================
function showCallDetail(index) {
    const call = state.filteredCalls[index];
    if (!call)
        return;
    const modalTitle = document.getElementById('callDetailModalLabel');
    const modalContent = document.getElementById('call-detail-content');
    if (!modalContent)
        return;
    // Get utility functions from window (defined in main.ts)
    const escapeHtmlFn = (text) => window.escapeHtml ? window.escapeHtml(text) : text;
    const callNumber = call.CallNumber || call.call_number || 'Unknown';
    const lastName = call.ConsumerInfo_ConsumerLastName || call.lastname || '';
    const firstName = call.ConsumerInfo_ConsumerFirstName || call.firstname || '';
    const address = call.ConsumerInfo_ConsumerAddress1 || call.address || '';
    const city = call.ConsumerInfo_PostcodeLevel3 || call.city || '';
    const state_val = call.ConsumerInfo_PostcodeLevel1 || call.state || '';
    const zip = call.ConsumerInfo_Postcode || call.zip || '';
    const phone1 = call.ConsumerInfo_Phone1 || call.phone || '';
    const phone2 = call.ConsumerInfo_Phone2 || call.phone2 || '';
    const brand = call.ProductInfo_SPBrandDesc || call.brand || '';
    const product = call.ProductInfo_SPProductDesc || call.product || '';
    const model = call.ProductInfo_MobelNo || call.ProductInfo_ModelNo || call.model || '';
    const serial = call.ProductInfo_SerialNo || call.serial || '';
    const status = call.CallStatus || call.call_status || 'NEW';
    const subStatus = call.CallSubStatus || call.call_substatus || '';
    const warranty = call.WarrantyType || call.warranty_type || '';
    const problemDesc = call.ProbelmDesc || call.problem_desc || 'No description provided';
    // Clean phone numbers for display and SMS
    const cleanPhone1 = cleanPhoneNumber(phone1);
    const cleanPhone2 = cleanPhoneNumber(phone2);
    modalContent.innerHTML = `
        <div class="row g-3">
            <div class="col-md-6">
                <div class="card bg-light">
                    <div class="card-header"><strong>Customer Information</strong></div>
                    <div class="card-body">
                        <p><strong>Name:</strong> ${escapeHtmlFn(firstName)} ${escapeHtmlFn(lastName)}</p>
                        <p><strong>Address:</strong> ${escapeHtmlFn(address)}</p>
                        <p><strong>City:</strong> ${escapeHtmlFn(city)}, ${escapeHtmlFn(state_val)} ${escapeHtmlFn(zip)}</p>
                        <p><strong>Phone:</strong> ${cleanPhone1}</p>
                        ${phone2 && phone2 !== '0' ? '<p><strong>Phone 2:</strong> ' + cleanPhone2 + '</p>' : ''}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card bg-light">
                    <div class="card-header"><strong>Product Information</strong></div>
                    <div class="card-body">
                        <p><strong>Brand:</strong> ${escapeHtmlFn(brand)}</p>
                        <p><strong>Product:</strong> ${escapeHtmlFn(product)}</p>
                        <p><strong>Model:</strong> ${escapeHtmlFn(model) || '-'}</p>
                        <p><strong>Serial:</strong> ${escapeHtmlFn(serial) || '-'}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <div class="card bg-light">
                    <div class="card-header"><strong>Service Information</strong></div>
                    <div class="card-body">
                        <p><strong>Status:</strong> ${getStatusBadge(status)}</p>
                        ${subStatus ? '<p><strong>Sub-Status:</strong> ' + escapeHtmlFn(subStatus) + '</p>' : ''}
                        <p><strong>Warranty:</strong> ${escapeHtmlFn(warranty) || 'Not specified'}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <div class="card bg-light">
                    <div class="card-header"><strong>Problem Description</strong></div>
                    <div class="card-body">
                        <p>${escapeHtmlFn(problemDesc)}</p>
                    </div>
                </div>
            </div>
            <div class="col-12">
                <h6 class="mb-2">Quick Actions</h6>
                <div class="d-flex gap-2 flex-wrap mb-3">
                    ${phone1 ? `<button class="btn btn-warning" onclick="sendSMS('${phone1}')">
                        <i class="bi bi-chat-dots"></i> Send SMS
                    </button>` : ''}
                    <button class="btn btn-success" onclick="updateSingleCallSubstatus('${callNumber}', 'ACT35')">
                        <i class="bi bi-hourglass-split"></i> Waiting on Customer
                    </button>
                    <button class="btn btn-info" onclick="updateSingleCallSubstatus('${callNumber}', 'ACT03')">
                        <i class="bi bi-calendar-check"></i> Appointment Scheduled
                    </button>
                    <button class="btn btn-primary" onclick="updateSingleCallSubstatus('${callNumber}', 'ACT02')">
                        <i class="bi bi-check-circle"></i> Appointment Confirmed
                    </button>
                </div>
                <h6 class="mb-2">Status Updates</h6>
                <div class="d-flex gap-2 flex-wrap mb-3">
                    <button class="btn btn-outline-success" onclick="updateCallStatus('${callNumber}', 'ACCEPTED', 'ACT10')">
                        <i class="bi bi-check-circle"></i> Accept & Contact Customer
                    </button>
                    <button class="btn btn-outline-primary" onclick="updateCallStatus('${callNumber}', 'COMPLETED', 'COMPLETED')">
                        <i class="bi bi-check-all"></i> Mark Complete
                    </button>
                    <button class="btn btn-outline-danger" onclick="updateCallStatus('${callNumber}', 'REJECTED', 'DECLINED')">
                        <i class="bi bi-x-circle"></i> Reject Call
                    </button>
                </div>
                <h6 class="mb-2">Other Actions</h6>
                <div class="d-flex gap-2 flex-wrap">
                    <button class="btn btn-outline-secondary" onclick="showAddNotesModal('${callNumber}')">
                        <i class="bi bi-chat-left-text"></i> Add Notes
                    </button>
                    <button class="btn btn-outline-info" onclick="exportSingleCall(${index})">
                        <i class="bi bi-file-earmark-arrow-down"></i> Export to DBF
                    </button>
                </div>
            </div>
        </div>
    `;
    if (modalTitle) {
        modalTitle.textContent = `Call Details: ${callNumber}`;
    }
    const modal = new window.bootstrap.Modal(document.getElementById('callDetailModal'));
    modal.show();
}
// =============================================================================
// Update Call Status
// =============================================================================
async function updateCallStatus(callNumber, status, substatus) {
    window.ServiceDispatch.ToastManager.info('Updating call status...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/calls/update', {
            call_number: callNumber,
            status,
            substatus,
        });
        if (response.success) {
            window.ServiceDispatch.ToastManager.success('Call status updated successfully');
            // Close modal
            const modal = window.bootstrap.Modal.getInstance(document.getElementById('callDetailModal'));
            if (modal)
                modal.hide();
            // Refresh calls
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Failed to update call status');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
// =============================================================================
// Bulk Operations
// =============================================================================
async function bulkUpdateStatus(status, substatus) {
    if (state.selectedCallIndices.size === 0)
        return;
    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });
    window.ServiceDispatch.ToastManager.info(`Updating ${callNumbers.length} calls...`);
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/calls/bulk-update', {
            call_numbers: callNumbers,
            status,
            substatus,
        });
        if (response.success) {
            window.ServiceDispatch.ToastManager.success(`Updated ${response.success_count || callNumbers.length} calls`);
            clearSelection();
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Bulk update failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
// =============================================================================
// New Bulk Operations (Enhanced)
// =============================================================================
async function bulkUpdateSubstatus(substatusId = 'ACT35', notes) {
    if (state.selectedCallIndices.size === 0) {
        window.ServiceDispatch.ToastManager.warning('Please select calls to update');
        return;
    }
    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });
    window.ServiceDispatch.ToastManager.info(`Updating substatus for ${callNumbers.length} calls...`);
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/update-substatus', {
            call_numbers: callNumbers,
            substatus_id: substatusId,
            notes: notes || undefined,
        });
        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;
            if (failedCount > 0) {
                window.ServiceDispatch.ToastManager.warning(`Updated ${successCount} calls. ${failedCount} failed.`);
            }
            else {
                window.ServiceDispatch.ToastManager.success(`Successfully updated ${successCount} calls`);
            }
            clearSelection();
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Substatus update failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
async function bulkUpdateScheduleDate(scheduleDate, notes) {
    if (state.selectedCallIndices.size === 0) {
        window.ServiceDispatch.ToastManager.warning('Please select calls to reschedule');
        return;
    }
    if (!scheduleDate) {
        window.ServiceDispatch.ToastManager.error('Please select a schedule date');
        return;
    }
    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });
    window.ServiceDispatch.ToastManager.info(`Rescheduling ${callNumbers.length} calls...`);
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/update-schedule', {
            call_numbers: callNumbers,
            schedule_date: scheduleDate,
            notes: notes || undefined,
        });
        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;
            if (failedCount > 0) {
                window.ServiceDispatch.ToastManager.warning(`Rescheduled ${successCount} calls. ${failedCount} failed.`);
            }
            else {
                window.ServiceDispatch.ToastManager.success(`Successfully rescheduled ${successCount} calls to ${scheduleDate}`);
            }
            clearSelection();
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Schedule update failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
async function bulkAddTicketNotes(ticketNumber) {
    if (state.selectedCallIndices.size === 0) {
        window.ServiceDispatch.ToastManager.warning('Please select calls to add notes');
        return;
    }
    if (!ticketNumber) {
        window.ServiceDispatch.ToastManager.error('Please enter a ticket number');
        return;
    }
    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });
    window.ServiceDispatch.ToastManager.info(`Adding ticket number to ${callNumbers.length} calls...`);
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/add-notes', {
            call_numbers: callNumbers,
            notes: ticketNumber,
        });
        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;
            if (failedCount > 0) {
                window.ServiceDispatch.ToastManager.warning(`Added notes to ${successCount} calls. ${failedCount} failed.`);
            }
            else {
                window.ServiceDispatch.ToastManager.success(`Successfully added ticket number to ${successCount} calls`);
            }
            clearSelection();
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Failed to add notes');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
async function generateSMSMessage() {
    var _a, _b, _c, _d, _e;
    const customerName = ((_a = document.getElementById('sms-customer-name')) === null || _a === void 0 ? void 0 : _a.value) || 'Customer';
    const product = ((_b = document.getElementById('sms-product')) === null || _b === void 0 ? void 0 : _b.value) || 'appliance';
    const dealerInvoice = ((_c = document.getElementById('sms-dealer-invoice')) === null || _c === void 0 ? void 0 : _c.value) || '';
    window.ServiceDispatch.ToastManager.info('Generating SMS message...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/generate-sms', {
            customer_name: customerName,
            product: product,
            dealer_invoice: dealerInvoice || undefined,
        });
        if (response.success) {
            const smsMessage = ((_d = response.data) === null || _d === void 0 ? void 0 : _d.sms_message) || '';
            const charCount = ((_e = response.data) === null || _e === void 0 ? void 0 : _e.character_count) || 0;
            // Display in modal
            const smsOutput = document.getElementById('sms-output');
            const smsCharCount = document.getElementById('sms-char-count');
            if (smsOutput) {
                smsOutput.value = smsMessage;
            }
            if (smsCharCount) {
                smsCharCount.textContent = `${charCount} characters`;
            }
            window.ServiceDispatch.ToastManager.success('SMS message generated');
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Failed to generate SMS');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
function copySMSToClipboard() {
    const smsOutput = document.getElementById('sms-output');
    if (smsOutput && smsOutput.value) {
        smsOutput.select();
        document.execCommand('copy');
        window.ServiceDispatch.ToastManager.success('SMS copied to clipboard');
    }
}
function showBulkOperationsModal() {
    const modal = new window.bootstrap.Modal(document.getElementById('bulkOperationsModal'));
    modal.show();
}
// Individual operation wrappers
async function updateSingleCallSubstatus(callNumber, substatusId, notes) {
    window.ServiceDispatch.ToastManager.info('Updating call substatus...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/update-substatus', {
            call_numbers: [callNumber],
            substatus_id: substatusId,
            notes: notes || undefined,
        });
        if (response.success) {
            window.ServiceDispatch.ToastManager.success('Call substatus updated');
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Update failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
async function updateSingleCallSchedule(callNumber, scheduleDate, notes) {
    window.ServiceDispatch.ToastManager.info('Updating schedule...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/update-schedule', {
            call_numbers: [callNumber],
            schedule_date: scheduleDate,
            notes: notes || undefined,
        });
        if (response.success) {
            window.ServiceDispatch.ToastManager.success('Schedule updated');
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Update failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
async function addSingleCallNotes(callNumber, notes) {
    window.ServiceDispatch.ToastManager.info('Adding notes...');
    try {
        const response = await window.ServiceDispatch.ApiClient.post('/api/bulk/add-notes', {
            call_numbers: [callNumber],
            notes: notes,
        });
        if (response.success) {
            window.ServiceDispatch.ToastManager.success('Notes added');
            await fetchCalls();
        }
        else {
            window.ServiceDispatch.ToastManager.error(response.error || 'Failed to add notes');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
function showAddNotesModal(callNumber) {
    // Create a simple prompt for notes
    const notes = prompt('Enter notes to add to this call:');
    if (notes && notes.trim()) {
        addSingleCallNotes(callNumber, notes.trim());
    }
}
async function exportSelected() {
    if (state.selectedCallIndices.size === 0)
        return;
    const callsToExport = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return mapCallToExport(call);
    });
    await exportCallsToDBF(callsToExport);
}
async function exportSingleCall(index) {
    const call = state.filteredCalls[index];
    if (!call)
        return;
    const callToExport = mapCallToExport(call);
    await exportCallsToDBF([callToExport]);
}
// =============================================================================
// Export Helper Functions
// =============================================================================
function mapCallToExport(call) {
    return {
        invoice: call.CallNumber || call.call_number,
        lastname: call.ConsumerInfo_ConsumerLastName || call.lastname,
        firstname: call.ConsumerInfo_ConsumerFirstName || call.firstname,
        address: call.ConsumerInfo_ConsumerAddress1 || call.address,
        city: call.ConsumerInfo_PostcodeLevel3 || call.city,
        state: call.ConsumerInfo_PostcodeLevel1 || call.state,
        zip: call.ConsumerInfo_Postcode || call.zip,
        phone: call.ConsumerInfo_Phone1 || call.phone,
        phone2: call.ConsumerInfo_Phone2 || call.phone2,
        make: call.ProductInfo_SPBrandDesc || call.brand,
        typ: call.ProductInfo_SPProductDesc || call.product,
        model: call.ProductInfo_MobelNo || call.ProductInfo_ModelNo || call.model,
        serial: call.ProductInfo_SerialNo || call.serial,
        servicereq: call.ProbelmDesc || call.problem_desc,
        dlrinvoice: call.CallNumber || call.call_number,
        btaddress: call.CallNumber || call.call_number,
    };
}
async function exportCallsToDBF(calls) {
    window.ServiceDispatch.ToastManager.info('Generating DBF file...');
    try {
        const response = await fetch('/api/export/dbf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ calls }),
        });
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `lotus_tickets_${Date.now()}.dbf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            window.ServiceDispatch.ToastManager.success('DBF file downloaded');
        }
        else {
            const data = await response.json();
            window.ServiceDispatch.ToastManager.error(data.error || 'Export failed');
        }
    }
    catch (error) {
        window.ServiceDispatch.ToastManager.error('Error: ' + error.message);
    }
}
// =============================================================================
// Charts Display
// =============================================================================
function updateChartsDisplay() {
    const chartsRow = document.getElementById('charts-row');
    if (chartsRow && state.allCalls.length > 0) {
        chartsRow.classList.remove('d-none');
        if (typeof initializeCharts === 'function') {
            initializeCharts(state.allCalls);
        }
    }
}
// Make functions globally available
if (typeof window !== 'undefined') {
    window.setDateRange = setDateRange;
    window.fetchCalls = fetchCalls;
    window.refreshCalls = refreshCalls;
    window.toggleCallSelection = toggleCallSelection;
    window.toggleSelectAll = toggleSelectAll;
    window.clearSelection = clearSelection;
    window.showCallDetail = showCallDetail;
    window.updateCallStatus = updateCallStatus;
    window.bulkUpdateStatus = bulkUpdateStatus;
    window.exportSelected = exportSelected;
    window.exportSingleCall = exportSingleCall;
    // New bulk operations
    window.bulkUpdateSubstatus = bulkUpdateSubstatus;
    window.bulkUpdateScheduleDate = bulkUpdateScheduleDate;
    window.bulkAddTicketNotes = bulkAddTicketNotes;
    window.generateSMSMessage = generateSMSMessage;
    window.copySMSToClipboard = copySMSToClipboard;
    window.showBulkOperationsModal = showBulkOperationsModal;
    // Individual operations
    window.updateSingleCallSubstatus = updateSingleCallSubstatus;
    window.updateSingleCallSchedule = updateSingleCallSchedule;
    window.addSingleCallNotes = addSingleCallNotes;
    window.showAddNotesModal = showAddNotesModal;
    // SMS and filtering
    window.sendSMS = sendSMS;
    window.filterByStatus = filterByStatus;
    window.clearFilter = clearFilter;
}
//# sourceMappingURL=calls.js.map