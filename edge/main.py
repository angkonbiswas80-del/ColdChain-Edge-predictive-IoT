import time
import json
import logging
import paho.mqtt.client as mqtt
from simulator import generate_sensor_data

# Added init_local_database here!
from simulator import generate_sensor_data
from local_db import init_local_database, buffer_telemetry_data, get_unsynced_data, mark_as_synced

# Configuration Constants
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "coldchain/telemetry"

# Professional Logging Configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] (ColdChainEdgeAgent) - %(message)s'
)
logger = logging.getLogger()

class ColdChainEdgeAgent:
    def __init__(self):
        # 1. Initialize the database and create the table before doing anything else!
        init_local_database()
        
        self.is_online = False
        
        # 2. Initialize MQTT Client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("🟢 System Online. Connected to MQTT Broker successfully.")
            self.is_online = True
            self.sync_local_buffer()
        else:
            logger.error(f"❌ Connection failed with result code {rc}")
            self.is_online = False

    def on_disconnect(self, client, userdata, rc):
        logger.warning("🔴 System Offline! Lost connection to MQTT Broker. Diverting payload to failover SQLite instance.")
        self.is_online = False

    def sync_local_buffer(self):
        """Fetches accumulated offline data from SQLite and publishes to the cloud broker once online."""
        unsynced_packets = get_unsynced_data()
        if unsynced_packets:
            logger.warning(f"🔄 Network restored! Found {len(unsynced_packets)} unsynced packets in SQLite buffer. Synchronizing...")
            
            for packet in unsynced_packets:
                payload = {
                    "timestamp": packet['timestamp'],
                    "temperature": packet['temperature'],
                    "humidity": packet['humidity'],
                    "shock": packet['shock'],
                    "status": packet['status']
                }
                
                self.client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
                logger.info(f"📤 Syncing buffered packet from {payload['timestamp']}")
                
                # Delete synced packet from local buffer
                mark_as_synced(packet['id'])
                time.sleep(0.2) 
            
            logger.info("✅ Historical database buffer successfully cleared and synchronized.")

    def run(self):
        logger.info("🚀 Initializing ColdChain Edge Agent architecture...")
        
        try:
            self.client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Initial asynchronous connection network error: {e}")

        logger.info("🧠 ColdChain Edge Agent Engine is officially running.")
        
        try:
            while True:
                payload = generate_sensor_data()
                
                if self.is_online:
                    try:
                        result = self.client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logger.info(f"☁️ [MQTT Publish] Successfully streamed payload to cloud topic '{MQTT_TOPIC}': Temp={payload['temperature']}°C, Status={payload['status']}")
                        else:
                            raise Exception("Internal publish queue bottleneck")
                    except Exception as mqtt_error:
                        logger.error(f"⚠ MQTT Publish failed: {mqtt_error}. Routing to local failover buffer.")
                        buffer_telemetry_data(payload)
                else:
                    logger.warning(f"⚠ Network offline. Packet buffered locally at {payload['timestamp']}")
                    buffer_telemetry_data(payload)
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            logger.warning("🛑 Edge Agent shutdown sequence initiated by user.")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    agent = ColdChainEdgeAgent()
    agent.run()