import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import date
import ProcessamentoDaTabela as ProcTab



pd.options.display.float_format = '{:.2f}'.format
st.set_page_config(layout="wide",
                   page_title= 'Inicio')

hoje = date.today()

emp = st.sidebar.radio(    "Selecione o Empreendimento",
    options=['Viashopping', 'Viabrasil'], index = 0)

ResumoLojas, DF_Fluxo_Mensal, DF_ApenasLojas_main = ProcTab.TabelaOriginal(emp)


#Título

# st.markdown(
#     """
#     <h6>Grupo Na<sub style="color: #00b7db; font-weight: bold" > V </sub>a</h6>
#     """,
#     unsafe_allow_html=True
# )
# st.title("Relatório de Performance :blue[4.0]")
# st.divider()

# st.sidebar.header('Filtros')
# Empreendimento = st.sidebar.radio(
#    "Empreendimento", ['ViaShopping', 'ViaBrasil']
# )
# sliderIntervalo = st.sidebar.slider("Modifique o período",
#                      min_value=date(2018,1,1),
#                      max_value=date.today(),
#                      value = (date(2024,1,1), hoje),
#                      format= "MM YYYY"
# )

# segmentosUnicos = DF_ApenasLojas_main['Segmento'].unique().tolist()
# SegmentosSelecionados = st.sidebar.multiselect(
#         'Selecione os segmentos que deseja visualizar',
#     options=segmentosUnicos,
#     default=segmentosUnicos
# )


# inicio, fim = sliderIntervalo
# inicio = inicio.replace(day=1)
# fim = fim.replace(day=1)
# inicio = pd.to_datetime(inicio)
# fim = pd.to_datetime(fim)


# ##############   TABELAS    #######################
# ##VENDAS TOTAIS


# st.subheader("Vendas Totais (em milhões)", divider=False)

# col1, col2 = st.columns(2)

# dataLine = DesempenhoMes[['Data', 'VendaAA', 'Venda', '% Venda AA']]
# dataLine['Venda'] = dataLine['Venda'].apply(lambda x: round(x/1000000,3))
# dataLine['VendaAA'] = dataLine['VendaAA'].apply(lambda x: round(x/1000000,3))
# dataLine = dataLine.melt(id_vars = ['Data', '% Venda AA'], value_vars=["Venda", "VendaAA"],
#                   var_name="Série", value_name="Valor" )

# st.markdown(
#     """
#     <style>
#       /* Altera a fonte do título do slider ("Período") */
#     label[for^="slider"] {
#         font-size: 1px !important;
#     }
#     /* Altera os valores exibidos acima da barra do slider */
#     .stSlider span {
#         font-size: 3px !important;
#     }

#     /* Altera os labels abaixo da barra do slider (data inicial e final) */
#     .stSlider div[data-baseweb="slider"] > div > div {
#         font-size: 0px !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )




# data_filtrada = dataLine[
#     (dataLine['Data'] >= inicio) &
#     (dataLine['Data'] <= fim)
# ]

# figVendatotal = px.line(data_filtrada, x='Data', y='Valor', color = 'Série', color_discrete_sequence=['#00b7db', '#000000'], hover_data = {'% Venda AA': ':.2f'})



# with col1:
#     st.plotly_chart(figVendatotal)


# with col2:


#     filtro = (
#         (DF_ApenasLojas_main['Data'] <= fim) &
#         (DF_ApenasLojas_main['Data'] >= inicio) &
#         (DF_ApenasLojas_main['Segmento'].isin(SegmentosSelecionados))
#     )
#     df_top10 = (
#         DF_ApenasLojas_main.loc[filtro].groupby(['ID', 'Segmento'])
#         .agg({'Venda': 'sum'})
#         .sort_values(by='Venda', ascending=True)
#         .tail(10).reset_index()
#     )
#     fig = px.bar(
#         df_top10,
#         x='Venda',
#         y='ID',
#         orientation='h'
#     )

#     st.plotly_chart(fig, use_container_width=True)

# st.divider()


# # ####### Aceleração de crescimento do ViaShopping

# # st.subheader('Aceleração de crescimento')
# # st.markdown('Percentual de venda / venda a.a comparada mês a mês. :blue-background[Quanto mais tempo acima da linha 0, maior o crescimento do empreendimento]')
# # DesempenhoMesComZero = DesempenhoMes[(DesempenhoMes['Data'] >= inicio)&(DesempenhoMes['Data'] <= fim)].iloc[:,:-2]
# # DesempenhoMesComZero['Zero'] = 0
# # DesempenhoMesComZero.set_index('Data', inplace=True)

# # st.line_chart(DesempenhoMesComZero[['Desempenho do Mês', 'Zero']] )


# # st.divider()


# ##VENDA POR SEGMENTO
# # Classificacoes = ['Satelites', 'Âncoras', 'Conveniência / Serviços', 'Semi Âncoras', 'Mega Lojas', 'Entretenimento', 'Quiosque', 'Praça de Alimentação']

# # fig2 = make_subplots(rows=4, cols=2, subplot_titles=(Classificacoes), vertical_spacing = 0.09)

