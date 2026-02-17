import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from .config import PROCESSED_DATA_DIR, FIGURES_DIR

PROCESSED_FILENAME = "amazon_sales_clean.csv"


def load_processed_sales_data(filename: str = PROCESSED_FILENAME) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    df = pd.read_csv(path, parse_dates=["order_date"])
    return df


def sales_trend_over_time(df: pd.DataFrame):
    df = df.copy()
    df["year_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        df.groupby("year_month")["total_revenue"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=monthly, x="year_month", y="total_revenue", marker="o")
    plt.title("Tendência de Receita Mensal")
    plt.xlabel("Ano-Mês")
    plt.ylabel("Receita Total")
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig_path = FIGURES_DIR / "sales_trend_over_time.png"
    plt.savefig(fig_path)
    plt.close()


def top_categories_by_sales(df: pd.DataFrame, top_n: int = 10):
    grouped = (
        df.groupby("product_category")["total_revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(x=grouped.values, y=grouped.index)
    plt.title(f"Top {top_n} Categorias por Receita")
    plt.xlabel("Receita Total")
    plt.ylabel("Categoria")
    plt.tight_layout()
    fig_path = FIGURES_DIR / "top_categories_by_sales.png"
    plt.savefig(fig_path)
    plt.close()


if __name__ == "__main__":
    df = load_processed_sales_data()
    sales_trend_over_time(df)
    top_categories_by_sales(df)
