import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from src.config import PROCESSED_DATA_DIR
from src.data_preprocessing import PROCESSED_FILENAME


@st.cache_data
df = load_processed_data()
    """
    Carrega o CSV já processado a partir de data/processed.
    No Streamlit Cloud, assumimos que o arquivo já está versionado no repositório.
    """
    path = PROCESSED_DATA_DIR / PROCESSED_FILENAME
    df = pd.read_csv(path, parse_dates=["order_date"])
    return df


def main():
    st.set_page_config(
        page_title="Amazon Sales Analysis",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Amazon Sales Analysis")
    st.markdown(
        """
        Dashboard interativo de vendas da Amazon, baseado em dataset público do Kaggle.
        """
    )

    # Carregar dados
    df = load_or_create_processed_data()

    # Filtros na barra lateral
    st.sidebar.header("Filtros")

    # Intervalo de datas
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["order_date"] >= pd.to_datetime(start_date)) &
                (df["order_date"] <= pd.to_datetime(end_date))]

    # Filtro de região
    regions = ["Todas"] + sorted(df["customer_region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Região do Cliente", regions)
    if selected_region != "Todas":
        df = df[df["customer_region"] == selected_region]

    # Filtro de categoria
    categories = ["Todas"] + sorted(df["product_category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Categoria do Produto", categories)
    if selected_category != "Todas":
        df = df[df["product_category"] == selected_category]

    # KPIs principais
    total_revenue = df["total_revenue"].sum()
    total_orders = df["order_id"].nunique()
    avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
    avg_rating = df["rating"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", f"${total_revenue:,.2f}")
    col2.metric("Nº de Pedidos", f"{total_orders:,}")
    col3.metric("Ticket Médio", f"${avg_ticket:,.2f}")
    col4.metric("Rating Médio", f"{avg_rating:.2f}")

    st.markdown("---")

    # Gráfico 1: Tendência de receita no tempo
    st.subheader("Tendência de Receita Mensal")

    df_temp = df.copy()
    df_temp["year_month"] = df_temp["order_date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        df_temp.groupby("year_month")["total_revenue"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=monthly, x="year_month", y="total_revenue", marker="o", ax=ax1)
    ax1.set_xlabel("Ano-Mês")
    ax1.set_ylabel("Receita Total")
    ax1.tick_params(axis="x", rotation=45)
    st.pyplot(fig1)

    # Gráfico 2: Top categorias por receita
    st.subheader("Top Categorias por Receita")

    top_n = st.slider("Top N categorias", min_value=5, max_value=20, value=10, step=1)
    cat_revenue = (
        df.groupby("product_category")["total_revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=cat_revenue, x="total_revenue", y="product_category", ax=ax2)
    ax2.set_xlabel("Receita Total")
    ax2.set_ylabel("Categoria")
    st.pyplot(fig2)

    # Gráfico 3: Receita por região
    st.subheader("Receita por Região")

    region_revenue = (
        df.groupby("customer_region")["total_revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=region_revenue, x="total_revenue", y="customer_region", ax=ax3)
    ax3.set_xlabel("Receita Total")
    ax3.set_ylabel("Região")
    st.pyplot(fig3)

    # Tabela detalhada
    st.subheader("Amostra de Dados Filtrados")
    st.dataframe(df.head(50))


if __name__ == "__main__":
    main()
