
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SGIL - Gestão Logística",
    page_icon="🚚",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    pedidos = pd.read_csv("pedidos_logisticos.csv")
    historico = pd.read_csv("historico_procura.csv")
    previsao = pd.read_csv("previsao_procura.csv")

    pedidos["Data"] = pd.to_datetime(pedidos["Data"], format="mixed", dayfirst=True)
    historico["Data"] = pd.to_datetime(historico["Data"], format="mixed", dayfirst=True)
    previsao["Data"] = pd.to_datetime(previsao["Data"], format="mixed", dayfirst=True)

    return pedidos, historico, previsao

df, historico, previsao = carregar_dados()

st.title("🚚 SGIL 1.0")
st.subheader("Sistema de Gestão e Inteligência Logística")
st.caption("Gestão de pedidos | Indicadores | Previsão da procura")

menu = st.sidebar.selectbox(
    "MENU PRINCIPAL",
    [
        "Painel Executivo",
        "Registar Pedido",
        "Consultar Pedidos",
        "Previsão da Procura"
    ]
)

def calcular_kpis(dados):
    return {
        "Pedidos": len(dados),
        "OTD": (dados["Entregue_no_Prazo"] == "Sim").mean() * 100,
        "Pedidos Perfeitos": (dados["Pedido_Perfeito"] == "Sim").mean() * 100,
        "Tempo Médio": dados["Tempo_de_Entrega"].mean(),
        "Custo Médio": dados["Custo_Envio_MZN"].mean(),
        "Urgentes": (dados["Urgente"] == "Sim").mean() * 100
    }

if menu == "Painel Executivo":
    st.header("Painel de Desempenho Logístico")
    kpi = calcular_kpis(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Pedidos", kpi["Pedidos"])
    c2.metric("OTD", f'{kpi["OTD"]:.1f}%')
    c3.metric("Pedidos Perfeitos", f'{kpi["Pedidos Perfeitos"]:.1f}%')

    c4, c5, c6 = st.columns(3)
    c4.metric("Tempo Médio", f'{kpi["Tempo Médio"]:.2f} dias')
    c5.metric("Custo Médio", f'{kpi["Custo Médio"]:.2f} MZN')
    c6.metric("Pedidos Urgentes", f'{kpi["Urgentes"]:.1f}%')

    st.subheader("Pedidos por Região")
    st.bar_chart(df.groupby("Região")["ID_Pedido"].count())

    st.subheader("Últimos Pedidos")
    st.dataframe(df.tail(10), use_container_width=True)

elif menu == "Registar Pedido":
    st.header("Registo de Novo Pedido")

    with st.form("formulario_pedido"):
        id_pedido = st.text_input("ID do Pedido")
        data = st.date_input("Data")
        produto = st.selectbox("Produto", ["Arroz 25kg", "Milho", "Feijão"])
        quantidade = st.number_input("Quantidade", min_value=1, value=100)
        regiao = st.selectbox("Região", ["Nacala", "Nampula", "Pemba", "Cuamba"])
        prazo = st.selectbox("Entregue no prazo?", ["Sim", "Não"])
        perfeito = st.selectbox("Pedido perfeito?", ["Sim", "Não"])
        tempo = st.number_input("Tempo de entrega (dias)", min_value=0)
        custo = st.number_input("Custo de envio (MZN)", min_value=0.0)
        urgente = st.selectbox("Pedido urgente?", ["Sim", "Não"])

        submeter = st.form_submit_button("Registar Pedido")

        if submeter:
            if not id_pedido.strip():
                st.error("Introduza o ID do pedido.")
            elif id_pedido.strip() in df["ID_Pedido"].astype(str).values:
                st.error("Este ID já existe.")
            else:
                novo = {
                    "ID_Pedido": id_pedido.strip(),
                    "Data": str(data),
                    "Produto": produto,
                    "Quantidade": quantidade,
                    "Região": regiao,
                    "Entregue_no_Prazo": prazo,
                    "Pedido_Perfeito": perfeito,
                    "Tempo_de_Entrega": tempo,
                    "Custo_Envio_MZN": custo,
                    "Urgente": urgente
                }

                novo_df = pd.DataFrame([novo])
                df = pd.concat([df, novo_df], ignore_index=True)
                df.to_csv("pedidos_logisticos.csv", index=False)

                st.success("Pedido registado com sucesso!")
                st.cache_data.clear()
                st.rerun()

elif menu == "Consultar Pedidos":
    st.header("Consulta da Base de Dados")

    pesquisa = st.text_input("Pesquisar por ID do pedido")

    if pesquisa:
        resultado = df[
            df["ID_Pedido"].astype(str).str.contains(
                pesquisa, case=False, na=False
            )
        ]
        st.dataframe(resultado, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    st.download_button(
        "Descarregar Base de Dados CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="pedidos_logisticos.csv",
        mime="text/csv"
    )

elif menu == "Previsão da Procura":
    st.header("Previsão da Procura")
    st.write("Estimativas para os próximos seis meses.")

    st.dataframe(previsao, use_container_width=True)

    grafico = previsao.set_index("Data")["Procura_Prevista"]
    st.line_chart(grafico)

    st.download_button(
        "Descarregar Previsões",
        data=previsao.to_csv(index=False).encode("utf-8"),
        file_name="previsao_procura.csv",
        mime="text/csv"
    )

st.sidebar.divider()
st.sidebar.caption("SGIL 1.0 | Projeto Académico 2026")
st.sidebar.caption("Gestão de Transportes e Logística")
