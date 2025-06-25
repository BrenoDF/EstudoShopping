import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from graphviz import Digraph
from dateutil.relativedelta import relativedelta

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

ResumoLojas, DF_Fluxo, DF_ApenasLojas = ProcTab.TabelaOriginal(emp)

hoje = date.today()
hoje = hoje.replace(day=1)

sliderIntervalo = st.sidebar.date_input("Período",
                     value = (date(2025,1,1),DF_ApenasLojas['Data'].max()),
                     min_value=date(2018,1,1),
                     max_value=DF_ApenasLojas['Data'].max(),
                     format= "DD/MM/YYYY"
)
inicio, fim = sliderIntervalo
inicio = inicio.replace(day=1)
fim = fim.replace(day=1)
inicio = pd.to_datetime(inicio)
fim = pd.to_datetime(fim)
segmentosUnicos = DF_ApenasLojas['Segmento'].unique().tolist()
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
        options = DF_ApenasLojas['Piso'].dropna().unique().tolist(),
        selection_mode = 'multi',
        default = DF_ApenasLojas['Piso'].dropna().unique().tolist()
    )


### MARKDOWN PARA INFORMAÇÕES ###
st.markdown("""
              <style>
        .bloco-de-info {
        display: inline-block;
        padding: 6px 10px;
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        color: #111111;
        text-align: center;
        align:center;
        width: 100%;
        margin: 50px 0 0 0;
      }
      .bloco-de-info h3 {
        display: flex;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0;
        /* text-align: center; */
        flex-wrap: wrap;
        align-content: space-around;
        align-items: center;
        flex-direction: column-reverse;
        justify-content: center; 
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0;
        text-align: center;
      }
      .bloco-de-info h3 a,
      .bloco-de-info h3 button,
      .bloco-de-info h3 svg {
        display: none !important;
      }
      .bloco-de-info p {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        text-align: center;
      }
      .bloco-de-info .positive {
      color: #28a745;  /* verde */
      }
      .bloco-de-info .negative {
        color: #dc3545;  /* vermelho */
      }
      
      .info-bloco {
      background: #f9f9f9;
      padding: 10px;
      border-radius: 8px;
      font-size: 14px;
      width: fit-content;
      margin: 10px auto;
      }

    .linha, .linha-centralizada {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      margin-top: 6px;
      }

    .linha-centralizada {
      justify-content: center;
      gap: 25%;
      }

    .linha div, .linha-centralizada div {
      line-height: 1.2;
      min-width: 100px;
      }

    .variacao {
      background: #e6f0ff;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: bold;
      color: #0056b3;
      }
    </style>

      """, unsafe_allow_html=True)

# Bloco 1
st.title("Relatório de Performance - Grupo NA:blue[v]A")
st.header("Vendas Totais")


