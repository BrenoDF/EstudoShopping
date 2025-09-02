import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
import streamlit.components.v1 as components


pd.options.display.float_format = '{:.2f}'.format
st.set_page_config(layout="wide",
page_title= 'Análise de Loja',
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

def cls(valor):
    if valor is None:
        return ''
    return 'ok' if valor >= 0 else 'warn'
def arrendondador(valor):
    return round(valor,2)

# -------------------------------SIDE BAR-------------------------------- #

## SIDE BAR ##

# -------------------------------/SIDE BAR-------------------------------- #
# st.title("Análise de Loja")
hoje = date.today()
hoje = hoje.replace(day=1)

sliderIntervalo = st.sidebar.date_input("Período",
                    value = (date(2025,1,1),df_final_fluxo[df_final_fluxo['Fluxo de Carros']>0].index.max()),
                    min_value=date(2018,1,1),
                    max_value=df_final_fluxo[df_final_fluxo['Fluxo de Carros']>0].index.max(),
                    format= "DD/MM/YYYY",
                    key='date_input1'
)
inicio, fim = sliderIntervalo
inicio = pd.to_datetime(inicio)
fim = pd.to_datetime(fim)

# ------------------------------- FILTRANDO O DF -------------------------------- #
df_apenaslojas_filtrado_final = df_final_apenaslojas[(df_final_apenaslojas['Data'] >= inicio) & (df_final_apenaslojas['Data'] < (fim+pd.offsets.MonthBegin(1)))]

loja_selecionada = st.sidebar.selectbox(
    "Selecione a loja",
    df_apenaslojas_filtrado_final['ID'].unique(),
    placeholder="Selecione a loja",
    index = None,
    key='select_analise_loja'
)


if loja_selecionada is None:
    st.warning("Por favor, selecione uma loja no menu lateral.")
else:


# ------------------------------- FILTRANDO O Fluxo (?) -------------------------------- #

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

    FluxoMes = df_final_fluxo.groupby(['Mês','Ano', 'Empreendimento'])[['Fluxo de Pessoas']].sum().reset_index()
    FluxoMes['Data'] = pd.to_datetime(FluxoMes['Ano'].astype(str) + '/' + FluxoMes['Mês'].str.lower().map(meses_dict).astype(str)+'/'+ '01')
    FluxoMes = FluxoMes.sort_values(by='Data')
    FluxoMes = FluxoMes.drop(columns=['Mês', 'Ano'])
    FluxoMes = FluxoMes[['Data', 'Fluxo de Pessoas', 'Empreendimento']]
    df_fluxo_filtrado_final = FluxoMes[(FluxoMes['Data'] >= inicio) & (FluxoMes['Data'] < (fim + pd.offsets.MonthBegin(1)))&(FluxoMes['Empreendimento']==df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Empreendimento'].iloc[0])]
    fluxo_pessoas = df_fluxo_filtrado_final['Fluxo de Pessoas'].sum()


    loja = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]
    tempo_operacao = (loja['Data que saiu'].min() - loja['Data que entrou'].min()).days // 30
    classificacao_selecionada = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Classificação'].iloc[0]
    segmento_selecionado = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Segmento'].iloc[0]
    piso_selecionado = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Piso'].iloc[0]
    lado_selecionado = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Lado'].iloc[0]
    venda_media_piso = df_apenaslojas_filtrado_final[(df_apenaslojas_filtrado_final['Piso']==piso_selecionado)]['Venda'].mean()
    venda_media_segmento = df_apenaslojas_filtrado_final[(df_apenaslojas_filtrado_final['Segmento']==segmento_selecionado)]['Venda'].mean()
    venda_media = loja['Venda'].mean()
    regras = {
        'Âncoras': 5, 
        'Conveniência / Serviços': 15, 
        'Satélites': 15, 
        'Semi Âncoras': 5,
        'Mega Lojas': 10,  
        'Entretenimento': 15, 
        'Quiosque':15
    }
    regra_map = regras[classificacao_selecionada]
    loja['Venda Ideal'] = loja['CTO Comum']*(regra_map/100)
    loja = loja.groupby(['Luc','Nome Fantasia']).agg({
        'M2': 'last',
        'Venda': 'sum',
        'VendaAA': 'sum',
        'Venda Ideal': 'sum',
        'Aluguel': 'sum',
        'Encargo Comum': 'sum',
        'F.Reserva Enc.Comum': 'sum',
        'I.P.T.U.': 'sum',
        'Água/Esgoto': 'sum',
        'Ar Condicionado':'sum',
        'Energia':'sum',
        'Multa EDNG (Empreendedor)': 'sum',
        'Seguro Parte Privativa': 'sum',
        'CTO Total': 'sum',
        'CTO Comum': 'sum',
        'Desconto': 'sum',
        'Inadimplência': 'sum',
        'Empreendimento': 'last'
        
    }).reset_index()

    m2 = loja['M2'].item()
    venda = arrendondador(loja['Venda'].item())
    venda_aa = arrendondador(loja['VendaAA'].item())
    aluguel = arrendondador(loja['Aluguel'].item())
    aluguel_m2 = arrendondador(loja['Aluguel'].item()/m2)

    if venda_aa == 0:
        variacao_venda = None  # ou 0, ou float('nan'), depende da sua regra de negócio
    else:
        variacao_venda = arrendondador(((venda / venda_aa) -1) * 100)

    nome = loja['Nome Fantasia'].item()
    venda_p_m2 = arrendondador(venda/m2)
    if loja['CTO Comum'].item() == 0 or loja['Venda'].item() == 0:
        venda_por_cto_comum = 0
    else:
        venda_por_cto_comum = arrendondador((loja['CTO Comum'].item()/loja['Venda'].item())*100)

    # Gráfico:
    loja_melted = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]
    loja_melted = loja_melted.melt(id_vars=['Data'], value_vars=['Venda', 'VendaAA'], var_name='Tipo de Venda', value_name='Valor da Venda')
    fig = px.bar(
        loja_melted,
        x="Data",
        y="Valor da Venda",
        color="Tipo de Venda",
        title=f"Vendas de {loja_selecionada} ao longo do período",
        barmode="group",
        color_discrete_sequence=["#1f77b4", "#383838"]
    )
    ########################################
    with open("painel_compacto_analise_loja.html", "r", encoding="utf-8") as f:
        html = f.read()


    html = html.replace('class="title">Nome_Loja', f'class="title">{nome}')
    html = html.replace('class="value">venda_valor', f'class="value">{venda}')
    html = html.replace('class="value">vendaaa_valor', f'class="value">{venda_aa}')
    html = html.replace('class="value ok">var_venda_aa_valor', f'class="value {cls(variacao_venda)}">{variacao_venda}{"%" if variacao_venda is not None else ""}')
    html = html.replace('class="value">m2_valor', f'class="value muted">{m2}')
    html = html.replace('class="value">venda_ideal_valor', f'class="value">{arrendondador(loja["Venda Ideal"].item())}')
    html = html.replace('class="value">venda_media_valor', f'class="value">{arrendondador(venda_media)}')
    html = html.replace('class="metric-value">aluguel_valor', f'class="metric-value muted">{aluguel}')
    html = html.replace('class="metric-value">venda_por_m2_valor', f'class="metric-value muted">{venda_p_m2}')
    html = html.replace('class="metric-value ok">venda_por_cto_comum_valor', f'class="metric-value {"ok" if venda_por_cto_comum<=regra_map else "warn"}">{venda_por_cto_comum}%')
    html = html.replace('class="metric-value warn">inadimplencia_mes_valor', f'class="metric-value {'muted' if loja["Inadimplência"].item() == 0 else 'warn'}">{arrendondador(loja["Inadimplência"].item())}')
    html = html.replace('class="metric-value warn">desconto_valor', f'class="metric-value {'muted' if loja["Desconto"].item() == 0 else 'warn'}">{arrendondador(loja["Desconto"].item())}')
    html = html.replace('class="metric-value">cto_comum_valor', f'class="metric-value muted">{arrendondador(loja["CTO Comum"].item())}')
    html = html.replace('class="metric-value">cto_total_valor', f'class="metric-value muted">{arrendondador(loja["CTO Total"].item())}')
    html = html.replace('class="metric-value">cto_comum_por_m2', f'class="metric-value muted">{arrendondador(loja["CTO Comum"].item()/m2)}')
    html = html.replace('class="metric-value muted">segmento_e_piso', f'class="metric-value muted">{segmento_selecionado} / {piso_selecionado} - {lado_selecionado}')
    html = html.replace('class="metric-value">venda_media_segmento', f'class="metric-value muted">{arrendondador(venda_media_segmento)}')
    html = html.replace('class="metric-value">venda_media_piso', f'class="metric-value muted">{arrendondador(venda_media_piso)}')
    html = html.replace('class="metric-value">aluguel_m2_valor', f'class="metric-value muted">{aluguel_m2}')
    html = html.replace('class="metric-value muted">tempo_op_valor', f'class="metric-value muted">{tempo_operacao} meses aprox.')


    html = html.replace("<!-- GRAFICO_AQUI -->", f'{fig.to_html(full_html=False, include_plotlyjs="cdn")}')


    components.html(html, height=900)

    # ---------------------------    Tabela     -------------------------------- #

    loja_sem_agrupamento = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]
    loja_sem_agrupamento = loja_sem_agrupamento[['Data', 'Nome Fantasia', 'M2', 'Venda', 'VendaAA', '% Venda AA', 'Venda/M²', 
                                                'Aluguel', 'CTO Comum', 'CTO Comum/Venda', 'CTOcomum/M²', 'CTO Total', 'Desconto', 'Inadimplência']]

    st.dataframe(loja_sem_agrupamento, hide_index=True, use_container_width=True)