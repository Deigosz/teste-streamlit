import streamlit as st
import pandas as pd
import os

# --- Configuração Inicial ---
st.set_page_config(layout="wide")
base_path = os.path.dirname(__file__)
imagem_leite_placeholder = os.path.join(base_path, "imagens", "leite.png")


# Função auxiliar para garantir que a imagem exista ou usar um placeholder URL
def get_image_path(path):
    if os.path.exists(path):
        return path
    return "https://placehold.co/400x300/F0F2F6/262730?text=IMAGEM+PRODUTO"


# --- Simulação de banco de dados de produtos ---

caminho_csv = os.path.join(base_path, "db", "dbitens.csv")


if os.path.exists(caminho_csv):
    produtos = pd.read_csv(caminho_csv, sep=';')
else:
    st.error("❌ Arquivo db/dbitens.csv não encontrado! Verifique se ele foi incluído no repositório.")
    st.stop()
# produtos = pd.read_csv(r"db/dbitens.csv", sep=';')
produtos = produtos.rename(columns={
    "descricao": "produto",
    "qtd_por_caixa": "quantidade_por_caixa",
    "qtd_por_pallet": "quantidade_por_pallet",
    "qtd_por_camada": "quantidade_por_camada"
})

# --- Inicializa sessão para armazenar contagens ---
if "contagens" not in st.session_state:
    st.session_state.contagens = pd.DataFrame(columns=[
        "barracao", "rua", "codigo", "produto",
        "tipo_contagem", "quantidade_informada", "quantidade_total_unidades"
    ])

st.title("App")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    barracao = st.selectbox("Selecione o barracão:", ["A", "B", "C", "D", "E", "F", "G"], index=None, placeholder="Selecione...")
with col2:
    ruas = [f"{i:02d}" for i in range(1, 31)]
    rua = st.selectbox("Selecione a rua:", ruas, index=None, placeholder="Selecione...")

st.markdown("---")
produto_selecionado = st.selectbox(
    "Selecione o produto:",
    produtos["produto"]
)

# --- Informações do produto (USANDO COLUNAS) ---
info = produtos[produtos["produto"] == produto_selecionado].iloc[0]
col_img, col_info = st.columns([1, 2])
with col_img:
    st.image("https://placehold.co/400x300/F0F2F6/262730?text=SEM+IMAGEM", caption=produto_selecionado, width=400)

with col_info:
    st.markdown("#### Características Logísticas")
    st.write(f"📦 **Quantidade por caixa:** `{info['quantidade_por_caixa']}`")
    st.write(f"🧱 **Quantidade por camada:** `{info['quantidade_por_camada']}`")
    st.write(f"🏗️ **Quantidade por palete:** `{info['quantidade_por_pallet']}`")

st.markdown("---")

tipo_contagem = st.radio(
    "Como deseja informar a contagem?",
    ("Pallets", "Caixas", "Unidades")
)

# --- Entrada dinâmica ---
if tipo_contagem == "Pallets":
    qtd = st.number_input("Quantidade de pallets:", min_value=0, step=1)
    quantidade_total = qtd * info["quantidade_por_pallet"] * info["quantidade_por_caixa"]

elif tipo_contagem == "Caixas":
    qtd = st.number_input("Quantidade de caixas:", min_value=0, step=1)
    quantidade_total = qtd * info["quantidade_por_caixa"]

else:
    qtd = st.number_input("Quantidade de unidades:", min_value=0, step=1)
    quantidade_total = qtd


# --- Botão adicionar ---
if st.button("➕ Adicionar contagem"):
    if not barracao or not rua:
        st.warning("⚠️ Selecione barracão e rua antes de adicionar.")
    elif qtd <= 0:
        st.warning("⚠️ Informe uma quantidade válida.")
    else:
        # Verifica duplicidade
        if ((st.session_state.contagens["barracao"]==barracao) & (st.session_state.contagens["rua"]==rua)).any():
            st.warning("⚠️ Já existe uma contagem registrada para este barracão e rua.")
        else:
            novo_registro = {
                "barracao": barracao,
                "rua": rua,
                "codigo": info["codigo"],
                "produto": info["produto"],
                "tipo_contagem": tipo_contagem,
                "quantidade_informada": qtd,
                "quantidade_total_unidades": int(quantidade_total)
            }
            st.session_state.contagens = pd.concat([st.session_state.contagens, pd.DataFrame([novo_registro])], ignore_index=True)
            st.success(f"✅ Contagem adicionada para barracão {barracao}, rua {rua}.")
            # Limpa a seleção da rua
            st.session_state.rua = None

# --- Mostrar tabela editável ---
if not st.session_state.contagens.empty:
    st.markdown("### 📝 Contagens registradas")
    st.data_editor(st.session_state.contagens, num_rows="dynamic")

    # --- Exportar CSV ---
    if st.button("💾 Exportar CSV"):
        caminho = os.path.join(base_path, "db", "contagens_exportadas.csv")
        st.session_state.contagens.to_csv(caminho, index=False, sep=';')
        st.success(f"✅ Contagens exportadas com sucesso para `{caminho}`")