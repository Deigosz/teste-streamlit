import streamlit as st
import pandas as pd
import os
import json
import time

# --- Configuração Inicial e Constantes ---
st.set_page_config(layout="wide", page_title="Stock Fast Laticínio")

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, "db")
INVENTORY_DB_FILE = os.path.join(DB_PATH, "inventory_db.json")

# Garante que a pasta 'db' exista
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# --- MOCK DE DADOS DE PRODUTOS (Simulando dbItens.csv com Marca e Tipo) ---
MOCK_PRODUCTS = [
    {'codigo': 'L001', 'produto': 'Leite Integral 1L', 'marca': 'Líder', 'tipo': 'Leite UHT', 'quantidade_por_caixa': 12, 'quantidade_por_pallet': 1080, 'quantidade_por_camada': 60},
    {'codigo': 'L002', 'produto': 'Leite Semi-Desnatado 1L', 'marca': 'Líder', 'tipo': 'Leite UHT', 'quantidade_por_caixa': 12, 'quantidade_por_pallet': 1080, 'quantidade_por_camada': 60},
    {'codigo': 'A005', 'produto': 'Iogurte Natural 170g', 'marca': 'Aurora', 'tipo': 'Refrigerado', 'quantidade_por_caixa': 24, 'quantidade_por_pallet': 2160, 'quantidade_por_camada': 120},
    {'codigo': 'X101', 'produto': 'Creme de Leite 200g', 'marca': 'Xuxa', 'tipo': 'Culinário', 'quantidade_por_caixa': 27, 'quantidade_por_pallet': 1944, 'quantidade_por_camada': 108},
    {'codigo': 'A006', 'produto': 'Mussarela Fatiada 1kg', 'marca': 'Aurora', 'tipo': 'Refrigerado', 'quantidade_por_caixa': 10, 'quantidade_por_pallet': 800, 'quantidade_por_camada': 40},
]
PRODUCTS_DF = pd.DataFrame(MOCK_PRODUCTS).astype({'quantidade_por_caixa': int, 'quantidade_por_pallet': int, 'quantidade_por_camada': int})


# --- Funções de Persistência (Simulação de Banco de Dados) ---

