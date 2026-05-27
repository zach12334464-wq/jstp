(() => {
  const contactsList = document.getElementById('contactsList');
  const messagesEl = document.getElementById('messages');
  const chatTitle = document.getElementById('chatTitle');
  const contactSearch = document.getElementById('contactSearch');
  const chatForm = document.getElementById('chatForm');
  const messageInput = document.getElementById('messageInput');

  let currentContactId = null;

  function loadStorage(){
    return JSON.parse(localStorage.getItem('jstp_chat') || '{}');
  }

  function saveStorage(data){
    localStorage.setItem('jstp_chat', JSON.stringify(data));
  }

  function renderMessages(){
    messagesEl.innerHTML = '';
    const store = loadStorage();
    const conv = (store[currentContactId] || []);
    conv.forEach(m => {
      const div = document.createElement('div');
      div.className = 'msg ' + (m.from === 'me' ? 'me' : 'them');
      div.textContent = m.text;
      const meta = document.createElement('div'); meta.className = 'msg-meta'; meta.textContent = m.time;
      const wrapper = document.createElement('div'); wrapper.appendChild(div); wrapper.appendChild(meta);
      messagesEl.appendChild(wrapper);
    });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function selectContact(el){
    document.querySelectorAll('.contact-item').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    currentContactId = el.getAttribute('data-id');
    chatTitle.textContent = el.textContent;
    if(!loadStorage()[currentContactId]){
      const store = loadStorage(); store[currentContactId] = [{ from: 'them', text: 'Hi there! This is a demo chat.', time: new Date().toLocaleTimeString() }]; saveStorage(store);
    }
    renderMessages();
    messageInput.focus();
  }

  contactsList.addEventListener('click', (e) => { const btn = e.target.closest('.contact-item'); if(btn) selectContact(btn); });

  contactSearch.addEventListener('input', function(){ const q = this.value.toLowerCase(); document.querySelectorAll('.contact-item').forEach(c => { c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none'; }); });

  chatForm.addEventListener('submit', function(e){ e.preventDefault(); if(!currentContactId) return; const text = messageInput.value.trim(); if(!text) return; const store = loadStorage(); store[currentContactId] = store[currentContactId] || []; const msg = { from: 'me', text, time: new Date().toLocaleTimeString() }; store[currentContactId].push(msg); saveStorage(store); renderMessages(); messageInput.value = '';
    // simulated reply
    setTimeout(()=>{ const store2 = loadStorage(); store2[currentContactId].push({ from: 'them', text: 'Thanks — we received your message.', time: new Date().toLocaleTimeString() }); saveStorage(store2); renderMessages(); }, 900);
  });

  // Auto-select first contact
  const first = document.querySelector('.contact-item'); if(first) selectContact(first);

})();
