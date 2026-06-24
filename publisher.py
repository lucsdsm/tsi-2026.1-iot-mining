import paho.mqtt.client as mqtt
import json, time, random

# Conecta ao Broker MQTT local do Docker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)
client.loop_start()

print("Simulador de Telemetria de Ativos de Mineração... Pressione Ctrl+C para parar.")

# Estados possíveis do veículo na mina
states = ["MOVING", "IDLE", "OFF"]

try:
    while True:
        current_state = random.choices(states, weights=[70, 25, 5], k=1)[0]
        
        if current_state == "MOVING":
            speed = round(random.uniform(15, 45), 1)
            fuel_instant = round(random.uniform(35, 75), 2)
        elif current_state == "IDLE":
            speed = 0.0
            fuel_instant = round(random.uniform(6, 12), 2)
        else: # OFF
            speed = 0.0
            fuel_instant = 0.0

        # Cálculo da eficiência (km/L = km/h / L/h)
        # Evita divisão por zero se o consumo for 0
        fuel_efficiency = round(speed / fuel_instant, 2) if fuel_instant > 0 else 0.0

        payload = {
          "engineStatus": current_state,
          "speed": speed,
          "fuelInstant": fuel_instant,
          "fuelEfficiency": fuel_efficiency # Novo campo calculado na borda
        }

        # Publica no tópico
        client.publish("/mining/truck001/telemetry", json.dumps(payload))
        print(f"MQTT -> Status: {current_state} | Velocidade: {speed} km/h | Consumo: {fuel_instant} L/h | Eficiência: {fuel_efficiency} km/L")
        
        time.sleep(4)

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()