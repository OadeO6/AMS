/* ══════════════════════════════════════════════════════════════════════════
   AMS Test Console — API Helper
   ══════════════════════════════════════════════════════════════════════════ */

const api = {
    baseUrl: localStorage.getItem('ams_api_url') || 'http://localhost:8000/api/v1',

    _getToken() {
        const a = JSON.parse(localStorage.getItem('ams_active_role') || 'null');
        return a ? a.access_token : null;
    },

    _headers(extra = {}) {
        const h = { ...extra };
        const t = this._getToken();
        if (t) h['Authorization'] = 'Bearer ' + t;
        return h;
    },

    async request(method, path, { body, formData, query } = {}) {
        let url = this.baseUrl + path;
        if (query) {
            const p = new URLSearchParams();
            for (const [k, v] of Object.entries(query)) {
                if (v !== undefined && v !== null && v !== '') p.set(k, v);
            }
            const qs = p.toString();
            if (qs) url += '?' + qs;
        }

        const opts = { method, headers: this._headers() };
        if (formData) {
            opts.body = formData;
        } else if (body) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }

        const res = await fetch(url, opts);
        const text = await res.text();
        let data;
        try { data = JSON.parse(text); } catch { data = text; }

        if (!res.ok) {
            const err = new Error(data?.detail || data?.message || `HTTP ${res.status}`);
            err.status = res.status;
            err.data = data;
            throw err;
        }
        return data;
    },

    get(p, q)  { return this.request('GET', p, { query: q }); },
    post(p, b) { return this.request('POST', p, { body: b }); },
    patch(p,b) { return this.request('PATCH', p, { body: b }); },
    del(p)     { return this.request('DELETE', p); },
    upload(p, fd) { return this.request('POST', p, { formData: fd }); },
};

/* ── Toast ── */
function showToast(msg, type = 'info') {
    let c = document.getElementById('toast-container');
    if (!c) { c = document.createElement('div'); c.id = 'toast-container'; document.body.appendChild(c); }
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = msg;
    c.appendChild(el);
    setTimeout(() => el.remove(), 3500);
}

/* ── Output helper ── */
function setOutput(id, text, isError = false) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = typeof text === 'string' ? text : JSON.stringify(text, null, 2);
    el.className = 'output' + (isError ? ' error' : ' success');
}

/* ── Theme ── */
function initTheme() {
    const saved = localStorage.getItem('ams_theme') || 'dark';
    document.documentElement.dataset.theme = saved;
    updateThemeBtn();
}
function toggleTheme() {
    const cur = document.documentElement.dataset.theme;
    const next = cur === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('ams_theme', next);
    updateThemeBtn();
}
function updateThemeBtn() {
    const btn = document.getElementById('theme-btn');
    if (!btn) return;
    btn.textContent = document.documentElement.dataset.theme === 'dark' ? '☀ Light' : '🌙 Dark';
}
initTheme();
