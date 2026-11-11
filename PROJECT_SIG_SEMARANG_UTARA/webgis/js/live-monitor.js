/* ==========================================================================
   SEMARANG FLOOD & ROB GIS — NEAR-REALTIME MONITORING CLIENT
   Polls the FastAPI monitoring endpoint when available and falls back to a
   clearly-labelled deterministic simulation for static hosting/demo use.
   ========================================================================== */
(function () {
  'use strict';

  const params = new URLSearchParams(location.search);
  const apiParam = params.get('api');
  const STATIC_PORTS = ['8765', '5500', '3000', '8080', '8081'];
  const API_ENABLED = apiParam !== null ? apiParam !== '0' : !STATIC_PORTS.includes(location.port);
  const API_BASE = (window.APP_CONFIG && window.APP_CONFIG.apiBase) || '';
  const DEFAULT_POLL_SECONDS = 30;

  const state = {
    status: null,
    history: null,
    apiConnected: false,
    lastSync: null,
    showSimulation: localStorage.getItem('simShow') === '1'
  };

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  const MODES = {
    live: { label: 'LIVE', className: 'is-live', note: 'Data observasi nyata diperbarui dalam 30 menit terakhir.' },
    hybrid: { label: 'HYBRID', className: 'is-hybrid', note: 'Sebagian data berasal dari observasi, sebagian simulasi.' },
    stale: { label: 'TERAKHIR', className: 'is-stale', note: 'Observasi terakhir sudah melewati jendela realtime.' },
    demo: { label: 'SIMULASI', className: 'is-demo', note: 'Belum ada observasi lapangan; nilai ditampilkan sebagai simulasi.' },
    'demo-local': { label: 'SIMULASI LOKAL', className: 'is-demo', note: 'Backend monitoring belum terhubung; nilai dihasilkan secara lokal untuk demonstrasi.' }
  };

  function demoValue(parameter, moment) {
    const epoch = moment.getTime() / 1000;
    if (parameter === 'tide_level') {
      return Math.max(0.2, 1.36 + 0.42 * Math.sin(2 * Math.PI * epoch / 43200) + 0.08 * Math.sin(2 * Math.PI * epoch / 21600));
    }
    if (parameter === 'water_level') {
      return Math.max(0, 44 + 27 * Math.sin(2 * Math.PI * epoch / 43200 + 0.62) + 9 * Math.sin(2 * Math.PI * epoch / 10800));
    }
    return Math.max(0, 6.5 + 11.5 * Math.sin(2 * Math.PI * epoch / 21600 + 1.15) + 3.2 * Math.sin(2 * Math.PI * epoch / 3600));
  }

  function classify(parameter, value) {
    if (parameter === 'tide_level') return value >= 1.9 ? 'kritis' : value >= 1.7 ? 'waspada' : 'normal';
    if (parameter === 'water_level') return value >= 80 ? 'kritis' : value >= 60 ? 'waspada' : 'normal';
    return value >= 20 ? 'kritis' : value >= 10 ? 'waspada' : 'normal';
  }

  function localDemo() {
    const now = new Date();
    const readings = {
      tide_level: { label: 'Muka air laut', unit: 'm', station: 'Simulasi lokal · bukan sensor', decimals: 2 },
      water_level: { label: 'Muka air sungai', unit: 'cm', station: 'Simulasi lokal · bukan sensor', decimals: 1 },
      rainfall: { label: 'Curah hujan', unit: 'mm/jam', station: 'Simulasi lokal · bukan sensor', decimals: 1 }
    };
    Object.keys(readings).forEach(key => {
      const reading = readings[key];
      reading.value = Number(demoValue(key, now).toFixed(reading.decimals));
      reading.status = classify(key, reading.value);
      reading.source = 'simulasi lokal';
      reading.source_type = 'simulation';
      reading.is_live = false;
      reading.confidence = 'low';
      reading.confidence_label = 'Rendah';
    });

    const history = { series: {} };
    Object.keys(readings).forEach(key => {
      const series = [];
      for (let i = 48; i >= 0; i--) {
        const moment = new Date(now.getTime() - i * 30 * 60 * 1000);
        series.push({ t: moment.toISOString(), v: Number(demoValue(key, moment).toFixed(readings[key].decimals)) });
      }
      history.series[key] = series;
    });

    return {
      status: {
        mode: 'demo-local',
        is_live: false,
        generated_at: now.toISOString(),
        last_update: now.toISOString(),
        refresh_interval_seconds: DEFAULT_POLL_SECONDS,
        source: 'Simulasi lokal di browser',
        note: MODES['demo-local'].note,
        observation_count: 0,
        readings,
        data_health: {
          overall: 'offline',
          mode: 'demo-local',
          checked_at: now.toISOString(),
          open_meteo: { status: 'unavailable', fetched_at: null, provider: null },
          petabencana: { status: 'unavailable', fetched_at: null, count: 0, period_days: 7 },
          local_sensor: { water_level: 'missing' },
          observation_count: 0,
          simulation_parameters: Object.keys(readings),
          stale_parameters: [],
          warnings: ['Backend monitoring tidak terhubung', 'Semua nilai adalah simulasi lokal']
        },
        current_condition: {
          level: 'unknown',
          headline: 'Status realtime belum tersedia',
          detail: 'Backend monitoring tidak terhubung. Data tematik tetap snapshot analisis, bukan kejadian saat ini.',
          updated_at: now.toISOString()
        }
      },
      history
    };
  }

  async function fetchJson(path, timeout = 3500) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(API_BASE + path, { signal: controller.signal, cache: 'no-store' });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return await response.json();
    } finally {
      clearTimeout(timer);
    }
  }

  function formatNumber(value, decimals) {
    return Number(value).toLocaleString('id-ID', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  }

  function relativeTime(isoString) {
    if (!isoString) return 'belum tersedia';
    const then = new Date(isoString).getTime();
    if (Number.isNaN(then)) return 'belum tersedia';
    const seconds = Math.max(0, Math.round((Date.now() - then) / 1000));
    if (seconds < 10) return 'baru saja';
    if (seconds < 60) return `${seconds} detik lalu`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} menit lalu`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} jam lalu`;
    return `${Math.floor(hours / 24)} hari lalu`;
  }

  function modeInfo(mode) {
    return MODES[mode] || MODES.demo;
  }

  function statusColor(status) {
    if (status === 'kritis') return '#ef4444';
    if (status === 'waspada') return '#f59e0b';
    return '#22c55e';
  }

  function sparkline(svg, points, color) {
    if (!svg || !points || !points.length) return;
    const width = 120;
    const height = 32;
    const pad = 2;
    const values = points.map(p => Number(p.v));
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    const step = (width - pad * 2) / Math.max(1, values.length - 1);
    const coords = values.map((value, index) => {
      const x = pad + index * step;
      const y = pad + (height - pad * 2) * (1 - (value - min) / span);
      return [x, y];
    });
    const line = coords.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const area = `${pad},${height - pad} ${line} ${width - pad},${height - pad}`;
    svg.innerHTML = `
      <polygon points="${area}" fill="${color}" opacity="0.10"></polygon>
      <polyline points="${line}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
      <circle cx="${coords[coords.length - 1][0].toFixed(1)}" cy="${coords[coords.length - 1][1].toFixed(1)}" r="2.3" fill="${color}"></circle>`;
  }

  function render(data, apiConnected) {
    state.status = data.status;
    state.history = data.history;
    state.apiConnected = apiConnected;
    state.lastSync = new Date();

    const info = modeInfo(data.status.mode);
    const root = document;
    const modeLabel = $('[data-live-mode-label]', root);
    if (modeLabel) modeLabel.textContent = info.label;
    $$('[data-live-mode]', root).forEach(el => {
      el.textContent = info.label;
      el.classList.remove('is-live', 'is-hybrid', 'is-stale', 'is-demo');
      el.classList.add(info.className);
    });
    $$('[data-live-dot]', root).forEach(el => {
      el.classList.remove('is-live', 'is-hybrid', 'is-stale', 'is-demo');
      el.classList.add(info.className);
    });
    $$('[data-live-source]', root).forEach(el => { el.textContent = data.status.source; });
    $$('[data-live-note]', root).forEach(el => { el.textContent = data.status.note; });
    $$('[data-live-count]', root).forEach(el => { el.textContent = String(data.status.observation_count); });
    $$('[data-live-updated]', root).forEach(el => {
      el.textContent = relativeTime(data.status.last_update);
      el.setAttribute('title', new Date(data.status.last_update).toLocaleString('id-ID'));
    });

    Object.entries(data.status.readings || {}).forEach(([key, reading]) => {
      const simulated = reading.source_type === 'simulation';
      const visible = !simulated || state.showSimulation;
      $$(`[data-live-value="${key}"]`, root).forEach(el => {
        el.textContent = visible ? formatNumber(reading.value, reading.decimals) : '—';
      });
      $$(`[data-live-unit="${key}"]`, root).forEach(el => { el.textContent = visible ? reading.unit : ''; });
      $$(`[data-live-station="${key}"]`, root).forEach(el => {
        el.textContent = visible ? reading.station : 'Belum ada sensor TMA — simulasi disembunyikan';
      });
      $$(`[data-live-status="${key}"]`, root).forEach(el => {
        const label = simulated && !state.showSimulation
          ? 'Belum tersedia'
          : simulated
            ? 'Simulasi'
            : reading.status === 'normal'
              ? 'Normal'
              : reading.status === 'waspada'
                ? 'Waspada'
                : reading.status === 'kritis'
                  ? 'Kritis'
                  : 'Belum terkalibrasi';
        el.textContent = label;
        const cls = simulated && !state.showSimulation ? 'unavailable' : simulated ? 'simulation' : reading.status;
        el.classList.remove('is-normal', 'is-waspada', 'is-kritis', 'is-simulation', 'is-unavailable', 'is-uncalibrated');
        el.classList.add('is-' + cls);
      });
      $$(`[data-live-card="${key}"]`, root).forEach(el => {
        const cls = simulated && !state.showSimulation ? 'unavailable' : simulated ? 'simulation' : reading.status;
        el.classList.remove('is-normal', 'is-waspada', 'is-kritis', 'is-simulation', 'is-unavailable', 'is-uncalibrated');
        el.classList.add('is-' + cls);
        const station = el.querySelector('[data-live-station]');
        if (station) {
          const text = visible ? reading.station : 'Belum ada sensor TMA — simulasi disembunyikan';
          station.innerHTML = '';
          station.append(document.createTextNode(text + ' '));
          const chip = document.createElement('span');
          chip.className = 'confidence-chip is-' + (reading.confidence || 'low');
          chip.textContent = 'Keyakinan: ' + (reading.confidence_label || 'Rendah');
          chip.title = reading.source_type === 'observation'
            ? 'Observasi lapangan/sensor'
            : reading.source_type === 'external'
              ? 'Model eksternal, bukan sensor lokal'
              : 'Nilai simulasi — bukan data pengukuran';
          station.appendChild(chip);
        }
      });
    });

    if (data.history && data.history.series) {
      Object.entries(data.history.series).forEach(([key, points]) => {
        const svg = $(`[data-live-spark="${key}"]`, root);
        const reading = data.status.readings[key];
        if (svg && reading) {
          const hide = reading.source_type === 'simulation' && !state.showSimulation;
          svg.style.opacity = hide ? '0.18' : '1';
          if (hide) svg.innerHTML = '';
          else sparkline(svg, points, reading.source_type === 'simulation' ? '#94a3b8' : statusColor(reading.status));
        }
      });
    }

    const condition = data.status.current_condition || {
      level: 'unknown',
      headline: 'Status realtime belum tersedia',
      detail: 'Sumber eksternal belum terhubung.',
      updated_at: null
    };
    $$('[data-condition-banner]', root).forEach(el => {
      el.classList.remove('is-normal', 'is-waspada', 'is-kritis', 'is-unknown');
      el.classList.add('is-' + (condition.level || 'unknown'));
    });
    $$('[data-condition-headline]', root).forEach(el => { el.textContent = condition.headline; });
    $$('[data-condition-detail]', root).forEach(el => { el.textContent = condition.detail; });
    $$('[data-condition-updated]', root).forEach(el => { el.textContent = relativeTime(condition.updated_at); });
    $$('[data-condition-icon]', root).forEach(el => {
      const level = condition.level || 'unknown';
      const icon = level === 'kritis' ? 'fa-circle-exclamation' : level === 'waspada' ? 'fa-triangle-exclamation' : level === 'normal' ? 'fa-shield-heart' : 'fa-circle-question';
      el.className = 'fa-solid ' + icon;
    });

    const health = data.status.data_health;
    $$('[data-data-health]', root).forEach(el => {
      if (!health) {
        el.className = 'data-health is-offline';
        el.textContent = 'Kesehatan data: belum tersedia';
        return;
      }
      el.className = 'data-health is-' + (health.overall || 'degraded');
      const chip = (label, status) => {
        const stateClass = status === 'ok' ? 'is-ok' : status === 'missing' ? 'is-missing' : 'is-warn';
        return `<span class="health-chip ${stateClass}">${label}</span>`;
      };
      const warning = (health.warnings || []).slice(0, 2).join(' · ');
      el.innerHTML = `<span class="health-title"><i class="fa-solid fa-heart-pulse me-1"></i>Kesehatan data</span>`
        + chip('Open-Meteo', health.open_meteo ? health.open_meteo.status : 'unavailable')
        + chip('PetaBencana', health.petabencana ? health.petabencana.status : 'unavailable')
        + chip('Sensor TMA', health.local_sensor && health.local_sensor.water_level === 'missing' ? 'missing' : 'ok')
        + (warning ? `<span class="health-warning">${warning}</span>` : '');
    });

    const thresholds = data.status.thresholds;
    $$('[data-threshold-table]', root).forEach(el => {
      if (!thresholds) { el.textContent = 'Ambang belum tersedia.'; return; }
      const params = thresholds.parameters || {};
      const rows = Object.entries(params).map(([key, item]) => {
        const warning = item.warning == null ? 'Belum ditetapkan' : formatNumber(item.warning, key === 'tide_level' ? 2 : 1) + ' ' + item.unit;
        const critical = item.critical == null ? 'Belum ditetapkan' : formatNumber(item.critical, key === 'tide_level' ? 2 : 1) + ' ' + item.unit;
        const cal = (item.warning == null || item.critical == null)
          ? '<span class="badge bg-light text-dark border">Belum ditetapkan</span>'
          : item.calibration_type === 'model_percentile'
            ? '<span class="badge badge-info-soft">Anomali model</span>'
            : item.calibrated
              ? '<span class="badge badge-success-soft">Terkalibrasi</span>'
              : '<span class="badge badge-warning-soft">Indikatif</span>';
        return `<tr><td><b>${item.label}</b><div class="small text-muted">${item.basis || '-'}</div></td><td>${warning}</td><td>${critical}</td><td>${item.source || '-'}<br>${cal}</td></tr>`;
      }).join('');
      el.innerHTML = `<div class="table-responsive"><table class="table table-sm align-middle mb-2"><thead><tr><th>Parameter</th><th>Waspada</th><th>Kritis</th><th>Sumber / status</th></tr></thead><tbody>${rows}</tbody></table></div><p class="small text-muted mb-0">Versi ${thresholds.version || '-'} · ditinjau ${thresholds.reviewed_at || '-'} · ${thresholds.method || ''}</p>`;
    });

    $$('[data-toggle-simulation]', root).forEach(btn => {
      btn.setAttribute('aria-pressed', state.showSimulation ? 'true' : 'false');
      btn.innerHTML = state.showSimulation
        ? '<i class="fa-solid fa-eye-slash me-1"></i>Sembunyikan simulasi'
        : '<i class="fa-solid fa-eye me-1"></i>Tampilkan simulasi';
    });

    const external = data.status.external_data || {};
    const setExtra = (key, text, title) => {
      $$(`[data-live-extra="${key}"]`, root).forEach(el => {
        el.textContent = text;
        if (title) el.setAttribute('title', title);
      });
    };
    setExtra('river_discharge',
      external.river_discharge ? formatNumber(external.river_discharge.value, 2) : '—',
      external.river_discharge ? 'Open-Meteo Flood API (GloFAS) · model debit sungai' : 'Data debit sungai belum tersedia');
    setExtra('wave_height',
      external.wave_height && external.wave_height.value != null ? formatNumber(external.wave_height.value, 2) : '—',
      'Open-Meteo Marine API · tinggi gelombang model');
    const citizen = external.citizen_reports;
    setExtra('citizen_reports',
      citizen && citizen.status === 'connected' ? String(citizen.count) : '—',
      citizen ? `PetaBencana.id · ${citizen.period_days || 7} hari terakhir` : 'Laporan warga belum tersedia');

    $$('[data-live-refresh]', root).forEach(btn => btn.classList.remove('is-loading'));

    document.dispatchEvent(new CustomEvent('live:update', { detail: { ...state } }));
  }

  async function load(manual = false) {
    if (manual) $$('[data-live-refresh]').forEach(btn => btn.classList.add('is-loading'));

    if (API_ENABLED) {
      try {
        const [status, history] = await Promise.all([
          fetchJson('/api/monitoring/status'),
          fetchJson('/api/monitoring/history?hours=24')
        ]);
        render({ status, history }, true);
        schedule((status.refresh_interval_seconds || DEFAULT_POLL_SECONDS) * 1000);
        return;
      } catch (error) {
        // Static hosting or backend offline: fall back to a transparent local simulation.
        if (manual && window.appToast) {
          window.appToast('Backend monitoring belum terhubung. Mode simulasi lokal aktif.', 'fa-triangle-exclamation');
        }
      }
    }

    const fallback = localDemo();
    render(fallback, false);
    schedule(DEFAULT_POLL_SECONDS * 1000);
  }

  let timer = null;
  function schedule(delay) {
    clearTimeout(timer);
    timer = setTimeout(() => load(false), delay);
  }

  document.addEventListener('click', event => {
    if (event.target.closest('[data-live-refresh]')) load(true);
    if (event.target.closest('[data-toggle-simulation]')) {
      state.showSimulation = !state.showSimulation;
      localStorage.setItem('simShow', state.showSimulation ? '1' : '0');
      if (state.status) render({ status: state.status, history: state.history }, state.apiConnected);
    }
  });

  window.addEventListener('online', () => load(false));
  window.addEventListener('offline', () => {
    const fallback = localDemo();
    fallback.status.note = 'Perangkat offline. Nilai simulasi lokal ditampilkan.';
    render(fallback, false);
  });

  setInterval(() => {
    if (!state.status) return;
    $$('[data-live-updated]').forEach(el => {
      el.textContent = relativeTime(state.status.last_update);
    });
  }, 15000);

  window.LiveMonitor = {
    refresh: () => load(true),
    getState: () => state,
    isApiEnabled: API_ENABLED
  };

  load(false);
})();
