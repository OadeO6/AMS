const Layout = {
    inject() {
        // Create header
        const header = document.createElement('header');
        header.innerHTML = `
            <div class="header-left">
                <span class="logo">▲ AMS</span>
                <span class="sep">/</span>
                <a href="${window.location.pathname.includes('/materials') ? '../' : ''}index.html" class="page-title">Console</a>
                <span class="sep">/</span>
                <span class="page-title current" id="layout-page-title">...</span>
            </div>
            <div class="header-right">
                <span id="health-dot" class="dot off" title="API offline"></span>
                <span id="api-url-show" class="mono" style="font-size:.72rem;color:var(--text-dim);margin-right:8px;">—</span>
                <span id="hdr-role-badge" class="badge" style="display:none"></span>
                <span id="hdr-role-name" class="mono" style="font-size:.72rem;color:var(--text-dim);margin-right:8px;">not logged in</span>
                <button class="theme-toggle" id="theme-btn" onclick="toggleTheme()">☀</button>
            </div>
        `;

        // Create main layout structure
        const sidebar = `
            <aside id="sidebar">
                <section class="card">
                    <h2>API Connection</h2>
                    <div class="field">
                        <label>Base URL</label>
                        <input type="text" id="api-url" value="http://localhost:8000/api/v1" spellcheck="false">
                    </div>
                    <button id="btn-health" class="btn btn-sm" style="width:100%">Check Health</button>
                    <pre id="health-output" class="output"></pre>
                </section>
                <section class="card">
                    <h2>Quick Login (Default Users)</h2>
                    <div class="role-list" id="default-users"></div>
                </section>
                <section class="card">
                    <h2>Saved Roles</h2>
                    <div class="role-list" id="saved-roles"></div>
                    <hr>
                    <details>
                        <summary>+ Add Custom Login</summary>
                        <div class="field"><label>Email</label><input type="text" id="login-email" spellcheck="false"></div>
                        <div class="field"><label>Password</label><input type="password" id="login-password"></div>
                        <div class="field"><label>Label <span class="hint">(opt)</span></label><input type="text" id="login-label" spellcheck="false"></div>
                        <button id="btn-login" class="btn btn-sm" style="width:100%">Login & Save</button>
                        <pre id="login-output" class="output"></pre>
                        <div style="margin-top: 16px; text-align: center; font-size: 0.8rem;">
                            Need a new account?<br>
                            <a href="#" onclick="window.location.href = window.location.pathname.includes('/test_pages/') ? window.location.pathname.split('/test_pages/')[0] + '/test_pages/register.html' : 'register.html'" style="color: var(--accent); text-decoration: underline;">Go to Registration Page</a>
                        </div>
                    </details>
                </section>
                <section class="card hidden" id="session-card">
                    <h2>Active Session</h2>
                    <div class="kv"><span>User</span><span id="session-user" class="mono">—</span></div>
                    <div class="kv"><span>Role</span><span id="session-role" class="mono badge">—</span></div>
                    <div class="kv"><span>Dept</span><span id="session-dept" class="mono">—</span></div>
                    <div class="kv"><span>ID</span><span id="session-id" class="mono truncate">—</span></div>
                    <button id="btn-logout" class="btn btn-sm btn-ghost" style="width:100%;margin-top:4px">Logout</button>
                </section>
            </aside>
        `;

        // We assume the page has <main> containing the specific content.
        // We will insert header before <main>
        const main = document.querySelector('main');
        if (main) {
            document.body.insertBefore(header, main);
            main.insertAdjacentHTML('afterbegin', sidebar);
            
            // Fix header title based on what was in the original header
            const oldHeader = document.querySelector('header.old-header');
            if (oldHeader) {
                const cur = oldHeader.querySelector('.current');
                if (cur) {
                    document.getElementById('layout-page-title').textContent = cur.textContent;
                }
                oldHeader.remove();
            } else {
                document.getElementById('layout-page-title').textContent = document.title;
            }
        }
    }
};
// Inject immediately before DOMContentLoaded so elements exist for other scripts
Layout.inject();

document.addEventListener('DOMContentLoaded', () => {
    // ── API URL ──
    const urlInput = document.getElementById('api-url');
    const urlShow  = document.getElementById('api-url-show');
    if (urlInput && urlShow) {
        function syncUrl() {
            api.baseUrl = urlInput.value;
            localStorage.setItem('ams_api_url', urlInput.value);
            urlShow.textContent = urlInput.value;
        }
        const savedUrl = localStorage.getItem('ams_api_url');
        if (savedUrl) { urlInput.value = savedUrl; api.baseUrl = savedUrl; }
        urlShow.textContent = urlInput.value;
        urlInput.addEventListener('input', syncUrl);
    }

    // ── Health Check ──
    const btnHealth = document.getElementById('btn-health');
    if (btnHealth) {
        btnHealth.addEventListener('click', async () => {
            const out = document.getElementById('health-output');
            const dot = document.getElementById('health-dot');
            out.textContent = 'Checking…';
            out.className = 'output';
            try {
                const r = await api.get('/healthz');
                out.textContent = JSON.stringify(r, null, 2);
                out.className = 'output success';
                dot.className = 'dot on';
                dot.title = 'API online';
            } catch (e) {
                out.textContent = 'ERROR: ' + e.message;
                out.className = 'output error';
                dot.className = 'dot off';
                dot.title = 'API offline';
            }
        });
    }

    // ── Init UI ──
    if (typeof auth !== 'undefined') {
        auth.renderDefaults();
        auth.renderRoleList();
        auth.renderSessionCard();
    }
    
    // Auto-check health on load
    if (btnHealth) {
        btnHealth.click();
    }
});
