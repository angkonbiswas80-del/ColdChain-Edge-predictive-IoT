import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
MQTT_BROKER = "localhost"  
MQTT_TOPIC = "coldchain/telemetry"
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "NChgbOfcU8m0XRMr2p6COjkzYaoCopmmfZHpEfGaMwXS7eoQfxwcfJBsjDrrb0-UIaAqBeZj4hiIjNNw-XZ9OA==" 
INFLUX_ORG = "ColdChainOrg"
INFLUX_BUCKET = "telemetry_bucket"

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"📥 Received: {payload}")
    
    # InfluxDB Point Creation
    point = Point("telemetry") \
        .tag("device_id", "edge_node_01") \
        .field("temperature", float(payload['temperature'])) \
        .field("humidity", float(payload['humidity'])) \
        .field("shock", float(payload['shock'])) \
        .field("status", str(payload['status']))
    
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print("✅ Data saved to InfluxDB")

# MQTT Setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.subscribe(MQTT_TOPIC)

print("🚀 Cloud Ingestor Service Started...")
mqtt_client.loop_forever()