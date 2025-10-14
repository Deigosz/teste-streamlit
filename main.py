import streamlit as st
import pandas as pd
import os
import time

# --- Configuração de Caminhos e Inicialização ---
# Nota: Para um ambiente real, o ideal é usar um banco de dados (como Firestore ou PostgreSQL)
# para persistência e colaboração, mas para este ambiente local, usaremos CSV com autosave.

# Define o caminho base e o diretório de dados
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, "db")
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

PRODUTOS_CSV = os.path.join(DB_PATH, "dbItens.csv")
CONTAGENS_CSV = os.path.join(DB_PATH, "contagens_ativas.csv")

# Exemplo de conteúdo mock para dbItens.csv, caso o arquivo não exista
MOCK_PRODUTOS = pd.DataFrame({
    "codigo": [1001, 1002, 2005, 3010],
    "descricao": ["Leite Integral 1L", "Leite Semidesnatado 1L", "Creme de Leite 200g", "Iogurte Natural 170g"],
    "qtd_por_caixa": [12, 12, 27, 24],
    "qtd_por_camada": [60, 60, 108, 120],
    "qtd_por_pallet": [1080, 1080, 1944, 2160]
}).rename(columns={
    "descricao": "produto",
    "qtd_por_caixa": "quantidade_por_caixa",
    "qtd_por_pallet": "quantidade_por_pallet",
    "qtd_por_camada": "quantidade_por_camada"
})

def carregar_dados_produtos():
    """Carrega ou simula a base de dados de produtos."""
    try:
        if os.path.exists(PRODUTOS_CSV):
            produtos = pd.read_csv(PRODUTOS_CSV, sep=';')
            # Garante que as colunas tenham os nomes esperados
            produtos = produtos.rename(columns={
                "descricao": "produto",
                "qtd_por_caixa": "quantidade_por_caixa",
                "qtd_por_pallet": "quantidade_por_pallet",
                "qtd_por_camada": "quantidade_por_camada"
            })
            return produtos
        else:
            st.warning(f"⚠️ Arquivo de produtos '{PRODUTOS_CSV}' não encontrado. Usando dados mock para demonstração.")
            return MOCK_PRODUTOS
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")
        st.stop()

def carregar_contagens_existentes():
    """Carrega as contagens ativas ou cria um DataFrame vazio."""
    if os.path.exists(CONTAGENS_CSV):
        try:
            return pd.read_csv(CONTAGENS_CSV, sep=';')
        except:
            return pd.DataFrame(columns=[
                "barracao", "rua", "codigo", "produto",
                "tipo_contagem", "quantidade_informada", "quantidade_total_unidades"
            ])
    return pd.DataFrame(columns=[
        "barracao", "rua", "codigo", "produto",
        "tipo_contagem", "quantidade_informada", "quantidade_total_unidades"
    ])

def salvar_contagens(df):
    """Salva o DataFrame de contagens ativas automaticamente."""
    df.to_csv(CONTAGENS_CSV, index=False, sep=';')

# --- Execução Principal e Inicialização de Estado ---

produtos_df = carregar_dados_produtos()
produtos_df = produtos_df.astype({'codigo': str, 'quantidade_por_caixa': int, 'quantidade_por_pallet': int, 'quantidade_por_camada': int})

if "contagens" not in st.session_state:
    st.session_state.contagens = carregar_contagens_existentes()

st.set_page_config(layout="wide")

st.title("🥛 Contagem de Estoque Laticínio - Versão Rápida")
st.markdown("---")

# 1. SELEÇÃO DE LOCAL (BARRACÃO E RUA)
# Foco na Rua, pois a contagem é sequencial por rua.
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    barracoes = ["A", "B", "C", "D", "E", "F", "G"]
    barracao = st.selectbox("1. 🏢 Barracão:", barracoes, index=0)

with col2:
    ruas = [f"{i:02d}" for i in range(1, 31)]
    # Mantém o valor da sessão se existir, para agilizar a contagem sequencial
    if 'rua_selecionada' not in st.session_state:
         st.session_state.rua_selecionada = None
    
    rua = st.selectbox("2. 🛣️ Rua:", ruas, key='rua_selecionada', index=None, placeholder="Selecione a rua...")

with col3:
    if barracao and rua:
        st.success(f"LOCAL ATUAL: Barracão {barracao} / Rua {rua}", icon="📍")
    else:
        st.info("Selecione o Barracão e a Rua para começar a contagem.")

st.markdown("---")

# 2. SELEÇÃO DE PRODUTO
# Usa o código e a descrição para facilitar a busca rápida ou simular o scanner
opcoes_produto_formatadas = [f"[{row['codigo']}] {row['produto']}" for index, row in produtos_df.iterrows()]

produto_selecionado_str = st.selectbox(
    "3. 🔎 Produto (Digite Código ou Nome):",
    opcoes_produto_formatadas,
    index=0 # Assume-se que o primeiro produto é um bom default
)

# Extrai o código do produto selecionado
codigo_selecionado = produto_selecionado_str.split(']')[0].replace('[', '')
info = produtos_df[produtos_df["codigo"] == codigo_selecionado].iloc[0]

# --- Informações do produto e Visualização ---
col_img, col_info, col_vazio = st.columns([1, 1, 2])
with col_img:
    # Usando um placeholder estático (você pode substituir por uma URL real se tiver)
    st.image(
        "https://placehold.co/400x300/F0F2F6/262730?text=SEM+IMAGEM",
        caption=f"Produto: {info['produto']}",
        width=200
    )

with col_info:
    st.markdown("#### Logística")
    st.markdown(f"**Código:** `{info['codigo']}`")
    st.markdown(f"**Caixa (UN):** `{info['quantidade_por_caixa']}`")
    st.markdown(f"**Camada (CX):** `{info['quantidade_por_camada']}`")
    st.markdown(f"**Palete (CX):** `{info['quantidade_por_pallet']}`")

