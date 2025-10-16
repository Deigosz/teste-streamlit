import streamlit as st
import os
import pandas as pd
from datetime import datetime

if '_mock_fichas_storage' not in st.session_state:
    st.session_state['_mock_fichas_storage'] = {
        "sheets": [
            {"name": "Ficha de Exemplo 1", "data": []}
        ]
    }

def carregar_fichas():
    return st.session_state['_mock_fichas_storage']

def salvar_fichas(data):
    st.session_state['_mock_fichas_storage'] = data

def criar_ficha(nome):
    return {"name": nome, "data": []}

def listar_fichas():
    return [sheet["name"] for sheet in st.session_state['_mock_fichas_storage']["sheets"]]

BARRACAO_OPCOES = ["A", "B", "C", "D", "E"]

def carregar_dados_produtos():
    caminho_produtos = "db/dbItens.csv" 
    try:
        df = pd.read_csv(caminho_produtos, sep=';')
        return df
    except pd.errors.ParserError as e:
        st.error(f"Erro ao carregar dados: Verifique se o arquivo CSV '{caminho_produtos}' está formatado corretamente.")
        st.error(f"Detalhes do erro: {e}")
        return pd.DataFrame()


@st.cache_data
def get_produtos_df():
    return carregar_dados_produtos()


def configure_page():
    st.set_page_config(layout="wide", page_title="Stock Fast Laticínio")
    st.title("🥛 Contagem de Estoque")
    st.markdown("---")


def criar_nova_ficha():
    fichas_data = carregar_fichas()
    nome_ficha = f"Contagem - {datetime.now().strftime('%d/%m/%Y | %H:%M')}"
    nova_ficha = criar_ficha(nome_ficha)
    fichas_data["sheets"].append(nova_ficha)
    salvar_fichas(fichas_data)
    
    st.session_state.fichas_lista = listar_fichas()
    st.session_state.ficha_atual = nome_ficha
    
    st.session_state.contagens_registradas = []
    
    st.toast(f"Ficha '{nome_ficha}' criada com sucesso!", icon="✅", duration=3)


def ficha_management():
    st.subheader("Gerenciamento de Fichas")
    
    st.session_state.fichas_lista = listar_fichas()
        
    if 'ficha_atual' not in st.session_state and st.session_state.fichas_lista:
        st.session_state.ficha_atual = st.session_state.fichas_lista[0]
        fichas_data = carregar_fichas()
        ficha_encontrada = next((f for f in fichas_data["sheets"] if f["name"] == st.session_state.ficha_atual), None)
        st.session_state.contagens_registradas = ficha_encontrada["data"] if ficha_encontrada else []


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
            ficha_selecionada = None 

    with col2:
        if st.button("🆕 Nova Ficha", use_container_width=True):
            criar_nova_ficha()
            st.rerun()
    
    
    if ficha_selecionada:
        if ficha_selecionada != st.session_state.ficha_atual:
            st.session_state.ficha_atual = ficha_selecionada
            
            fichas_data = carregar_fichas()
            ficha_encontrada = next((f for f in fichas_data["sheets"] if f["name"] == ficha_selecionada), None)
            
            if ficha_encontrada:
                st.session_state.contagens_registradas = ficha_encontrada["data"]
            else:
                st.session_state.contagens_registradas = []
            
            st.toast(f"Ficha '{ficha_selecionada}' carregada com {len(st.session_state.contagens_registradas)} registros!", icon="📄", duration=3)
            st.rerun()
        
        st.info(f"Ficha selecionada: **{st.session_state.ficha_atual}**")
    
def get_lista_ruas_sequenciais(num_ruas):
    return [f"{i:02}" for i in range(1, num_ruas + 1)]


