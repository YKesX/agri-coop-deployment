import json
import logging
import os

import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

THRESHOLD = int(os.getenv("MOISTURE_THRESHOLD", "35"))
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agricoop")
DB_USER = os.getenv("DB_USER", "agricoop")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

QUERY = """
SELECT v.name AS village, AVG(sr.soil_moisture_pct) AS avg_moisture
FROM sensor_readings sr
JOIN farms f ON f.id = sr.farm_id
JOIN farmers fa ON fa.id = f.farmer_id
JOIN villages v ON v.id = fa.village_id
WHERE sr.reading_time >= NOW() - INTERVAL '1 hour'
GROUP BY v.name
ORDER BY v.name;
"""


def handler(event, context):
    logger.info(json.dumps({"event": "lambda_invoked", "threshold": THRESHOLD}))

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
        connect_timeout=10,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(QUERY)
            rows = cur.fetchall()
    finally:
        conn.close()

    details = []
    alerts_published = 0
    sns = boto3.client("sns")

    for village, avg_moisture in rows:
        avg_val = float(avg_moisture)
        entry = {"village": village, "avg_moisture_pct": round(avg_val, 1)}

        if avg_val < THRESHOLD:
            entry["alert"] = True
            message = (
                f"[agri-coop] Low soil moisture in {village}: "
                f"{avg_val:.1f}% (threshold {THRESHOLD}%)"
            )
            if SNS_TOPIC_ARN:
                sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject="Low Soil Moisture Alert")
                alerts_published += 1
                logger.info(json.dumps({"event": "alert_published", "village": village, "moisture": avg_val}))
        else:
            entry["alert"] = False

        details.append(entry)

    result = {
        "checked_villages": len(rows),
        "alerts_published": alerts_published,
        "details": details,
    }
    logger.info(json.dumps({"event": "lambda_complete", "result": result}))
    return result
