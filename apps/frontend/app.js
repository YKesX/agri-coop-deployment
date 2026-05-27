const API_BASE = '/api/v1';

const DEMO_DATA = {
  farmers: [
    { id: 'F001', name: 'Ahmet Yilmaz', village: 'Harran', joined_date: '2024-04-01' },
    { id: 'F002', name: 'Mehmet Demir', village: 'Bozova', joined_date: '2024-04-01' },
    { id: 'F003', name: 'Ali Kaya', village: 'Siverek', joined_date: '2024-04-02' },
  ],
  villages: [
    { id: 1, name: 'Harran', farmer_count: 2 },
    { id: 2, name: 'Bozova', farmer_count: 2 },
    { id: 3, name: 'Siverek', farmer_count: 2 },
  ],
  crops: [
    { id: 1, name: 'cotton', current_price_usd_per_kg: 42.5, price_updated_at: new Date().toISOString() },
    { id: 2, name: 'wheat', current_price_usd_per_kg: 18.3, price_updated_at: new Date().toISOString() },
    { id: 3, name: 'pistachio', current_price_usd_per_kg: 210.0, price_updated_at: new Date().toISOString() },
  ],
  alerts: [
    { id: 1, type: 'weather', severity: 'warning', message: 'Low soil moisture detected on Farm 3', farm_id: 3, created_at: new Date(Date.now() - 18000000).toISOString(), resolved_at: null },
    { id: 2, type: 'weather', severity: 'critical', message: 'Soil moisture critically low on Farm 9', farm_id: 9, created_at: new Date(Date.now() - 7200000).toISOString(), resolved_at: null },
  ],
  sensorsLatest: [
    { farm_id: 1, farmer_name: 'Ahmet Yilmaz', reading_time: new Date().toISOString(), temperature_c: 28.4, humidity_pct: 55, soil_moisture_pct: 42 },
  ],
  yieldByVillage: [
    { village: 'Harran', total_yield_kg: 8500, total_hectares: 24.0 },
    { village: 'Bozova', total_yield_kg: 5000, total_hectares: 14.0 },
    { village: 'Siverek', total_yield_kg: 6500, total_hectares: 19.5 },
  ],
  readings: [
    { id: 1, farm_id: 1, reading_time: new Date(Date.now() - 7200000).toISOString(), temperature_c: 28, humidity_pct: 55, soil_moisture_pct: 44 },
    { id: 2, farm_id: 1, reading_time: new Date(Date.now() - 3600000).toISOString(), temperature_c: 29, humidity_pct: 53, soil_moisture_pct: 42 },
    { id: 3, farm_id: 1, reading_time: new Date().toISOString(), temperature_c: 30, humidity_pct: 50, soil_moisture_pct: 40 },
  ],
};

async function apiFetch(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

// ── Chart module — completely outside Alpine ──
const MoistureChart = {
  instance: null,

  async render(farmId, demoMode) {
    const canvas = document.getElementById('moistureChart');
    if (!canvas) return;

    let readings;
    if (demoMode) {
      readings = DEMO_DATA.readings;
    } else {
      try {
        readings = await apiFetch(`/sensors/${farmId}/readings?limit=48`);
      } catch { return; }
    }

    const sorted = readings.slice().reverse();
    const labels = sorted.map(r => {
      const d = new Date(r.reading_time);
      return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    });
    const data = sorted.map(r => r.soil_moisture_pct);
    if (data.length === 0) return;

    const vals = data.filter(v => v != null);
    const lo = Math.min(...vals);
    const hi = Math.max(...vals);
    const pad = Math.max((hi - lo) * 0.4, 5);

    if (this.instance) { this.instance.destroy(); this.instance = null; }

    // Size canvas to parent
    const wrap = canvas.parentElement;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.width = wrap.clientWidth * (window.devicePixelRatio || 1);
    canvas.height = wrap.clientHeight * (window.devicePixelRatio || 1);

    const ctx = canvas.getContext('2d');
    ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

    this.instance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Soil Moisture %',
          data,
          borderColor: '#2d5016',
          backgroundColor: 'rgba(45,80,22,0.15)',
          fill: true,
          tension: 0.3,
          pointRadius: 2,
          pointBackgroundColor: '#2d5016',
          pointHoverRadius: 6,
          pointHoverBackgroundColor: '#2d5016',
          pointHoverBorderColor: '#fff',
          pointHoverBorderWidth: 2,
          borderWidth: 2.5,
        }],
      },
      options: {
        responsive: false,
        animation: { duration: 500 },
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a3409',
            titleFont: { size: 11 },
            bodyFont: { size: 13, weight: 'bold' },
            padding: 10,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              label: function(c) { return c.parsed.y.toFixed(1) + '% moisture'; }
            }
          },
        },
        scales: {
          y: {
            min: Math.floor(lo - pad),
            max: Math.ceil(hi + pad),
            title: { display: true, text: 'Moisture %', font: { size: 11, weight: '600' }, color: '#888' },
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { font: { size: 10 }, color: '#888' },
            border: { display: false },
          },
          x: {
            ticks: { maxRotation: 35, maxTicksLimit: 7, font: { size: 9 }, color: '#888' },
            grid: { display: false },
            border: { display: false },
          },
        },
      },
    });
  }
};

