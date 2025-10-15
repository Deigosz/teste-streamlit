import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fichas_manager import carregar_fichas, salvar_fichas, criar_ficha, listar_fichas

BARRACAO_OPCOES = ["A", "B", "C", "D", "E"]

def carregar_dados_produtos():
    """Carrega os dados de produtos em um DataFrame do pandas."""
    data = [
        {'codigo_amarracao_imagem': '2320070006', 'codigo': '2320070006-109', 'descricao': 'BEB LACTEA ACHOCOLATADO SHEFA COM TAMPA 1000 ML', 'familia_comercial': 'Achoc - Litro', 'familia_material': 'ACHOCOL. 1000 ML SHEFA', 'qtd_por_caixa': 12, 'qtd_por_pallet': 85, 'qtd_por_camada': 17, 'marca': 'SHEFA', 'tipo': 'MIX'},
        {'codigo_amarracao_imagem': '2320060011', 'codigo': '2320060011-109', 'descricao': 'BEB LACTEA ACHOCOLATADO SHEFA 200 ML', 'familia_comercial': 'Achoc - 200', 'familia_material': 'ACHOCOL. 200 ML SHEFA', 'qtd_por_caixa': 27, 'qtd_por_pallet': 170, 'qtd_por_camada': 17, 'marca': 'SHEFA', 'tipo': 'MIX'},
        {'codigo_amarracao_imagem': '200150006', 'codigo': '200150006-109', 'descricao': 'ALIMENTO COM SOJA - SABOR ORIGINAL LIDER 1000 ML', 'familia_comercial': 'Soja - Originais', 'familia_material': 'ALIM. A BASE DE SOJA', 'qtd_por_caixa': 12, 'qtd_por_pallet': 85, 'qtd_por_camada': 17, 'marca': 'LIDER', 'tipo': 'MIX'},
        {'codigo_amarracao_imagem': '2320090003', 'codigo': '2320090003-109', 'descricao': 'BEB LACTEA COM AVEIA SHEFA 1000 ML', 'familia_comercial': 'Aveia - Litro', 'familia_material': 'AVEIA 1000 ML SHEFA', 'qtd_por_caixa': 12, 'qtd_por_pallet': 85, 'qtd_por_camada': 17, 'marca': 'SHEFA', 'tipo': 'MIX'},
        {'codigo_amarracao_imagem': '2320080006', 'codigo': '2320080006-109', 'descricao': 'BEB LACTEA COM AVEIA SHEFA 200 ML', 'familia_comercial': 'Aveia - 200', 'familia_material': 'AVEIA 200 ML SHEFA', 'qtd_por_caixa': 27, 'qtd_por_pallet': 170, 'qtd_por_camada': 17, 'marca': 'SHEFA', 'tipo': 'MIX'},
        {'codigo_amarracao_imagem': '2120300001', 'codigo': '2120300001-106', 'descricao': 'REFRESCO SABORIZADO COM FRUTAS SHEFA - SABOR UVA 150 ML', 'familia_comercial': 'Beb de Fruta - 150', 'familia_material': 'BEB. FRUTAS 150 ML SHEFA', 'qtd_por_caixa': 27, 'qtd_por_pallet': 204, 'qtd_por_camada': 17, 'marca': 'SHEFA', 'tipo': 'BEBIDAS'}
    ]
    df = pd.DataFrame(data)
    return df

@st.cache_data
def get_produtos_df():
    return carregar_dados_produtos()


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
    
    
def selecao_de_item():
    """Permite ao usuário filtrar e selecionar um item usando um selectbox pesquisável."""
    st.markdown("---")
    st.subheader("🔎 Busca e Seleção de Item")

    df_produtos = get_produtos_df()

    # CORREÇÃO DE ROBUSTEZ: Garante que a coluna 'display' exista no df original, 
    # caso o cache não a tenha preservado corretamente.
    if 'display' not in df_produtos.columns:
        df_produtos['display'] = df_produtos['codigo'] + ' - ' + df_produtos['descricao']


    # 1. Filtros (Marca e Tipo)
    col_filtro_marca, col_filtro_tipo = st.columns(2)
    
    with col_filtro_marca:
        # Verifica se as colunas existem antes de tentar acessar
        if 'marca' in df_produtos.columns:
            marcas = [''] + sorted(df_produtos['marca'].unique().tolist()) # Adiciona item vazio
            filtro_marca = st.selectbox("Filtrar por Marca:", marcas, index=0)
        else:
            marcas = ['']
            filtro_marca = ''
            st.warning("Coluna 'marca' não encontrada nos dados.")
        
    with col_filtro_tipo:
        if 'tipo' in df_produtos.columns:
            tipos = [''] + sorted(df_produtos['tipo'].unique().tolist()) # Adiciona item vazio
            filtro_tipo = st.selectbox("Filtrar por Tipo:", tipos, index=0)
        else:
            tipos = ['']
            filtro_tipo = ''
            st.warning("Coluna 'tipo' não encontrada nos dados.")

    df_filtrado = df_produtos.copy()

    if filtro_marca != '' and 'marca' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['marca'] == filtro_marca]

    if filtro_tipo != '' and 'tipo' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['tipo'] == filtro_tipo]
        
    if df_filtrado.empty:
        st.info("Nenhum produto encontrado com os filtros aplicados.")
        st.session_state.item_selecionado = None
        return 

    st.markdown("---")
    opcoes_display = ['Selecione um produto ou comece a digitar...'] + df_filtrado['display'].tolist()
    
    item_selecionado_display = st.selectbox(
        "Selecione o Produto (SKU/Descrição):",
        options=opcoes_display,
        index=0,
        key="selectbox_item",
    )
    
    if item_selecionado_display != 'Selecione um produto ou comece a digitar...':
        item_selecionado = df_filtrado[df_filtrado['display'] == item_selecionado_display].iloc[0]
        
        st.session_state.item_selecionado = item_selecionado.to_dict()
        st.success(f"Item Selecionado: **{item_selecionado['codigo']} - {item_selecionado['descricao']}**")
        st.markdown("#### Detalhes de Amarrações")
        
        col_img, col_dados = st.columns([1, 2])
        with col_img:
            caminho_imagem_relativo = "imagens/leite.png"
            try:
                # Tenta exibir a imagem usando o caminho relativo
                st.image(
                    caminho_imagem_relativo, 
                    caption=f"Cód. Imagem: {item_selecionado['codigo_amarracao_imagem']}"
                )
            except FileNotFoundError:
                st.error(f"Imagem não encontrada! Verifique se '{caminho_imagem_relativo}' existe.")
            except Exception as e:
                # Outros erros de media file storage
                st.warning(f"Erro ao exibir a imagem. Detalhes: {e}")

        with col_dados:
            st.metric("SKU Completo", item_selecionado['codigo'])
            st.metric("Qtd por Caixa", f"{item_selecionado['qtd_por_caixa']} un")
            st.metric("Qtd por Lastro (Camada)", f"{item_selecionado['qtd_por_camada']} caixas")
            st.metric("Qtd por Pallet", f"{item_selecionado['qtd_por_pallet']} caixas")

    else:
        st.session_state.item_selecionado = None
        st.info("Aguardando seleção do item...")



if __name__ == "__main__":
    configure_page()
    ficha_management()
    contagem_local_especifico()
    selecao_de_item()