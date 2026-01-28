/**
 * Calls Management TypeScript Module
 * Handles fetching, displaying, and managing service calls
 */

// =============================================================================
// Type Definitions
// =============================================================================

interface CallInfo {
    CallNumber?: string;
    call_number?: string;
    ConsumerInfo_ConsumerLastName?: string;
    lastname?: string;
    ConsumerInfo_ConsumerFirstName?: string;
    firstname?: string;
    ConsumerInfo_ConsumerAddress1?: string;
    address?: string;
    ConsumerInfo_PostcodeLevel3?: string;
    city?: string;
    ConsumerInfo_PostcodeLevel1?: string;
    state?: string;
    ConsumerInfo_Postcode?: string;
    zip?: string;
    ConsumerInfo_Phone1?: string;
    phone?: string;
    ConsumerInfo_Phone2?: string;
    phone2?: string;
    ProductInfo_SPBrandDesc?: string;
    brand?: string;
    ProductInfo_SPProductDesc?: string;
    product?: string;
    ProductInfo_MobelNo?: string;
    ProductInfo_ModelNo?: string;
    model?: string;
    ProductInfo_SerialNo?: string;
    serial?: string;
    ProductInfo_InstallDate?: string;
    CallStatus?: string;
    call_status?: string;
    CallSubStatus?: string;
    call_substatus?: string;
    WarrantyType?: string;
    warranty_type?: string;
    ScheduleDate?: string;
    schedule_date?: string;
    CallAcceptedDateTime?: string;
    ProbelmDesc?: string;
    problem_desc?: string;
}

interface CallsState {
    allCalls: CallInfo[];
    filteredCalls: CallInfo[];
    selectedCallIndices: Set<number>;
    currentStatusFilter: string;
}

// =============================================================================
// State Management
// =============================================================================

const state: CallsState = {
    allCalls: [],
    filteredCalls: [],
    selectedCallIndices: new Set<number>(),
    currentStatusFilter: '',
};

// =============================================================================
// Date Range Management
// =============================================================================

function setDateRange(days: number): void {
    const today = new Date();
    const fromDate = new Date(today);

    if (days > 0) {
        fromDate.setDate(today.getDate() - days);
    }

    const fromInput = document.getElementById('from-date') as HTMLInputElement;
    const toInput = document.getElementById('to-date') as HTMLInputElement;

    if (fromInput) fromInput.value = (window as any).ServiceDispatch.DateUtils.toISODate(fromDate);
    if (toInput) toInput.value = (window as any).ServiceDispatch.DateUtils.toISODate(today);

    // Update button active states
    document.querySelectorAll('.btn-group .btn').forEach((btn, index) => {
        btn.classList.remove('active');
    });

    const quickButtons = [0, 2, 7, 14, 30];
    const buttonIndex = quickButtons.indexOf(days);
    if (buttonIndex >= 0) {
        document.querySelectorAll('.btn-group .btn')[buttonIndex]?.classList.add('active');
    }
}

// =============================================================================
// Fetch Calls from API
// =============================================================================

async function fetchCalls(): Promise<void> {
    const fromDateInput = document.getElementById('from-date') as HTMLInputElement;
    const toDateInput = document.getElementById('to-date') as HTMLInputElement;
    const statusFilterInput = document.getElementById('status-filter') as HTMLSelectElement;

    const fromDate = fromDateInput?.value;
    const toDate = toDateInput?.value;
    const statusFilter = statusFilterInput?.value;

    if (!fromDate || !toDate) {
        (window as any).ServiceDispatch.ToastManager.error('Please select a date range');
        return;
    }

    (window as any).ServiceDispatch.LoadingManager.show();
    (window as any).ServiceDispatch.ToastManager.info('Fetching calls from ServicePower...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/calls', {
            from_date: fromDate,
            to_date: toDate,
            status: statusFilter || undefined,
        });

        (window as any).ServiceDispatch.LoadingManager.hide();

        if (response.success) {
            state.allCalls = response.calls || [];
            state.filteredCalls = [...state.allCalls];

            renderCallsTable(state.filteredCalls);
            updateStats(state.allCalls);
            updateChartsDisplay();

            (window as any).ServiceDispatch.ToastManager.success(`Loaded ${state.allCalls.length} calls`);
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Failed to fetch calls');
        }
    } catch (error) {
        (window as any).ServiceDispatch.LoadingManager.hide();
        console.error('Fetch error:', error);
        (window as any).ServiceDispatch.ToastManager.error('Error fetching calls: ' + (error as Error).message);
    }
}

