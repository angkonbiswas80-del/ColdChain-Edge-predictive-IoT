import random
from datetime import datetime

def analyze_risk(temperature, humidity, shock):
    """
    Edge Intelligence Engine:
    Analyses sensor data in real-time to predict shipment risks.
    """
    # Predictive logic for Cold Chain
    if temperature > 8.0 or temperature < 2.0:
        return "RISK_TEMPERATURE_EXCURSION"
    elif shock > 2.0:
        return "RISK_PHYSICAL_SHOCK"
    elif humidity > 65.0:
        return "RISK_HIGH_HUMIDITY"
    else:
        return "NORMAL"

def generate_sensor_data():
    """
    Generates simulated IoT telemetry data for cold chain monitoring.
    """
    # Generating realistic variations
    temperature = round(random.uniform(0.0, 12.0), 2) # Simulated range: 0 to 12 degrees
    humidity = round(random.uniform(30.0, 80.0), 2)    # Simulated range: 30% to 80%
    shock = round(random.uniform(0.0, 3.0), 2)        # Simulated shock: 0 to 3 G-force

    # Run Edge Intelligence
    status = analyze_risk(temperature, humidity, shock)

    # Payload Structure
    payload = {
        "timestamp": datetime.now().isoformat(),
        "temperature": temperature,
        "humidity": humidity,
        "shock": shock,
        "status": status
    }
    
    return payload

if __name__ == "__main__":
    # Test block to verify if the simulator is working
    print("Testing Simulator Output:")
    print(generate_sensor_data())