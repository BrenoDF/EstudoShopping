import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from graphviz import Digraph
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


# regras = {
#       'Âncoras': 5, 
#       'Conveniência / Serviços': 15, 
#       'Satélites': 15, 
#       'Semi Âncoras': 5,
#       'Mega Lojas': 10,  
#       'Entretenimento': 15, 
#       'Quiosque':15
# }

# CriticoAcumulado = DF_Filtrado[(DF_Filtrado['Desconto']>0) | (DF_Filtrado['Inadimplência']>0)]
# CriticoAcumulado = DF_Filtrado.groupby(['ID'], as_index=False).agg({
#     'M2': 'last',
#     'VendaAA': 'sum',
#     'Venda': 'sum',
#     'CTO Comum': 'sum',
#     'Aluguel Mínimo': 'sum',
#     'Aluguel Complementar': 'sum',
#     'Encargo Comum': 'sum',
#     'Classificação': 'last',
#     'Piso': 'last',
#     'Lado': 'last',
#     'Desconto': 'sum',
#     'Inadimplência': 'sum'
    
# })
# CriticoAcumulado['CTO Comum/Venda'] = round((CriticoAcumulado['CTO Comum'] / CriticoAcumulado['Venda']) * 100, 2)

# VendaMenorQueAA = CriticoAcumulado[CriticoAcumulado['Venda'] < CriticoAcumulado['VendaAA']]




# criticoCTOAlto = VendaMenorQueAA[(VendaMenorQueAA['CTO Comum/Venda'] > VendaMenorQueAA['Classificação'].map(regras))]
# fluxograma = Digraph(comment='Lojas Críticas')
# fluxograma.node('1', 'Lojas')
# fluxograma.node('2', 'Vendas < Vendas AA')
# fluxograma.node('3', 'Custo de Operação Alto')
# fluxograma.node('4', 'Desconto e/ou Inadimplência')
# fluxograma.node('A', f"{len(VendaMenorQueAA)}")
# fluxograma.node('B', f"{len(criticoCTOAlto)}")
# fluxograma.edge('1', '2')
# with fluxograma.subgraph() as s:
#     s.attr(rank='same')
#     s.node('2')
#     s.node('A')
# with fluxograma.subgraph() as s:
#     s.attr(rank='same')
#     s.node('3')
#     s.node('B')
#     fluxograma.edge('2', 'A')
#     fluxograma.edge('3', 'B')
#     fluxograma.edge('A', 'B')
#     fluxograma.edge('2', '3')
#     fluxograma.edge('3', '4')
# for i in range(len(criticoCTOAlto)):
#     fluxograma.node(f'{i+5}', criticoCTOAlto['ID'].iloc[i])
#     fluxograma.edge('4', f'{i+5}')
# st.header('Lojas Críticas')

# colx, coly, colz = st.columns([0.15, 0.7, 0.15], gap="large")
# with coly:
#     st.graphviz_chart(fluxograma, use_container_width=True)

# st.dataframe(criticoCTOAlto.iloc[:,:-1].reset_index(drop=True), use_container_width=True, hide_index=True)

########

st.subheader('Lojas que entraram e saíram')
UltimaData = DF_Filtrado['Data que entrou'].max()
EntradaSaida = DF_Filtrado[['Nome Fantasia', 'Data que entrou', 'Data que saiu']]
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