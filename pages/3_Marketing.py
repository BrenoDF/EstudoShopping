import ProcessamentoDaTabela as ProcTab
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
import io

# Configurações de página
st.set_page_config(layout="wide",
page_title= 'Análise de CTO',
initial_sidebar_state="collapsed")
st.logo('Imagens/NAVA-preta.png', icon_image='Imagens/NAVA-preta.png', size='large')
global_widget_keys = ["data"]
if 'data' in st.session_state:
  for key in global_widget_keys:
      if key in st.session_state:
          st.session_state[key] = st.session_state[key]
    
# ======= Funcoes
          
def titulo_aquisicao(texto):
    html_titulo = f"""
    <div style="
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, 'Noto Sans', sans-serif;
        text-align: center;
        font-size: 1.5em;
        font-weight: 800;
        background: linear-gradient(90deg, #6a85b6, #bac8e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
        margin-bottom: 5px;
    ">
        {texto}
    </div>
    """
    return html_titulo
def pct(part, whole):
    return 0 if whole == 0 else round(100 * part / whole, 2)
# =============

# ------------------------------- Trazendo o DF -------------------------------- #
DF_Fluxo, DFLojas = ProcTab.TabelaOriginal()
df_vendas = ProcTab.vendas_diarias()

###########################

todos_locais = {
    "Barreiro": (-19.990571691842725, -44.026536721844074),
    "Betânia": (-19.961331439911678, -43.99406267939647),
    "Savassi": (-19.935731226864483, -43.93481120197042),
    "Venda Nova": (-19.816274160382815, -43.95625433493147),
    "Castelo": (-19.882737848346455, -43.99860571029591),
    "Camargos": (-19.940663771581836, -44.01791421949377),
    "Região Shopping Contagem": (-19.88013048878981, -44.03963212494502),
    "Cidade Industrial": (-19.952423506620857, -44.018338789038026),
    "Ibiritexas": (-20.00220965112124, -44.07202165128704),
    "Durval": (-19.985213639624565, -44.06498144170459),
    "Vale do Jatobá": (-20.006772026602906, -44.036456454642035),
    "Milionários": (-19.979643907284842, -43.99667085524975),
    "Pampulha": (-19.85134824966138, -43.95186171572862),
    "Mercado novo": (-19.920582243442308, -43.94560806932097),
    "Santa Tereza": (-19.914896903414018, -43.918188198085666),
    "Eldorado": (-19.942723373396266, -44.04025003845475),
    "Sarzedo": (-20.0389954358913, -44.14212954621412),
    "Lourdes": (-19.93176417465712, -43.94390254337979),
    "Buritis": (-19.975191416429283, -43.96854467874752),
    "Nova Lima": (-19.987987343340045, -43.85229259121683),
    "Vila da Serra": (-19.978392089627032, -43.93850203248684),
    "São Lucas": (-19.929844128860452, -43.92060748221753),
    "Ouro Preto": (-19.872002272015667, -43.98568305515161)
}

    # === Configurações ===


# ------------------    INICIO DAS TABS    ------------------ #
tab_mkt, tab_aquisicao = st.tabs(["Marketing", "Aquisição"])

