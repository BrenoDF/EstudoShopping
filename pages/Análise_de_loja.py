import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta



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
st.title("Análise de Loja")
hoje = date.today()
hoje = hoje.replace(day=1)

sliderIntervalo = st.sidebar.date_input("Período",
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

loja_selecionada = st.sidebar.selectbox(
    "Selecione a loja",
    df_apenaslojas_filtrado_final['ID'].unique(),
    placeholder="Selecione a loja",
    key='select_analise_loja'
)
loja = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]
classificacao_selecionada = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Classificação'].iloc[0]
segmento_selecionado = df_apenaslojas_filtrado_final[df_apenaslojas_filtrado_final['ID']==loja_selecionada]['Segmento'].iloc[0]
venda_media = loja['Venda'].mean()
loja = loja.groupby(['Luc','Nome Fantasia']).agg({
    'M2': 'last',
    'Venda': 'sum',
    'VendaAA': 'sum',
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

venda = arrendondador(loja['Venda'].item())
venda_aa = arrendondador(loja['VendaAA'].item())
aluguel = arrendondador(loja['Aluguel'].item())

if venda_aa == 0:
    variacao_venda = None  # ou 0, ou float('nan'), depende da sua regra de negócio
else:
    variacao_venda = arrendondador(((venda / venda_aa) * 100) - 1)

with open("painel_compacto_analise_loja.html", "r", encoding="utf-8") as f:
    html = f.read()

regras = {
      'Âncoras': 0.05, 
      'Conveniência / Serviços': 0.15, 
      'Satélites': 0.15, 
      'Semi Âncoras': 0.05,
      'Mega Lojas': 0.01,  
      'Entretenimento': 0.15, 
      'Quiosque':0.15
}
m2 = loja['M2'].item()
regra_map = regras[classificacao_selecionada]
venda_x_ideal = (loja['Venda'].item()/(loja['CTO Comum'].item()*regra_map)-1)*100
nome = loja['Nome Fantasia'].item()
venda_p_m2 = arrendondador(venda/m2)

html = html.replace('class="title">Nome_Loja', f'class="title">{nome}')
html = html.replace('class="value">venda_valor', f'class="value">{venda}')
html = html.replace('class="value">vendaaa_valor', f'class="value">{venda_aa}')
html = html.replace('class="value ok">var_venda_aa_valor', f'class="value {cls(variacao_venda)}">{variacao_venda}')
html = html.replace('class="value">venda_ideal_valor', f'class="value">{arrendondador(loja['CTO Comum'].item()*regra_map)}')
html = html.replace('class="value ok">venda_x_ideal_valor', f'class="value {cls(venda_x_ideal)}">{arrendondador(venda_x_ideal)}')
html = html.replace('class="value">venda_media_valor', f'class="value">{arrendondador(venda_media)}')
html = html.replace('class="metric-value">aluguel_valor', f'class="metric-value">{aluguel}')
html = html.replace('class="metric-value">m2_valor', f'class="metric-value">{m2}')
html = html.replace('class="metric-value">venda_por_m2_valor', f'class="metric-value">{venda_p_m2}')
html = html.replace('class="metric-value">venda_por_m2_valor', f'class="metric-value">{venda_p_m2}')


st.html(html)

