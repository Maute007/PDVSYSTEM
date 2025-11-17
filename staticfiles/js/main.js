/**
 * PDV System - Custom JavaScript Functions
 * Enhanced functionality for the sales management system
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    setupEventListeners();
    initializeTooltips();
    setupSearchFunctionality();
    setupFormValidation();
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Navbar scroll effect
    window.addEventListener('scroll', handleScroll);
    
    // Auto-hide alerts
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

/**
 * Handle scroll events
 */
function handleScroll() {
    const navbar = document.querySelector('.navbar-custom');
    if (window.scrollY > 50) {
        navbar?.classList.add('scrolled');
    } else {
        navbar?.classList.remove('scrolled');
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup search functionality
 */
function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="Buscar"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function(e) {
            performSearch(e.target.value);
        }, 300));
    });
}

/**
 * Perform search
 */
function performSearch(query) {
    if (query.length < 2) return;
    
    console.log('Searching for:', query);
    // Add your search logic here
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast('Por favor, preencha todos os campos obrigatórios', 'error');
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    if (!toastElement) return;
    
    const toastBody = toastElement.querySelector('.toast-body');
    const toastHeader = toastElement.querySelector('.toast-header-custom');
    const toastTitle = toastHeader.querySelector('strong');
    
    // Update content
    toastBody.textContent = message;
    
    // Update icon and title
    const icons = {
        success: 'check-circle',
        error: 'x-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    const titles = {
        success: 'Sucesso',
        error: 'Erro',
        warning: 'Atenção',
        info: 'Informação'
    };
    
    const colors = {
        success: 'linear-gradient(135deg, #22c55e, #10b981)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        info: 'linear-gradient(135deg, #06b6d4, #0891b2)'
    };
    
    const icon = toastHeader.querySelector('i');
    icon.className = `bi bi-${icons[type]} me-2`;
    toastTitle.textContent = titles[type];
    toastHeader.style.background = colors[type];
    
    // Show toast
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

/**
 * Format date
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

/**
 * Calculate percentage
 */
function calculatePercentage(value, total) {
    if (total === 0) return 0;
    return ((value / total) * 100).toFixed(2);
}

/**
 * Confirm action
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Loading overlay
 */
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner-custom"></div>';
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Erro ao copiar', 'error');
    });
}

/**
 * Print element
 */
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Imprimir</title>');
    printWindow.document.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(element.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

/**
 * Export to CSV
 */
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }
        
        csv.push(row.join(','));
    }
    
    const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * Validate CPF
 */
function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
    
    let sum = 0;
    let remainder;
    
    for (let i = 1; i <= 9; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }
    
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(9, 10))) return false;
    
    sum = 0;
    for (let i = 1; i <= 10; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }
    
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(10, 11))) return false;
    
    return true;
}

/**
 * Format phone number
 */
function formatPhone(phone) {
    phone = phone.replace(/\D/g, '');
    
    if (phone.length === 11) {
        return phone.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '($1) $2-$3-$4');
    } else if (phone.length === 9) {
        return phone.replace(/(\d{3})(\d{3})(\d{3})/, '$1-$2-$3');
    }
    
    return phone;
}

// Export functions for use in other scripts
window.PDVSystem = {
    showToast,
    formatCurrency,
    formatDate,
    calculatePercentage,
    confirmAction,
    showLoading,
    hideLoading,
    copyToClipboard,
    printElement,
    exportToCSV,
    validateCPF,
    formatPhone
};