with tab_mkt:
    st.header("Marketing")
    st.subheader('Comparativo de campanhas')
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        data_base = st.date_input("Data da campanha anterior:", 
                                    value = (date(2025,1,1),DFLojas['Data'].max()),
                                    min_value=date(2018,1,1),
                                    max_value=DFLojas['Data'].max(),
                                    format= "DD/MM/YYYY")
    with col_filtro2:
        data_comparativa = st.date_input("Data da campanha atual:", 
                                            value = (date(2025,1,1),DFLojas['Data'].max()),
                                            min_value=date(2018,1,1),
                                            max_value=DFLojas['Data'].max(),
                                            format= "DD/MM/YYYY")
    with col_filtro3:
        emp = st.radio('Empreendimento', ['Viashopping', 'Viabrasil'], horizontal=True)
    
    # ------------------------------- FILTRANDO O DF -------------------------------- #
    if (len(data_base) < 2) | (len(data_comparativa) < 2):
        st.error('É necessário colocar um intervalo de data nos dois periodos de campanha acima!', icon="🚨")
    else:
        
        inicio_b, fim_b = [pd.to_datetime(d) for d in data_base]
        inicio_c, fim_c = [pd.to_datetime(d) for d in data_comparativa]

        def criar_df_ticket(df_vendas, df_fluxo,inicio, fim):
            
            df_filtrado_mask = (df_vendas['Data'] >= inicio) & (df_vendas['Data'] <= fim)
            df_filtrado_mask_f = (df_fluxo['Data'] >= inicio) & (df_fluxo['Data'] <= fim)
            
            df_filtrado = df_vendas.loc[df_filtrado_mask]
            df_filtrado = df_filtrado.groupby(['Data', 'Empreendimento'], as_index=False).sum()
            df_filtrado = df_filtrado[['Data', 'Vendas', 'Empreendimento']]
            
            df_fluxo_filtrado = df_fluxo.loc[df_filtrado_mask_f]
            df_fluxo_filtrado = df_fluxo_filtrado[['Data','Fluxo de Pessoas', 'Empreendimento']]
            
            df_ticket = pd.merge(df_filtrado,df_fluxo_filtrado, how = 'left', on =['Data', 'Empreendimento'])
            df_ticket_final = df_ticket[['Data', 'Empreendimento', 'Vendas', 'Fluxo de Pessoas']]
            df_ticket_final['Ticket'] = (df_ticket_final['Vendas']/df_ticket_final['Fluxo de Pessoas']).round(2)
            return df_ticket_final
        
        df_data_base = criar_df_ticket(df_vendas, DF_Fluxo, inicio_b, fim_b)
        df_data_comparativa = criar_df_ticket(df_vendas, DF_Fluxo, inicio_c, fim_c)
        
        dfs = [df_data_base, df_data_comparativa]
        
        df_data_base = df_data_base[df_data_base['Empreendimento'] == emp]
        df_data_comparativa = df_data_comparativa[df_data_comparativa['Empreendimento'] == emp]
        
        config_col = ProcTab.config_tabela(df_data_base)
        col_comp_fluxo1, col_comp_fluxo2, col_comp_fluxo3 = st.columns(3)
        with col_comp_fluxo1:
            st.dataframe(df_data_base, hide_index= True, column_config= config_col,
                         column_order=['Data', 'Fluxo de Pessoas', 'Vendas', 'Ticket', 'Empreendimento'])
        with col_comp_fluxo2:
            st.dataframe(df_data_comparativa, hide_index= True, column_config= config_col, 
                         column_order=['Data', 'Fluxo de Pessoas', 'Vendas', 'Ticket', 'Empreendimento'])
        with col_comp_fluxo3:
            ## Metricas:
            total_fluxo_base = df_data_base['Fluxo de Pessoas'].sum()
            total_fluxo_comparativa = df_data_comparativa['Fluxo de Pessoas'].sum()
            dif_total_fluxo = total_fluxo_comparativa - total_fluxo_base
            dif_total_fluxo_var = round((((total_fluxo_comparativa / total_fluxo_base) - 1) * 100),2)
            total_venda_base = df_data_base['Vendas'].sum()
            total_venda_comparativa = df_data_comparativa['Vendas'].sum()
            dif_total_venda = ProcTab.formata_numero(total_venda_comparativa - total_venda_base)
            dif_total_venda_var = round((((total_venda_comparativa / total_venda_base) - 1) * 100),2)
            media_ticket_base = df_data_base['Ticket'].mean()
            media_ticket_comparativa = round(df_data_comparativa['Ticket'].mean(),2)
            dif_media_ticket_var = round((((media_ticket_comparativa / media_ticket_base) - 1) * 100),2)
            
            st.metric('Diferença de Fluxo:', f'{dif_total_fluxo} pessoas', delta = f'{dif_total_fluxo_var}%')
            st.metric('Diferença de Vendas:', f'R${dif_total_venda}', delta = f'{dif_total_venda_var}%')
            st.metric('Ticket médio:', f'R${media_ticket_comparativa}', delta = f'{dif_media_ticket_var}%')

