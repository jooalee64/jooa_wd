(async () => {
  const cat = await RD.catalog();
  const $ = id => document.getElementById(id);
  const canvas = $('canvas');
  const uid = () => Math.random().toString(36).slice(2, 10);
  let room = { id: uid(), name: 'My Room', wall: '#EFEAE2', floor: '#C9B79A', items: [] };
  let selected = null;

  const params = new URLSearchParams(location.search);
  if (params.get('room')) {
    const found = RD.get('rd_rooms', []).find(r => r.id === params.get('room'));
    if (found) room = structuredClone(found);
  }

  // ---------- render
  function render() {
    canvas.style.background = room.wall;
    $('floor-band').style.background = room.floor;
    $('wall').value = room.wall; $('floor').value = room.floor;
    canvas.querySelectorAll('.piece').forEach(n => n.remove());
    room.items.forEach(it => {
      const f = cat[it.fid]; if (!f) return;
      const el = document.createElement('div');
      el.className = 'piece' + (it.uid === selected ? ' sel' : '');
      el.style.cssText = `left:${it.x*100}%;top:${it.y*100}%;background:${f.color};transform:translate(-50%,-50%) rotate(${it.rot}deg) scale(${it.scale})`;
      el.innerHTML = `<span>${f.icon}</span><small>${f.name}</small>`;
      el.dataset.uid = it.uid;
      el.onpointerdown = e => startDrag(e, it, el);
      canvas.appendChild(el);
    });
    $('selbar').hidden = !selected;
  }

  // ---------- drag (pointer events = mouse + touch)
  function startDrag(e, it, el) {
    e.preventDefault(); selected = it.uid;
    canvas.querySelectorAll('.piece').forEach(n => n.classList.toggle('sel', n === el));
    $('selbar').hidden = false;
    el.setPointerCapture(e.pointerId);
    const move = ev => {
      const r = canvas.getBoundingClientRect();
      it.x = Math.min(0.97, Math.max(0.03, (ev.clientX - r.left) / r.width));
      it.y = Math.min(0.97, Math.max(0.03, (ev.clientY - r.top) / r.height));
      el.style.left = it.x * 100 + '%'; el.style.top = it.y * 100 + '%';
    };
    const up = () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); };
    el.addEventListener('pointermove', move); el.addEventListener('pointerup', up);
  }
  canvas.addEventListener('pointerdown', e => { if (e.target === canvas || e.target.id === 'floor-band') { selected = null; render(); } });
  canvas.addEventListener('wheel', e => {
    const it = room.items.find(i => i.uid === selected); if (!it) return;
    e.preventDefault(); it.scale = clamp(it.scale * (e.deltaY < 0 ? 1.08 : 0.92), 0.4, 2.5); render();
  }, { passive: false });
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  // ---------- selection toolbar
  $('selbar').onclick = e => {
    const act = e.target.dataset.act; const it = room.items.find(i => i.uid === selected); if (!act || !it) return;
    if (act === 'bigger') it.scale = clamp(it.scale * 1.15, 0.4, 2.5);
    if (act === 'smaller') it.scale = clamp(it.scale / 1.15, 0.4, 2.5);
    if (act === 'rotl') it.rot -= 15;
    if (act === 'rotr') it.rot += 15;
    if (act === 'front') { room.items = room.items.filter(i => i !== it).concat(it); }
    if (act === 'del') { room.items = room.items.filter(i => i !== it); selected = null; }
    render();
  };
  document.addEventListener('keydown', e => {
    if ((e.key === 'Delete' || e.key === 'Backspace') && selected && document.activeElement.tagName !== 'INPUT') {
      room.items = room.items.filter(i => i.uid !== selected); selected = null; render();
    }
  });

  // ---------- top toolbar
  $('wall').oninput = e => { room.wall = e.target.value; render(); };
  $('floor').oninput = e => { room.floor = e.target.value; render(); };
  $('reset').onclick = () => { if (confirm('Clear this room?')) { room = { id: uid(), name: 'My Room', wall: '#EFEAE2', floor: '#C9B79A', items: [] }; selected = null; render(); } };
  $('save').onclick = () => {
    if (!room.items.length) return alert('Add some furniture first.');
    const name = prompt('Room name', room.name); if (!name) return;
    room.name = name; room.style = RD.profile()?.primary || null;
    const rooms = RD.get('rd_rooms', []); const i = rooms.findIndex(r => r.id === room.id);
    i >= 0 ? rooms[i] = room : rooms.push(room); RD.set('rd_rooms', rooms);
    if (confirm('Saved! Open My Rooms?')) location.href = '/rooms';
  };

  // ---------- picker (recommendations first)
  let items = Object.values(cat), pcat = '';
  const p = RD.profile();
  if (p) items = await (await fetch('/api/recommend?' + new URLSearchParams({ primary: p.primary, secondary: p.secondary, budget: p.budget }))).json();
  function renderPicker() {
    const cats = ['', ...new Set(items.map(i => i.category))];
    $('pcats').innerHTML = cats.map(c => `<button class="chipbtn ${c === pcat ? 'on' : ''}" data-c="${c}">${c || 'All'}</button>`).join('');
    $('pcats').querySelectorAll('button').forEach(b => b.onclick = () => { pcat = b.dataset.c; renderPicker(); });
    $('pgrid').innerHTML = items.filter(i => !pcat || i.category === pcat).map(i =>
      `<button class="pitem" data-id="${i.id}"><div class="pthumb" style="background:${i.color}">${i.icon}</div><span>${i.name}</span><small>$${Math.round(i.price)}</small></button>`).join('');
    $('pgrid').querySelectorAll('button').forEach(b => b.onclick = () => addItem(b.dataset.id));
  }
  function addItem(fid) {
    const it = { uid: uid(), fid, x: 0.5, y: 0.45, scale: 1, rot: 0 };
    room.items.push(it); selected = it.uid; render();
  }
  renderPicker();
  if (params.get('add') && cat[params.get('add')]) addItem(params.get('add'));
  render();
})();