# # fig2.add_trace(px.line(Satelite [(Satelite['Data']>=inicio)&(Satelite['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).update_traces(name='Venda', showlegend=True).data[0], row=1, col=1)
# # fig2.add_trace(px.line(Ancoras  [(Ancoras['Data']>=inicio)&(Ancoras['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=1, col=2)
# # fig2.add_trace(px.line(ConvServ [(ConvServ['Data']>=inicio)&(ConvServ['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=2, col=1)
# # fig2.add_trace(px.line(Semi     [(Semi['Data']>=inicio)&(Semi['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=2, col=2)
# # fig2.add_trace(px.line(Mega     [(Mega['Data']>=inicio)&(Mega['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=3, col=1)
# # fig2.add_trace(px.line(Entret   [(Entret['Data']>=inicio)&(Entret['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=3, col=2)
# # fig2.add_trace(px.line(Quiosque [(Quiosque['Data']>=inicio)&(Quiosque['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=4, col=1)
# # fig2.add_trace(px.line(Praca    [(Praca['Data']>=inicio)&(Praca['Data']<=fim)], x='Data', y='Venda', hover_data = 'Lojas', color_discrete_sequence=['#00b7db']).data[0], row=4, col=2)

# # fig2.add_trace(px.line(Satelite [(Satelite['Data']>=inicio)&(Satelite['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).update_traces(name='Venda AA', showlegend=True).data[0], row=1, col=1)
# # fig2.add_trace(px.line(Ancoras  [(Ancoras['Data']>=inicio)&(Ancoras['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=1, col=2)
# # fig2.add_trace(px.line(ConvServ [(ConvServ['Data']>=inicio)&(ConvServ['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=2, col=1)
# # fig2.add_trace(px.line(Semi     [(Semi['Data']>=inicio)&(Semi['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=2, col=2)
# # fig2.add_trace(px.line(Mega     [(Mega['Data']>=inicio)&(Mega['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=3, col=1)
# # fig2.add_trace(px.line(Entret   [(Entret['Data']>=inicio)&(Entret['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=3, col=2)
# # fig2.add_trace(px.line(Quiosque [(Quiosque['Data']>=inicio)&(Quiosque['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=4, col=1)
# # fig2.add_trace(px.line(Praca    [(Praca['Data']>=inicio)&(Praca['Data']<=fim)], x='Data', y='Venda AA', hover_data = 'Lojas', color_discrete_sequence=['black']).data[0], row=4, col=2)


# # fig2.update_layout(height=1000, width = 800)


# # fig2.update_yaxes(
# #     tickmode = 'linear',
# #     tick0 = 200000,
# #     dtick = 500000,
# #     row=6,
# #     col=1
# # )

# # fig2.update_layout(
# #     paper_bgcolor = 'white',
# #     plot_bgcolor = 'white',
# #     title = dict(
# #         font = dict(
# #             size = 20,
# #             color = 'black'
# #         ),
# #         text = 'Vendas Totais por Segmento'
# #     ),
# #     hoverlabel = dict(
# #         bgcolor = 'white',
# #         font = dict(
# #             color = 'black',
# #             weight = 1,
# #             size = 10
# #         )
# #     ),
# #     margin_pad = 5,
# #     legend=dict(
# #         x=0.5,
# #         y=1.05,
# #         xanchor='center',
# #         yanchor='bottom',
# #         orientation='h'
# #     )
# # )



# # fig2.update_yaxes(title_text='Venda',
# #                  tickfont=dict(size=10, weight=300, color='black'),
# #                  title = dict(font_color =  '#2a3e4a',
# #                               standoff = 10,
# #                               font_size = 12)
# #                  )
# # fig2.update_xaxes(
# #     tickfont=dict(size=10, weight=300, color='black'),
# #     title = dict(
# #     text = 'Data',
# #     font_color =  '#2a3e4a',
# #     standoff = 20,
# #     font_size = 12
# #     )
# # )


# # st.plotly_chart(fig2)

# TabelaResumoLojas = ResumoLojas[
#     (ResumoLojas['Data'] >= inicio) &
#     (ResumoLojas['Data'] <= fim) &
#     (ResumoLojas['Segmento'].isin(SegmentosSelecionados))
#     ].iloc[:,:-3]

# TabelaResumoLojas
# st.divider()

# ###### BOXPLOT DAS LOJAS POR SEGMENTO

# st.header("Lojas que se destacaram: ")

# dtBoxPlot = st.date_input("Mês:", date(hoje.year, hoje.month - 1, 1), format = 'DD/MM/YYYY')
# dtBoxPlot = pd.to_datetime(dtBoxPlot)

# boxplotSegmentos = ResumoLojas[(ResumoLojas['Venda'] > 0)&(ResumoLojas['Data'] == dtBoxPlot)&(ResumoLojas['Nome Fantasia']!= 'SUPERMERCADOS BH')]


# figBox = go.Figure()
# figBox.add_trace(px.box(boxplotSegmentos, x='Segmento', y='Venda', hover_data ='Nome Fantasia', title = 'Outliers').data[0])

