import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date


# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Relatório Nava',
initial_sidebar_state="collapsed")
st.logo('Imagens/NAVA-preta.png', icon_image='Imagens/NAVA-preta.png', size='large')

# ------------------------------- Trazendo o DF Completo -------------------------------- #

empresas = ['Viashopping', 'Viabrasil']

dfs_compclasspos = []
dfs_fluxo = []
dfs_apenaslojas = []

for emp in empresas:
    DF_Fluxo, DF_ApenasLojas = ProcTab.TabelaOriginal(emp)

    # anota a origem sem tocar na função
    DF_Fluxo = DF_Fluxo.copy()
    DF_ApenasLojas = DF_ApenasLojas.copy()

    DF_Fluxo['Empreendimento'] = emp
    DF_ApenasLojas['Empreendimento'] = emp

    dfs_fluxo.append(DF_Fluxo)
    dfs_apenaslojas.append(DF_ApenasLojas)

df_final_fluxo = pd.concat(dfs_fluxo)  # mantém o índice Data
df_final_apenaslojas = pd.concat(dfs_apenaslojas, ignore_index=True)


# ------------------------------- --------------------- -------------------------------- #


# -------------------------------SIDE BAR-------------------------------- #

## SIDE BAR ##
mostrar_legenda = st.sidebar.toggle('Legenda no gráfico de Pizza?', value = True, key='toggle_legenda')

# -------------------------------/SIDE BAR-------------------------------- #
comparativo_1, comparativo_2 = st.tabs(["Comparativo de Lojas", "Comparativo por Classificação e Tipo"])
with comparativo_1:
    st.title("Comparativo de Lojas")
    col1, col2, col3 = st.columns([0.2, 0.3, 0.5])
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
    if df_com_lojas_selecionadas.empty:
        st.warning("Nenhuma loja selecionada.")
    else:
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
        st.dataframe(df_com_lojas_selecionadas, use_container_width=True, hide_index=True)

    st.divider()

