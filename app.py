import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Mining IoT Dashboard", layout="wide")
st.markdown("Monitoramento do Gêmeo Digital **MiningTruck:001**")

PRECO_DIESEL = 6.15

@st.cache_data(ttl=5)
def fetch_data_from_db():
    url = "http://localhost:4200/_sql"
    # Consulta SQL direta na tabela gerada pelo QuantumLeap (colunas em minúsculo por padrão do banco)
    query = {
        "stmt": "SELECT time_index, enginestatus, fuelefficiency, fuelinstant, speed, wastealert FROM etvehicle ORDER BY time_index ASC LIMIT 1000"
    }
    try:
        response = requests.post(url, json=query)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

data = fetch_data_from_db()

if data and 'rows' in data and len(data['rows']) > 0:
    # Monta o DataFrame a partir das linhas e colunas retornadas pelo banco CrateDB
    df = pd.DataFrame(data['rows'], columns=data['cols'])
    
    # O CrateDB armazena e retorna a data em milissegundos
    df['Horário'] = pd.to_datetime(df['time_index'], unit='ms')
    df.set_index("Horário", inplace=True)
    
    # 2. Lógica de Negócio: Cálculo de Desperdício
    df['litros_gastos_janela'] = (df['fuelinstant'] / 3600) * 4
    
    df_waste = df[df['wastealert'] == True]
    
    litros_desperdicados = df_waste['litros_gastos_janela'].sum()
    prejuizo_reais = litros_desperdicados * PRECO_DIESEL
    
    # 3. Construção da Interface Visual (KPIs)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Status Atual do Motor", value=df['enginestatus'].iloc[-1])
    with col2:
        st.metric(label="Eficiência Atual (km/L)", value=f"{df['fuelefficiency'].iloc[-1]:.2f}")
    with col3:
        st.metric(
            label="Prejuízo Operacional (Motor Ocioso)", 
            value=f"R$ {prejuizo_reais:.2f}",
            delta=f"-{litros_desperdicados:.2f} Litros perdidos",
            delta_color="inverse"
        )
        
    st.divider()
    
    # 4. Gráficos Históricos
    st.subheader("Histórico de Consumo Instantâneo (L/h)")
    st.line_chart(df['fuelinstant'], color="#ff4a5a")
    
    st.subheader("Histórico de Velocidade (km/h)")
    st.line_chart(df['speed'], color="#00f2fe")

else:
    st.warning("Aguardando dados do Banco CrateDB... Certifique-se de que o publisher.py está rodando.")