# figBox.update_layout(
#     boxgap = 0.5,
#     boxgroupgap = 0.5,
#     width = 900,
#     title_text="Outliers nas Vendas do ViaShopping"
# )

# figBox.add_annotation(
#     x = 1,
#     y = 1.05,
#     xref = 'paper',
#     yref = 'paper',
#     text = '<i>*Supermercados BH removido para uma melhor precisão</i>',
#     font = dict(size = 10, color = 'gray'),
#     showarrow = False
# )

# figBox.update_xaxes(
#     tickfont=dict(size=10, weight=300, color='black'),
# )


# st.plotly_chart(figBox)


# st.divider()

# st.header("Lojas que entradam e saíram:")

# st.markdown("")


# ####### FATURAMENTO POR PESSOA

# fig3 = go.Figure()

# fig3.add_trace(go.Scatter(x=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2023]['Data'].dt.strftime('%b'),
#                          y=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2023]['Faturamento por Pessoa'],
#                          name = '2023', mode = 'lines'))
# fig3.add_trace(go.Scatter(x=DesempenhoMes[(DesempenhoMes['Data'].dt.year == 2024)&(DesempenhoMes['Data'] != '2024-08-01')]['Data'].dt.strftime('%b'),
#                          y=DesempenhoMes[(DesempenhoMes['Data'].dt.year == 2024)&(DesempenhoMes['Data'] != '2024-08-01')]['Faturamento por Pessoa'],
#                          name = '2024', mode = 'lines'))

# fig3.add_trace(go.Scatter(x=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2022]['Data'].dt.strftime('%b'),
#                          y=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2022]['Faturamento por Pessoa'],
#                          name = '2022', mode = 'lines'))
# fig3.add_trace(go.Scatter(x=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2021]['Data'].dt.strftime('%b'),
#                          y=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2021]['Faturamento por Pessoa'],
#                          name = '2021', mode = 'lines'))

# fig3.add_trace(go.Scatter(x=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2025]['Data'].dt.strftime('%b'),
#                          y=DesempenhoMes[DesempenhoMes['Data'].dt.year == 2025]['Faturamento por Pessoa'],
#                          name = '2025', mode = 'lines'))




# fig3.update_layout(
#     title = dict(
#         text = 'Faturamento por Pessoa'
#     )
# )

# fig3.update_xaxes(
#     tickfont=dict(size=10, weight=300, color='black'),
#     title = dict(
#     text = 'Data',
#     font_color =  '#2a3e4a',
#     standoff = 30,
#     font_size = 12
#     )
# )

# fig3.update_yaxes(
#     tickfont=dict(size=10, weight=300, color='black'),
#     title = dict(
#     text = 'Venda (R$)',
#     font_color =  '#2a3e4a',
#     standoff = 10,
#     font_size = 12
#     )
# )

# fig3.add_annotation(
#     x= 1.09,
#     y = -0,
#     xref = 'paper',
#     yref = 'paper',
#     text = '<i>*O mês de Agosto<br>em 2024 foi removido<br>por erro no fluxo</i>',
#     align = 'left',
#     font = dict(size = 9, color = 'gray'),
#     showarrow=False
# )

# fig3.add_annotation(
#     x = 'Jul',
#     y = 126,
#     # y = SemAgosto24[(SemAgosto24['Data'].dt.strftime('%b') == "Jul")&(SemAgosto24['Data'].dt.year == 2024)]['Faturamento por Pessoa'].values[0],
#     xref = 'x',
#     yref = 'y',
#     text = 'Nos últimos dois anos,<br>julho (2024) foi o mês onde os<br>clientes mais compraram no Via',
#     align = 'left',
#     font = dict(size = 10, color = 'gray'),

# )
# st.plotly_chart(fig3)

# st.markdown(":gray[Faturamento por Pessoa são: Vendas divididas pelo nosso fluxo. Ou seja, :blue-background[quanto UM cliente compra em nosso estabelecimento], teoricamente.]")

# st.divider()

# @st.cache_data
# def Entrada_Saida():
#     EntradaSaida = ResumoLojas[['Nome Fantasia', 'Data que entrou', 'Data que saiu']]
#     df_entradas = EntradaSaida[["Data que entrou", "Nome Fantasia"]].rename(columns={"Data que entrou": "Data", "Nome Fantasia": "Entrou"})
#     df_saidas = EntradaSaida[["Data que saiu", "Nome Fantasia"]].rename(columns={"Data que saiu": "Data", "Nome Fantasia": "Saiu"})
#     df_saidas = df_saidas[df_saidas["Data"].dt.month != date.today().month-1]
#     EntradaSaida = pd.concat([df_entradas, df_saidas])
#     EntradaSaida = EntradaSaida.groupby("Data").agg(lambda x: ', '.join(x.dropna().unique())).reset_index()
#     EntradaSaida['Data'] = EntradaSaida['Data'].dt.strftime('%d/%m/%Y')
#     return EntradaSaida

# EntradaSaida = Entrada_Saida()

# coluna1, coluna2, coluna3 = st.columns([1,12,1])
# with coluna2:
#     EntradaSaida
# with coluna3:
#     st.markdown("<small>👈  Pesquise!</small>", unsafe_allow_html=True)
