import pandas as pd
import numpy as np
import streamlit as st


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

    desconto = pd.read_excel('./Desconto.xlsx') 
    inadimplencia = pd.read_excel('./Inadimplência.xlsx')
    desconto = desconto[desconto['Empreendimento'] == emp] 
    inadimplencia = inadimplencia[inadimplencia['Empreendimento'] == emp] 
    inadimplencia['Data']= pd.to_datetime(inadimplencia['Data'])
    desconto = desconto.groupby(['Luc', 'Nome Fantasia', 'Data', 'Empreendimento'])['Desconto'].sum().reset_index()
    inadimplencia = inadimplencia.groupby(['Luc', 'Nome Fantasia', 'Data', 'Empreendimento'])['Inadimplência'].sum().reset_index()
    
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

    CompClassPos = pd.merge(CompClassVS, PosicaoVS, on = 'Luc', how='left')

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
    CompClassPos['VendaAA'] = CompClassPos.groupby('ID')['Venda'].shift(12)
    CompClassPos.drop(columns = ['Corredor'], inplace = True)
    CompClassPos['% Venda AA'] =  [(((v / vAA)-1)*100) if v != 0 and pd.notna(vAA) and vAA != 0 else np.nan for v, vAA in zip(CompClassPos['Venda'], CompClassPos['VendaAA'])]
    CompClassPos['% Venda AA'] = [str(round(x, 2)) + '%' if pd.notna(x) else x for x in CompClassPos['% Venda AA']]
    CompClassPos = CompClassPos[~CompClassPos['Luc'].str.contains(r'[DMX]', na = False, case = False)]
    CompClassPos['Aluguel'] = [
        (x + y) if (id_val != '1016_1001 FESTAS' and id_val != '1009_ATACAREJÃO DO LAR') else (x + y + z)
        for x, y, z, id_val in zip(
            CompClassPos['Aluguel Mínimo'],
            CompClassPos['Aluguel Percentual'],
            CompClassPos['Aluguel Complementar'],
            CompClassPos['ID']
        )
    ]
    CompClassPos['CTO Comum'] = CompClassPos['Aluguel'] + CompClassPos['Fundo Promoção'] + CompClassPos['Encargo Comum'] + CompClassPos['F.Reserva Enc.Comum']
    CompClassPos.rename(columns = {'Total': 'CTO Total'}, inplace = True)
    CompClassPos['Venda/M²'] = CompClassPos['Venda'] / CompClassPos['M2']
    CompClassPos['CTOcomum/M²'] = CompClassPos['CTO Comum'] / CompClassPos['M2']
    CompClassPos['CTO Total/M²'] = CompClassPos['CTO Total'] / CompClassPos['M2']
    CompClassPos['CTO Total/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPos['CTO Total'] , CompClassPos['Venda'])]
    CompClassPos['CTO Comum/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPos['CTO Comum'] , CompClassPos['Venda'])]


    DF_ApenasLojas = CompClassPos[~CompClassPos['Luc'].str.contains(r'[DMX]', na = False, case = False)]
    colunasDF = DF_ApenasLojas.columns.tolist()
    colunasDF.remove('Data')
    colunasDF = ['Data'] + colunasDF
    DF_ApenasLojas = DF_ApenasLojas[colunasDF]
    DF_ApenasLojas = DF_ApenasLojas.merge(desconto[['Luc', 'Nome Fantasia', 'Data', 'Desconto']], how = 'left', on = ['Luc', 'Nome Fantasia', 'Data'])
    DF_ApenasLojas = DF_ApenasLojas.merge(inadimplencia[['Luc', 'Nome Fantasia', 'Data', 'Inadimplência']], how = 'left', on = ['Luc', 'Nome Fantasia', 'Data'])
    
    return (DF_Fluxo, DF_ApenasLojas)
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f"{prefixo}{valor:.2f} {unidade}"
        valor /= 1000
    return f"{prefixo}{valor:.2f} milhões"
##################
