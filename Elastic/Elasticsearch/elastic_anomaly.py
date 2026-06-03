import os
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, exceptions

# ======================= KONFIGURATION =======================

ML_JOB_ID = "population-user"

# Elasticsearch Verbindungsdetails (aus Ihren Dateien ausgelesen)
ELASTIC_HOST = "http://localhost:9200"
ELASTIC_USER = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "Mahmoud07")  # Liest das Passwort oder nutzt den Standardwert
CA_CERTS_PATH = "ca.crt"

# Wartezeit in Sekunden, um der Pipeline (Filebeat, ES, ML-Job) Zeit zur Verarbeitung zu geben.
WAIT_TIME_SECONDS = 45


# ======================= SKRIPT-LOGIK =======================

def verify_ml_anomalies():
    """
    Verbindet sich mit Elasticsearch, wartet auf die Datenverarbeitung und
    fragt die erkannten Anomalien des spezifizierten ML-Jobs ab.
    """
    print("🐍 Anomalie-Verifizierungs-Skript gestartet.")

    # 1. Mit Elasticsearch verbinden
    try:
        print(f"Verbinde mit Elasticsearch unter {ELASTIC_HOST}...")
        es = Elasticsearch(
            hosts=[ELASTIC_HOST],
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            # ca_certs=CA_CERTS_PATH,
            verify_certs=False
        )
        # Teste die Verbindung
        if not es.ping():
            raise exceptions.ConnectionError("Verbindung fehlgeschlagen.")
        print("✅ Verbindung erfolgreich hergestellt.")
    except exceptions.AuthenticationException:
        print("❌ FEHLER: Authentifizierung fehlgeschlagen. Überprüfen Sie ELASTIC_PASSWORD.")
        return
    except exceptions.ConnectionError as e:
        print(
            f"❌ FEHLER: Verbindung zu Elasticsearch konnte nicht hergestellt werden. Läuft der Container? Details: {e}")
        return
    except FileNotFoundError:
        print(f"❌ FEHLER: Zertifikatsdatei nicht gefunden unter '{CA_CERTS_PATH}'.")
        print("Stellen Sie sicher, dass das Skript im richtigen Verzeichnis ausgeführt wird.")
        return

    # 2. Warten, bis die Daten verarbeitet wurden
    print(f"\n▶️ BITTE STARTEN SIE JETZT IHR LOG-GENERATOR-SKRIPT IN EINEM ZWEITEN TERMINAL.")
    print(f"Warte {WAIT_TIME_SECONDS} Sekunden, damit die Datenpipeline die neuen Logs verarbeiten kann...")
    time.sleep(WAIT_TIME_SECONDS)

    # 3. Abfrage definieren, um die ML-Ergebnisse zu holen
    print("\n🔎 Suche nach erkannten Anomalien vom ML-Job...")

    # Definiere den Zeitfilter für die Abfrage
    time_filter = datetime.utcnow() - timedelta(seconds=WAIT_TIME_SECONDS + 30)

    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"job_id": ML_JOB_ID}},
                    {"match": {"result_type": "record"}}
                ],
                "filter": [
                    {"range": {"timestamp": {"gte": time_filter.isoformat()}}}
                ]
            }
        },
        "size": 100,
        "sort": [{"anomaly_score": "desc"}]  # Sortiere nach höchstem Anomalie-Score
    }

    # 4. Abfrage ausführen und Ergebnisse ausgeben
    try:
        response = es.search(index=".ml-anomalies-shared", body=query_body)
        hits = response['hits']['hits']

        if not hits:
            print("\n❌ Keine neuen Anomalien in den letzten Minuten für diesen Job gefunden.")
            print(
                "Mögliche Gründe: ML-Job-Name ist falsch, Logs wurden nicht verarbeitet, oder es wurden keine Anomalien mit hohem Score erkannt.")
            return

        print("\n==================================================")
        print(f"🔬 WISSENSCHAFTLICHER BEWEIS: {len(hits)} ANOMALIEN ERKANNT")
        print("==================================================")

        for hit in hits:
            source = hit['_source']
            print(
                f"Zeitstempel: {source['timestamp']} | "
                f"Anomalie-Score: {source['anomaly_score']:.2f} | "
                f"Beschreibung: {source.get('record_info', {}).get('typical', 'N/A')}"
            )

    except exceptions.NotFoundError:
        print("❌ FEHLER: Der Index '.ml-anomalies-shared' wurde nicht gefunden. Läuft der ML-Job?")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


if __name__ == "__main__":
    if ML_JOB_ID == "ihr_ml_job_name_hier_einfuegen":
        print("BITTE ÖFFNEN SIE DAS SKRIPT UND SETZEN SIE DIE VARIABLE 'ML_JOB_ID'!")
    else:
        verify_ml_anomalies()