import csv
import math
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import text


SEED_DIR = Path(__file__).parent


def run_seed(engine):
    with engine.connect() as conn:
        existing = conn.execute(text("SELECT count(*) FROM villages")).scalar()
        if existing > 0:
            return

        schema_sql = (SEED_DIR / "schema.sql").read_text()
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))

        villages = {}
        crops = {}
        farmers_rows = []

        csv_path = SEED_DIR / "farmers_data.csv"
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                village_name = row["village"]
                if village_name not in villages:
                    result = conn.execute(
                        text("INSERT INTO villages (name) VALUES (:n) RETURNING id"),
                        {"n": village_name},
                    )
                    villages[village_name] = result.scalar()

                crop_name = row["crop"]
                if crop_name not in crops:
                    result = conn.execute(
                        text(
                            "INSERT INTO crops (name, current_price_usd_per_kg) "
                            "VALUES (:n, :p) RETURNING id"
                        ),
                        {"n": crop_name, "p": float(row["price_usd_per_kg"])},
                    )
                    crops[crop_name] = result.scalar()

                farmers_rows.append(row)

        for row in farmers_rows:
            conn.execute(
                text(
                    "INSERT INTO farmers (id, name, village_id, joined_date) "
                    "VALUES (:id, :name, :vid, :jd)"
                ),
                {
                    "id": row["farmer_id"],
                    "name": row["name"],
                    "vid": villages[row["village"]],
                    "jd": row["last_updated"],
                },
            )

            conn.execute(
                text(
                    "INSERT INTO farms (farmer_id, crop_id, area_hectares, expected_yield_kg) "
                    "VALUES (:fid, :cid, :area, :yield)"
                ),
                {
                    "fid": row["farmer_id"],
                    "cid": crops[row["crop"]],
                    "area": float(row["area_hectares"]),
                    "yield": float(row["yield_kg"]),
                },
            )

        farm_ids = [r[0] for r in conn.execute(text("SELECT id FROM farms ORDER BY id")).fetchall()]

        now = datetime.now(timezone.utc)
        rng = random.Random(42)

        for farm_id in farm_ids:
            base_temp = rng.uniform(24, 34)
            base_humidity = rng.uniform(40, 65)
            base_moisture = rng.uniform(30, 55)

            for i in range(100):
                t = now - timedelta(hours=(100 - i) * 1.68)
                hour_of_day = t.hour + t.minute / 60.0
                diurnal = math.sin((hour_of_day - 6) / 24 * 2 * math.pi) * 4
                temp = round(base_temp + diurnal + rng.gauss(0, 1), 2)
                humidity = round(base_humidity - diurnal * 1.5 + rng.gauss(0, 2), 2)
                moisture_drift = -0.03 * i + rng.gauss(0, 0.8)
                moisture = round(max(15, min(70, base_moisture + moisture_drift)), 2)

                conn.execute(
                    text(
                        "INSERT INTO sensor_readings "
                        "(farm_id, reading_time, temperature_c, humidity_pct, soil_moisture_pct) "
                        "VALUES (:fid, :rt, :t, :h, :m)"
                    ),
                    {"fid": farm_id, "rt": t, "t": temp, "h": humidity, "m": moisture},
                )

        alert_data = [
            ("weather", "warning", "Low soil moisture detected on Farm 3", 3, now - timedelta(hours=5), None),
            ("weather", "critical", "Soil moisture critically low on Farm 9", 9, now - timedelta(hours=2), None),
            ("price", "info", "Cotton price dropped below seasonal average", 1, now - timedelta(days=2), now - timedelta(days=1)),
            ("weather", "warning", "High temperature alert for Farm 7", 7, now - timedelta(days=3), now - timedelta(days=2)),
            ("system", "info", "Sensor calibration completed for Farm 5", 5, now - timedelta(days=1), now - timedelta(hours=12)),
        ]

        farm_id_list = farm_ids
        for atype, severity, message, farm_idx, created, resolved in alert_data:
            fid = farm_id_list[farm_idx - 1] if farm_idx <= len(farm_id_list) else farm_id_list[0]
            params = {
                "type": atype,
                "severity": severity,
                "message": message,
                "fid": fid,
                "cat": created,
            }
            if resolved:
                conn.execute(
                    text(
                        "INSERT INTO alerts (type, severity, message, farm_id, created_at, resolved_at) "
                        "VALUES (:type, :severity, :message, :fid, :cat, :rat)"
                    ),
                    {**params, "rat": resolved},
                )
            else:
                conn.execute(
                    text(
                        "INSERT INTO alerts (type, severity, message, farm_id, created_at) "
                        "VALUES (:type, :severity, :message, :fid, :cat)"
                    ),
                    params,
                )

        conn.commit()
