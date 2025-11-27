import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="SLife Analytics", page_icon="🎓", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO E LIMPEZA ---
@st.cache_data
def carregar_dados_imoveis():
    try:
        # Lê o CSV usando separador de ponto e vírgula (padrão brasileiro)
        df = pd.read_csv('slife_imoveis.csv', sep=';')
        
        # --- LIMPEZA DE DADOS ---
        # 1. Converter colunas de dinheiro e distância (texto "1.200,00" para número 1200.00)
        cols_numericas = ['valor_aluguel', 'distancia_universidade_km', 'nota_avaliacao']
        for col in cols_numericas:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        # 2. Converter booleanos (True/False) para 1/0
        cols_bool = ['tem_mobilia', 'tem_internet', 'tem_lavanderia']
        for col in cols_bool:
            df[col] = df[col].astype(int)
            
        # 3. Mapear o "Tipo" para números (para a IA entender)
        # Vamos criar uma coluna nova 'tipo_cod'
        tipos = df['tipo'].unique()
        mapa_tipos = {tipo: i for i, tipo in enumerate(tipos)}
        df['tipo_cod'] = df['tipo'].map(mapa_tipos)
        
        return df, mapa_tipos
        
    except Exception as e:
        st.error(f"Erro ao ler 'slife_imoveis.csv': {e}")
        return None, None

@st.cache_data
def carregar_kpis():
    # Carrega os outros arquivos para os gráficos de dashboard
    try:
        df_contratos = pd.read_csv('slife_contratos.csv', sep=';')
        df_avaliacoes = pd.read_csv('slife_avaliacoes.csv', sep=';')
        
        # Limpeza básica de vírgulas
        cols_dinheiro = ['receita_total', 'valor_medio_republica', 'valor_medio_kitnet']
        for col in cols_dinheiro:
            if col in df_contratos.columns and df_contratos[col].dtype == 'object':
                df_contratos[col] = df_contratos[col].astype(str).str.replace(',', '.').astype(float)
                
        return df_contratos, df_avaliacoes
    except:
        return None, None

# Carrega tudo
df_imoveis, mapa_tipos = carregar_dados_imoveis()
df_contratos, df_avaliacoes = carregar_kpis()

# --- INTERFACE ---
st.title("🎓 SLife - Inteligência Imobiliária")
st.markdown("Solução integrada para precificação inteligente e análise de mercado.")

# Abas para separar as funcionalidades
tab1, tab2 = st.tabs(["🏠 Calculadora de Aluguel (IA)", "📊 Dashboard de Mercado"])

# === ABA 1: A CALCULADORA (IA) ===
with tab1:
    if df_imoveis is not None:
        # Treinamento do Modelo
        # Features: Tipo, Quartos, Vagas, Distancia, Mobilia, Internet, Lavanderia
        X = df_imoveis[['tipo_cod', 'quartos', 'vagas_totais', 'distancia_universidade_km', 
                        'tem_mobilia', 'tem_internet', 'tem_lavanderia']]
        y = df_imoveis['valor_aluguel']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Layout
        col_esq, col_dir = st.columns([1, 2])
        
        with col_esq:
            st.subheader("Simular Imóvel")
            
            # Inputs baseados nas colunas reais
            # Invertemos o mapa para usar no selectbox
            mapa_invertido = {v: k for k, v in mapa_tipos.items()}
            tipo_selecionado = st.selectbox("Tipo do Imóvel", list(mapa_tipos.keys()))
            
            quartos = st.slider("Quartos", 1, 5, 1)
            vagas = st.number_input("Vagas de Garagem", 0, 5, 0)
            distancia = st.number_input("Distância da Faculdade (km)", 0.1, 15.0, 1.5)
            
            st.write("Comodidades:")
            mobilia = st.checkbox("Mobiliado", value=True)
            internet = st.checkbox("Internet Inclusa", value=True)
            lavanderia = st.checkbox("Lavanderia", value=False)
            
            btn_calcular = st.button("Calcular Preço Justo", type="primary")
            
        with col_dir:
            if btn_calcular:
                # Preparar entrada
                entrada = pd.DataFrame({
                    'tipo_cod': [mapa_tipos[tipo_selecionado]],
                    'quartos': [quartos],
                    'vagas_totais': [vagas],
                    'distancia_universidade_km': [distancia],
                    'tem_mobilia': [1 if mobilia else 0],
                    'tem_internet': [1 if internet else 0],
                    'tem_lavanderia': [1 if lavanderia else 0]
                })
                
                preco_predito = model.predict(entrada)[0]
                
                st.success("Cálculo Finalizado!")
                st.metric("Valor Sugerido de Aluguel", f"R$ {preco_predito:.2f}")
                
                # Gráfico comparativo
                st.write("#### Comparativo: Preço vs Distância")
                st.caption("Como seu imóvel se compara com outros do mesmo tipo (Pontos vermelhos)")
                
                # Filtra imóveis do mesmo tipo para comparar
                df_filtro = df_imoveis[df_imoveis['tipo'] == tipo_selecionado]
                st.scatter_chart(df_filtro, x='distancia_universidade_km', y='valor_aluguel', color='#FF4B4B')
    else:
        st.warning("Erro ao carregar dados de imóveis.")

# === ABA 2: DASHBOARD (EXTRAS) ===
with tab2:
    st.header("Visão Geral da Empresa")
    if df_contratos is not None and df_avaliacoes is not None:
        # Métricas Gerais (Pega o último mês disponível)
        ultimo_mes = df_contratos.iloc[-1]
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Receita Total (Mês)", f"R$ {ultimo_mes['receita_total']:,.2f}")
        kpi2.metric("Contratos Ativos", int(ultimo_mes['contratos_ativos']))
        kpi3.metric("Taxa de Ocupação", f"{ultimo_mes['taxa_ocupacao']}%")
        kpi4.metric("Novos Contratos", int(ultimo_mes['novos_contratos']))
        
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Evolução da Receita")
            st.line_chart(df_contratos, x='mes', y='receita_total')
            
        with c2:
            st.subheader("Qualidade (Avaliações)")
            # Pega a média das notas do último mês disponível em avaliações
            notas_cols = ['nota_limpeza', 'nota_localizacao', 'nota_atendimento', 'nota_custo_beneficio']
            # Tratamento rápido para garantir que são floats
            df_avaliacoes_float = df_avaliacoes.copy()
            for c in notas_cols:
                df_avaliacoes_float[c] = df_avaliacoes_float[c].astype(str).str.replace(',', '.').astype(float)
                
            notas_ultimas = df_avaliacoes_float.iloc[-1][notas_cols]
            st.bar_chart(notas_ultimas)
            
    else:
        st.info("Arquivos de contratos ou avaliações não encontrados para gerar dashboard.")