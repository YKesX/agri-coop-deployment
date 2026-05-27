const API_BASE = '/api/v1';

const DEMO_DATA = {
  health: { status: 'ok', db: 'degraded', version: 'demo' },
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
    { id: 1, type: 'weather', severity: 'warning', message: 'Low soil moisture detected on Farm 3', farm_id: 3, created_at: new Date().toISOString(), resolved_at: null },
    { id: 2, type: 'weather', severity: 'critical', message: 'Soil moisture critically low on Farm 9', farm_id: 9, created_at: new Date().toISOString(), resolved_at: null },
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
    { id: 1, farm_id: 1, reading_time: new Date(Date.now() - 3600000).toISOString(), temperature_c: 28, humidity_pct: 55, soil_moisture_pct: 42 },
    { id: 2, farm_id: 1, reading_time: new Date().toISOString(), temperature_c: 29, humidity_pct: 53, soil_moisture_pct: 40 },
  ],
};

async function apiFetch(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

function dashboard() {
  return {
    demoMode: false,
    loading: true,
    lastUpdated: '',
    stats: { totalFarmers: 0, totalHectares: 0, activeAlerts: 0, avgMoisture: 0 },
    crops: [],
    farms: [],
    selectedFarm: '',
    villageSummary: [],
    alerts: [],
    chart: null,

    async init() {
      try {
        await apiFetch('/health');
        this.demoMode = false;
      } catch {
        this.demoMode = true;
      }
      await this.loadAll();
      this.loading = false;
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

        this.$nextTick(() => { this.loadChart(); });
      } catch (e) {
        console.error('Load error:', e);
      }
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

    async loadChart() {
      const farmId = this.selectedFarm;
      if (!farmId) return;

      const canvas = document.getElementById('moistureChart');
      if (!canvas) return;

      try {
        const readings = await this.fetch(`/sensors/${farmId}/readings?limit=48`);
        const sorted = readings.slice().reverse();
        const labels = sorted.map(r => {
          const d = new Date(r.reading_time);
          return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        });
        const data = sorted.map(r => r.soil_moisture_pct);

        if (this.chart) this.chart.destroy();
        this.chart = new Chart(canvas, {
          type: 'line',
          data: {
            labels,
            datasets: [{
              label: 'Soil Moisture %',
              data,
              borderColor: '#2d5016',
              backgroundColor: 'rgba(45,80,22,0.15)',
              fill: true,
              tension: 0.35,
              pointRadius: 2,
              pointHoverRadius: 5,
              borderWidth: 2,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: 'rgba(45,80,22,0.9)',
                titleFont: { size: 12 },
                bodyFont: { size: 13 },
                padding: 10,
                cornerRadius: 6,
                callbacks: {
                  label: function(ctx) { return `Moisture: ${ctx.parsed.y.toFixed(1)}%`; }
                }
              },
            },
            scales: {
              y: {
                min: 10,
                max: 70,
                title: { display: true, text: 'Moisture %', font: { size: 12 } },
                grid: { color: 'rgba(0,0,0,0.06)' },
              },
              x: {
                ticks: { maxRotation: 45, maxTicksLimit: 10, font: { size: 10 } },
                grid: { display: false },
              },
            },
          },
        });
      } catch (e) {
        console.error('Chart load error:', e);
      }
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
  };
}
