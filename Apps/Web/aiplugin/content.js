function injectInspectorUI() {
  // headless check
  if (/Headless/i.test(navigator.userAgent)) {
    console.log("Headless mode detected. ZeuZ AI Inspector UI skipped.");
    return;
  }

  const host = document.createElement('div');
  host.id = 'zeuz-ai-inspector-host';
  
  // initial position (fixed)
  Object.assign(host.style, {
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    zIndex: '2147483647', // maximum z-index
    width: 'auto',
    height: 'auto',
    filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.15))'
  });

  document.body.appendChild(host);

  // shadow dom
  const shadow = host.attachShadow({ mode: 'open' });

  const style = document.createElement('style');
  style.textContent = `
    :host {
      font-family: sans-serif;
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: grab; /* Cursor indicates draggable */
      user-select: none;
    }
    .container:active {
      cursor: grabbing;
    }
    
    /* The Main Button */
    .ai-fab {
      width: 56px;
      height: 56px;
      background: #d3a8ffff;
      border-radius: 50%;
      border: 2px solid #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      color: white;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    
    .ai-fab img {
      pointer-events: none;
    }
    
    /* Active State */
    .ai-fab.active {
      background: #ff8d8dff;
      animation: pulse 2s infinite;
      cursor: default;
    }
    
    /* Hover Effect */
    .container:hover .ai-fab {
      transform: scale(1.05);
    }

    /* Close Button */
    .close-btn {
      position: absolute;
      top: -8px;
      right: -8px;
      width: 20px;
      height: 20px;
      background: #4b5563;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: bold;
      cursor: pointer;
      opacity: 0; /* Hidden by default */
      transition: opacity 0.2s;
      border: 2px solid white;
    }

    /* close button on hover */
    .container:hover .close-btn {
      opacity: 1;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
      70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
      100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
  `;
  shadow.appendChild(style);

  const container = document.createElement('div');
  container.className = 'container';

  // main button
  const btn = document.createElement('div');
  btn.className = 'ai-fab';
  const btnImg = document.createElement('img');
  btnImg.src = chrome.runtime.getURL('zeuz.png');
  btnImg.style.width = '32px';
  btnImg.style.height = '32px';
  btn.appendChild(btnImg);

  // close btn
  const closeBtn = document.createElement('div');
  closeBtn.className = 'close-btn';
  closeBtn.innerHTML = '✕';
  
  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    host.remove(); // remove the whole UI
  });

  container.appendChild(btn);
  container.appendChild(closeBtn);
  shadow.appendChild(container);

  // drag
  let isDragging = false;
  let hasMoved = false;
  let startX, startY;

  const onMouseDown = (e) => {
    // don't drag if inspector is active
    if (btn.classList.contains('active')) return;
    
    isDragging = true;
    hasMoved = false;
    
    const rect = host.getBoundingClientRect();
    
    host.style.right = 'auto';
    host.style.bottom = 'auto';
    host.style.left = rect.left + 'px';
    host.style.top = rect.top + 'px';

    startX = e.clientX;
    startY = e.clientY;
    
    e.preventDefault();
  };

  const onMouseMove = (e) => {
    if (!isDragging) return;
    
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      hasMoved = true;
    }

    host.style.left = (host.offsetLeft + dx) + 'px';
    host.style.top = (host.offsetTop + dy) + 'px';
    
    startX = e.clientX;
    startY = e.clientY;
  };

  const onMouseUp = () => {
    isDragging = false;
  };

  // drag listeners
  container.addEventListener('mousedown', onMouseDown);
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
  
  btn.addEventListener('click', (e) => {
    if (!hasMoved && !btn.classList.contains('active')) {
      chrome.runtime.sendMessage({ action: 'toggle_from_content_script' });
    }
    hasMoved = false; // Reset after click
  });

  // right-click context menu for deactivation when inspector is active
  btn.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    if (btn.classList.contains('active')) {
      chrome.runtime.sendMessage({ action: 'toggle_from_content_script' });
    }
  });

  chrome.runtime.onMessage.addListener((request) => {
    if (request.action === 'activate') {
      btn.classList.add('active');
      btnImg.src = chrome.runtime.getURL('zeuz-active.png');
    } else if (request.action === 'deactivate') {
      btn.classList.remove('active');
      btnImg.src = chrome.runtime.getURL('zeuz.png');
    }
  });
}

injectInspectorUI();