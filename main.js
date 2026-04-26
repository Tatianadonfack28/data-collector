// ===== FONCTIONS UTILITAIRES GLOBALES =====

// Afficher un message d'erreur
function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = message;
        el.style.display = 'block';
    }
}

// Afficher un message de succès
function showSuccess(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = message;
        el.style.display = 'block';
    }
}

// Effacer un message
function clearMessage(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = '';
    }
}

// Rediriger après un délai
function redirectAfter(url, delay = 1500) {
    setTimeout(() => {
        window.location.href = url;
    }, delay);
}

// Formater une date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Vérifier si un champ est vide
function isEmpty(value) {
    return !value || value.trim() === '';
}

// ===== ACTIVE LINK NAVBAR =====
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.fontWeight = 'bold';
            link.style.borderBottom = '2px solid white';
        }
    });
});