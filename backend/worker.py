import redis
import json
import time
from db import cursor, conn

# connect to Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

print("Worker started...")

while True:
    signal = r.brpop("signal_queue", timeout=5)

    if signal:
        _, data = signal
        signal_data = json.loads(data)

        component_id = signal_data["component_id"]
        severity = signal_data["severity"]

        key = f"debounce:{component_id}"

        if r.exists(key):
            print(f"Duplicate signal ignored for {component_id}")
        else:
            r.setex(key, 10, "active")

            # store incident in PostgreSQL
            cursor.execute(
                "INSERT INTO work_items (component_id, severity, status) VALUES (%s, %s, %s)",
                (component_id, severity, "OPEN")
            )
            conn.commit()

            print(f"🚨 Incident stored for {component_id}")

    time.sleep(1)