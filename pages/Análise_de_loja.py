import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta



pd.options.display.float_format = '{:.2f}'.format
# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Entrada e Vacância',
initial_sidebar_state="collapsed")


## SIDE BAR ##
st.sidebar.image(r'Imagens/NAVA-preta.png')

st.sidebar.header('Filtros')
emp = st.sidebar.radio(    "Selecione o Empreendimento",
    options=['Viashopping', 'Viabrasil'], index = 0)

ResumoLojas, DF_Fluxo, DFLojas = ProcTab.TabelaOriginal(emp)

hoje = date.today()
hoje = hoje.replace(day=1)

sliderIntervalo = st.sidebar.date_input("Período",
                     value = (date(2025,1,1),DFLojas['Data'].max()),
                     min_value=date(2018,1,1),
                     max_value=DFLojas['Data'].max(),
                     format= "DD/MM/YYYY"
)
inicio, fim = sliderIntervalo
inicio = inicio.replace(day=1)
fim = fim.replace(day=1)
inicio = pd.to_datetime(inicio)
fim = pd.to_datetime(fim)
classificacao_unica = DFLojas['Classificação'].unique().tolist()
classificacao_inutil = ['Comodato', 'Depósito']
default = [x for x in classificacao_unica if x not in classificacao_inutil]

with st.sidebar.expander("Filtros Avançados", expanded=False):

    ClassificacaoSelecionadas = st.pills(
            'Selecione as classificações que deseja visualizar',
        options=classificacao_unica,
        selection_mode= 'multi',
        default= default
    )

    LadoSelecionado = st.segmented_control(
        'Lado:',
        options = ['Lado A', 'Lado B', 'Ambos'],
        default = 'Ambos'
    )

    PisosSelecionados = st.pills(
        'Selecione os pisos que deseja visualizar',
        options = DFLojas['Piso'].dropna().unique().tolist(),
        selection_mode = 'multi',
        default = DFLojas['Piso'].dropna().unique().tolist()
    )

DF_Filtrado = DFLojas[(DFLojas['Data'] >= inicio)&(DFLojas['Data'] <= fim)&(DFLojas['Classificação'].isin(ClassificacaoSelecionadas))&(DFLojas['Piso'].isin(PisosSelecionados))]