def contagem_local_especifico():
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
            
            current_rua_final = st.session_state.get('rua_final', rua_inicial)
            try:
                default_index = opcoes_rua_final.index(current_rua_final)
            except ValueError:
                default_index = 0
            
            rua_final = st.selectbox(
                "Rua Final:", 
                opcoes_rua_final,
                index=default_index,
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


if 'form_pallets_totais_value' not in st.session_state:
    st.session_state.form_pallets_totais_value = 1
if 'form_caixas_soltas_value' not in st.session_state:
    st.session_state.form_caixas_soltas_value = 0


def salvar_e_visualizar_contagem(item_selecionado, pallets, caixas):
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    novo_registro = {
        'Hora': timestamp,
        'SKU': item_selecionado['codigo'],
        'Descrição': item_selecionado['descricao'],
        'Barracão': st.session_state.barracao_selecionado, 
        'Rua Inicial': st.session_state.rua_inicial,
        'Rua Final': st.session_state.rua_final, 
        'Pallets': pallets,
        'Caixas Soltas': caixas
    }
    
    st.session_state.contagens_registradas.append(novo_registro)
    
    fichas_data = carregar_fichas()
    ficha_atual_nome = st.session_state.ficha_atual
    
    for ficha in fichas_data["sheets"]:
        if ficha["name"] == ficha_atual_nome:
            ficha["data"] = st.session_state.contagens_registradas
            break
            
    salvar_fichas(fichas_data)
    
    st.toast(f"✅ Item {item_selecionado['codigo']} registrado e salvo!", icon="📝")
    
    st.session_state.form_pallets_totais_value = 1
    st.session_state.form_caixas_soltas_value = 0
    st.rerun()


def selecao_de_item():
    st.markdown("---")
    st.subheader("🔎 Busca e Seleção de Item")

    df_produtos = get_produtos_df()
    
    if df_produtos.empty:
        st.warning("Não foi possível carregar os dados de produtos. Verifique o arquivo `db/dbItens.csv`.")
        return 

    if 'display' not in df_produtos.columns:
        df_produtos['display'] = df_produtos['codigo'].astype(str) + ' - ' + df_produtos['descricao'].astype(str)
        
    col_filtro_marca, col_filtro_tipo = st.columns(2)
    
    with col_filtro_marca:
        if 'marca' in df_produtos.columns:
            marcas = [''] + sorted(df_produtos['marca'].unique().tolist())
            filtro_marca = st.selectbox("Filtrar por Marca:", marcas, index=0)
        else:
            marcas = ['']
            filtro_marca = ''
            st.warning("Coluna 'marca' não encontrada nos dados.")
        
    with col_filtro_tipo:
        if 'tipo' in df_produtos.columns:
            tipos = [''] + sorted(df_produtos['tipo'].unique().tolist())
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
    #i
    
    if item_selecionado_display != 'Selecione um produto ou comece a digitar...':
        item_selecionado = df_filtrado[df_filtrado['display'] == item_selecionado_display].iloc[0]
        st.session_state.item_selecionado = item_selecionado.to_dict()
        
        st.success(f"Item Selecionado: **{item_selecionado['codigo']} - {item_selecionado['descricao']}**")
        st.markdown("#### Detalhes e Contagem Rápida")
        
        col_detalhes_e_amarracoes, col_contagem_rapida = st.columns([1, 2.5]) 
        
        with col_detalhes_e_amarracoes:
            st.markdown("##### Amarrações")
            
            caminho_imagem_relativo = "imagens/leite.png" 
            
            try:
                st.image(
                    caminho_imagem_relativo, 
                    caption=f"Cód. Amarr.: {item_selecionado.get('codigo_amarracao_imagem')}",
                    width=200
                )
            except Exception:
                st.warning("Imagem Indisponível", icon="🖼️")

            st.markdown("""
                <style>
                div[data-testid="stMetricValue"] {
                    font-size: 1.1rem; 
                }
                div[data-testid="stMetricLabel"] > div {
                    font-size: 0.8rem;
                }
                </style>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.metric("SKU", item_selecionado['codigo'])
            st.metric("Qtd/Pallet", f"{item_selecionado['qtd_por_pallet']} cx")
            st.metric("Qtd/Lastro", f"{item_selecionado['qtd_por_camada']} cx")
            st.metric("Qtd/Caixa", f"{item_selecionado['qtd_por_caixa']} un")


        with col_contagem_rapida:
            st.markdown("##### 📝 Registro de Contagem")
            
            ficha_atual = st.session_state.get('ficha_atual')
            barracao = st.session_state.get('barracao_selecionado')
            rua_inicial = st.session_state.get('rua_inicial')
            
            if not (ficha_atual and barracao and rua_inicial):
                st.error("Selecione a Localização (Barracão/Rua) na seção acima.")
                return
            
            with st.form("form_contagem_rapida_integrada", clear_on_submit=False): 
                
                col_pallet, col_caixa = st.columns(2)
                
                with col_pallet:
                    pallets_totais = st.number_input(
                        "Total de PALLETS Contados:", 
                        min_value=1, step=1, 
                        key="form_pallets_totais",
                        value=st.session_state.form_pallets_totais_value, 
                    )
                
                with col_caixa:
                    caixas_soltas = st.number_input(
                        "Caixas Soltas:",
                        min_value=0, step=1,
                        key="form_caixas_soltas",
                        value=st.session_state.form_caixas_soltas_value, 
                    )
                
                submitted = st.form_submit_button("💾 SALVAR CONTAGEM (ENTER)", type="primary", use_container_width=True)

            if submitted:
                salvar_e_visualizar_contagem(item_selecionado, pallets_totais, caixas_soltas)

            st.markdown("---")
            st.markdown("##### Contagens Registradas nesta Ficha")
            
            if st.session_state.contagens_registradas:
                df_registros = pd.DataFrame(st.session_state.contagens_registradas)

                csv_data = df_registros.to_csv(index=False).encode('utf-8')
                
                col_tabela, col_download = st.columns([4, 1])

                with col_tabela:
                    st.dataframe(
                        df_registros,
                        column_order=["Hora", "SKU", "Barracão", "Rua Inicial", "Rua Final", "Pallets", "Caixas Soltas"],
                        column_config={
                            "Barracão": st.column_config.Column(width="small"),
                            "Rua Inicial": st.column_config.Column("Rua Ini", width="small"),
                            "Rua Final": st.column_config.Column("Rua Fim", width="small"),
                        },
                        hide_index=True,
                        use_container_width=True,
                        height=300
                    )
                
                with col_download:
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"{st.session_state.ficha_atual.replace(' | ', '_').replace('/', '-')}_export.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("Nenhuma contagem registrada para este item na ficha atual.")

    else:
        st.session_state.item_selecionado = None
        st.info("Aguardando seleção do item...")

if __name__ == "__main__":
    configure_page()
    ficha_management()
    contagem_local_especifico()
    selecao_de_item()