with tab_aquisicao:
    st.header("Aquisição")
    colunas_aq1 , colunas_aq2, colunas_aq3 = st.columns([3.33,3.33,3.33])
    st.html(titulo_aquisicao('Buscador de Leads 🚀'))

    # --- Inputs do usuário (Aquisição) ---
    # API key (preferir st.secrets; aqui usamos fallback)
    default_key = st.secrets.get("RAPIDAPI_KEY", "")

    # escolha de locais base (usa seu dict todos_locais definido acima)
    locais_escolhidos = st.multiselect(
        "Locais base",
        options=list(todos_locais.keys()),
        default=[],
        help="Selecione um ou mais bairros/regiões para varredura."
    )

    # categorias separadas por vírgula
    categorias_str = st.text_input(
        "Categorias (separe por vírgula)",
        value="restaurante, cafeteria, pizzaria",
        help="Ex.: restaurante, cafeteria, pizzaria"
    )
    categorias = [c.strip() for c in categorias_str.split(",") if c.strip()]

    colA, colB = st.columns(2)
    with colA:
        rating_minimo = st.slider("Nota mínima (Google)", 0.0, 5.0, 4.0, 0.1)
    with colB:
        reviews_minimo = st.number_input("Mínimo de avaliações", min_value=0, value=30, step=5)

    with st.expander("Avançado"):
        radius_metros = st.number_input("Raio de busca (m)", 100, 5000, 1000, 100)
        grid_offset_graus = st.number_input("Offset do grid (°)", min_value=0.000, max_value=0.02, value=0.000, step=0.001, format="%.3f")
        grid_halfspan = st.slider("Semiextensão do grid (2 => 5x5)", 0, 4, 0)
        max_paginas_textsearch = st.selectbox("Páginas por busca (TextSearch)", [1, 2, 3], index=2)

    executar = st.button("🚀 Buscar lugares")

    # --- Resultado ---
    if executar:
        if not locais_escolhidos:
            st.info("Selecione ao menos um local base.")
            st.stop()
        if not categorias:
            st.info("Informe ao menos uma categoria.")
            st.stop()
        if not default_key:
            st.error("Informe sua RapidAPI Key.")
            st.stop()

        df_lugares = ProcTab.places(
            rating_minimo=rating_minimo,
            reviews_minimo=reviews_minimo,
            locais_escolhidos=locais_escolhidos,
            categorias=categorias,
            todos_locais=todos_locais,
            api_key=default_key,
            radius_metros=radius_metros,
            grid_offset_graus=grid_offset_graus,
            grid_halfspan=grid_halfspan,
            max_paginas_textsearch=max_paginas_textsearch,
            sleep_next_page=2.0,
        )

        if df_lugares.empty:
            st.warning("Nenhum resultado com os filtros definidos.")
        else:
            # --- Gerar o arquivo Excel em memória ---
            buffer = io.BytesIO()
            df_lugares.to_excel(buffer, index=False)   # df é o seu DataFrame
            buffer.seek(0)  # reposiciona o ponteiro no início
            st.success(f"✅ {len(df_lugares)} resultados únicos.")
            st.dataframe(df_lugares, use_container_width=True)
            st.download_button(
            label="Download CSV",
            data=buffer,
            file_name="lugares.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
            )

            # Mapa
            with st.expander("Mapa"):
                st.map(df_lugares.rename(columns={"lat": "latitude", "lng": "longitude"})[["latitude", "longitude"]])
    st.divider()
    colA1 , colB1 = st.columns(2)
    with colA1:
        setor_radio = st.radio("Verificar funil comercial ou aquisição:",
            options=['Aquisição', 'Comercial'], index = 1, key='funil_aq_radio', horizontal = True)
    with colB1:
        meta = st.number_input("Meta de Aquisições:", min_value=0, value=100, step=1, key='meta_aq_input')
    
    dados_pipe = ProcTab.pipe_aquisicao().copy()
    dados_pipe['status'] = dados_pipe['status'].map({'open':'EM ABERTO', 'won':'GANHO', 'lost':'PERDA'})
    dados_pipe['Data Aquisicao'] = dados_pipe.apply(lambda row: row['add_time'] if pd.isna(row['data_reuniao']) else row['data_reuniao'], axis=1)
    
    # dados Aquisição
    dados_aq = dados_pipe.copy()
    dados_aq = dados_aq[dados_aq['Data Aquisicao'] >= pd.to_datetime('2025-07-01')]
    dados_aq = dados_aq[dados_aq['Funil de Origem'] != 'Comercial']
    em_aberto_aq = dados_aq[dados_aq['Status Aquisicao'] == 'EM ABERTO']
    ganhos_aq    = dados_aq[dados_aq['Status Aquisicao'] == 'GANHO']
    perdas_aq    = dados_aq[dados_aq['Status Aquisicao'] == 'PERDA']
    penultimo_bloco = 000
    
    #dados Comercial
    dados_com = dados_pipe.copy()
    dados_com = dados_com[dados_com['add_time'] >= pd.to_datetime('2025-07-01')]
    dados_com = dados_com[dados_com['Funil de Origem'] == 'Comercial']
    em_aberto_com = dados_com[dados_com['status'] == 'EM ABERTO']
    ganhos_com    = dados_com[dados_com['status'] == 'GANHO']
    perdas_com    = dados_com[dados_com['status'] == 'PERDA']
    
    if setor_radio == 'Aquisição':
        total_leads     = len(dados_aq)                  # número total de leads Aquisicao
        em_aberto       = len(em_aberto_aq)              # número total de leads Comercial
        ganhos          = len(ganhos_aq)                 # leads que viraram vendas/ganhos
        perdas          = len(perdas_aq)                 # leads perdidos
        data_ganho_med  = (ganhos_aq['data_reuniao'] - ganhos_aq['add_time']).dropna().dt.days.mean() # cálculo do tempo até perda
    
    else:
        total_leads     = len(dados_com)     
        em_aberto       = len(em_aberto_com) 
        ganhos          = len(ganhos_com)    
        perdas          = len(perdas_com)    
        data_ganho_med  = (ganhos_com['local_won_date'] - ganhos_com['add_time']).dropna().dt.days.mean()
        
    aberto_pct   = pct(em_aberto, total_leads)    # % de leads contatados
    ganho_pct    = pct(ganhos, total_leads)       # % de leads ganhos
    perda_pct    = pct(perdas, total_leads)       # % de leads perdidos
    aberto_pct   = pct(em_aberto, total_leads)    # % de leads abertos
    aberto_bar   = int(round(aberto_pct))
    ganho_bar    = int(round(ganho_pct))
    perda_bar    = int(round(perda_pct))
    aberto_bar   = int(round(aberto_pct))

    
    html = f"""
    <div class="wrap">
    <div class="header">
        <div class="title">Relatório de Leads</div>
        <div class="subtitle">Resumo de desempenho e funil</div>
    </div>

    <div class="grid">
        <!-- Card: Total Leads In. -->
        <div class="card">
        <div class="card-top">
            <div class="label">Total de leads Aquisicao</div>
            <div class="value xl">{total_leads}</div>
        </div>
        <div class="foot-note">{('Considerando funis de origem Outbound e Inbound, a partir de julho. Ganho contabilizado após reunião realizada.' if setor_radio == 'Aquisição' 
        else 'Considerando o funil de origem "Comercial" a partir ed julho.')}</div>
        </div>

        <!-- Card: Ganhos -->
        <div class="card">
        <div class="card-top">
            <div class="label">Ganhos</div>
            <div class="value">{ganhos}</div>
        </div>
        <div class="meter"><span class="ok" style="width:{ganho_bar}%"></span></div>
        <div class="meta">
            <span class="pill ok">{ganho_pct}% do total</span>
            <span class="pill glow">Tempo Médio para ganho: {data_ganho_med:.1f}d</span>
        </div>
        </div>
        
        <!-- Card: Perdas -->
        <div class="card">
        <div class="card-top">
            <div class="label">Perdas</div>
            <div class="value">{perdas}</div>
        </div>
        <div class="meter"><span class="warn" style="width:{perda_bar}%"></span></div>
        <div class="meta">
            <span class="pill warn">{perda_pct}% do total</span>
        </div>
        </div>

        <!-- Card: Em aberto -->
        <div class="card">
        <div class="card-top">
            <div class="label">Em aberto</div>
            <div class="value">{em_aberto}</div>
        </div>
        <div class="meter"><span class="info" style="width:{aberto_bar}%"></span></div>
        <div class="meta">
            <span class="pill info">{aberto_pct}% do total</span>
        </div>
        </div>
        
        <!-- Card: ??? -->
        <div class="card">
        <div class="card-top">
            <div class="label">???</div>
            <div class="value">{penultimo_bloco}</div>
        </div>
        <div class="meter"><span class="warn" style="width:{penultimo_bloco}%"></span></div>
        <div class="meta">
            <span class="pill warn">{penultimo_bloco}% do total</span>
        </div>
        </div>

        <!-- Card: Meta -->
        <div class="card">
        <div class="card-top">
            <div class="label">Meta</div>
            <div class="value">{meta}</div>
        </div>
        <span class="pill glow">Progresso: {("Selecione uma meta" if meta == None else round(ganhos/meta*100, 2))}%</span>
        </div>
    </div>
    </div>

    <style>
    :root {{
        --bg: #0f172a;          /* fundo escuro (slate-900) */
        --panel: #111827;       /* painel (gray-900) */
        --border: rgba(255,255,255,.06);
        --text: #e5e7eb;        /* texto principal */
        --muted:#9ca3af;        /* texto secundário */
        --ok: #86efac;          /* verde pastel */
        --warn:#fca5a5;         /* vermelho pastel */
        --info:#93c5fd;         /* azul pastel */
        --accent1: #6a85b6;     /* degrade sutil */
        --accent2: #bac8e0;
        --radius: 14px;
    }}

    *{{box-sizing:border-box}}
    .wrap{{
        max-width: 1200px; margin: 28px auto; padding: 0 16px;
        color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, 'Noto Sans', sans-serif;
    }}
    .header{{text-align:center; margin-bottom: 18px}}
    .title{{
        font-weight: 800; font-size: 2.0rem;
        background: linear-gradient(90deg,var(--accent1),var(--accent2));
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }}
    .subtitle{{color:var(--muted); font-size:.95rem; margin-top:4px}}

    .grid{{
        display:grid; gap:14px;
        grid-template-columns: repeat(3, minmax(0,1fr));
    }}
    @media (max-width: 980px) {{ .grid{{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
    @media (max-width: 640px) {{ .grid{{ grid-template-columns: 1fr; }} }}

    .card{{
        background:
        radial-gradient(800px 300px at 120% -20%, rgba(186,200,224,.08), transparent),
        radial-gradient(800px 300px at -20% 120%, rgba(106,133,182,.08), transparent),
        var(--panel);
        border:1px solid var(--border);
        border-radius: var(--radius);
        padding: 16px 16px 14px;
        box-shadow: 0 10px 28px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.03);
    }}
    .card.win{{
        background:
        radial-gradient(800px 300px at 120% -20%, rgba(186,200,224,.08), transparent),
        radial-gradient(800px 300px at -20% 120%, rgba(106,133,182,.08), transparent),
        #f1c40f;
    }}
    .card-top{{ display:flex; align-items:baseline; justify-content:space-between; gap:10px }}
    .label{{ color:var(--muted); font-weight:600; letter-spacing:.02em }}
    .value{{ font-size:1.8rem; font-weight:800 }}
    .value.xl{{ font-size:2.4rem }}

    .meter{{
        position:relative; height:10px; margin-top:10px; margin-bottom:8px;
        background: rgba(255,255,255,.05); border-radius:999px; overflow:hidden; border:1px solid var(--border);
    }}
    .meter > span{{
        display:block; height:100%;
        background: linear-gradient(90deg, var(--accent1), var(--accent2));
    }}
    .meter > span.ok{{ background: linear-gradient(90deg, #34d399, var(--ok)) }}
    .meter > span.warn{{ background: linear-gradient(90deg, #fb7185, var(--warn)) }}
    .meter > span.info{{ background: linear-gradient(90deg, #60a5fa, var(--info)) }}

    .meta{{ display:flex; flex-wrap:wrap; gap:8px; margin-top:6px }}
    .pill{{
        padding:6px 10px; border-radius:999px; font-size:.85rem; font-weight:700; letter-spacing:.02em;
        border:1px solid var(--border); background: rgba(255,255,255,.03); color:var(--text)
    }}
    .pill.ok{{ background: rgba(134,239,172,.12) }}
    .pill.warn{{ background: rgba(252,165,165,.12) }}
    .pill.info{{ background: rgba(147,197,253,.12) }}
    .pill.neutral{{ background: rgba(255,255,255,.06) }}
    .pill.glow{{
        box-shadow: 0 0 0 3px rgba(186,200,224,.12), 0 8px 18px rgba(106,133,182,.18);
    }}
    .foot-note{{ color:var(--muted); font-size:.9rem; margin-top:6px }}
    body{{ background: linear-gradient(180deg,#0b1220, var(--bg)); margin:0; }}
    </style>
    """
    st.html(html)
    dados_pipe = dados_pipe[['id', 'title', 'stage_id', 'pipeline_id', 'add_time', 'status', 'lost_reason', 
                             'close_time', 'local_won_date', 'local_close_date', 'origin', 'funil_origem', 'origem_lead', 
                             'sub_origem', 'empreendimento', 'utm_content', 'reuniao_realizada', 'data_reuniao', 'persona',
                             'utm_source', 'creator_name', 'user_name', 'owner_name', 'Funil de Origem', 'Status Aquisicao']]
    coluna1, coluna2, coluna3 = st.columns([0.45,0.1,0.45])
    with st.expander("Tabela Completa de Leads"):
            st.dataframe(dados_pipe, use_container_width=True, hide_index=True)

    
# CSS para metric

st.markdown("""
    <style>
    /* Container da métrica */
    div[data-testid="stMetric"] {
        background-color: #f9f9f9;
        border: 1px solid #e3e3e3;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.2s ease-in-out;
        max-width: 300px;
    }

    /* Efeito hover leve */
    div[data-testid="stMetric"]:hover {
        background-color: #fdfdfd;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }

    /* Título (label da métrica) */
    div[data-testid="stMetric"] > label {
        color: #555;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 6px;
    }

    /* Valor principal */
    div[data-testid="stMetric"] > div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #222;
    }

    /* Delta (variação) */
    div[data-testid="stMetric"] > div[data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 500;
        border-radius: 6px;
        padding: 2px 6px;
        margin-top: 6px;
    }

    /* Delta positivo */
    div[data-testid="stMetric"] > div[data-testid="stMetricDelta"][style*="green"] {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71 !important;
    }

    /* Delta negativo */
    div[data-testid="stMetric"] > div[data-testid="stMetricDelta"][style*="red"] {
        background-color: rgba(231, 76, 60, 0.15);
        color: #e74c3c !important;
    }
    </style>
""", unsafe_allow_html=True)
