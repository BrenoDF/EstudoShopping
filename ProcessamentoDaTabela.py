import pandas as pd
import streamlit as st
import numpy as np


# ------ CONSTRUÇÃO DA TABELA USADA -------- #
path1 = 'Banco de dados.xlsx'
pathFluxoVS = 'Controle Tesouraria Viashopping.xlsx'
pathFluxoVB = 'Controle Tesouraria Viabrasil.xlsx'


@st.cache_data
def TabelaOriginal(emp):
    if emp == 'Viashopping':
        Composicao = pd.read_excel(path1, sheet_name='ComposicaoBoletoVS')
        ClassVS = pd.read_excel(path1, sheet_name='ClassBar')
        PosicaoVS = pd.read_excel(path1, sheet_name='PosicaoBar')
        df_fluxo = pd.read_excel(pathFluxoVS)
    elif emp == 'Viabrasil':
        Composicao = pd.read_excel(path1, sheet_name='ComposicaoBoletoVB')
        ClassVS = pd.read_excel(path1, sheet_name='ClassPamp')
        PosicaoVS = pd.read_excel(path1, sheet_name='PosicaoPamp')
        df_fluxo = pd.read_excel(pathFluxoVB)


    ComposicaoData = Composicao["Data"]
    Composicao = Composicao.iloc[:,4:-4]
    Composicao['Data'] = ComposicaoData
    Composicao['ID'] = Composicao['Luc'].astype(str) + "_" + Composicao['Nome Fantasia']
    Composicao['ID'] = Composicao['ID'].str.upper()


    ClassVS.drop(columns = ['Empreendimento', 'ID_Class', 'Tempo permanência'], inplace= True)
    ClassVS["ID"] = ClassVS["Luc"].astype(str) + "_" + ClassVS['Nome Fantasia']
    ClassVS["ID"] = ClassVS['ID'].str.upper()
    ClassVS.drop(columns = ['Luc', 'Nome Fantasia', 'M2'], inplace= True)
    CompClassVS = pd.merge(Composicao, ClassVS, on = 'ID', how='left')


    PosicaoVS.drop(columns = ['Empreendimento', 'ID_Posicao'], inplace= True)

    CompClassPosVs = pd.merge(CompClassVS, PosicaoVS, on = 'Luc', how='left')

# ------- FINAL DA CONSTRUÇÃO DA TABELA ORIGINAL -------- #

# ------- FLUXO ------ #
    DF_Fluxo = df_fluxo[['Data','Mês','Ano', 'Fluxo Total', 'Receita Total Sistema', 'Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções']].copy()
    DF_Fluxo = DF_Fluxo.dropna(subset=['Fluxo Total'])
    DF_Fluxo['Fluxo de Pessoas'] = [round(((x*2.8)/0.65)) for x in DF_Fluxo['Fluxo Total']]
    DF_Fluxo['Data'] = pd.to_datetime(DF_Fluxo['Data'], dayfirst= True, format='%d/%m/%Y')
    DF_Fluxo = DF_Fluxo.sort_values(by = 'Data', ascending= False)
    DF_Fluxo['Ano'] = DF_Fluxo['Ano'].astype(int).astype(str)
    DF_Fluxo['Dia'] = DF_Fluxo['Data'].dt.day.astype(int).astype(str)
    DF_Fluxo.rename(columns = {'Fluxo Total':'Fluxo de Carros'}, inplace = True)
    DF_Fluxo['Data'] = pd.to_datetime(DF_Fluxo['Data'])
    DF_Fluxo = DF_Fluxo[['Data', 'Dia', 'Mês', 'Ano', 'Fluxo de Carros', 'Fluxo de Pessoas', 'Receita Total Sistema', 'Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções']].set_index('Data')
# -------  FIM FLUXO ------ #
# ------- CONSTRUÇÃO DA TABELA MAIN --------#
    CompClassPosVs['VendaAA'] = CompClassPosVs.groupby('ID')['Venda'].shift(12)
    CompClassPosVs.drop(columns = ['Corredor'], inplace = True)
    CompClassPosVs['% Venda AA'] =  [(((v / vAA)-1)*100) if v != 0 and pd.notna(vAA) and vAA != 0 else np.nan for v, vAA in zip(CompClassPosVs['Venda'], CompClassPosVs['VendaAA'])]
    CompClassPosVs['% Venda AA'] = [str(round(x, 2)) + '%' if pd.notna(x) else x for x in CompClassPosVs['% Venda AA']]
    CompClassPosVs = CompClassPosVs[~CompClassPosVs['Luc'].str.contains(r'[DMX]', na = False, case = False)]
    CompClassPosVs['Aluguel'] = [
        (x + y) if (id_val != '1016_1001 FESTAS' and id_val != '1009_ATACAREJÃO DO LAR') else (x + y + z)
        for x, y, z, id_val in zip(
            CompClassPosVs['Aluguel Mínimo'],
            CompClassPosVs['Aluguel Percentual'],
            CompClassPosVs['Aluguel Complementar'],
            CompClassPosVs['ID']
        )
    ]
    CompClassPosVs['CTO Comum'] = CompClassPosVs['Aluguel'] + CompClassPosVs['Fundo Promoção'] + CompClassPosVs['Encargo Comum'] + CompClassPosVs['F.Reserva Enc.Comum']
    CompClassPosVs.rename(columns = {'Total': 'CTO Total'}, inplace = True)
    CompClassPosVs['Venda/M²'] = CompClassPosVs['Venda'] / CompClassPosVs['M2']
    CompClassPosVs['CTOcomum/M²'] = CompClassPosVs['CTO Comum'] / CompClassPosVs['M2']
    CompClassPosVs['CTO Total/M²'] = CompClassPosVs['CTO Total'] / CompClassPosVs['M2']
    CompClassPosVs['CTO Total/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPosVs['CTO Total'] , CompClassPosVs['Venda'])]
    CompClassPosVs['CTO Comum/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPosVs['CTO Comum'] , CompClassPosVs['Venda'])]


    DF_ApenasLojas = CompClassPosVs[~CompClassPosVs['Luc'].str.contains(r'[DMX]', na = False, case = False)]

# ------ FIM DA CONSTRUÇÃO DA TABELA MAIN ------ #


# ------- TABELA DO MÊS ----- #
    # DesempenhoMes = CompClassPosVs[['Data', 'Venda']].groupby('Data').sum()
    # DesempenhoMes = DesempenhoMes.reset_index()
    # DesempenhoMes['VendaAA'] = DesempenhoMes['Venda'].shift(12)
    # DesempenhoMes = DesempenhoMes[['Data', 'VendaAA', 'Venda']]
    # DesempenhoMes['% Venda AA'] = [((x/y)-1)*100 for x, y in zip(DesempenhoMes['Venda'], DesempenhoMes['VendaAA'])]
    # DesempenhoMes['% Venda AA - Mes Anterior'] = DesempenhoMes['% Venda AA'].shift(1)
    # DesempenhoMes['Desempenho do Mês'] = [x-y for x, y in zip(DesempenhoMes['% Venda AA'], DesempenhoMes['% Venda AA - Mes Anterior'])]
    # DesempenhoMes = DesempenhoMes.merge(DF_Fluxo, on = 'Data', how = 'left')
    # DesempenhoMes['Faturamento por Pessoa'] = [round((x/y), 2) if y!=0 else np.nan for x, y in zip(DesempenhoMes['Venda'], DesempenhoMes['Fluxo de Carros'])]
# ------- FIM DA TABELA DO MÊS ----- #



    return (CompClassPosVs,DF_Fluxo, DF_ApenasLojas)
##################
