/* ══════════════════════════════════════════════════════════════════════════
   AMS Test Console — Auth / Role Switcher
   ══════════════════════════════════════════════════════════════════════════ */

const DEFAULT_USERS = [
    { label: 'Test Admin',    email: 'admin@ams.edu',    password: 'TestPass123!', expectedRole: 'admin',    hint: 'Must be seeded in DB — no self-register for admins' },
    { label: 'Test Lecturer', email: 'lecturer@ams.edu', password: 'TestPass123!', expectedRole: 'lecturer', hint: 'Self-registers via /auth/register/lecturer' },
    { label: 'Test Student',  email: 'student@ams.edu',  password: 'TestPass123!', expectedRole: 'student',  hint: 'Self-registers via /auth/register/student' },
    { label: 'Test HOD',      email: 'hod@ams.edu',      password: 'TestPass123!', expectedRole: 'hod',      hint: 'Register as lecturer, then admin assigns HOD' },
];

const auth = {
    STORAGE_KEY: 'ams_saved_roles',
    ACTIVE_KEY:  'ams_active_role',

    getSavedRoles() {
        let roles = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
        // Auto-cleanup corrupted roles from previous bug
        if (roles.some(r => !r.role || r.role === 'undefined')) {
            roles = roles.filter(r => r.role && r.role !== 'undefined');
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(roles));
        }
        return roles;
    },
    saveSavedRoles(r) { localStorage.setItem(this.STORAGE_KEY, JSON.stringify(r)); },
    getActiveRole()   { return JSON.parse(localStorage.getItem(this.ACTIVE_KEY) || 'null'); },
    setActiveRole(r)  { localStorage.setItem(this.ACTIVE_KEY, JSON.stringify(r)); },
    clearActiveRole() { localStorage.removeItem(this.ACTIVE_KEY); },

    async login(email, password, label, expectedRole) {
        const data = await api.post('/auth/login', { email, password });
        // Temporarily set token to fetch /me
        const tmp = { access_token: data.access_token };
        localStorage.setItem(this.ACTIVE_KEY, JSON.stringify(tmp));

        let user;
        try { user = await api.get('/auth/me'); }
        catch (e) { this.clearActiveRole(); throw e; }

        let primaryRole = 'unknown';
        if (user.roles && user.roles.length > 0) {
            if (expectedRole && user.roles.includes(expectedRole)) {
                primaryRole = expectedRole;
            } else if (user.roles.includes('admin')) {
                primaryRole = 'admin';
            } else if (user.roles.includes('hod')) {
                primaryRole = 'hod';
            } else {
                primaryRole = user.roles[0];
            }
        }

        const role = {
            label: label || `${user.first_name} ${user.last_name}`,
            email, role: primaryRole, user_id: user.id,
            first_name: user.first_name, last_name: user.last_name,
            access_token: data.access_token, refresh_token: data.refresh_token,
            department: user.department,
            all_roles: user.roles
        };

        const roles = this.getSavedRoles().filter(r => r.email !== email);
        roles.push(role);
        this.saveSavedRoles(roles);
        this.setActiveRole(role);
        return role;
    },

    switchTo(email) {
        const r = this.getSavedRoles().find(r => r.email === email);
        if (!r) return;
        this.setActiveRole(r);
        this.renderRoleList();
        this.renderSessionCard();
        this.renderHeaderBadge();
        showToast(`Switched to ${r.label} (${r.role})`, 'success');
        // Fire custom event so pages can react
        window.dispatchEvent(new CustomEvent('roleChanged', { detail: r }));
    },

    removeRole(email) {
        this.saveSavedRoles(this.getSavedRoles().filter(r => r.email !== email));
        const a = this.getActiveRole();
        if (a && a.email === email) this.clearActiveRole();
        this.renderRoleList();
        this.renderSessionCard();
        this.renderHeaderBadge();
    },

    /* ── Render: role list in sidebar ── */
    renderRoleList() {
        const c = document.getElementById('saved-roles');
        if (!c) return;
        const roles = this.getSavedRoles();
        const active = this.getActiveRole();

        if (!roles.length) {
            c.innerHTML = '<div style="font-size:.72rem;color:var(--text-dim);padding:4px;">No saved roles yet.</div>';
            return;
        }

        c.innerHTML = roles.map(r => `
            <div class="role-item ${active && active.email === r.email ? 'active' : ''}" data-email="${r.email}">
                <div class="ri-info">
                    <div class="ri-label">${r.label}</div>
                    <div class="ri-email">${r.email}</div>
                    <div style="margin-top:4px"><input type="text" readonly value="${r.access_token || ''}" style="font-size:0.65rem; padding:2px 4px; border:1px solid var(--border); border-radius:3px; width:90px; background:var(--surface1); color:var(--text-dim); cursor:copy;" onclick="event.stopPropagation(); this.select(); document.execCommand('copy'); showToast('Token copied', 'success');" title="Click to copy token"></div>
                </div>
                <div class="ri-right">
                    <span class="badge ${r.role}">${r.role}</span>
                    <span class="ri-remove" data-rm="${r.email}" title="Remove">✕</span>
                </div>
            </div>`).join('');

        c.querySelectorAll('.role-item').forEach(el => {
            el.addEventListener('click', e => {
                if (e.target.classList.contains('ri-remove')) return;
                auth.switchTo(el.dataset.email);
            });
        });
        c.querySelectorAll('.ri-remove').forEach(el => {
            el.addEventListener('click', e => { e.stopPropagation(); auth.removeRole(el.dataset.rm); });
        });
    },

    /* ── Render: session card ── */
    renderSessionCard() {
        const card = document.getElementById('session-card');
        if (!card) return;
        const a = this.getActiveRole();
        if (!a) { card.classList.add('hidden'); return; }
        card.classList.remove('hidden');
        const el = (id) => document.getElementById(id);
        el('session-user').textContent = a.label;
        const b = el('session-role');
        b.textContent = a.role;
        b.className = 'mono badge ' + a.role;
        el('session-id').textContent = a.user_id;
        if (a.department) el('session-dept').textContent = a.department.name || '—';
        else el('session-dept').textContent = '—';
        const t = el('session-token');
        if (t) t.value = a.access_token || '';
    },

    /* ── Render: header badge on sub-pages ── */
    renderHeaderBadge() {
        const badge = document.getElementById('hdr-role-badge');
        const name  = document.getElementById('hdr-role-name');
        if (!badge || !name) return;
        const a = this.getActiveRole();
        if (a) {
            badge.textContent = a.role;
            badge.className = 'badge ' + a.role;
            badge.style.display = '';
            name.textContent = a.label;
        } else {
            badge.style.display = 'none';
            name.textContent = 'not logged in';
        }
    },

    /* ── Render: default user quick-login buttons ── */
    renderDefaults() {
        const c = document.getElementById('default-users');
        if (!c) return;
        c.innerHTML = DEFAULT_USERS.map(u => `
            <div class="role-item" data-demail="${u.email}" title="${u.hint}">
                <div class="ri-info">
                    <div class="ri-label">${u.label}</div>
                    <div class="ri-email">${u.email}</div>
                </div>
                <div class="ri-right">
                    <span class="badge ${u.expectedRole}">${u.expectedRole}</span>
                </div>
            </div>`).join('');

        c.querySelectorAll('.role-item').forEach(el => {
            el.addEventListener('click', async () => {
                const u = DEFAULT_USERS.find(d => d.email === el.dataset.demail);
                if (!u) return;
                el.style.opacity = '.4';
                try {
                    await auth.login(u.email, u.password, u.label, u.expectedRole);
                    auth.renderRoleList();
                    auth.renderSessionCard();
                    auth.renderHeaderBadge();
                    showToast(`✓ Logged in as ${u.label}`, 'success');
                } catch (e) {
                    showToast(`Login failed for ${u.email}: ${e.message}. Try registering first.`, 'error');
                } finally {
                    el.style.opacity = '';
                }
            });
        });
    },
};

