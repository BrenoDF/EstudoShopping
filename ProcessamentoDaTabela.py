import pandas as pd
import streamlit as st
import numpy as np


# ------ CONSTRUÇÃO DA TABELA USADA -------- #
path1 = 'Banco de dados.xlsx'
path2 = path1
path3 = path1
pathFluxo = 'Controle Tesouraria Viashopping.xlsx'

@st.cache_data
def TabelaOriginal():
    
    ComposicaoVS = pd.read_excel(path1)


    ComposicaoVSData = ComposicaoVS["Data"]
    ComposicaoVS = ComposicaoVS.iloc[:,4:-4]
    ComposicaoVS['Data'] = ComposicaoVSData
    ComposicaoVS['ID'] = ComposicaoVS['Luc'].astype(str) + "_" + ComposicaoVS['Nome Fantasia']
    ComposicaoVS['ID'] = ComposicaoVS['ID'].str.upper()


    ClassVS = pd.read_excel(path2, sheet_name='ClassBar')
    ClassVS.drop(columns = ['Empreendimento', 'ID_Class', 'Tempo permanência'], inplace= True)
    ClassVS["ID"] = ClassVS["Luc"].astype(str) + "_" + ClassVS['Nome Fantasia']
    ClassVS["ID"] = ClassVS['ID'].str.upper()
    ClassVS.drop(columns = ['Luc', 'Nome Fantasia', 'M2'], inplace= True)
    CompClassVS = pd.merge(ComposicaoVS, ClassVS, on = 'ID', how='left')


    PosicaoVS = pd.read_excel(path3, sheet_name='PosicaoBar')
    PosicaoVS.drop(columns = ['Empreendimento', 'ID_Posicao'], inplace= True)

    CompClassPosVs = pd.merge(CompClassVS, PosicaoVS, on = 'Luc', how='left')

# ------- FINAL DA CONSTRUÇÃO DA TABELA ORIGINAL -------- #

# ------- FLUXO ------ #
    df_fluxo = pd.read_excel(pathFluxo)
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
    DesempenhoMes = CompClassPosVs[['Data', 'Venda']].groupby('Data').sum()
    DesempenhoMes = DesempenhoMes.reset_index()
    DesempenhoMes['VendaAA'] = DesempenhoMes['Venda'].shift(12)
    DesempenhoMes = DesempenhoMes[['Data', 'VendaAA', 'Venda']]
    DesempenhoMes['% Venda AA'] = [((x/y)-1)*100 for x, y in zip(DesempenhoMes['Venda'], DesempenhoMes['VendaAA'])]
    DesempenhoMes['% Venda AA - Mes Anterior'] = DesempenhoMes['% Venda AA'].shift(1)
    DesempenhoMes['Desempenho do Mês'] = [x-y for x, y in zip(DesempenhoMes['% Venda AA'], DesempenhoMes['% Venda AA - Mes Anterior'])]
    DesempenhoMes = DesempenhoMes.merge(DF_Fluxo, on = 'Data', how = 'left')
    DesempenhoMes['Faturamento por Pessoa'] = [round((x/y), 2) if y!=0 else np.nan for x, y in zip(DesempenhoMes['Venda'], DesempenhoMes['Fluxo de Carros'])]
# ------- FIM DA TABELA DO MÊS ----- #



    return (CompClassPosVs,DesempenhoMes,DF_Fluxo, DF_ApenasLojas)
##################
#####ViaBrasil#####
##################


# @st.cache_data
# def TabelaOriginalVB():
    
#     ComposicaoVB = pd.read_excel(path1)


#     ComposicaoVBData = ComposicaoVB["Data"]
#     ComposicaoVB = ComposicaoVB.iloc[:,4:-4]
#     ComposicaoVB['Data'] = ComposicaoVBData
#     ComposicaoVB['ID'] = ComposicaoVB['Luc'].astype(str) + "_" + ComposicaoVB['Nome Fantasia']
#     ComposicaoVB['ID'] = ComposicaoVB['ID'].str.upper()


#     ClassVB = pd.read_excel(path2, sheet_name='ClassPamp')
#     ClassVB.drop(columns = ['Empreendimento', 'ID_Class', 'Tempo permanência'], inplace= True)
#     ClassVB["ID"] = ClassVB["Luc"].astype(str) + "_" + ClassVB['Nome Fantasia']
#     ClassVB["ID"] = ClassVB['ID'].str.upper()
#     ClassVB.drop(columns = ['Luc', 'Nome Fantasia', 'M2'], inplace= True)
#     CompClassVB = pd.merge(ComposicaoVB, ClassVB, on = 'ID', how='left')


#     PosicaoVB = pd.read_excel(path3, sheet_name='PosicaoPamp')
#     PosicaoVB.drop(columns = ['Empreendimento', 'ID_Posicao'], inplace= True)

#     CompClassPosVB = pd.merge(CompClassVB, PosicaoVB, on = 'Luc', how='left')

