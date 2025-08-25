import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from graphviz import Digraph
from dateutil.relativedelta import relativedelta

# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Relatório Nava',
initial_sidebar_state="collapsed")



# -------------------------------SIDE BAR-------------------------------- #


## SIDE BAR ##
st.sidebar.image(r'Imagens/NAVA-preta.png')

st.sidebar.header('Filtros')
emp = st.sidebar.radio("Selecione o Empreendimento",
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



## --------------------- Página principal ----------------------------------- ##


st.title("Relatório de Performance - Grupo NA:blue[v]A")

# Aplicando os Filtros do SideBar
filtroSideBar = ((DFLojas['Classificação'].isin(ClassificacaoSelecionada)) &
    (DFLojas['Piso'].isin(PisosSelecionados)) &
    ((LadoSelecionado == 'Ambos')
      |
      (DFLojas['Lado']==LadoSelecionado)
      ))

#Buscando o periodo de Ano Anterior
inicio_aa = inicio - relativedelta(years=1)
fim_aa    = fim    - relativedelta(years=1)

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



figVendatotal = px.line(
  mes_a_mes,
  x='Data',
  y=['Venda','VendaAA'],
  markers=True,
  custom_data=['Variação'],                
  color_discrete_map={'Venda':'#00b7db','VendaAA':'#000000'}, title='Vendas por Mês'
)

for trace in figVendatotal.data:
    if trace.name == 'Venda':
        trace.hovertemplate = (
            "Data: %{x|%d/%m/%Y}<br>"
            "Venda: R$ %{y:,.2f}<br>"
            "Variação: %{customdata[0]:.2f}%<extra></extra>"
        )
    else:
        trace.hovertemplate = (
            "Data: %{x|%d/%m/%Y}<br>"
            f"{trace.name}: R$ "+"%{y:,.2f}<extra></extra>"
        )

tabMain, tabDF =  st.tabs(["Resumos", "Tabelas"]) ## Criação das abas



with tabMain:
  st.title('Resumos')
  st.divider()
  st.header("Vendas Totais")
  col1, col2, col3 = st.columns([0.43,0.14,0.43], gap="large")
  with col1:
    figVendatotal.update_layout(height=450)
    st.plotly_chart(figVendatotal, use_container_width=True)
  with col2:
    st.metric(label="Vendas Totais",
                value=f"{round(mes_a_mes['Venda'].sum()/1000000,2)}M",
                delta=f"{round(variacao,2)}% / AA",
                width="content",
                border= True)
    st.metric(label="Vendas Ano Anterior",
                value=f"{round(mes_a_mes['VendaAA'].sum()/1000000,2)}M",
                width="content",
                border= True)
    st.metric(label="Operações Ativas", value=f"{len(DFLojasAtual['ID'].unique())} und.",
                width="content",
                border= True
                )

  with col3:
      DF_ApenasLojasSegmentos = (
      DFLojasAtual.groupby(['Data', 'Classificação'], as_index=False)
        [['Venda','VendaAA']]
        .sum().sort_values(by=['Data', 'Venda'], ascending=True)
        )
      
      DF_ApenasLojasSegmentos['Venda'] = DF_ApenasLojasSegmentos['Venda'].apply(lambda x: round(x, 2))
      DF_ApenasLojasSegmentos['VendaAA'] = DF_ApenasLojasSegmentos['VendaAA'].apply(lambda x: round(x, 2))
      
      
      
      DF_ApenasLojasSegmentos['Variacao'] = round((DF_ApenasLojasSegmentos['Venda'] / DF_ApenasLojasSegmentos['VendaAA'] - 1)*100,2)
      DF_ApenasLojasSegmentos['Variacao'] = DF_ApenasLojasSegmentos['Variacao'].apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}%")
      
      DF_ApenasLojasSegmentos['Data'] = DF_ApenasLojasSegmentos['Data'].dt.strftime('%m/%Y')
      
      ordem = DF_ApenasLojasSegmentos.groupby('Classificação')['Venda'].sum().sort_values(ascending=False).index.tolist()

      fig = px.bar(
          DF_ApenasLojasSegmentos,
          x='Venda',
          y='Classificação',
          orientation='h',
          hover_data=['VendaAA', 'Variacao', 'Data'],
          color='Classificação',
          color_discrete_sequence=px.colors.sequential.Blues[::-1],
          category_orders={'Classificação': ordem}, title='Vendas por Classificação',
      )
      fig.update_layout(height=450,
                        showlegend=False)
      st.plotly_chart(fig, use_container_width=True)

  

  st.divider()

        # ------------- PISO PISO PISO ----------------
  
  st.subheader("Vendas por Piso e Lado")


  pisos = ['PISO 1', 'PISO 2', 'PISO 3']
  lados = ['LADO A', 'LADO B']
  
  def resumo_bloco(piso, lado):
    LojasSemFiltroPiso_e_Lado = DFLojas.loc[(DFLojas['Segmento'].isin(ClassificacaoSelecionada)) & (DFLojas['Data'] >= inicio) & (DFLojas['Data'] <= fim)]
    LojasSemFiltroPiso_e_LadoAA = DFLojas.loc[(DFLojas['Segmento'].isin(ClassificacaoSelecionada)) & (DFLojas['Data'] >= inicio_aa) & (DFLojas['Data'] <= fim_aa)]

    ## SSS dos PISOS ##
    if sss:
      # depois de gerar DFLojasAtual e DFLojasAA -----------------------------

      for df in (LojasSemFiltroPiso_e_Lado, LojasSemFiltroPiso_e_LadoAA):
          df['month'] = df['Data'].dt.month        # 1) mês numérico

      # 2) pares (ID, month) presentes nos dois períodos
      pares_comuns = (
          LojasSemFiltroPiso_e_Lado[['ID', 'month']].drop_duplicates()
          .merge(LojasSemFiltroPiso_e_LadoAA[['ID', 'month']].drop_duplicates(),
                on=['ID', 'month'], how='inner')
      )

      # 3) aplica interseção – agora cada loja só tem meses em que existia nos DOIS anos
      LojasSemFiltroPiso_e_Lado = LojasSemFiltroPiso_e_Lado.merge(pares_comuns, on=['ID', 'month'], how='inner')
      LojasSemFiltroPiso_e_LadoAA    = LojasSemFiltroPiso_e_LadoAA.merge(pares_comuns, on=['ID', 'month'], how='inner')
      ## FIM DO SSS DOS PISOS ##
      
    
    LojasSemFiltroPiso_e_Lado = LojasSemFiltroPiso_e_Lado.groupby(['Data', 'Piso','Lado'], as_index=False)[['Venda','CTO Comum']].sum()
    LojasSemFiltroPiso_e_LadoAA = LojasSemFiltroPiso_e_LadoAA.groupby(['Data', 'Piso','Lado'], as_index=False)[['Venda']].sum()
    
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
    vendaAA_k  = ProcTab.formata_numero(soma_AA)
    venda_k    = ProcTab.formata_numero(soma)
    cto_k      = ProcTab.formata_numero(cto)
    cto_venda  = round(cto/soma*100, 2) if cto else 0
    variacao   = round((soma/soma_AA-1)*100, 2) if soma_AA else 0
    classeVarPiso = "positivo" if variacao >= 0 else "negativo"
    total_piso = round(
        (soma / DFLojas.loc[
          filtroDataSelecionada & DFLojas['Segmento'].isin(ClassificacaoSelecionada)
        ]['Venda'].sum()*100), 2
    ) if soma else 0

    return f"""
  <div class="info-bloco">
    <div><h4>{piso}</h4></div>
    <div class="linha">
      <div>VendaAA:<br><b>{vendaAA_k}</b></div>
      <div>Venda:<br><b>{venda_k}</b></div>
      <div>CTO c.:<br><b>{cto_k}</b></div>
      <div>CTO c./Venda:<br><b>{cto_venda}%</b></div>
    </div>
    <div class="linha-centralizada">
      <div>Variação:<br><span class="variacao {classeVarPiso}">{variacao}%</span></div>
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

  st.divider()
  st.subheader("Dados de Fluxo")


  colx, coly, colz = st.columns([0.4,0.15,0.4])
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
      title='Fluxo Categórico Agregado',
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
      title='Fluxo de Pessoas por Mês',
      custom_data=['Variação'],
      color_discrete_map={'Fluxo de Pessoas':'#00b7db','Fluxo de Pessoas AA':'#000000'}
  )
  #
  with colx:
    st.plotly_chart(figFluxo, use_container_width=True)
    

    
  with coly:
      st.metric('Fluxo de Pessoas', ProcTab.formata_numero(DF_FluxoFiltrado['Fluxo de Pessoas'].sum().astype(int)), 
                delta = f'{round((DF_FluxoFiltrado['Fluxo de Pessoas'].sum()/DF_FluxoFiltradoAA['Fluxo de Pessoas'].sum()-1)*100,2)}% / AA',
                width="stretch",
                border= True)
      st.metric('Média por mês', ProcTab.formata_numero(DF_FluxoFiltrado.groupby('Mês')['Fluxo de Pessoas'].sum().mean().astype(int)),
                width="stretch",
                border= True)
      st.metric('Fluxo de Carros', ProcTab.formata_numero(DF_FluxoFiltrado['Fluxo de Carros'].sum().astype(int)),
                width="stretch",
                border= True)
      st.metric('Receita', ProcTab.formata_numero(DF_FluxoFiltrado['Receita Total Sistema'].sum()),
                width="stretch",
                border= True)
      
  with colz:
      st.plotly_chart(fig, use_container_width=True)


with tabDF:
  st.title("Tabelas")
  st.divider()
  st.subheader("Tabela de Lojas")
  st.dataframe(DFLojasAtual, use_container_width=True, hide_index=True, column_config={
    'Data': st.column_config.DateColumn(
        format="DD/MM/YYYY"
    )
  } )
  st.divider()
  st.subheader("Tabela de Fluxo")
  st.dataframe(DF_FluxoFiltrado, use_container_width=True, hide_index=True)



## vvv CSS vvv ##
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
      }
      .positivo {
        color: #0056b3;
      }
      .negativo {
        color: #dc3545;
        }
      [data-testid="stMetric"] {
        display: grid;
        justify-content: center;
        align-items: center;
      }
      [data-testid="stMetricValue"] {
        font-size: 2.00rem;
      }
      
      [data-testid="metric-container"] {
          width: fit-content;
          margin: auto;
      }

      [data-testid="metric-container"] > div {
          width: fit-content;
          margin: auto;
      }

      [data-testid="metric-container"] label {
          width: fit-content;
          margin: auto;
      }
      </style>

      """, unsafe_allow_html=True)