def load_db():
    """Carrega as fichas de contagem do arquivo JSON."""
    if os.path.exists(INVENTORY_DB_FILE):
        try:
            with open(INVENTORY_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Erro ao ler o arquivo de dados. Criando um novo arquivo.")
            return {"sheets": []}
    return {"sheets": []}

def save_db(db_data):
    """Salva as fichas de contagem no arquivo JSON."""
    with open(INVENTORY_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)


# --- Inicialização do Estado (Apenas na Primeira Execução) ---

if 'db_data' not in st.session_state:
    st.session_state.db_data = load_db()

    # Define a ficha selecionada (a mais recente ou cria uma)
    if not st.session_state.db_data["sheets"]:
        st.session_state.selected_sheet_id = None
    else:
        st.session_state.selected_sheet_id = st.session_state.db_data["sheets"][-1]["id"] # Pega a última ficha

    # Estado da interface
    st.session_state.barracao = 'A'
    st.session_state.rua = '01'
    st.session_state.drive_inicial = 1
    st.session_state.drive_final = 1
    st.session_state.qtd_input = 0
    st.session_state.tipo_contagem = 'Pallets'
    st.session_state.marca_filter = 'TODAS'
    st.session_state.tipo_filter = 'TODAS'
    st.session_state.selected_product_code = PRODUCTS_DF.iloc[0]['codigo']

# --- Funções de Lógica ---

def create_sheet():
    """Cria uma nova ficha de contagem e a salva no DB."""
    new_id = f"sheet_{int(time.time())}"
    new_name = f"Ficha {time.strftime('%Y-%m-%d %H:%M')}"
    new_sheet = {
        "id": new_id,
        "name": new_name,
        "createdAt": time.time(),
        "counts": [] # Lista para armazenar as contagens
    }
    st.session_state.db_data["sheets"].append(new_sheet)
    st.session_state.selected_sheet_id = new_id
    save_db(st.session_state.db_data)
    st.success(f"✅ Ficha '{new_name}' criada e selecionada!")
    # Força um re-run para atualizar a UI
    st.rerun() 

# Garante que haja pelo menos uma ficha ao iniciar
if not st.session_state.db_data["sheets"]:
    if st.button("Criar Primeira Ficha de Contagem"):
        create_sheet()
    else:
        st.info("Para começar, crie uma Ficha de Contagem.")
        st.stop()


def get_current_sheet():
    """Retorna a ficha de contagem atualmente selecionada."""
    if not st.session_state.selected_sheet_id:
        return None
    
    sheet = next((s for s in st.session_state.db_data["sheets"] if s["id"] == st.session_state.selected_sheet_id), None)
    return sheet


def calculate_total_units(quantity, product_info, type_contagem):
    """Calcula o total de unidades com base no tipo de contagem."""
    if product_info.empty:
        return 0
        
    product = product_info.iloc[0]
    
    if type_contagem == 'Pallets':
        return int(quantity * product['quantidade_por_pallet'] * product['quantidade_por_caixa'])
    elif type_contagem == 'Caixas':
        return int(quantity * product['quantidade_por_caixa'])
    elif type_contagem == 'Unidades':
        return int(quantity)
    return 0

def handle_submit_count(product_info, total_calculado):
    """
    Processa a contagem, lida com Range Counting e Auto-Advance da Rua.
    """
    barracao = st.session_state.barracao
    rua = st.session_state.rua
    drive_inicial = st.session_state.drive_inicial
    drive_final = st.session_state.drive_final
    qtd = st.session_state.qtd_input
    tipo = st.session_state.tipo_contagem
    
    current_sheet = get_current_sheet()
    
    if not current_sheet or qtd <= 0 or drive_inicial > drive_final:
        st.error("🚨 Erro: Verifique a ficha, quantidade ou drives.")
        return

    product_code = product_info.iloc[0]['codigo']
    product_name = product_info.iloc[0]['produto']
    
    drives = range(drive_inicial, drive_final + 1)
    counts_updated = 0

    for drive in drives:
        count_id = f"{barracao}_{rua}_{drive}_{product_code}"
        
        new_count = {
            "id": count_id,
            "barracao": barracao,
            "rua": rua,
            "drive": drive,
            "codigo": product_code,
            "produto": product_name,
            "tipo_contagem": tipo,
            "quantidade_informada": qtd,
            "quantidade_total_unidades": total_calculado,
            "timestamp": time.time()
        }
        
        # Procura por uma contagem existente (para UPDATE)
        found = False
        for i, count in enumerate(current_sheet["counts"]):
            if count["id"] == count_id:
                # Atualiza a contagem existente (permite correção rápida)
                current_sheet["counts"][i] = new_count
                found = True
                counts_updated += 1
                break
        
        if not found:
            # Adiciona a nova contagem
            current_sheet["counts"].append(new_count)
            counts_updated += 1

    # Salva a alteração no arquivo JSON
    save_db(st.session_state.db_data)
    
    # --- Lógica de Auto-Advance de Rua ---
    if counts_updated > 0:
        st.session_state.qtd_input = 0 # Zera a quantidade para a próxima entrada
        
        # Se foi uma contagem de drive único (ou a última rua)
        if drive_inicial == drive_final:
            ruas_list = [f"{i:02d}" for i in range(1, 31)]
            current_index = ruas_list.index(rua)
            
            if current_index < len(ruas_list) - 1:
                # Avança para a próxima rua
                st.session_state.rua = ruas_list[current_index + 1]
                st.session_state.drive_inicial = 1
                st.session_state.drive_final = 1
                st.success(f"✅ Contagem(ns) registrada(s)! Avançando para Rua {st.session_state.rua}.")
            else:
                st.session_state.rua = '01'
                st.warning("⚠️ Fim das Ruas! Voltando para '01'. Sugerimos mudar o Barracão.")

# --- UI PRINCIPAL ---

st.title("🥛 Stock Fast: Contagem de Estoque - Streamlit")
st.markdown("---")

current_sheet = get_current_sheet()
if not current_sheet:
    st.warning("⚠️ Nenhuma ficha de contagem selecionada ou criada.")
    st.stop()


# --- 1. SELEÇÃO E GERENCIAMENTO DE FICHA ---
st.header(f"📍 Ficha Ativa: {current_sheet['name']}")

col_sheet, col_new = st.columns([3, 1])
sheet_options = {s["id"]: s["name"] for s in st.session_state.db_data["sheets"]}

with col_sheet:
    st.session_state.selected_sheet_id = st.selectbox(
        "Selecione a Ficha de Contagem:",
        options=list(sheet_options.keys()),
        format_func=lambda x: sheet_options[x],
        index=list(sheet_options.keys()).index(st.session_state.selected_sheet_id) if st.session_state.selected_sheet_id in sheet_options else 0,
        key='sheet_selector'
    )
with col_new:
    st.button("➕ Nova Ficha", on_click=create_sheet, use_container_width=True)

st.markdown("---")

# --- 2. LOCAL DE CONTAGEM (BARRACÃO, RUA, DRIVES) ---

st.subheader("🗺️ Localização e Drives")
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.session_state.barracao = st.selectbox(
        "🏢 Barracão:", ["A", "B", "C", "D", "E", "F", "G"],
        index=["A", "B", "C", "D", "E", "F", "G"].index(st.session_state.barracao),
        key='barracao'
    )

with col2:
    ruas = [f"{i:02d}" for i in range(1, 31)]
    st.session_state.rua = st.selectbox(
        "🛣️ Rua:", ruas,
        index=ruas.index(st.session_state.rua),
        key='rua'
    )

with col3:
    st.session_state.drive_inicial = st.number_input(
        "Drive Inicial:", min_value=1, step=1, value=st.session_state.drive_inicial, key='drive_inicial'
    )

with col4:
    st.session_state.drive_final = st.number_input(
        "Drive Final:", min_value=st.session_state.drive_inicial, step=1, value=st.session_state.drive_final, key='drive_final'
    )

drives_count = st.session_state.drive_final - st.session_state.drive_inicial + 1
st.info(f"📍 **Local Atual:** Barracão **{st.session_state.barracao}**, Rua **{st.session_state.rua}**. Contando **{drives_count} drive(s)**.")

# Checagem de alerta para rua já contada
rua_has_counts = any(c['barracao'] == st.session_state.barracao and c['rua'] == st.session_state.rua for c in current_sheet['counts'])
if rua_has_counts:
    st.warning(f"⚠️ **Atenção:** A Rua {st.session_state.rua} já possui contagens nesta ficha. A nova contagem será adicionada/atualizada.")

st.markdown("---")

# --- 3. SELEÇÃO DE PRODUTO COM FILTROS (Marca e Tipo) ---

st.subheader("🔎 Produto (Filtros e Busca)")

col_marca, col_tipo = st.columns(2)
marcas = ['TODAS'] + sorted(PRODUCTS_DF['marca'].unique().tolist())
tipos = ['TODOS'] + sorted(PRODUCTS_DF['tipo'].unique().tolist())

with col_marca:
    st.session_state.marca_filter = st.selectbox(
        "Filtrar por Marca:", marcas,
        index=marcas.index(st.session_state.marca_filter) if st.session_state.marca_filter in marcas else 0,
        key='marca_filter'
    )
    
with col_tipo:
    st.session_state.tipo_filter = st.selectbox(
        "Filtrar por Tipo:", tipos,
        index=tipos.index(st.session_state.tipo_filter) if st.session_state.tipo_filter in tipos else 0,
        key='tipo_filter'
    )

# Aplica os filtros
filtered_df = PRODUCTS_DF.copy()
if st.session_state.marca_filter != 'TODAS':
    filtered_df = filtered_df[filtered_df['marca'] == st.session_state.marca_filter]
if st.session_state.tipo_filter != 'TODAS':
    filtered_df = filtered_df[filtered_df['tipo'] == st.session_state.tipo_filter]

# Cria as opções formatadas para o selectbox
product_options = {row['codigo']: f"[{row['codigo']}] {row['produto']}" 
                   for index, row in filtered_df.iterrows()}

if not product_options:
    st.error("Nenhum produto encontrado com os filtros selecionados.")
    st.stop()
    
# Garante que o produto selecionado exista
if st.session_state.selected_product_code not in product_options:
    st.session_state.selected_product_code = filtered_df.iloc[0]['codigo']

st.session_state.selected_product_code = st.selectbox(
    "Selecione o Produto (Busca por Código/Nome):",
    options=list(product_options.keys()),
    format_func=lambda x: product_options[x],
    key='product_code_selector'
)

# Pega as informações logísticas
current_product_info = PRODUCTS_DF[PRODUCTS_DF['codigo'] == st.session_state.selected_product_code]
if not current_product_info.empty:
    info = current_product_info.iloc[0]
    
    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image("https://placehold.co/150x150/F0F2F6/262730?text=IMAGEM", caption=info['produto'], width=150)

    with col_info:
        st.markdown("#### Características Logísticas")
        st.markdown(f"**📦 Qtd por caixa:** `{info['quantidade_por_caixa']}`")
        st.markdown(f"**🧱 Qtd por camada:** `{info['quantidade_por_camada']}`")
        st.markdown(f"**🏗️ Qtd por palete (Caixas):** `{info['quantidade_por_pallet']}`")
else:
    st.error("Produto não encontrado!")
    st.stop()


st.markdown("---")

# --- 4. ENTRADA DE QUANTIDADE E AÇÃO ---

st.subheader("🔢 Contagem e Ação")

st.session_state.tipo_contagem = st.radio(
    "Tipo de Contagem:",
    ("Pallets", "Caixas", "Unidades"),
    index=["Pallets", "Caixas", "Unidades"].index(st.session_state.tipo_contagem),
    horizontal=True,
    key='tipo_contagem'
)

st.session_state.qtd_input = st.number_input(
    f"Quantidade de **{st.session_state.tipo_contagem}** informada:",
    min_value=0,
    step=1,
    value=st.session_state.qtd_input,
    key='qtd_input'
)

total_calculado = calculate_total_units(st.session_state.qtd_input, current_product_info, st.session_state.tipo_contagem)

st.success(f"**TOTAL CALCULADO:** `{total_calculado:,.0f}` unidades", icon="✔️")


# Botão de Ação
st.button(
    "✅ Adicionar/Atualizar Contagem (ENTER)",
    on_click=lambda: handle_submit_count(current_product_info, total_calculado),
    use_container_width=True,
    type="primary",
    disabled=st.session_state.qtd_input <= 0
)

st.markdown("---")

# --- 5. VISUALIZAÇÃO E EXPORTAÇÃO ---

st.subheader("📝 Contagens Registradas na Ficha Atual")

if current_sheet['counts']:
    counts_df = pd.DataFrame(current_sheet['counts'])
    counts_df['drive'] = counts_df['drive'].astype(int)
    
    # Ordena a tabela por Rua e Drive para melhor visualização
    counts_df = counts_df.sort_values(by=['barracao', 'rua', 'drive'])
    
    # Colunas para exibir
    display_cols = [
        "barracao", "rua", "drive", "codigo", "produto", 
        "tipo_contagem", "quantidade_informada", "quantidade_total_unidades"
    ]
    
    st.dataframe(
        counts_df[display_cols],
        column_config={
            "barracao": "Barracão",
            "rua": "Rua",
            "drive": "Drive",
            "codigo": "Cód.",
            "produto": "Produto",
            "tipo_contagem": "Tipo Qtd",
            "quantidade_informada": "Qtd. Informada",
            "quantidade_total_unidades": st.column_config.NumberColumn(
                "Total Unidades", format="%d"
            ),
        },
        use_container_width=True,
        hide_index=True
    )

    # Função para exportar CSV (usando o DataFrame já processado)
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False, sep=';').encode('utf-8')

    csv_export = convert_df_to_csv(counts_df)

    st.download_button(
        label="💾 Exportar Ficha Atual (.csv)",
        data=csv_export,
        file_name=f'ficha_estoque_{current_sheet["name"].replace(" ", "_")}.csv',
        mime='text/csv',
        type="secondary"
    )

else:
    st.info("Nenhuma contagem registrada nesta ficha ainda.")

st.markdown("---")
st.caption(f"Dados persistidos em: `{INVENTORY_DB_FILE}`. Salve este arquivo para manter suas fichas!")