@st.cache_data
def VendasTotaisComite(DFLojas, Segmento, Lado, Piso, inicio, fim, sss):
  #Buscando o periodo de Ano Anterior
  inicio_aa = inicio - relativedelta(years=1)
  fim_aa    = fim    - relativedelta(years=1)

  # Aplicando os Filtros do SideBar
  filtroSideBar = ((DFLojas['Segmento'].isin(Segmento)) &
      (DFLojas['Piso'].isin(Piso)) &
      ((Lado == 'Ambos')
       |
       (DFLojas['Lado']==Lado)
       ))

  filtroDataSelecionada = (DFLojas['Data'] >= inicio) & (DFLojas['Data'] <= fim)
  filtroDataSelecionada_AA = (DFLojas['Data'] >= inicio_aa) & (DFLojas['Data'] <= fim_aa)
  
  DFLojasAtual = DFLojas.loc[filtroSideBar & filtroDataSelecionada]
  DFLojasAA = DFLojas.loc[filtroSideBar & filtroDataSelecionada_AA]
  
  ## SSS ##
  if sss:
    # depois de gerar DFLojasAtual e DFLojasAA -----------------------------

    for df in (DFLojasAtual, DFLojasAA):
        df['month'] = df['Data'].dt.month        # 1) mês numérico

    # 2) pares (ID, month) presentes nos dois períodos
    pares_comuns = (
        DFLojasAtual[['ID', 'month']].drop_duplicates()
        .merge(DFLojasAA[['ID', 'month']].drop_duplicates(),
              on=['ID', 'month'], how='inner')
    )

    # 3) aplica interseção – agora cada loja só tem meses em que existia nos DOIS anos
    DFLojasAtual = DFLojasAtual.merge(pares_comuns, on=['ID', 'month'], how='inner')
    DFLojasAA    = DFLojasAA.merge(pares_comuns, on=['ID', 'month'], how='inner')
  ## FIM DO SSS ##
  
  #Trazendo Mês-a-Mês
  group_v   = DFLojasAtual.groupby('Data')['Venda'].sum()
  group_aa  = DFLojasAA.groupby('Data')['Venda'].sum()
  mes_a_mes = pd.DataFrame({'Data':     pd.to_datetime(group_v.index),
                            'Venda':    group_v.values,
                            'VendaAA':  group_aa.values})
  mes_a_mes['Variação'] = round(((mes_a_mes['Venda'] / mes_a_mes['VendaAA']) -1) * 100,2)

  variacao = (((mes_a_mes['Venda'].sum() / mes_a_mes['VendaAA'].sum()) - 1) * 100).round(2)
  
  col1, col2, col3 = st.columns([0.43,0.14,0.43], gap="large")

  figVendatotal = px.line(
   mes_a_mes,
   x='Data',
   y=['Venda','VendaAA'],
   markers=True,
   custom_data=['Variação'],                
   color_discrete_map={'Venda':'#00b7db','VendaAA':'#000000'}
  )

  # agora respesos hover templates
  for trace in figVendatotal.data:
      if trace.name == 'Venda':
          trace.hovertemplate = (
              "Data: %{x|%d/%m/%Y}<br>"
              "Venda: R$ %{y:,.2f}<br>"
              "Variação: %{customdata[0]:.2f}%<extra></extra>"
          )
      else:  # VendaAA
          trace.hovertemplate = (
              "Data: %{x|%d/%m/%Y}<br>"
              f"{trace.name}: R$ "+"%{y:,.2f}<extra></extra>"
          )

  with col1:
    figVendatotal.update_layout(height=450)
    st.plotly_chart(figVendatotal, use_container_width=True)
  with col2:
    st.metric(label="Vendas Totais",
                value=f"{round(mes_a_mes['Venda'].sum()/1000000,2)}M",
                delta=f"{round(variacao,2)}%",
                width="content",
                border= True)
    st.metric(label="Vendas Ano Anterior",
                value=f"{round(mes_a_mes['VendaAA'].sum()/1000000,2)}M",
                width="content",
                border= True)
    st.metric(label="Operações Ativas", value=f"{len(DFLojasAtual['ID'].unique())} un.",
                width="stretch",
                border= True
                )

  with col3:
      DF_ApenasLojasSegmentos = (
      DFLojasAtual.groupby(['Data', 'Segmento'], as_index=False)
        [['Venda','VendaAA']]
        .sum().sort_values(by='Venda', ascending=True)
        )
      fig = px.bar(
          DF_ApenasLojasSegmentos,
          x='Venda',
          y='Segmento',
          orientation='h'
      )
      fig.update_layout(height=450)
      st.plotly_chart(fig, use_container_width=True)

  regras = {
      'Âncoras': 5, 
      'Conveniência / Serviços': 15, 
      'Satélites': 15, 
      'Semi Âncoras': 5,
      'Mega Lojas': 10,  
      'Entretenimento': 15, 
      'Quiosque':15
  }

  CriticoAcumulado = DFLojasAtual.groupby(['ID'], as_index=False).agg({
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
  desconto = ['LP01_MARIA CAFÉ', 'QL238_CASA DA PELÚCIA', 'Q104_BENDITA EMPADA', 'Q109_PRAÇAÍ', '1000_SUPERMERCADOS BH']
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

  st.divider()

        # ------------- PISO PISO PISO ----------------
  LojasSemFiltroPiso_e_Lado = DFLojas.loc[(DFLojas['Segmento'].isin(Segmento)) & (DFLojas['Data'] >= inicio) & (DFLojas['Data'] <= fim)]
  LojasSemFiltroPiso_e_LadoAA = DFLojas.loc[(DFLojas['Segmento'].isin(Segmento)) & (DFLojas['Data'] >= inicio_aa) & (DFLojas['Data'] <= fim_aa)]

  LojasSemFiltroPiso_e_Lado = LojasSemFiltroPiso_e_Lado.groupby(['Data', 'Piso','Lado'], as_index=False)[['Venda','CTO Comum']].sum()
  LojasSemFiltroPiso_e_LadoAA = LojasSemFiltroPiso_e_LadoAA.groupby(['Data', 'Piso','Lado'], as_index=False)[['Venda']].sum()


  pisos = ['Piso 1', 'Piso 2', 'Piso 3']
  lados = ['Lado A', 'Lado B']
  
  def resumo_bloco(piso, lado):
      # extrai os sums de forma genérica
      soma_AA = LojasSemFiltroPiso_e_LadoAA.query(
          "Piso == @piso and Lado == @lado"
      )['Venda'].sum()
      soma    = LojasSemFiltroPiso_e_Lado.query(
          "Piso == @piso and Lado == @lado"
      )['Venda'].sum()
      cto     = LojasSemFiltroPiso_e_Lado.query(
          "Piso == @piso and Lado == @lado"
      )['CTO Comum'].sum()
      # calcula métricas
      vendaAA_k  = round(soma_AA/1000, 2)
      venda_k    = round(soma/1000, 2)
      cto_k      = round(cto/1000, 2)
      cto_venda  = round(cto/soma*100, 2) if cto else 0
      variacao   = round((soma/soma_AA-1)*100, 2) if soma_AA else 0
      total_piso = round(
          (soma / DFLojas.loc[
            filtroDataSelecionada & DFLojas['Segmento'].isin(Segmento)
          ]['Venda'].sum()*100), 2
      ) if soma else 0
  
      return f"""
  <div class="info-bloco">
    <div><h4>{piso}</h4></div>
    <div class="linha">
      <div>VendaAA:<br><b>{vendaAA_k}k</b></div>
      <div>Venda:<br><b>{venda_k}k</b></div>
      <div>CTO:<br><b>{cto_k}k</b></div>
      <div>CTO/Venda:<br><b>{cto_venda}%</b></div>
    </div>
    <div class="linha-centralizada">
      <div>Variação:<br><span class="variacao">{variacao}%</span></div>
      <div>Venda Total / Piso:<br><b>{total_piso}%</b></div>
    </div>
  </div>
  """
  
  cols = st.columns(2)
  for col, lado in zip(cols, lados):
      with col:
          st.subheader(lado)
          for piso in pisos:
              html = resumo_bloco(piso, lado)
              st.markdown(html, unsafe_allow_html=True)
        
    # ------------- FIM PISO PISO PISO ----------------
  
    # ------------- LOJAS QUE ENTRARAM E SAÍRAM ----------------
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

  

    # ------------- FIM LOJAS QUE ENTRARAM E SAÍRAM ----------------





VendasTotaisComite(DF_ApenasLojas, SegmentosSelecionados, LadoSelecionado, PisosSelecionados, inicio, fim, sss)

col1, col2, col3 = st.columns([0.4,0.2,0.4])
inicioF, fimF = sliderIntervalo
inicioF = pd.to_datetime(inicioF)
fimF = pd.to_datetime(fimF)

DF_FluxoFiltrado = DF_Fluxo[(DF_Fluxo.index >= inicioF)&(DF_Fluxo.index <= fimF)]
DF_FluxoFiltradoAA = DF_Fluxo[(DF_Fluxo.index >= inicioF - relativedelta(years=1))&(DF_Fluxo.index <= fimF - relativedelta(years=1))]

DF_FluxoMap = DF_Fluxo['Fluxo de Pessoas'].to_dict()
DF_FluxoFiltrado['Fluxo de Pessoas AA'] = DF_FluxoFiltrado.index.map(
  lambda d: DF_FluxoMap.get(d - pd.DateOffset(years=1), 0)
  )




Pagantes_Fluxo = DF_FluxoFiltrado.melt(
    id_vars=['Dia','Mês', 'Ano'],
    value_vars=['Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções'],
    var_name='Tipo',
    value_name='Valor'
)
fig = px.pie(
    Pagantes_Fluxo,
    values='Valor',
    names='Tipo',
    title='Pagantes',
    color_discrete_sequence=px.colors.qualitative.Plotly
)

meses_dict = {
    'janeiro': 1,
    'fevereiro': 2,
    'março': 3,
    'abril': 4,
    'maio': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12
}

FluxoMes = DF_FluxoFiltrado.groupby(['Mês','Ano'])[['Fluxo de Pessoas', 'Fluxo de Pessoas AA']].sum().reset_index()
FluxoMes['Variação'] = round((FluxoMes['Fluxo de Pessoas'] / FluxoMes['Fluxo de Pessoas AA'] - 1) * 100, 2)
FluxoMes['Data'] = pd.to_datetime(FluxoMes['Ano'].astype(str) + '/' + FluxoMes['Mês'].str.lower().map(meses_dict).astype(str)+'/'+ '01')
FluxoMes = FluxoMes.sort_values(by='Data')
FluxoMes = FluxoMes.drop(columns=['Mês', 'Ano'])
FluxoMes = FluxoMes[['Data', 'Fluxo de Pessoas', 'Fluxo de Pessoas AA', 'Variação']]

figFluxo = px.line(
    FluxoMes,
    x='Data',
    y=['Fluxo de Pessoas', 'Fluxo de Pessoas AA'],
    markers=True,
    custom_data=['Variação'],
    color_discrete_map={'Fluxo de Pessoas':'#00b7db','Fluxo de Pessoas AA':'#000000'}
)
#
with col1:
  st.plotly_chart(figFluxo, use_container_width=True)

  
with col2:
    st.markdown(f'<div class="bloco-de-info" style = "margin: 2px auto;"><h3>Fluxo de Pessoas</h3><p>{DF_FluxoFiltrado['Fluxo de Pessoas'].sum().astype(int)}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bloco-de-info" style = "margin: 2px auto;"><h3>Variação AA</h3><p>{round((DF_FluxoFiltrado['Fluxo de Pessoas'].sum()/DF_FluxoFiltradoAA['Fluxo de Pessoas'].sum()-1)*100,2)}%</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bloco-de-info" style = "margin: 2px auto;"><h3>Média por mês</h3><p>{DF_FluxoFiltrado.groupby('Mês')['Fluxo de Pessoas'].sum().mean().astype(int)}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bloco-de-info" style = "margin: 2px auto;"><h3>Fluxo de carros</h3><p>{DF_FluxoFiltrado['Fluxo de Carros'].sum().astype(int)}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bloco-de-info" style = "margin: 2px auto;"><h3>Receita</br>Estacionamento</h3><p>R${round(DF_FluxoFiltrado['Receita Total Sistema'].sum()/1000,2)}k</p></div>', unsafe_allow_html=True)
with col3:
    st.plotly_chart(fig, use_container_width=True)


st.dataframe(DF_FluxoFiltrado, use_container_width=True, hide_index=True)