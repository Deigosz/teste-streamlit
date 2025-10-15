import streamlit as st
import os
from datetime import datetime
from fichas_manager import carregar_fichas, salvar_fichas, criar_ficha, listar_fichas

BARRACAO_OPCOES = ["A", "B", "C", "D", "E"]


def configure_page():
    st.set_page_config(layout="wide", page_title="Stock Fast Laticínio")
    st.title("🥛 Contagem de Estoque")
    st.markdown("---")


def criar_nova_ficha():
    """Cria uma ficha com nome automático e salva no JSON."""
    fichas_data = carregar_fichas()
    nome_ficha = f"Contagem - {datetime.now().strftime('%d/%m/%Y | %H:%M')}"
    nova_ficha = criar_ficha(nome_ficha)
    fichas_data["sheets"].append(nova_ficha)
    salvar_fichas(fichas_data)
    st.toast(f"Ficha '{nome_ficha}' criada com sucesso!", icon="✅", duration=3)
    
    if "fichas_lista" not in st.session_state:
        st.session_state.fichas_lista = []
    st.session_state.fichas_lista.append(nome_ficha)
    
    
def ficha_management():
    """Gerencia a criação e seleção de fichas."""
    st.subheader("Gerenciamento de Fichas")
    
    if "fichas_lista" not in st.session_state:
        st.session_state.fichas_lista = listar_fichas()
        
    if 'ficha_atual' not in st.session_state:
        if st.session_state.fichas_lista:
            st.session_state.ficha_atual = st.session_state.fichas_lista[0]
        else:
            st.session_state.ficha_atual = None

    fichas_lista = st.session_state.fichas_lista
    st.write("Selecione uma ficha:") 
    col1, col2 = st.columns([3,1]) 

    ficha_selecionada = st.session_state.ficha_atual

    with col1:
        if fichas_lista:
            current_index = fichas_lista.index(st.session_state.ficha_atual) if st.session_state.ficha_atual in fichas_lista else 0
            ficha_selecionada = st.selectbox("Selecione uma ficha:", fichas_lista, index=current_index, label_visibility="collapsed",key="selectbox_fichas")
        else:
            st.warning("Nenhuma ficha criada ainda.")
            ficha_selecionada = None # Garante que ficha_selecionada é None se a lista estiver vazia

    with col2:
        if st.button("🆕 Nova Ficha", use_container_width=True):
            criar_nova_ficha()
            
    
    if ficha_selecionada:
        if ficha_selecionada != st.session_state.ficha_atual:
            st.toast(f"Ficha '{ficha_selecionada}' selecionada!", icon="📄", duration=3)
            st.session_state.ficha_atual = ficha_selecionada
        st.info(f"Ficha selecionada: **{st.session_state.ficha_atual}**")
    


def get_lista_ruas_sequenciais(num_ruas):
    """Gera uma lista de strings de 1 até num_ruas."""
    return [f"{i:02}" for i in range(1, num_ruas + 1)]


def contagem_local_especifico():
    """
    Define e exibe a seleção de Barracão (A, B, C, D, E) 
    e ruas sequenciais de 1 a 30.
    """
    st.markdown("---")
    st.subheader("Seleção de Local de Contagem")
    
    lista_barracoes = BARRACAO_OPCOES 
    lista_ruas = get_lista_ruas_sequenciais(30)
    col_barracao, col_rua_inicial, col_rua_final  = st.columns(3) 
    
    with col_barracao:
        barracao_selecionado = st.selectbox("Selecione o Barracão:", options=lista_barracoes, key="barracao_selecionavel")

    with col_rua_inicial:
        rua_inicial = st.selectbox(
            "Rua Inicial:", 
            lista_ruas,
            key="rua_sequencial_inicial"
        )
        
    with col_rua_final:
        if rua_inicial:
            index_inicial = lista_ruas.index(rua_inicial)
            opcoes_rua_final = lista_ruas[index_inicial:]
            
            rua_final = st.selectbox(
                "Rua Final:", 
                opcoes_rua_final,
                index=0,
                key="rua_sequencial_final"
            )
        else:
            rua_final = st.selectbox("Rua Final:", ["-"], key="rua_final_disabled")

    
    st.session_state.barracao_selecionado = barracao_selecionado
    st.session_state.rua_inicial = rua_inicial
    st.session_state.rua_final = rua_final

    if rua_inicial == rua_final:
        mensagem_rua = f"Rua **{rua_inicial}**"
    else:
        mensagem_rua = f"Ruas de **{rua_inicial}** a **{rua_final}**"
    st.success(f"Local selecionado: Barracão **{barracao_selecionado}** | {mensagem_rua}")


if __name__ == "__main__":
    configure_page()
    ficha_management()
    contagem_local_especifico()