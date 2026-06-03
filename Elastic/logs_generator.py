import random
from datetime import datetime, timedelta
import os

import os

# Ordner erstellen, falls er nicht existiert
os.makedirs("anomalous_logs", exist_ok=True)

log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL']
services = ['ServiceA', 'ServiceB', 'ServiceC', 'ServiceD']
messages = [
    'File I/O', 'Critical Errors', 'Performance Warnings', 'Startup Messages',
    'Trace Information', 'Database Errors', 'Data Corruption', 'Status Updates',
    'Resource Warnings', 'Crashes', 'Algorithm Steps', 'Input Validation Warnings'
]
users = [f'User{n}' for n in range(1, 101)]
rare_ips = ['5.5.5.' + str(i) for i in range(1, 10)]
normal_ips = ['192.168.1.' + str(i) for i in range(1, 255)]

def generate_ip(anomalous=False):
    return random.choice(rare_ips if anomalous else normal_ips)

def generate_timestamp(start, i):
    delta = timedelta(seconds=i * random.randint(1, 2))
    return (start + delta).isoformat()

def generate_log_line(index, start_time, anomaly_ratio=0.03):
    timestamp = generate_timestamp(start_time, index)
    hour = datetime.fromisoformat(timestamp).hour
    user = random.choice(users)
    ip = generate_ip()
    response_time = f"{random.randint(10, 100)}ms"
    loglevel = random.choice(log_levels)
    message = random.choice(messages)

    # Inject anomaly
    if random.random() < anomaly_ratio:
        anomaly_type = random.choice(["spike", "suspicious_user", "rare_ip", "night", "slow"])
        if anomaly_type == "spike":
            loglevel = random.choice(["FATAL", "ERROR"])
        elif anomaly_type == "suspicious_user":
            user = "User99"  # z. B. viele Requests von User99
        elif anomaly_type == "rare_ip":
            ip = generate_ip(anomalous=True)
        elif anomaly_type == "night" and (hour < 5 or hour > 22):
            loglevel = "WARNING"
            message = "Unusual Access Time"
        elif anomaly_type == "slow":
            response_time = f"{random.randint(500, 1000)}ms"
            message = "Slow Request"

    return (
        f"{timestamp} | level={loglevel} | service={random.choice(services)}"
        f" | message={message} | request_id={random.randint(1000,9999)}"
        f" | user={user} | ip={ip} | time={response_time}"
    )

def write_log_file(file_path, num_lines):
    start_time = datetime.now() - timedelta(hours=1)
    with open(file_path, "w") as f:
        for i in range(num_lines):
            line = generate_log_line(i, start_time)
            f.write(line + "\n")
    print(f">>> {file_path} mit {num_lines} Einträgen erstellt.")

# Beispiel: Erzeuge mehrere Datensätze
os.makedirs("../../../anomalous_logs", exist_ok=True)
for size in [10_000, 100_000, 1_000_000]:  # optional: 10_000_000
    write_log_file(f"anomalous_logs/logdata_{size}.log", size)