#------------------------------- Comparativo por Classificação -------------------------------- #
with comparativo_2:
    st.title("Comparativo de loja pelos tipos")
    col1, col2, col3, col4 = st.columns([0.35, 0.35, 0.2, 0.1])
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


    df_apenaslojas_filtrado_final_2 = df_final_apenaslojas[(df_final_apenaslojas['Data'] >= inicio2) & (df_final_apenaslojas['Data'] <= fim2)]


    with col2:

        lojas_selecionadas2 = st.selectbox(
            "Selecione a loja",
            df_apenaslojas_filtrado_final_2['ID'].unique(),
            index= None,
            placeholder="Selecione a loja",
            key='select2'
        )
        
    df_loja_selecionada_2 = df_apenaslojas_filtrado_final_2[df_apenaslojas_filtrado_final_2['ID']==(lojas_selecionadas2)]
    emp_selecionado = df_loja_selecionada_2['Empreendimento'].iloc[0] if not df_loja_selecionada_2.empty else None

    if df_loja_selecionada_2.empty:
        st.warning("Nenhuma loja selecionada.")
    else:
        class_selecionada = df_loja_selecionada_2['Classificação'].iloc[0]
        if class_selecionada == 'Satélites' or class_selecionada == 'Quiosque':
            opcoes_para_pills = ['Classificação', 'Segmento', 'Atividade']
        else:
            opcoes_para_pills = ['Classificação', 'Segmento']
            
        with col3:
            pills2 = st.pills(
                "Selecione o tipo de comparação",
                options=opcoes_para_pills,
                default='Classificação',
                key='pills2'
            )
        with col4:
            verba_selecionada2 = st.radio(
                "Selecione a verba",
                options=['Venda','CTO Comum']
            )
            
        tipo_loja_selecionado = df_apenaslojas_filtrado_final_2[df_apenaslojas_filtrado_final_2['ID']==(lojas_selecionadas2)][pills2].iloc[0]
        df_a_comparar = df_apenaslojas_filtrado_final_2[(df_apenaslojas_filtrado_final_2[pills2] == (tipo_loja_selecionado)) & (df_apenaslojas_filtrado_final_2['Empreendimento'] == emp_selecionado)]
        total_df_a_comparar = df_a_comparar[verba_selecionada2].sum()
        total_loja_selecionada = df_loja_selecionada_2[verba_selecionada2].sum()
        delta_comparativo = ((total_loja_selecionada/total_df_a_comparar) *100).round(2) if total_df_a_comparar != 0 else 0
        
        coluna1, coluna2 = st.columns([0.5, 0.5])
        subcoluna1, subcoluna2, subcoluna3 = st.columns([0.1, 0.8, 0.1])
        media_todas_lojas = df_a_comparar[verba_selecionada2].mean()
        media_loja_unica = df_loja_selecionada_2[verba_selecionada2].mean()
        
        with coluna1:
            fig2 = px.pie(df_a_comparar, names='ID', values=verba_selecionada2, title=f'Participação de {lojas_selecionadas2} em {tipo_loja_selecionado} no {emp_selecionado}').update_traces(textposition='inside', textinfo='percent+label')
            pull = [0.2 if loja == lojas_selecionadas2 else 0 for loja in df_a_comparar['ID']]
            texto = [loja if loja == lojas_selecionadas2 else '' for loja in df_a_comparar['ID']]
            fig2.update_traces(pull=pull, text = texto, textfont_size=14, textinfo="text+percent")
            fig2.update_layout(showlegend=mostrar_legenda)
            st.plotly_chart(fig2, key='grafico_pizza', use_container_width=True)
        with coluna2:
            df_grafico_bar_fig3 = pd.DataFrame({'Média das Lojas': [media_todas_lojas], f'{lojas_selecionadas2}': [media_loja_unica]})
            fig3 = px.bar(df_grafico_bar_fig3,barmode='group' , title=f'Venda média por loja comparado a média de {lojas_selecionadas2} em {tipo_loja_selecionado} no {emp_selecionado}')
            fig3.update_layout(xaxis_title=None, yaxis_title=None, legend = {'orientation': 'h'})
            st.plotly_chart(fig3, key='grafico_barra', use_container_width=True)
        with subcoluna2:    
            st.markdown(f"A loja :blue-background[{lojas_selecionadas2}] compõem cerca de :blue[{delta_comparativo}%] de {verba_selecionada2} comparado a {tipo_loja_selecionado} e uma diferença de **R${abs(media_loja_unica-media_todas_lojas).round(2)}** na média entre eles no {emp_selecionado}.", width="stretch")
            st.toggle("Expandir tabela", key='toggle_tabela_comparativo1')
        if st.session_state['toggle_tabela_comparativo1']:
            st.dataframe(df_a_comparar, use_container_width=True, hide_index=True)

    ##------------------------------- Comparativo por Piso -------------------------------- #

        st.subheader("Comparativo por Piso")
        piso_loja_selecionada = df_loja_selecionada_2['Piso'].iloc[0]
        lado_loja_selecionada = df_loja_selecionada_2['Lado'].iloc[0]
        
        st.radio("Comparar com todas as lojas do piso ou apenas do mesmo tipo?",
                options=['Mesmo Tipo', 'Todas as Lojas do Piso'],
                key='radio_piso',
                horizontal=True)
        if st.session_state['radio_piso'] == 'Mesmo Tipo':
            df_a_comparar_com_piso = df_apenaslojas_filtrado_final_2[(df_apenaslojas_filtrado_final_2[pills2] == (tipo_loja_selecionado)) 
                                                                & (df_apenaslojas_filtrado_final_2['Empreendimento'] == emp_selecionado) 
                                                                & (df_apenaslojas_filtrado_final_2['Piso'] == piso_loja_selecionada)
                                                                & (df_apenaslojas_filtrado_final_2['Lado'] == lado_loja_selecionada)]
        elif st.session_state['radio_piso'] == 'Todas as Lojas do Piso':
            df_a_comparar_com_piso = df_apenaslojas_filtrado_final_2[(df_apenaslojas_filtrado_final_2['Empreendimento'] == emp_selecionado)
                                                                            & (df_apenaslojas_filtrado_final_2['Piso'] == piso_loja_selecionada)
                                                                            & (df_apenaslojas_filtrado_final_2['Lado'] == lado_loja_selecionada)]
            
        media_todas_lojas_piso = df_a_comparar_com_piso[verba_selecionada2].mean()
        coluna_piso1, coluna_piso2 = st.columns([0.5,0.5])
        subcoluna1_piso, subcoluna2_piso, subcoluna3_piso = st.columns([0.1, 0.8, 0.1])
        with coluna_piso1:
            fig4 = px.pie(df_a_comparar_com_piso, names='ID', values=verba_selecionada2, title=f'Participação de {lojas_selecionadas2} no {piso_loja_selecionada} no {emp_selecionado}').update_traces(textposition='inside', textinfo='percent+label')
            pull = [0.2 if loja == lojas_selecionadas2 else 0 for loja in df_a_comparar_com_piso['ID']]
            texto = [loja if loja == lojas_selecionadas2 else '' for loja in df_a_comparar_com_piso['ID']]
            fig4.update_traces(pull=pull, text = texto, textfont_size=14, textinfo="text+percent")
            fig4.update_layout(showlegend=mostrar_legenda)
            st.plotly_chart(fig4, key='grafico_pizzaPiso', use_container_width=True)

        with coluna_piso2:
            df_grafico_bar_fig3 = pd.DataFrame({'Média das Lojas': [media_todas_lojas_piso], f'{lojas_selecionadas2}': [media_loja_unica]})
            fig3 = px.bar(df_grafico_bar_fig3,barmode='group' , title=f'Venda média por loja comparado a média de {lojas_selecionadas2} no {piso_loja_selecionada} no {emp_selecionado}')
            fig3.update_layout(xaxis_title=None, yaxis_title=None, legend = {'orientation': 'h'})
            st.plotly_chart(fig3, key='grafico_barraPiso', use_container_width=True)
        with subcoluna2_piso:
            st.toggle("Expandir tabela", key='toggle_tabela_comparativo2')
        if st.session_state['toggle_tabela_comparativo2']:
            st.dataframe(df_a_comparar_com_piso, use_container_width=True, hide_index=True)




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