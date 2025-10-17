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

## SIDE BAR ##
st.sidebar.header('Filtros')
emp = st.sidebar.radio("Selecione o Empreendimento",
    options=['Viashopping', 'Viabrasil'], index = 0)

# ------------------------------- Trazendo o DF -------------------------------- #
DF_Fluxo, DFLojas = ProcTab.TabelaOriginal(emp)

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


# ------------------------------- FILTRANDO O DF -------------------------------- #
filtroSideBar = ((DFLojas['Classificação'].isin(ClassificacaoSelecionada)) &
    (DFLojas['Piso'].isin(PisosSelecionados)) &
    ((LadoSelecionado == 'Ambos')
      |
      (DFLojas['Lado']==LadoSelecionado)
      ))
filtroDataSelecionada = (DFLojas['Data'] >= inicio) & (DFLojas['Data'] <= fim)

DFLojasAtual = DFLojas.loc[filtroSideBar & filtroDataSelecionada]

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
    st.write("Em construção...")

with tab_aquisicao:
    st.header("Aquisição")

    # --- Inputs do usuário (Aquisição) ---
    # API key (preferir st.secrets; aqui usamos fallback)
    default_key = st.secrets.get("RAPIDAPI_KEY", "")
    api_key = st.text_input("RapidAPI Key", type="password", value=default_key,
                            help="Recomendado: colocar em st.secrets['RAPIDAPI_KEY'].")

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
        if not api_key:
            st.error("Informe sua RapidAPI Key.")
            st.stop()

        df_lugares = ProcTab.places(
            rating_minimo=rating_minimo,
            reviews_minimo=reviews_minimo,
            locais_escolhidos=locais_escolhidos,
            categorias=categorias,
            todos_locais=todos_locais,
            api_key=api_key,
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
    st.subheader("Dados do Pipe")
    