function refreshCalls(): void {
    fetchCalls();
}

// =============================================================================
// Phone Number Cleaning
// =============================================================================

function cleanPhoneNumber(phone: string): string {
    if (!phone || phone === '0') return '';

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

function sendSMS(phone: string): void {
    const cleanPhone = cleanPhoneNumber(phone).replace(/\D/g, '');

    if (!cleanPhone || cleanPhone.length < 10) {
        (window as any).ServiceDispatch.ToastManager.error('Invalid phone number');
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

    (window as any).ServiceDispatch.ToastManager.success('Opening Google Voice with SMS template');
}

// =============================================================================
// Client-Side Filtering
// =============================================================================

function filterByStatus(status: string): void {
    state.currentStatusFilter = status;

    if (!status || status === '' || status === 'all') {
        // Show all calls
        state.filteredCalls = [...state.allCalls];
    } else {
        // Filter by status (case-insensitive)
        state.filteredCalls = state.allCalls.filter(call => {
            const callStatus = (call.CallStatus || call.call_status || '').toUpperCase();
            const filterStatus = status.toUpperCase();

            // Match based on status keywords
            if (filterStatus.includes('COMPLET')) return callStatus.includes('COMPLET');
            if (filterStatus.includes('ACCEPT')) return callStatus.includes('ACCEPT');
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

    (window as any).ServiceDispatch.ToastManager.info(
        `Showing ${state.filteredCalls.length} of ${state.allCalls.length} calls`
    );
}

function updateFilterTags(): void {
    // Update any filter tag displays if they exist
    const filterTagsContainer = document.getElementById('filter-tags');
    if (filterTagsContainer && state.currentStatusFilter) {
        filterTagsContainer.innerHTML = `
            <span class="badge bg-primary me-2">
                Filter: ${state.currentStatusFilter}
                <button class="btn-close btn-close-white ms-2" onclick="clearFilter()" style="font-size: 0.7rem;"></button>
            </span>
        `;
    } else if (filterTagsContainer) {
        filterTagsContainer.innerHTML = '';
    }
}

function clearFilter(): void {
    state.currentStatusFilter = '';
    state.filteredCalls = [...state.allCalls];
    renderCallsTable(state.filteredCalls);
    updateFilterTags();
}

// =============================================================================
// Render Calls Table
// =============================================================================

function renderCallsTable(calls: CallInfo[]): void {
    const tbody = document.getElementById('calls-tbody');
    const callsCount = document.getElementById('calls-count');
    const tableInfo = document.getElementById('table-info');
    const lastUpdated = document.getElementById('last-updated');

    if (!tbody) return;

    if (!calls || calls.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-5">
                    <i class="bi bi-inbox text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-2">No calls found matching your filters.</p>
                </td>
            </tr>
        `;
        if (callsCount) callsCount.textContent = '0 calls';
        if (tableInfo) tableInfo.textContent = 'Showing 0 of 0 calls';
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
                    <small>${(window as any).ServiceDispatch.StringUtils.truncate(problemDesc, 50)}</small>
                </td>
                <td>${statusBadge}</td>
                <td>
                    ${warranty ? `<span class="badge bg-secondary">${warranty}</span>` : '-'}
                </td>
                <td>
                    <small>${(window as any).formatDate ? (window as any).formatDate(scheduleDate) : scheduleDate}</small>
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
    if (callsCount) callsCount.textContent = `${calls.length} calls`;
    if (tableInfo) tableInfo.textContent = `Showing ${calls.length} of ${state.allCalls.length} calls`;
    if (lastUpdated) lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}

// =============================================================================
// Status Badge Helper
// =============================================================================

function getStatusBadge(status: string): string {
    const statusUpper = (status || '').toUpperCase();

    let badgeClass = 'bg-secondary';
    if (statusUpper.includes('COMPLET')) badgeClass = 'bg-success';
    else if (statusUpper.includes('ACCEPT')) badgeClass = 'bg-info';
    else if (statusUpper.includes('CANCEL') || statusUpper.includes('REJECT')) badgeClass = 'bg-danger';
    else if (statusUpper.includes('SCHEDUL')) badgeClass = 'bg-primary';
    else if (statusUpper.includes('NEW') || statusUpper.includes('PEND')) badgeClass = 'bg-warning';

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

function updateStats(calls: CallInfo[]): void {
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
        if (status.includes('COMPLET')) stats.completed++;
        else if (status.includes('ACCEPT')) stats.accepted++;
        else if (status.includes('CANCEL') || status.includes('REJECT')) stats.cancelled++;
        else if (status.includes('NEW') || status.includes('PEND')) stats.pending++;

        const problem = (call.ProbelmDesc || call.problem_desc || '').toLowerCase();
        if (problem.includes('part')) stats.parts++;
    });

    document.getElementById('stat-total')!.textContent = stats.total.toString();
    document.getElementById('stat-pending')!.textContent = stats.pending.toString();
    document.getElementById('stat-completed')!.textContent = stats.completed.toString();
    document.getElementById('stat-accepted')!.textContent = stats.accepted.toString();
    document.getElementById('stat-cancelled')!.textContent = stats.cancelled.toString();
    document.getElementById('stat-parts')!.textContent = stats.parts.toString();
}

// =============================================================================
// Selection Management
// =============================================================================

function toggleCallSelection(index: number): void {
    if (state.selectedCallIndices.has(index)) {
        state.selectedCallIndices.delete(index);
    } else {
        state.selectedCallIndices.add(index);
    }

    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}

function toggleSelectAll(): void {
    const selectAllCheckbox = document.getElementById('select-all') as HTMLInputElement;

    if (selectAllCheckbox?.checked) {
        state.filteredCalls.forEach((_, index) => {
            state.selectedCallIndices.add(index);
        });
    } else {
        state.selectedCallIndices.clear();
    }

    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}

function clearSelection(): void {
    state.selectedCallIndices.clear();
    const selectAllCheckbox = document.getElementById('select-all') as HTMLInputElement;
    if (selectAllCheckbox) selectAllCheckbox.checked = false;

    updateBulkActionsBar();
    renderCallsTable(state.filteredCalls);
}

function updateBulkActionsBar(): void {
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');

    if (selectedCount) {
        selectedCount.textContent = state.selectedCallIndices.size.toString();
    }

    if (bulkActions) {
        if (state.selectedCallIndices.size > 0) {
            bulkActions.classList.remove('d-none');
        } else {
            bulkActions.classList.add('d-none');
        }
    }
}

// =============================================================================
// Call Detail Modal
// =============================================================================

function showCallDetail(index: number): void {
    const call = state.filteredCalls[index];
    if (!call) return;

    const modalTitle = document.getElementById('callDetailModalLabel');
    const modalContent = document.getElementById('call-detail-content');

    if (!modalContent) return;

    // Get utility functions from window (defined in main.ts)
    const escapeHtmlFn = (text: string) => (window as any).escapeHtml ? (window as any).escapeHtml(text) : text;

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

    const modal = new (window as any).bootstrap.Modal(document.getElementById('callDetailModal'));
    modal.show();
}

// =============================================================================
// Update Call Status
// =============================================================================

async function updateCallStatus(callNumber: string, status: string, substatus: string): Promise<void> {
    (window as any).ServiceDispatch.ToastManager.info('Updating call status...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/calls/update', {
            call_number: callNumber,
            status,
            substatus,
        });

        if (response.success) {
            (window as any).ServiceDispatch.ToastManager.success('Call status updated successfully');

            // Close modal
            const modal = (window as any).bootstrap.Modal.getInstance(document.getElementById('callDetailModal'));
            if (modal) modal.hide();

            // Refresh calls
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Failed to update call status');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

// =============================================================================
// Bulk Operations
// =============================================================================

async function bulkUpdateStatus(status: string, substatus: string): Promise<void> {
    if (state.selectedCallIndices.size === 0) return;

    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });

    (window as any).ServiceDispatch.ToastManager.info(`Updating ${callNumbers.length} calls...`);

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/calls/bulk-update', {
            call_numbers: callNumbers,
            status,
            substatus,
        });

        if (response.success) {
            (window as any).ServiceDispatch.ToastManager.success(`Updated ${response.success_count || callNumbers.length} calls`);
            clearSelection();
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Bulk update failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

// =============================================================================
// New Bulk Operations (Enhanced)
// =============================================================================

async function bulkUpdateSubstatus(substatusId: string = 'ACT35', notes?: string): Promise<void> {
    if (state.selectedCallIndices.size === 0) {
        (window as any).ServiceDispatch.ToastManager.warning('Please select calls to update');
        return;
    }

    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });

    (window as any).ServiceDispatch.ToastManager.info(`Updating substatus for ${callNumbers.length} calls...`);

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/update-substatus', {
            call_numbers: callNumbers,
            substatus_id: substatusId,
            notes: notes || undefined,
        });

        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;

            if (failedCount > 0) {
                (window as any).ServiceDispatch.ToastManager.warning(
                    `Updated ${successCount} calls. ${failedCount} failed.`
                );
            } else {
                (window as any).ServiceDispatch.ToastManager.success(
                    `Successfully updated ${successCount} calls`
                );
            }

            clearSelection();
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Substatus update failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

async function bulkUpdateScheduleDate(scheduleDate: string, notes?: string): Promise<void> {
    if (state.selectedCallIndices.size === 0) {
        (window as any).ServiceDispatch.ToastManager.warning('Please select calls to reschedule');
        return;
    }

    if (!scheduleDate) {
        (window as any).ServiceDispatch.ToastManager.error('Please select a schedule date');
        return;
    }

    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });

    (window as any).ServiceDispatch.ToastManager.info(`Rescheduling ${callNumbers.length} calls...`);

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/update-schedule', {
            call_numbers: callNumbers,
            schedule_date: scheduleDate,
            notes: notes || undefined,
        });

        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;

            if (failedCount > 0) {
                (window as any).ServiceDispatch.ToastManager.warning(
                    `Rescheduled ${successCount} calls. ${failedCount} failed.`
                );
            } else {
                (window as any).ServiceDispatch.ToastManager.success(
                    `Successfully rescheduled ${successCount} calls to ${scheduleDate}`
                );
            }

            clearSelection();
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Schedule update failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

async function bulkAddTicketNotes(ticketNumber: string): Promise<void> {
    if (state.selectedCallIndices.size === 0) {
        (window as any).ServiceDispatch.ToastManager.warning('Please select calls to add notes');
        return;
    }

    if (!ticketNumber) {
        (window as any).ServiceDispatch.ToastManager.error('Please enter a ticket number');
        return;
    }

    const callNumbers = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return call.CallNumber || call.call_number;
    });

    (window as any).ServiceDispatch.ToastManager.info(`Adding ticket number to ${callNumbers.length} calls...`);

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/add-notes', {
            call_numbers: callNumbers,
            notes: ticketNumber,
        });

        if (response.success) {
            const data = response.data || {};
            const successCount = data.success_count || 0;
            const failedCount = data.failed_count || 0;

            if (failedCount > 0) {
                (window as any).ServiceDispatch.ToastManager.warning(
                    `Added notes to ${successCount} calls. ${failedCount} failed.`
                );
            } else {
                (window as any).ServiceDispatch.ToastManager.success(
                    `Successfully added ticket number to ${successCount} calls`
                );
            }

            clearSelection();
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Failed to add notes');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

async function generateSMSMessage(): Promise<void> {
    const customerName = (document.getElementById('sms-customer-name') as HTMLInputElement)?.value || 'Customer';
    const product = (document.getElementById('sms-product') as HTMLInputElement)?.value || 'appliance';
    const dealerInvoice = (document.getElementById('sms-dealer-invoice') as HTMLInputElement)?.value || '';

    (window as any).ServiceDispatch.ToastManager.info('Generating SMS message...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/generate-sms', {
            customer_name: customerName,
            product: product,
            dealer_invoice: dealerInvoice || undefined,
        });

        if (response.success) {
            const smsMessage = response.data?.sms_message || '';
            const charCount = response.data?.character_count || 0;

            // Display in modal
            const smsOutput = document.getElementById('sms-output') as HTMLTextAreaElement;
            const smsCharCount = document.getElementById('sms-char-count');

            if (smsOutput) {
                smsOutput.value = smsMessage;
            }

            if (smsCharCount) {
                smsCharCount.textContent = `${charCount} characters`;
            }

            (window as any).ServiceDispatch.ToastManager.success('SMS message generated');
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Failed to generate SMS');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

function copySMSToClipboard(): void {
    const smsOutput = document.getElementById('sms-output') as HTMLTextAreaElement;
    if (smsOutput && smsOutput.value) {
        smsOutput.select();
        document.execCommand('copy');
        (window as any).ServiceDispatch.ToastManager.success('SMS copied to clipboard');
    }
}

function showBulkOperationsModal(): void {
    const modal = new (window as any).bootstrap.Modal(document.getElementById('bulkOperationsModal'));
    modal.show();
}

// Individual operation wrappers
async function updateSingleCallSubstatus(callNumber: string, substatusId: string, notes?: string): Promise<void> {
    (window as any).ServiceDispatch.ToastManager.info('Updating call substatus...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/update-substatus', {
            call_numbers: [callNumber],
            substatus_id: substatusId,
            notes: notes || undefined,
        });

        if (response.success) {
            (window as any).ServiceDispatch.ToastManager.success('Call substatus updated');
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Update failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

async function updateSingleCallSchedule(callNumber: string, scheduleDate: string, notes?: string): Promise<void> {
    (window as any).ServiceDispatch.ToastManager.info('Updating schedule...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/update-schedule', {
            call_numbers: [callNumber],
            schedule_date: scheduleDate,
            notes: notes || undefined,
        });

        if (response.success) {
            (window as any).ServiceDispatch.ToastManager.success('Schedule updated');
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Update failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

async function addSingleCallNotes(callNumber: string, notes: string): Promise<void> {
    (window as any).ServiceDispatch.ToastManager.info('Adding notes...');

    try {
        const response = await (window as any).ServiceDispatch.ApiClient.post('/api/bulk/add-notes', {
            call_numbers: [callNumber],
            notes: notes,
        });

        if (response.success) {
            (window as any).ServiceDispatch.ToastManager.success('Notes added');
            await fetchCalls();
        } else {
            (window as any).ServiceDispatch.ToastManager.error(response.error || 'Failed to add notes');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

function showAddNotesModal(callNumber: string): void {
    // Create a simple prompt for notes
    const notes = prompt('Enter notes to add to this call:');
    if (notes && notes.trim()) {
        addSingleCallNotes(callNumber, notes.trim());
    }
}

async function exportSelected(): Promise<void> {
    if (state.selectedCallIndices.size === 0) return;

    const callsToExport = Array.from(state.selectedCallIndices).map(index => {
        const call = state.filteredCalls[index];
        return mapCallToExport(call);
    });

    await exportCallsToDBF(callsToExport);
}

async function exportSingleCall(index: number): Promise<void> {
    const call = state.filteredCalls[index];
    if (!call) return;

    const callToExport = mapCallToExport(call);
    await exportCallsToDBF([callToExport]);
}

// =============================================================================
// Export Helper Functions
// =============================================================================

function mapCallToExport(call: CallInfo): any {
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

async function exportCallsToDBF(calls: any[]): Promise<void> {
    (window as any).ServiceDispatch.ToastManager.info('Generating DBF file...');

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
            (window as any).ServiceDispatch.ToastManager.success('DBF file downloaded');
        } else {
            const data = await response.json();
            (window as any).ServiceDispatch.ToastManager.error(data.error || 'Export failed');
        }
    } catch (error) {
        (window as any).ServiceDispatch.ToastManager.error('Error: ' + (error as Error).message);
    }
}

// =============================================================================
// Charts Display
// =============================================================================

function updateChartsDisplay(): void {
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
    (window as any).setDateRange = setDateRange;
    (window as any).fetchCalls = fetchCalls;
    (window as any).refreshCalls = refreshCalls;
    (window as any).toggleCallSelection = toggleCallSelection;
    (window as any).toggleSelectAll = toggleSelectAll;
    (window as any).clearSelection = clearSelection;
    (window as any).showCallDetail = showCallDetail;
    (window as any).updateCallStatus = updateCallStatus;
    (window as any).bulkUpdateStatus = bulkUpdateStatus;
    (window as any).exportSelected = exportSelected;
    (window as any).exportSingleCall = exportSingleCall;

    // New bulk operations
    (window as any).bulkUpdateSubstatus = bulkUpdateSubstatus;
    (window as any).bulkUpdateScheduleDate = bulkUpdateScheduleDate;
    (window as any).bulkAddTicketNotes = bulkAddTicketNotes;
    (window as any).generateSMSMessage = generateSMSMessage;
    (window as any).copySMSToClipboard = copySMSToClipboard;
    (window as any).showBulkOperationsModal = showBulkOperationsModal;

    // Individual operations
    (window as any).updateSingleCallSubstatus = updateSingleCallSubstatus;
    (window as any).updateSingleCallSchedule = updateSingleCallSchedule;
    (window as any).addSingleCallNotes = addSingleCallNotes;
    (window as any).showAddNotesModal = showAddNotesModal;

    // SMS and filtering
    (window as any).sendSMS = sendSMS;
    (window as any).filterByStatus = filterByStatus;
    (window as any).clearFilter = clearFilter;
}
