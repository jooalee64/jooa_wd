// Shared helpers. Profile, favorites and rooms live in the browser's localStorage
// (per-user, no database). The catalog + recommendations come from the Python API.
const RD = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? d; } catch { return d; } },
  set(k, v) { localStorage.setItem(k, JSON.stringify(v)); },
  profile() { return this.get('rd_profile', null); },
  favs() { return this.get('rd_favs', []); },
  toggleFav(id) {
    const f = this.favs(); const i = f.indexOf(id);
    i >= 0 ? f.splice(i, 1) : f.push(id); this.set('rd_favs', f);
  },
  _cat: null,
  async catalog() {
    if (!this._cat) {
      const list = await (await fetch('/api/catalog')).json();
      this._cat = Object.fromEntries(list.map(i => [i.id, i]));
    }
    return this._cat;
  },
  cardHTML(i) {
    return `<div class="card"><a href="/item/${i.id}"><div class="thumb" style="background:${i.color}"><span>${i.icon}</span></div></a>
      <button class="heart" data-fav="${i.id}">♡</button><div class="brand">${i.brand.toUpperCase()}</div>
      <a class="name" href="/item/${i.id}">${i.name}</a>
      <div class="price">$${Math.round(i.price)} <span class="tier">${i.tier}</span></div></div>`;
  },
  initHearts(root = document) {
    const paint = b => { const on = this.favs().includes(b.dataset.fav); b.textContent = on ? '♥' : '♡'; b.classList.toggle('on', on); };
    root.querySelectorAll('.heart').forEach(b => { paint(b); b.onclick = () => { this.toggleFav(b.dataset.fav); paint(b); }; });
  },
};
