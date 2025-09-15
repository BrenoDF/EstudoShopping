import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta

# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Análise de CTO',
initial_sidebar_state="collapsed")
st.logo('Imagens/NAVA-preta.png', icon_image='Imagens/NAVA-preta.png', size='large')
global_widget_keys = ["data"]
if 'data' in st.session_state:
  for key in global_widget_keys:
      if key in st.session_state:
          st.session_state[key] = st.session_state[key]

## SIDE BAR ##
st.sidebar.header('Filtros')
emp = st.sidebar.radio("Selecione o Empreendimento",
    options=['Viashopping', 'Viabrasil'], index = 0)
DF_Fluxo, DFLojas = ProcTab.TabelaOriginal(emp)

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

    ClassificacaoSelecionada = st.pills(
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


# ------------------------------- FILTRANDO O DF -------------------------------- #
filtroSideBar = ((DFLojas['Classificação'].isin(ClassificacaoSelecionada)) &
    (DFLojas['Piso'].isin(PisosSelecionados)) &
    ((LadoSelecionado == 'Ambos')
      |
      (DFLojas['Lado']==LadoSelecionado)
      ))
filtroDataSelecionada = (DFLojas['Data'] >= inicio) & (DFLojas['Data'] <= fim)

DFLojasAtual = DFLojas.loc[filtroSideBar & filtroDataSelecionada]

###########################

# ------------------    INICIO DA PÁGINA    ------------------ #

st.title("Marketing")

df_essencial = DFLojasAtual[['Data', 'Luc', 'Nome Fantasia','M2', 'Venda', 'Aluguel', 'CTO Comum']]
# DFLojasAtual