#     # ------- CONSTRUÇÃO DA TABELA MAIN --------#
#     CompClassPosVb['VendaAA'] = CompClassPosVb.groupby('ID')['Venda'].shift(12)
#     CompClassPosVb.drop(columns = ['Corredor'], inplace = True)
#     CompClassPosVb['% Venda AA'] =  [(((v / vAA)-1)*100) if v != 0 and pd.notna(vAA) and vAA != 0 else np.nan for v, vAA in zip(CompClassPosVb['Venda'], CompClassPosVb['VendaAA'])]
#     CompClassPosVb['% Venda AA'] = [str(round(x, 2)) + '%' if pd.notna(x) else x for x in CompClassPosVb['% Venda AA']]
#     CompClassPosVb= CompClassPosVb[~CompClassPosVb['Luc'].str.contains(r'[DMX]', na = False, case = False)]
#     CompClassPosVb['Aluguel'] = [
#         (x + y) if (id_val != '1016_1001 FESTAS' and id_val != '1009_ATACAREJÃO DO LAR') else (x + y + z)
#         for x, y, z, id_val in zip(
#             CompClassPosVb['Aluguel Mínimo'],
#             CompClassPosVb['Aluguel Percentual'],
#             CompClassPosVb['Aluguel Complementar'],
#             CompClassPosVb['ID']
#         )
#     ]
#     CompClassPosVb['CTO Comum'] = CompClassPosVb['Aluguel'] + CompClassPosVb['Fundo Promoção'] + CompClassPosVb['Encargo Comum'] + CompClassPosVb['F.Reserva Enc.Comum']
#     CompClassPosVb.rename(columns = {'Total': 'CTO Total'}, inplace = True)
#     CompClassPosVb['Venda/M²'] = CompClassPosVb['Venda'] / CompClassPosVb['M2']
#     CompClassPosVb['CTOcomum/M²'] = CompClassPosVb['CTO Comum'] / CompClassPosVb['M2']
#     CompClassPosVb['CTO Total/M²'] = CompClassPosVb['CTO Total'] / CompClassPosVb['M2']
#     CompClassPosVb['CTO Total/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPosVb['CTO Total'] , CompClassPosVb['Venda'])]
#     CompClassPosVb['CTO Comum/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPosVb['CTO Comum'] , CompClassPosVb['Venda'])]


#     DF_ApenasLojas = CompClassPosVb[~CompClassPosVb['Luc'].str.contains(r'[DMX]', na = False, case = False)]

# # ------ FIM DA CONSTRUÇÃO DA TABELA MAIN ------ #



# # ------  TABELA Fluxo ------ #

#     df_fluxo = pd.read_excel(pathFluxo)
#     DF_Fluxo = df_fluxo[['Data', 'Fluxo Total']].copy()
#     DF_Fluxo['Mês'] = DF_Fluxo['Data'].dt.month
#     DF_Fluxo['Ano'] = DF_Fluxo['Data'].dt.year
#     DF_Fluxo_Mensal = DF_Fluxo.groupby(['Ano', 'Mês'])['Fluxo Total'].sum().reset_index()
#     DF_Fluxo_Mensal['Data'] = pd.to_datetime(dict(year=DF_Fluxo_Mensal['Ano'], month=DF_Fluxo_Mensal['Mês'], day=1))
#     del DF_Fluxo_Mensal['Ano']
#     del DF_Fluxo_Mensal['Mês']
#     DF_Fluxo_Mensal = DF_Fluxo_Mensal[['Data', 'Fluxo Total']]
#     DF_Fluxo_Mensal['Fluxo_Total'] = [round(((x*2.8)/0.65)) for x in DF_Fluxo_Mensal['Fluxo Total']]
#     DF_Fluxo_Mensal.drop(columns = ['Fluxo Total'], inplace = True)
#     DF_Fluxo_Mensal.rename(columns = {'Fluxo_Total': 'Fluxo Total'}, inplace = True)
# # ------ FIM DA CONSTRUÇÃO DA TABELA Fluxo ------ #

# # ------- TABELA DO MÊS ----- #
#     DesempenhoMesVb = CompClassPosVb[['Data', 'Venda']].groupby('Data').sum()
#     DesempenhoMesVb = DesempenhoMesVb.reset_index()
#     DesempenhoMesVb['VendaAA'] = DesempenhoMesVb['Venda'].shift(12)
#     DesempenhoMesVb = DesempenhoMesVb[['Data', 'VendaAA', 'Venda']]
#     DesempenhoMesVb['% Venda AA'] = [((x/y)-1)*100 for x, y in zip(DesempenhoMesVb['Venda'], DesempenhoMesVb['VendaAA'])]
#     DesempenhoMesVb['% Venda AA - Mes Anterior'] = DesempenhoMesVb['% Venda AA'].shift(1)
#     DesempenhoMesVb['Desempenho do Mês'] = [x-y for x, y in zip(DesempenhoMesVb['% Venda AA'], DesempenhoMesVb['% Venda AA - Mes Anterior'])]
#     DesempenhoMesVb = DesempenhoMesVb.merge(DF_Fluxo_Mensal, on = 'Data', how = 'left')
#     DesempenhoMesVb['Faturamento por Pessoa'] = [round((x/y), 2) if y!=0 else np.nan for x, y in zip(DesempenhoMesVb['Venda'], DesempenhoMesVb['Fluxo Total'])]

    