st.markdown("---")

# 3. ENTRADA DE DADOS E AÇÃO (FLOW RÁPIDO)

# Usa st.form para agrupar entradas e garantir que o cálculo seja feito apenas
# na submissão, mantendo a interface mais responsiva.
with st.form("form_contagem", clear_on_submit=False):
    st.markdown("### 4. 🔢 Contagem")
    
    # Prioriza Pallets, que é o mais rápido no contexto de laticínios/drives
    tipo_contagem = st.radio(
        "Como deseja informar a quantidade?",
        ("Pallets", "Caixas", "Unidades"),
        index=0, # Pallets como default para celeridade
        horizontal=True
    )

    qtd = st.number_input(
        f"Quantidade de **{tipo_contagem}** informada:",
        min_value=0,
        step=1,
        value=0,
        key=f'qtd_input_{tipo_contagem}' # Chave única para evitar conflitos
    )

    quantidade_caixas = 0
    quantidade_total = 0

    if tipo_contagem == "Pallets":
        quantidade_caixas = qtd * info["quantidade_por_pallet"]
    elif tipo_contagem == "Caixas":
        quantidade_caixas = qtd
    else: # Unidades
        # Se for unidades, o cálculo é apenas a quantidade informada
        quantidade_total = qtd

    if quantidade_caixas > 0:
        # Calcula a quantidade total de unidades APENAS se for Pallets ou Caixas
        quantidade_total = quantidade_caixas * info["quantidade_por_caixa"]
    
    # Exibe o total calculado em unidades em tempo real
    st.info(f"**TOTAL CALCULADO:** `{int(quantidade_total):,}` unidades", icon="✔️")

    # Botão de submissão do formulário
    btn_adicionar = st.form_submit_button("✅ Adicionar/Atualizar Contagem (ENTER)")
    
    # Adicionando um atalho de teclado simulado (Streamlit não suporta atalhos nativos
    # sem JS customizado, mas a tecla ENTER geralmente submete o formulário por padrão.)
    st.markdown("_Pressione ENTER para adicionar rapidamente._")

    # --- Lógica de Adição/Atualização ---
    if btn_adicionar:
        if not barracao or not rua:
            st.error("⚠️ Erro: Selecione o **Barracão** e a **Rua**.")
        elif qtd <= 0:
            st.warning("⚠️ Atenção: Informe uma quantidade válida (maior que zero).")
        else:
            novo_registro = {
                "barracao": barracao,
                "rua": rua,
                "codigo": codigo_selecionado,
                "produto": info["produto"],
                "tipo_contagem": tipo_contagem,
                "quantidade_informada": qtd,
                "quantidade_total_unidades": int(quantidade_total),
                "timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Chaves para checar unicidade (Local + Produto)
            keys = (barracao, rua, codigo_selecionado)
            
            # Verifica se a contagem para este (Local + Produto) já existe
            exists = st.session_state.contagens[
                (st.session_state.contagens["barracao"] == barracao) &
                (st.session_state.contagens["rua"] == rua) &
                (st.session_state.contagens["codigo"] == codigo_selecionado)
            ]

            if not exists.empty:
                # Se existe, atualiza a linha
                index_to_update = exists.index[0]
                for key, value in novo_registro.items():
                    st.session_state.contagens.at[index_to_update, key] = value
                st.success(f"🔄 Contagem **atualizada** para B:{barracao}, R:{rua}, Prod:{info['codigo']}.")
            else:
                # Se não existe, adiciona a nova linha
                st.session_state.contagens = pd.concat([st.session_state.contagens, pd.DataFrame([novo_registro])], ignore_index=True)
                st.success(f"➕ Contagem **adicionada** para B:{barracao}, R:{rua}, Prod:{info['codigo']}.")
            
            # Salva o estado atual automaticamente após a alteração
            salvar_contagens(st.session_state.contagens)
            
            # Limpa apenas a quantidade informada para o próximo produto na mesma rua
            st.session_state[f'qtd_input_{tipo_contagem}'] = 0
            
            # Não limpa a seleção da rua para permitir a contagem sequencial

st.markdown("---")

# 4. VISUALIZAÇÃO E EXPORTAÇÃO
if not st.session_state.contagens.empty:
    st.markdown("### 📝 Contagens Ativas (Autosalvas em `contagens_ativas.csv`)")
    
    # Filtro opcional
    barracao_filtro = st.selectbox(
        "Filtrar por Barracão para visualização:",
        ["TODOS"] + barracoes,
        index=0
    )

    df_display = st.session_state.contagens
    if barracao_filtro != "TODOS":
        df_display = df_display[df_display["barracao"] == barracao_filtro]

    # Ordena para melhor visualização
    df_display = df_display.sort_values(by=["barracao", "rua"])
    
    # Exibe a tabela editável
    st.data_editor(
        df_display,
        num_rows="dynamic",
        use_container_width=True,
        # Define as colunas que podem ser editadas (exceto as chaves)
        column_editable_state={
            "barracao": False, "rua": False, "codigo": False, "produto": False, "timestamp": False,
        }
    )

    # Botão de exportação
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False, sep=';').encode('utf-8')

    csv_export = convert_df_to_csv(st.session_state.contagens)

    st.download_button(
        label="💾 Exportar Todas Contagens (.csv)",
        data=csv_export,
        file_name=f'contagens_estoque_export_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.csv',
        mime='text/csv',
        type="primary"
    )

st.markdown("---")
st.markdown(f"💾 **Caminho de Autosave:** `{CONTAGENS_CSV}`")
