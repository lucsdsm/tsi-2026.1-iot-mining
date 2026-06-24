# IoT Mining Telemetry & Digital Twin Dashboard

## Sobre a aplicação
A aplicação simula a emissão e o processamento de telemetria de ativos de mineração (caminhões). O objetivo principal é monitorar o desperdício de combustível de motores operando em marcha lenta (`IDLE`) sem deslocamento, calculando a eficiência na borda (Edge Computing) e o prejuízo financeiro em tempo real através da integração com o ecossistema FIWARE e um painel analítico.

## Arquitetura e Serviços
O projeto adota uma arquitetura baseada em microsserviços, onde o fluxo de dados passa pelas seguintes etapas operacionais:

1. **Mosquitto:** Broker MQTT que atua como porta de entrada. O dispositivo simulado no caminhão publica seus dados brutos em um tópico e o Mosquitto os distribui para os assinantes.
2. **Node-RED:** Middleware de integração. Ele consome os dados do Mosquitto, aplica regras de negócio (identificação de desperdício) e envelopa o payload no padrão NGSI-v2 exigido pelo FIWARE. Em seguida, realiza um `Upsert` para o gêmeo digital.
3. **FIWARE Orion:** Context Broker central. Ele mantém o estado atual do caminhão em tempo real. Não guarda histórico, apenas a "captura" instantânea do ativo.
4. **MongoDB:** Banco de dados NoSQL utilizado internamente pelo Orion para salvar permanentemente o estado atual do gêmeo digital, prevenindo perda de dados em reinicializações.
5. **QuantumLeap:** Microsserviço especializado em séries temporais. É notificado pelo Orion (via *Subscription*) toda vez que o estado do caminhão muda. Ele atrela um *timestamp* aos dados e os estrutura para gravação.
6. **CrateDB:** Banco de dados SQL distribuído, otimizado para *Time-Series*. Armazena todo o histórico de leituras do caminhão de forma permanente.
7. **Streamlit:** Interface visual (Dashboard) em Python que consulta nativamente o CrateDB via SQL e plota indicadores econômicos e gráficos de desempenho do caminhão em tempo real.

## Como Executar o Projeto

### Pré-requisitos
* Docker e Docker Compose instalados (ou ambiente GitHub Codespaces).
* Python 3.8+ instalado localmente.

### Passo a Passo

**1. Subir a infraestrutura base:**
No terminal, na raiz do projeto, inicie os containers com o Docker Compose:
```bash
docker compose up -d
```

**2. Criar a Assinatura de Contexto (Subscription):**
Para garantir que o Orion avise o QuantumLeap sobre novos dados, registre a rota de integração rodando o comando:
```bash
curl -iX POST http://localhost:1026/v2/subscriptions/ \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "Notifica QL sobre telemetria do Caminhao 001",
    "subject": {
      "entities": [{"id": "MiningTruck:001", "type": "Vehicle"}],
      "condition": {
        "attrs": ["fuelInstant", "speed", "engineStatus", "wasteAlert", "fuelEfficiency"]
      }
    },
    "notification": {
      "http": {"url": "http://quantumleap:8668/v2/notify"},
      "attrs": ["fuelInstant", "speed", "engineStatus", "wasteAlert", "fuelEfficiency"],
      "metadata": ["dateCreated", "dateModified"]
    }
  }'
```

**3. Iniciar o simulador do caminhão (Edge):**
Em um terminal, instale as dependências (se ainda não o fez) e inicie o publicador de dados MQTT:
```bash
pip install paho-mqtt
python publisher.py
```

**4. Iniciar o Dashboard (Interface Visual):**
Em um segundo terminal, instale as dependências visuais e inicie o painel:
```
pip install streamlit pandas requests
streamlit run app.py
```