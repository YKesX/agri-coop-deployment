# Lambda: Sensor Aggregator

Checks average soil moisture per village over the last hour.
Publishes SNS alerts for villages below the moisture threshold.

## Environment variables

| Variable | Description |
|---|---|
| `DB_HOST` | RDS endpoint |
| `DB_PORT` | Database port (default 5432) |
| `DB_NAME` | Database name (default agricoop) |
| `DB_USER` | Database user (default agricoop) |
| `DB_PASSWORD` | Database password |
| `SNS_TOPIC_ARN` | ARN of the alerts SNS topic |
| `MOISTURE_THRESHOLD` | Moisture % below which to alert (default 35) |

## Trigger

EventBridge schedule: `rate(1 hour)`

## Return value

```json
{
  "checked_villages": 10,
  "alerts_published": 2,
  "details": [{"village": "Harran", "avg_moisture_pct": 32.1, "alert": true}]
}
```
