import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date


# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Relatório Nava',
initial_sidebar_state="collapsed")

# ------------------------------- Trazendo o DF Completo -------------------------------- #

empresas = ['Viashopping', 'Viabrasil']

dfs_compclasspos = []
dfs_fluxo = []
dfs_apenaslojas = []

for emp in empresas:
    CompClassPos, DF_Fluxo, DF_ApenasLojas = ProcTab.TabelaOriginal(emp)

    # anota a origem sem tocar na função
    CompClassPos = CompClassPos.copy()
    DF_Fluxo = DF_Fluxo.copy()
    DF_ApenasLojas = DF_ApenasLojas.copy()

    CompClassPos['Empreendimento'] = emp
    DF_Fluxo['Empreendimento'] = emp
    DF_ApenasLojas['Empreendimento'] = emp

    dfs_compclasspos.append(CompClassPos)
    dfs_fluxo.append(DF_Fluxo)
    dfs_apenaslojas.append(DF_ApenasLojas)

df_final_compclasspos = pd.concat(dfs_compclasspos, ignore_index=True)
df_final_fluxo = pd.concat(dfs_fluxo)  # mantém o índice Data
df_final_apenaslojas = pd.concat(dfs_apenaslojas, ignore_index=True)


# ------------------------------- --------------------- -------------------------------- #


# -------------------------------SIDE BAR-------------------------------- #

## SIDE BAR ##
st.sidebar.image(r'Imagens/NAVA-preta.png')


# -------------------------------/SIDE BAR-------------------------------- #
st.title("Comparativo de Lojas")
col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
with col1:
    hoje = date.today()
    hoje = hoje.replace(day=1)

    sliderIntervalo = st.date_input("Período",
                        value = (date(2025,1,1),df_final_apenaslojas['Data'].max()),
                        min_value=date(2018,1,1),
                        max_value=df_final_apenaslojas['Data'].max(),
                        format= "DD/MM/YYYY",
                        key='date_input1'
    )
    inicio, fim = sliderIntervalo
    inicio = inicio.replace(day=1)
    fim = fim.replace(day=1)
    inicio = pd.to_datetime(inicio)
    fim = pd.to_datetime(fim)


df_apenaslojas_filtrado_final = df_final_apenaslojas[(df_final_apenaslojas['Data'] >= inicio) & (df_final_apenaslojas['Data'] <= fim)]


with col2:

    lojas_selecionadas = st.multiselect(
        "Selecione as lojas",
        df_apenaslojas_filtrado_final['ID'].unique(),
        default= None,
        placeholder="Selecione as lojas",
        key='multiselect1'
    )
    df_com_lojas_selecionadas = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID'].isin(lojas_selecionadas)]
with col3:
    verba_selecionada = st.pills(
        "Selecione a verba",
        options=['Venda', 'Aluguel', 'CTO Comum', 'CTOcomum/M²', 'CTO Comum/Venda'],
        default='Venda'
    )
col1, col2 = st.columns([0.8, 0.2])
with col1:    
    fig = px.line(df_com_lojas_selecionadas, x = 'Data', y = verba_selecionada, color = 'ID')
    fig.update_layout(
    xaxis=dict(
        showgrid=True,
        gridwidth=0.1,
        gridcolor="#F5F5F5"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    for loja in lojas_selecionadas:
        df_loja = df_com_lojas_selecionadas[df_com_lojas_selecionadas['ID'] == loja]

        s = (df_loja.sort_values('Data')[verba_selecionada].dropna())

        if len(s) >= 2:
            first = s.iloc[0]
            last  = s.iloc[-1]
            delta_valor = 0 if first == 0 else (last/first - 1)
        else:
            delta_valor = 0

        st.metric(
            label=str(loja),
            value=round(float(df_loja[verba_selecionada].sum()), 2),
            help=f"Total de {verba_selecionada} da loja {loja} no período selecionado. E a variação percentual do primeiro para o último mês.",
            delta=(f"{delta_valor:.2%}" if pd.notna(delta_valor) else "—")
        )
df_com_lojas_selecionadas

st.divider()

#------------------------------- Comparativo por Classificação -------------------------------- #

st.title("Comparativo de loja pela classificação")
col1, col2 = st.columns([0.5, 0.5])
with col1:
    hoje2 = date.today()
    hoje2 = hoje2.replace(day=1)

    sliderIntervalo2 = st.date_input("Período",
                        value = (date(2025,1,1),df_final_apenaslojas['Data'].max()),
                        min_value=date(2018,1,1),
                        max_value=df_final_apenaslojas['Data'].max(),
                        format= "DD/MM/YYYY",
                        key='date_input2'
    )
    inicio2, fim2 = sliderIntervalo2
    inicio2 = inicio2.replace(day=1)
    fim2 = fim2.replace(day=1)
    inicio2 = pd.to_datetime(inicio2)
    fim2 = pd.to_datetime(fim2)


df_apenaslojas_filtrado_final_2 = df_final_apenaslojas[(df_final_apenaslojas['Data'] >= inicio) & (df_final_apenaslojas['Data'] <= fim)]


with col2:

    lojas_selecionadas2 = st.multiselect(
        "Selecione as lojas",
        df_apenaslojas_filtrado_final_2['ID'].unique(),
        default= None,
        placeholder="Selecione as lojas",
        key='multiselect2'
    )
    df_com_lojas_selecionadas2 = df_apenaslojas_filtrado_final_2[df_apenaslojas_filtrado_final_2['ID'].isin(lojas_selecionadas2)]
    
    
    
    
# ------------------------------- Estilo CSS -------------------------------- #

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: #F5F5F5;
        border-radius: 5px;
        border: 1px solid #E0E0E0;
        padding: 10px;
    }
    [data-testid="stMetricValue"] {
        font-size: 20px;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        font-size: 8px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)