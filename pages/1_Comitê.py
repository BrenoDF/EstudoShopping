import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from graphviz import Digraph
from dateutil.relativedelta import relativedelta


#Lojas com desconto ou inadimplência INSERIR (formato lista)

desconto = []



pd.options.display.float_format = '{:.2f}'.format
st.set_page_config(layout="wide",
                   page_title= 'Inicio')
# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Comitê de Performance',
initial_sidebar_state="collapsed")


## SIDE BAR ##
st.sidebar.image(r'Imagens/NAVA-preta.png')

st.sidebar.header('Filtros')
emp = st.sidebar.radio(    "Selecione o Empreendimento",
    options=['Viashopping', 'Viabrasil'], index = 0)

sss = st.sidebar.toggle("Vendas SSS",
    value=False,
    help="Vendas Same Store Sales (Vendas de lojas abertas há mais de 12 meses).")

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
segmentosUnicos = DFLojas['Segmento'].unique().tolist()
segmentoInutil = ['Comodato', 'Depósito']
default = [x for x in segmentosUnicos if x not in segmentoInutil]

with st.sidebar.expander("Filtros Avançados", expanded=False):

    SegmentosSelecionados = st.pills(
            'Selecione os segmentos que deseja visualizar',
        options=segmentosUnicos,
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






regras = {
      'Âncoras': 5, 
      'Conveniência / Serviços': 15, 
      'Satélites': 15, 
      'Semi Âncoras': 5,
      'Mega Lojas': 10,  
      'Entretenimento': 15, 
      'Quiosque':15
}

CriticoAcumulado = DFLojas.groupby(['ID'], as_index=False).agg({
    'M2': 'last',
    'VendaAA': 'sum',
    'Venda': 'sum',
    'CTO Comum': 'sum',
    'Aluguel Mínimo': 'sum',
    'Aluguel Complementar': 'sum',
    'Encargo Comum': 'sum',
    'Segmento': 'last',
    'Piso': 'last',
    'Lado': 'last'
    
})
CriticoAcumulado['CTO Comum/Venda'] = round((CriticoAcumulado['CTO Comum'] / CriticoAcumulado['Venda']) * 100, 2)
CriticoAcumulado = CriticoAcumulado[['ID', 
                                    'VendaAA', 
                                    'Venda', 
                                    'CTO Comum', 
                                    'CTO Comum/Venda', 
                                    'Aluguel Mínimo', 
                                    'Aluguel Complementar', 
                                    'Encargo Comum', 
                                    'Segmento', 
                                    'Piso', 
                                    'Lado']]
VendaMenorQueAA = CriticoAcumulado[CriticoAcumulado['Venda'] < CriticoAcumulado['VendaAA']]




criticoCTOAlto = VendaMenorQueAA[(VendaMenorQueAA['CTO Comum/Venda'] > VendaMenorQueAA['Segmento'].map(regras))]
criticoFinal = criticoCTOAlto[criticoCTOAlto['ID'].isin(desconto)]
fluxograma = Digraph(comment='Lojas Críticas')
fluxograma.node('1', 'Lojas')
fluxograma.node('2', 'Vendas < Vendas AA')
fluxograma.node('3', 'Custo de Operação Alto')
fluxograma.node('4', 'Desconto e/ou Inadimplência')
fluxograma.node('A', f"{len(VendaMenorQueAA)}")
fluxograma.node('B', f"{len(criticoCTOAlto)}")
fluxograma.edge('1', '2')
with fluxograma.subgraph() as s:
    s.attr(rank='same')
    s.node('2')
    s.node('A')
with fluxograma.subgraph() as s:
    s.attr(rank='same')
    s.node('3')
    s.node('B')
    fluxograma.edge('2', 'A')
    fluxograma.edge('3', 'B')
    fluxograma.edge('A', 'B')
    fluxograma.edge('2', '3')
    fluxograma.edge('3', '4')
for i in range(len(criticoFinal)):
    fluxograma.node(f'{i+5}', criticoFinal['ID'].iloc[i])
    fluxograma.edge('4', f'{i+5}')
st.header('Lojas Críticas')

colx, coly, colz = st.columns([0.15, 0.7, 0.15], gap="large")
with coly:
    st.graphviz_chart(fluxograma, use_container_width=True)

st.dataframe(criticoFinal.iloc[:,:-3].reset_index(drop=True), use_container_width=True, hide_index=True)

########



st.subheader('Lojas que entraram e saíram')
UltimaData = DFLojas['Data que entrou'].max()
EntradaSaida = DFLojas[['Nome Fantasia', 'Data que entrou', 'Data que saiu']]
df_entradas = EntradaSaida[["Data que entrou", "Nome Fantasia"]].rename(columns={"Data que entrou": "Data", "Nome Fantasia": "Entrou"})
df_saidas = EntradaSaida[["Data que saiu", "Nome Fantasia"]].rename(columns={"Data que saiu": "Data", "Nome Fantasia": "Saiu"})
df_saidas.loc[df_saidas['Data'] == UltimaData, 'Data'] = pd.NaT
EntradaSaida = pd.concat([df_entradas, df_saidas])
EntradaSaida = EntradaSaida.groupby("Data").agg(lambda x: ', '.join(x.dropna().unique())).reset_index().sort_values(by = ['Data'], ascending=False)
mascaraDeContagemVirgulaEntrou = EntradaSaida['Entrou'].fillna('').str.count(',')
mascaraDeContagemVirgulaSaiu = EntradaSaida['Saiu'].fillna('').str.count(',')
EntradaSaida['Entrou (Contagem)'] = (
(mascaraDeContagemVirgulaEntrou + 1).where(EntradaSaida['Entrou'] != '', 0)
.astype(int)
)
EntradaSaida['Saiu (Contagem)'] = (
(mascaraDeContagemVirgulaSaiu + 1).where(EntradaSaida['Saiu'] != '', 0)
.astype(int)
)
EntradaSaida = EntradaSaida[(EntradaSaida['Data'] >= inicio)&(EntradaSaida['Data'] <= fim)]
EntradaSaida['Data'] = EntradaSaida['Data'].dt.strftime('%d/%m/%Y')
EntradaSaida = EntradaSaida[['Data', 'Entrou (Contagem)', 'Saiu (Contagem)', 'Entrou', 'Saiu']]

st.dataframe(EntradaSaida, hide_index=True, use_container_width=True)