/* ── DOM bindings ── */
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    const btn = document.getElementById('btn-login');
    if (btn) {
        btn.addEventListener('click', async () => {
            const email = document.getElementById('login-email')?.value.trim();
            const pwd   = document.getElementById('login-password')?.value;
            const lbl   = document.getElementById('login-label')?.value.trim();
            if (!email || !pwd) { setOutput('login-output', 'Email and password required.', true); return; }
            btn.disabled = true; btn.textContent = 'Logging in…';
            try {
                const r = await auth.login(email, pwd, lbl);
                setOutput('login-output', `✓ ${r.label} (${r.role})`);
                auth.renderRoleList(); auth.renderSessionCard(); auth.renderHeaderBadge();
                showToast(`Logged in as ${r.label}`, 'success');
                document.getElementById('login-email').value = '';
                document.getElementById('login-password').value = '';
                document.getElementById('login-label').value = '';
            } catch (e) {
                setOutput('login-output', 'Failed: ' + e.message, true);
                showToast('Login failed: ' + e.message, 'error');
            } finally { btn.disabled = false; btn.textContent = 'Login & Save'; }
        });
    }
    // Logout
    document.getElementById('btn-logout')?.addEventListener('click', () => {
        auth.clearActiveRole(); auth.renderRoleList(); auth.renderSessionCard(); auth.renderHeaderBadge();
        window.dispatchEvent(new CustomEvent('roleChanged'));
        showToast('Logged out');
    });
});

// ── Sync across tabs ──
window.addEventListener('storage', (e) => {
    if (e.key === auth.ACTIVE_KEY || e.key === auth.STORAGE_KEY) {
        if (typeof auth !== 'undefined') {
            auth.renderRoleList();
            auth.renderSessionCard();
            auth.renderHeaderBadge();
            const r = auth.getActiveRole();
            window.dispatchEvent(new CustomEvent('roleChanged', { detail: r }));
        }
    }
});