// Make it accessible from Alpine and the select's onchange
window.MoistureChart = MoistureChart;

// ── Alpine component ──
function dashboard() {
  return {
    demoMode: false,
    lastUpdated: '',
    stats: { totalFarmers: 0, totalHectares: 0, activeAlerts: 0, avgMoisture: 0 },
    crops: [],
    farms: [],
    selectedFarm: '',
    villageSummary: [],
    alerts: [],

    async init() {
      try {
        await apiFetch('/health');
        this.demoMode = false;
      } catch {
        this.demoMode = true;
      }
      await this.loadAll();
    },

    async loadAll() {
      try {
        const [farmers, villages, crops, alerts, latest, yields] = await Promise.all([
          this.fetch('/farmers?limit=200'),
          this.fetch('/villages'),
          this.fetch('/crops'),
          this.fetch('/alerts?resolved=false'),
          this.fetch('/sensors/latest'),
          this.fetch('/stats/yield-by-village'),
        ]);

        this.crops = crops;
        this.alerts = alerts;
        this.farms = latest;

        this.stats.totalFarmers = farmers.length;
        this.stats.activeAlerts = alerts.length;

        const totalHa = yields.reduce((s, v) => s + v.total_hectares, 0);
        this.stats.totalHectares = totalHa.toFixed(1);

        if (latest.length > 0) {
          const avgM = latest.reduce((s, r) => s + r.soil_moisture_pct, 0) / latest.length;
          this.stats.avgMoisture = avgM.toFixed(1);
        }

        this.villageSummary = yields.map(y => {
          const v = villages.find(vi => vi.name === y.village);
          return { ...y, farmer_count: v ? v.farmer_count : 0 };
        });

        if (latest.length > 0 && !this.selectedFarm) {
          this.selectedFarm = String(latest[0].farm_id);
        }

        this.lastUpdated = new Date().toLocaleTimeString();

        // Render chart outside Alpine's reactivity
        if (this.selectedFarm) {
          MoistureChart.render(this.selectedFarm, this.demoMode);
        }
      } catch (e) {
        console.error('Load error:', e);
      }
    },

    onFarmChange() {
      MoistureChart.render(this.selectedFarm, this.demoMode);
    },

    async fetch(path) {
      if (this.demoMode) return this.demoFetch(path);
      return apiFetch(path);
    },

    demoFetch(path) {
      if (path.startsWith('/farmers')) return DEMO_DATA.farmers;
      if (path.startsWith('/villages')) return DEMO_DATA.villages;
      if (path.startsWith('/crops')) return DEMO_DATA.crops;
      if (path.startsWith('/alerts')) return DEMO_DATA.alerts;
      if (path.startsWith('/sensors/latest')) return DEMO_DATA.sensorsLatest;
      if (path.startsWith('/sensors/')) return DEMO_DATA.readings;
      if (path.startsWith('/stats/yield')) return DEMO_DATA.yieldByVillage;
      return [];
    },

    async resolveAlert(id) {
      if (this.demoMode) {
        this.alerts = this.alerts.filter(a => a.id !== id);
        this.stats.activeAlerts = this.alerts.length;
        return;
      }
      try {
        await fetch(`${API_BASE}/alerts/${id}/resolve`, { method: 'POST' });
        this.alerts = this.alerts.filter(a => a.id !== id);
        this.stats.activeAlerts = this.alerts.length;
      } catch (e) {
        console.error('Resolve failed:', e);
      }
    },

    fmtNum(n) {
      return Number(n).toLocaleString();
    },

    timeAgo(iso) {
      const diff = Date.now() - new Date(iso).getTime();
      const mins = Math.floor(diff / 60000);
      if (mins < 1) return 'just now';
      if (mins < 60) return mins + 'm ago';
      const hrs = Math.floor(mins / 60);
      if (hrs < 24) return hrs + 'h ago';
      return Math.floor(hrs / 24) + 'd ago';
    },
  };
}
