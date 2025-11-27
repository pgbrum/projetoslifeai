import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os

#CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="SLife Intelligence", page_icon="🏢", layout="wide")

#CSS PARA CARDS AMARELOS E LETRAS PRETAS
st.markdown("""
<style>
    /* === MUDANÇA PRINCIPAL: CARDS DE MÉTRICAS === */
    div[data-testid="stMetric"] {
        background-color: #FFD700 !important; /* Fundo Amarelo Dourado */
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3); /* Sombra para destacar */
        border: 1px solid #E6C200;
    }

    /* Forçar TODAS as letras dentro do card para ficarem PRETAS */
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div,
    div[data-testid="stMetric"] p,
    div[data-testid="stMetric"] span {
        color: #000000 !important;
    }
    
    /* Título da Métrica (Ex: Receita Mensal) - Preto Negrito */
    div[data-testid="stMetricLabel"] p {
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    /* Valor da Métrica (Número Grande) - Preto Extra Negrito */
    div[data-testid="stMetricValue"] div {
        font-weight: 900 !important;
    }
    
    /* Setinhas de porcentagem (Delta) - Pretas */
    div[data-testid="stMetricDelta"] svg {
        fill: #000000 !important;
    }

    /* === BOTÕES (Mantendo o padrão amarelo) === */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: black !important;
        font-weight: bold !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #FFC107 !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

#CARREGAMENTO DE DADOS
@st.cache_data
def carregar_dados():
    try:
        if not os.path.exists('slife_imoveis.csv'):
            return None, None, None, None
            
        df_imoveis = pd.read_csv('slife_imoveis.csv', sep=';')
        
        cols_numericas = ['valor_aluguel', 'distancia_universidade_km', 'nota_avaliacao']
        for col in cols_numericas:
            if df_imoveis[col].dtype == 'object':
                df_imoveis[col] = df_imoveis[col].astype(str).str.replace(',', '.').astype(float)

        cols_bool = ['tem_mobilia', 'tem_internet', 'tem_lavanderia']
        for col in cols_bool:
            df_imoveis[col] = df_imoveis[col].astype(int)
            
        tipos = df_imoveis['tipo'].unique()
        mapa_tipos = {tipo: i for i, tipo in enumerate(tipos)}
        df_imoveis['tipo_cod'] = df_imoveis['tipo'].map(mapa_tipos)
        
        df_contratos = None
        df_avaliacoes = None
        
        if os.path.exists('slife_contratos.csv'):
            df_contratos = pd.read_csv('slife_contratos.csv', sep=';')
            for col in ['receita_total', 'taxa_ocupacao']:
                if col in df_contratos.columns and df_contratos[col].dtype == 'object':
                    df_contratos[col] = df_contratos[col].astype(str).str.replace(',', '.').astype(float)
                    
        if os.path.exists('slife_avaliacoes.csv'):
            df_avaliacoes = pd.read_csv('slife_avaliacoes.csv', sep=';')
            for c in ['nota_limpeza', 'nota_localizacao', 'nota_atendimento', 'nota_custo_beneficio']:
                if c in df_avaliacoes.columns and df_avaliacoes[c].dtype == 'object':
                     df_avaliacoes[c] = df_avaliacoes[c].astype(str).str.replace(',', '.').astype(float)

        return df_imoveis, mapa_tipos, df_contratos, df_avaliacoes
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None

df_imoveis, mapa_tipos, df_contratos, df_avaliacoes = carregar_dados()

#HEADER
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=100)
    else:
        st.markdown("# 🏛️")

with col_titulo:
    st.title("SLife Intelligence")
    st.markdown("##### Plataforma de Gestão e Precificação Inteligente")

st.markdown("---")

#ABAS E CONTEÚDO
tab1, tab2 = st.tabs(["🏠 SIMULADOR DE PREÇO", "📊 DASHBOARD EXECUTIVO"])

# ABA 1: CALCULADORA
with tab1:
    if df_imoveis is not None:
        X = df_imoveis[['tipo_cod', 'quartos', 'vagas_totais', 'distancia_universidade_km', 
                        'tem_mobilia', 'tem_internet', 'tem_lavanderia']]
        y = df_imoveis['valor_aluguel']
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        st.subheader("Simulador de Aluguel (IA)")
        st.info("Preencha os dados abaixo para estimar o valor.")
        
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                tipo = st.selectbox("Tipo", list(mapa_tipos.keys()))
                dist = st.number_input("Distância (km)", 0.1, 15.0, 1.5)
            with c2:
                quartos = st.slider("Quartos", 1, 5, 1)
                vagas = st.slider("Vagas", 0, 5, 0)
            with c3:
                st.write("Inclusos:")
                mob = st.checkbox("Mobiliado", True)
                net = st.checkbox("Internet", True)
                lav = st.checkbox("Lavanderia", False)
            
            st.write("")
            if st.button("CALCULAR PREÇO ➔", type="primary", use_container_width=True):
                entrada = pd.DataFrame([[mapa_tipos[tipo], quartos, vagas, dist, int(mob), int(net), int(lav)]], 
                                     columns=X.columns)
                preco = model.predict(entrada)[0]
                
                st.markdown("---")
                rc1, rc2 = st.columns([1, 2])
                with rc1:
                    st.success("Preço Calculado!")
                    st.metric("Valor Sugerido", f"R$ {preco:,.2f}")
                with rc2:
                    st.write("**Comparação de Mercado**")
                    filtro = df_imoveis[df_imoveis['tipo'] == tipo]
                    st.scatter_chart(filtro, x='distancia_universidade_km', y='valor_aluguel', color='#FFD700')

# ABA 2: DASHBOARD
with tab2:
    if df_contratos is not None:
        st.subheader("Indicadores de Performance")
        ult = df_contratos.iloc[-1]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Receita (Mês)", f"R$ {ult['receita_total']:,.2f}")
        m2.metric("Ocupação", f"{ult['taxa_ocupacao']}%")
        m3.metric("Contratos Ativos", int(ult['contratos_ativos']))
        m4.metric("Novos Clientes", int(ult['novos_contratos']), "+15")
        
        st.write("")
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("**Evolução da Receita**")
            st.line_chart(df_contratos, x='mes', y='receita_total', color='#FFD700')
            
        with g2:
            st.markdown("**Qualidade (Avaliações)**")
            if df_avaliacoes is not None:
                notas = df_avaliacoes.iloc[-1][['nota_limpeza', 'nota_localizacao', 'nota_atendimento']]
                st.bar_chart(notas, color='#FFD700')
