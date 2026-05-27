CREATE TABLE IF NOT EXISTS villages (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS crops (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  current_price_usd_per_kg NUMERIC(10,2) NOT NULL,
  price_updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS farmers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  village_id INTEGER REFERENCES villages(id),
  joined_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS farms (
  id SERIAL PRIMARY KEY,
  farmer_id TEXT REFERENCES farmers(id),
  crop_id INTEGER REFERENCES crops(id),
  area_hectares NUMERIC(8,2),
  expected_yield_kg NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS sensor_readings (
  id BIGSERIAL PRIMARY KEY,
  farm_id INTEGER REFERENCES farms(id),
  reading_time TIMESTAMPTZ DEFAULT NOW(),
  temperature_c NUMERIC(5,2),
  humidity_pct NUMERIC(5,2),
  soil_moisture_pct NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS alerts (
  id SERIAL PRIMARY KEY,
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL,
  farm_id INTEGER REFERENCES farms(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_farm_time
  ON sensor_readings(farm_id, reading_time DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_unresolved
  ON alerts(created_at) WHERE resolved_at IS NULL;
