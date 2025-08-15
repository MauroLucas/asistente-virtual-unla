// custom-header.js
(function () {
  function insertLogo() {
    // intenta encontrar un selector típico donde aparece el saludo
    const possibleSelectors = [
      '.welcome',               // ejemplo
      '.header',                // ejemplo genérico
      '.user-greeting',         // clase si existe
      'h1',                     // último recurso
      'div'                     // fallback (buscar texto)
    ];

    let target = null;
    for (const sel of possibleSelectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText && el.innerText.toLowerCase().includes('hola')) {
        target = el;
        break;
      }
    }

    // si no lo encontramos por texto, tratar con clase conocida
    if (!target) target = document.querySelector('.user-greeting') || document.querySelector('header');

    if (!target) return;

    // evitar duplicar logo
    if (document.getElementById('unla-logo-injected')) return;

    const img = document.createElement('img');
    img.id = 'unla-logo-injected';
    img.src = '/static/assets/unla-logo.png'; // ruta pública del asset
    img.alt = 'UNLA';
    img.style.maxHeight = '48px';
    img.style.marginRight = '10px';
    img.style.verticalAlign = 'middle';

    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.alignItems = 'center';
    wrapper.style.gap = '10px';
    wrapper.appendChild(img);

    // Insertar al principio del target
    target.prepend(wrapper);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertLogo);
  } else {
    insertLogo();
  }

  // Reintentos por si el contenido se renderiza dinámicamente
  let tries = 0;
  const interval = setInterval(() => {
    tries++;
    insertLogo();
    if (tries > 10) clearInterval(interval);
  }, 500);
})();

