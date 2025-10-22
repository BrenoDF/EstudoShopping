import pandas as pd
import numpy as np
import streamlit as st
import sqlite3 as sqlite
from sqlalchemy import create_engine
import requests
import time
from typing import Dict, Tuple, List


# ------ CONSTRUÇÃO DA TABELA USADA -------- #
path1 = 'Banco de dados.xlsx'
pathFluxoVS = 'Controle Tesouraria Viashopping.xlsx'
pathFluxoVB = 'Controle Tesouraria Viabrasil.xlsx'

@st.cache_data
def TabelaOriginal(emp=None):
# ------- Chamando o BD -------- #    
    with sqlite.connect('banco_de_dados.db') as conn:
        query = "SELECT * FROM bd_lojas"
        CompClassPos = pd.read_sql(query, conn)
    col_datas = ['Data', 'Data que entrou', 'Data que saiu']
    for col in col_datas:
        CompClassPos[col] = pd.to_datetime(CompClassPos[col], errors='coerce')
# ------- Fim Chamando o BD -------- #

# ------- CONSTRUÇÃO DA TABELA MAIN --------#
    CompClassPos = CompClassPos.sort_values(['ID', 'Data'])
    CompClassPos['VendaAA'] = CompClassPos.groupby('ID', sort=False)['Venda'].shift(12)

    CompClassPos['% Venda AA'] =  [(((v / vAA)-1)*100) if v != 0 and pd.notna(vAA) and vAA != 0 else np.nan for v, vAA in zip(CompClassPos['Venda'], CompClassPos['VendaAA'])]
    CompClassPos = CompClassPos[~CompClassPos['Luc'].str.contains(r'[DMX]', na = False, case = False)]
    CompClassPos['Aluguel'] = (

        CompClassPos['Aluguel Mínimo'] +
        CompClassPos['Aluguel Percentual'] +
        CompClassPos['Aluguel Complementar'] 
        
    )
    CompClassPos['CTO Comum'] = CompClassPos['Aluguel'] + CompClassPos['Fundo Promoção'] + CompClassPos['Encargo Comum'] + CompClassPos['F.Reserva Enc.Comum']
    CompClassPos['CTO Total'] = CompClassPos['CTO Comum'] + CompClassPos['I.P.T.U.'] + CompClassPos['Água/Esgoto'] + CompClassPos['Ar Condicionado'] + CompClassPos['Energia'] + CompClassPos['Seguro Parte Privativa']
    CompClassPos['Venda/M²'] = CompClassPos['Venda'] / CompClassPos['M2']
    CompClassPos['Aluguel/M²'] = CompClassPos['Aluguel'] / CompClassPos['M2']
    CompClassPos['CTOcomum/M²'] = CompClassPos['CTO Comum'] / CompClassPos['M2']
    CompClassPos['CTO Total/M²'] = CompClassPos['CTO Total'] / CompClassPos['M2']
    CompClassPos['CTO Total/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPos['CTO Total'] , CompClassPos['Venda'])]
    CompClassPos['CTO Comum/Venda'] = [round(((x/y)*100), 2) if y!=0 else np.nan for x, y in zip(CompClassPos['CTO Comum'] , CompClassPos['Venda'])]

    desconto = pd.read_excel('./Desconto.xlsx') 
    inadimplencia = pd.read_excel('./Inadimplência.xlsx')
    desconto = desconto[desconto['Empreendimento'] == emp] 
    inadimplencia = inadimplencia[inadimplencia['Empreendimento'] == emp] 
    inadimplencia['Data']= pd.to_datetime(inadimplencia['Data'])
    desconto = desconto.groupby(['Luc', 'Nome Fantasia', 'Data', 'Empreendimento'])['Desconto'].sum().reset_index()
    inadimplencia = inadimplencia.groupby(['Luc', 'Nome Fantasia', 'Data', 'Empreendimento'])['Inadimplência'].sum().reset_index()

    DF_ApenasLojas = CompClassPos[~CompClassPos['Luc'].str.contains(r'[DMX]', na = False, case = False)]
    colunasDF = DF_ApenasLojas.columns.tolist()
    colunasDF.remove('Data')
    colunasDF = ['Data'] + colunasDF
    DF_ApenasLojas = DF_ApenasLojas[colunasDF]
    DF_ApenasLojas = DF_ApenasLojas.merge(desconto[['Luc', 'Nome Fantasia', 'Data', 'Desconto']], how = 'left', on = ['Luc', 'Nome Fantasia', 'Data'])
    DF_ApenasLojas = DF_ApenasLojas.merge(inadimplencia[['Luc', 'Nome Fantasia', 'Data', 'Inadimplência']], how = 'left', on = ['Luc', 'Nome Fantasia', 'Data'])
    
# ------- FLUXO ------ #
    df_vb = pd.read_excel(pathFluxoVB)
    df_vs = pd.read_excel(pathFluxoVS)

    df_vb['Empreendimento'] =  'Viabrasil'
    df_vs['Empreendimento'] =  'Viashopping'

    df_vb = df_vb[['Data','Mês','Ano', 'Fluxo Total', 'Receita Total Sistema', 'Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções', 'Empreendimento']]
    df_vs = df_vs[['Data','Mês','Ano', 'Fluxo Total', 'Receita Total Sistema', 'Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções', 'Empreendimento']]

    df_f = pd.concat([df_vb, df_vs], ignore_index=True)
    df_f = df_f.sort_values(by = 'Data', ascending= False)
    
    DF_Fluxo = df_f[['Data','Mês','Ano', 'Fluxo Total', 'Receita Total Sistema', 'Fluxo Pagante', 'Fluxo Mensalista', 
                     'Fluxo Carência', 'Total Isenções', 'Empreendimento']].copy()
    DF_Fluxo = DF_Fluxo.dropna(subset=['Fluxo Total'])
    DF_Fluxo['Fluxo de Pessoas'] = [round(((x*2.8)/0.65)) for x in DF_Fluxo['Fluxo Total']]
    DF_Fluxo['Data'] = pd.to_datetime(DF_Fluxo['Data'], dayfirst= True, format='%d/%m/%Y')
    DF_Fluxo = DF_Fluxo.sort_values(by = 'Data', ascending= False)
    DF_Fluxo['Ano'] = DF_Fluxo['Ano'].astype(int).astype(str)
    DF_Fluxo['Dia'] = DF_Fluxo['Data'].dt.day.astype(int).astype(str)
    DF_Fluxo.rename(columns = {'Fluxo Total':'Fluxo de Carros'}, inplace = True)
    DF_Fluxo['Data'] = pd.to_datetime(DF_Fluxo['Data'])
    DF_Fluxo = DF_Fluxo[['Data', 'Dia', 'Mês', 'Ano', 'Fluxo de Carros', 'Fluxo de Pessoas', 'Receita Total Sistema', 
                         'Fluxo Pagante', 'Fluxo Mensalista', 'Fluxo Carência', 'Total Isenções', 'Empreendimento']]
# -------  FIM FLUXO ------ #
    if emp is None:
        return (DF_Fluxo, DF_ApenasLojas)
    else:
        return (DF_Fluxo[DF_Fluxo['Empreendimento'] == emp],
        DF_ApenasLojas[DF_ApenasLojas['Empreendimento'] == emp])

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f"{prefixo}{valor:.2f} {unidade}"
        valor /= 1000
    return f"{prefixo}{valor:.2f} milhões"

def separador_br(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def colorir_var_venda(val):
    if val > 0:
        return "color: green;"
    else:
        return "color: red;"

def config_tabela(tabela):
    config = {}
    for col in tabela.select_dtypes(include=['number', 'datetime']).columns:
        if pd.api.types.is_numeric_dtype(tabela[col]):
            if col in ['CTO Comum/Venda', 'CTO Total/Venda', '% Venda AA']:
                config[col] = st.column_config.NumberColumn(format="%.2f%%")
            else:
                config[col] = st.column_config.NumberColumn(format="localized")
        
        elif pd.api.types.is_datetime64_any_dtype(tabela[col]):
            config[col] = st.column_config.DatetimeColumn(format="DD/MM/YYYY")
    
    return config
    
# ========== FUNÇÃO places (corrigida) ==========
def places(
    rating_minimo: float = 4.0,
    reviews_minimo: int = 30,
    locais_escolhidos: List[str] | None = None,
    categorias: List[str] | None = None,
    todos_locais: Dict[str, Tuple[float, float]] | None = None,
    api_key: str = st.secrets["RAPIDAPI_KEY"],
    radius_metros: int = 1000,
    grid_offset_graus: float = 0.005,   # ~ 500 m
    grid_halfspan: int = 0,             # 2 => 5x5
    max_paginas_textsearch: int = 3,
    sleep_next_page: float = 2.0,
) -> pd.DataFrame:

    if not todos_locais:
        return pd.DataFrame()
    if not api_key:
        st.error("Informe sua RapidAPI Key.")
        return pd.DataFrame()

    headers = {
        "x-rapidapi-key": api_key,  # <<< NÃO deixar hardcoded
        "x-rapidapi-host": "google-map-places.p.rapidapi.com",
    }
    TEXTSEARCH_URL = "https://google-map-places.p.rapidapi.com/maps/api/place/textsearch/json"

    # monta {nome_local: (lat, lng)} só com os escolhidos
    locais = {}
    for nome in (locais_escolhidos or []):
        if nome in todos_locais:
            # >>> CORREÇÃO: guardar tupla (lat, lng), não dict
            locais[nome] = todos_locais[nome]

    categorias = [c.strip() for c in (categorias or []) if c and c.strip()]
    if not locais or not categorias:
        return pd.DataFrame()

    MIN_RATING = rating_minimo
    MIN_REVIEWS = reviews_minimo
    grid_range = range(-grid_halfspan, grid_halfspan + 1)

    def gerar_grid_em_torno(lat_center: float, lng_center: float, offset: float) -> List[Tuple[float, float]]:
        lats = [lat_center + i * offset for i in grid_range]
        lngs = [lng_center + j * offset for j in grid_range]
        return [(la, ln) for la in lats for ln in lngs]

    def buscar_textsearch(query: str, location: str, radius: str = "1000",
                          categoria: str | None = None, local_base: str | None = None) -> list:
        resultados = []
        next_page_token = None
        page_count = 0

        while True:
            try:
                if next_page_token:
                    params = {"pagetoken": next_page_token, "language": "pt-BR", "region": "br"}
                else:
                    params = {
                        "query": query,
                        "location": location,   # "lat,lng"
                        "radius": radius,
                        "language": "pt-BR",
                        "region": "br",
                    }

                resp = requests.get(TEXTSEARCH_URL, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                st.warning(f"Erro na requisição para '{query}' em {location}: {e}")
                break

            for place in data.get("results", []):
                rating = place.get("rating", 0) or 0
                reviews = place.get("user_ratings_total", 0) or 0
                price_level = place.get("price_level", None)
                loc = place.get("geometry", {}).get("location", {}) or {}

                if rating >= MIN_RATING and reviews >= MIN_REVIEWS:
                    resultados.append({
                        "nome": place.get("name"),
                        "endereco": place.get("formatted_address"),
                        "nota": rating,
                        "quantidade_avaliacoes": reviews,
                        "price_level": price_level,
                        "tipos": ", ".join(place.get("types", [])),
                        "lat": loc.get("lat"),
                        "lng": loc.get("lng"),
                        "categoria_busca": categoria,
                        "local_base": local_base,
                    })

            next_page_token = data.get("next_page_token")
            page_count += 1
            if not next_page_token or page_count >= max_paginas_textsearch:
                break

            time.sleep(sleep_next_page)  # requerido pela API

        return resultados

    # varre grid de cada local_base em cada categoria
        # varre grid de cada local_base em cada categoria
    todos_os_resultados = []
    radius_str = str(radius_metros)

    total_passos = len(locais) * len(categorias)
    progresso = st.progress(0)
    status = st.empty()
    passo = 0

    with st.spinner("🔎 Buscando lugares, aguarde..."):
        for nome_local, (lat_c, lng_c) in locais.items():
            grid_coords = gerar_grid_em_torno(lat_c, lng_c, grid_offset_graus)

            for termo in categorias:
                passo += 1
                progresso.progress(min(1.0, passo / max(1, total_passos)))
                status.write(f"📍 {nome_local} — categoria **{termo}** ({passo}/{total_passos})")

                for (lat, lng) in grid_coords:
                    location = f"{lat},{lng}"
                    resultados = buscar_textsearch(
                        query=termo,
                        location=location,
                        radius=radius_str,
                        categoria=termo,
                        local_base=nome_local,
                    )
                    todos_os_resultados.extend(resultados)
                    time.sleep(0.1)  # respiro p/ limites

    progresso.progress(1.0)
    status.write("✅ Busca concluída!")


    df = pd.DataFrame(todos_os_resultados)
    if not df.empty:
        df = df.drop_duplicates(subset=["nome", "lat", "lng"]).reset_index(drop=True)

    return df

#### Pipe #####

def pipe_aquisicao():
    BASE_URL = "https://grupolgn.pipedrive.com/api/v1"
    API_TOKEN = "a24cc3c57ab15bbe8a1aee47e7ef1ddb002377ec"   # direto, sem env
    LIMIT    = 500
    SLEEP    = 0.25
    TIMEOUT  = 60

    CUSTOM_KEYS = ",".join([
        "07376eeceaecacb3a3447f172494011e089ef1dd",  # Funil de Origem
        "67f8e3a9b54e52d85decaf28677b3c49fae8c581",  # Origem do Lead
        "73dcb4ce94a11fcfd63be37bc14569f91c3827c0",  # Sub-Origem
        "ded9c8411ff1ad0a4ad435c7706a26da94f0453e",  # Empreendimento
        "eea389fa8d232424539617b36c0bda3dc97bff1e",  # utm_content
        "f44f4f8e48c7637f98fdbec8f65430728dd9fe3b",  # Reunião Realizada
        "41a03a78d2a501c5043deb0d6b87b31adcc9efba",  # Data da Reunião
        "acbd61e1a9860ea49b30bb9494d805ce9623307e",   # Persona
        "3c6564d8d8aa5263034312b633ef5eb3c7b7ee0d"
    ])

    CAMPOS_DESEJADOS = [
        "id","title","creator_user_id","owner_id","user_id","value","person_id","org_id",
        "stage_id","pipeline_id","add_time","update_time","stage_change_time",
        "status","is_archived","probability","lost_reason",
        "close_time","won_time","local_won_date","local_lost_date",
        "local_close_date","expected_close_date","active","deleted",
        "origin","pipeline_id",
        "07376eeceaecacb3a3447f172494011e089ef1dd",
        "67f8e3a9b54e52d85decaf28677b3c49fae8c581",
        "73dcb4ce94a11fcfd63be37bc14569f91c3827c0",
        "ded9c8411ff1ad0a4ad435c7706a26da94f0453e",
        "eea389fa8d232424539617b36c0bda3dc97bff1e",
        "f44f4f8e48c7637f98fdbec8f65430728dd9fe3b",
        "41a03a78d2a501c5043deb0d6b87b31adcc9efba",
        "acbd61e1a9860ea49b30bb9494d805ce9623307e",
        "3c6564d8d8aa5263034312b633ef5eb3c7b7ee0d"
    ]

    # ======================= MAPEAMENTOS =======================
    mapeamento_funil = {305: 'Inbound', 306: 'Outbound'}
    mapeamento_lead = {
        289:'Prospecção Ativa',290:'Tráfego Pago',291:'Relacionamento',
        292:'Indicação',293:'Bateu na Porta',294:'Ligação',621:'Site'
    }
    mapeamento_sub_origem = {
        295:'Prospecção Ativa - Google',296:'Prospecção Ativa - Ferramenta de busca',
        297:'Prospecção Ativa - Site concorrentes',298:'Prospecção Ativa - Site instituições',
        299:'Prospecção Ativa - Power BI',300:'Prospecção Ativa - Visitas',
        301:'Prospecção Ativa - Redes Sociais',302:'Reativação',
        303:'Indicação Lojista',304:'Indicação Setores',622:'Pesquisa no Google'
    }
    mapeamento_emp = {
        15:'Viashopping - Lado A',18:'Viashopping - Lado B',16:'Viabrasil',
        236:'Contagem',266:'Biergarten',286:'Vidi Midia'
    }

    mapeamento_reuniao = {
        586: 'Sim, foi realizada.',
        587: 'Não, não foi realizada.'
    }

    mapeamento_persona = {
        629: 'Expansão- Loja de Rua',
        628: 'Expansão - Loja de Shopping',
        646: 'Investidor',
        627: 'Sonhador',
        630: 'Sonhador - Franquia',
        631: 'N/A'
    }

    # ======================= HELPERS =======================
    def get_paginated(endpoint, params):
        dados, start = [], 0
        while True:
            q = dict(params, start=start, limit=LIMIT)
            r = requests.get(f"{BASE_URL}/{endpoint}", params=q, timeout=TIMEOUT)
            r.raise_for_status()
            payload = r.json() or {}
            items = payload.get("data") or []
            if not items:
                break
            dados.extend(items)
            pag = (payload.get("additional_data") or {}).get("pagination") or {}
            if not pag.get("more_items_in_collection"):
                break
            start = pag.get("next_start", 0)
            time.sleep(SLEEP)
        return dados

    def id_name_map(endpoint):
        arr = get_paginated(endpoint, {"api_token": API_TOKEN})
        if not arr: return {}
        df = pd.DataFrame(arr)
        if not {"id","name"}.issubset(df.columns): return {}
        return dict(zip(df["id"], df["name"]))

    def users_map():
        arr = get_paginated("users", {"api_token": API_TOKEN})
        if not arr: return {}, {}
        dfu = pd.DataFrame(arr)
        return dict(zip(dfu["id"], dfu["name"])), dict(zip(dfu["id"], dfu["email"]))

    def extract_user_id(val):
        if isinstance(val, dict):
            return val.get("id")
        return pd.to_numeric(val, errors="coerce")

    # ======================= COLETA =======================
    deals_raw = get_paginated("deals", {"api_token": API_TOKEN, "custom_fields": CUSTOM_KEYS})

    linhas = []
    for d in deals_raw:
        if not d.get("is_archived", True) and not d.get("deleted", True):
            linhas.append({c: d.get(c) for c in CAMPOS_DESEJADOS})
    df_deals = pd.DataFrame(linhas)

    # ======================= TRANSFORMAÇÕES =======================
    if not df_deals.empty:
        # creator_user_id
        df_deals["creator_id"]   = df_deals["creator_user_id"].apply(lambda x: x.get("id") if isinstance(x, dict) else None)
        df_deals["creator_name"] = df_deals["creator_user_id"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)

        # person_id
        df_deals["person_name"]  = df_deals["person_id"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
        df_deals["person_email"] = df_deals["person_id"].apply(lambda x: (x.get("email",[{}])[0].get("value") if isinstance(x, dict) and x.get("email") else None))
        df_deals["person_phone"] = df_deals["person_id"].apply(lambda x: (x.get("phone",[{}])[0].get("value") if isinstance(x, dict) and x.get("phone") else None))

        # org_id
        df_deals["org_name"]     = df_deals["org_id"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
        df_deals["org_owner_id"] = df_deals["org_id"].apply(lambda x: x.get("owner_id") if isinstance(x, dict) else None)
        df_deals["org_address"]  = df_deals["org_id"].apply(lambda x: x.get("address") if isinstance(x, dict) else None)

        # user_id (JSON) → user_name
        df_deals["user_name"] = df_deals["user_id"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)

        # owner_id_num (prioriza owner_id, senão cai no user_id)
        df_deals["owner_id_num"] = df_deals.apply(
            lambda r: extract_user_id(r.get("owner_id")) if r.get("owner_id") not in (None,"")
                    else extract_user_id(r.get("user_id")),
            axis=1
        )

        # Remover colunas JSON/brutas que não precisa
        df_deals.drop(columns=["creator_user_id","person_id","org_id","owner_id","creator_email","user_id"], inplace=True, errors="ignore")

        # renomear custom fields
        df_deals.rename(columns={
            "07376eeceaecacb3a3447f172494011e089ef1dd": "funil_origem",
            "67f8e3a9b54e52d85decaf28677b3c49fae8c581": "origem_lead",
            "73dcb4ce94a11fcfd63be37bc14569f91c3827c0": "sub_origem",
            "ded9c8411ff1ad0a4ad435c7706a26da94f0453e": "empreendimento",
            "eea389fa8d232424539617b36c0bda3dc97bff1e": "utm_content",
            "f44f4f8e48c7637f98fdbec8f65430728dd9fe3b": "reuniao_realizada",
            "41a03a78d2a501c5043deb0d6b87b31adcc9efba": "data_reuniao",
            "acbd61e1a9860ea49b30bb9494d805ce9623307e": "persona",
            "3c6564d8d8aa5263034312b633ef5eb3c7b7ee0d": "utm_source"
        }, inplace=True)

        # mapear valores fixos
        for col,mapping in [("funil_origem",mapeamento_funil),
                            ("origem_lead",mapeamento_lead),
                            ("sub_origem",mapeamento_sub_origem),
                            ("empreendimento",mapeamento_emp),
                            ("reuniao_realizada", mapeamento_reuniao),
                            ("persona", mapeamento_persona)]:
            if col in df_deals.columns:
                df_deals[col] = pd.to_numeric(df_deals[col], errors="coerce").replace(mapping).astype("object")

        # mapear stages/pipelines
        try:
            df_deals["stage_id"]    = pd.to_numeric(df_deals["stage_id"], errors="coerce").replace(id_name_map("stages")).astype("object")
            df_deals["pipeline_id"] = pd.to_numeric(df_deals["pipeline_id"], errors="coerce").replace(id_name_map("pipelines")).astype("object")
        except Exception as e:
            df_deals["__warn_stages_pipes"] = f"Falha ao mapear stages/pipelines: {e}"

        # mapear owners via /users
        try:
            owner_name_map, owner_email_map = users_map()
            df_deals["owner_name"]  = df_deals["owner_id_num"].map(owner_name_map)
            df_deals["owner_email"] = df_deals["owner_id_num"].map(owner_email_map)
        except Exception as e:
            df_deals["__warn_owners"] = f"Falha ao mapear owners: {e}"

        # datas
        for c in ["add_time","update_time","stage_change_time","close_time","won_time",
                "local_won_date","local_lost_date","local_close_date","expected_close_date", 'data_reuniao']:
            if c in df_deals.columns:
                df_deals[c] = pd.to_datetime(df_deals[c], errors="coerce")

        # ordenação
        df_deals.sort_values("id", ascending=False, inplace=True)
    criadores = ['Bruna Joice', 'Thainá Alves da Silva', 'Paola Starling']
    df_deals['funil_origem'] = df_deals['funil_origem'].fillna('')
    df_deals['utm_content']  = df_deals['utm_content'].fillna('')
    df_deals['creator_name']   = df_deals['creator_name'].fillna('')

    df_deals['Funil de Origem'] = df_deals.apply( lambda row: row['funil_origem'] if row['funil_origem'] != '' 
                                else 'Inbound' if row['utm_content'] != '' 
                                else 'Outbound' if row['creator_name'] in criadores 
                                else 'Comercial', axis=1 )
    df_deals['Status Aquisicao'] = df_deals.apply(
    lambda row: (
    'GANHO' if row['Funil de Origem'] in ['Inbound','Outbound'] and row['reuniao_realizada'] == 'Sim, foi realizada.'
    else 'EM ABERTO' if row['Funil de Origem'] in ['Inbound','Outbound'] and row['status'] == 'open' 
    else 'PERDA' if row['Funil de Origem'] in ['Inbound','Outbound'] and row['status'] == 'lost'
    else ''
    ),
    axis=1
    )
    return df_deals