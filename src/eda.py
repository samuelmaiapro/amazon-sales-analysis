import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from .config import PROCESSED_DATA_DIR, FIGURES_DIR

PROCESSED_FILENAME = "amazon_sales_clean.csv"


def load_processed_sales_data(filename: str = PROCESSED_FILENAME) -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / filename
    df = pd.read_csv(path, parse_dates=["order_date"])
    return df


def basic_eda(df: pd.DataFrame):
    print("==== Info ====")
    print(df.info())
    print("\n==== Describe (numéricas) ====")
    print(df.describe())

    # Distribuição de preço
    plt.figure(figsize=(8, 5))
    sns.histplot(df["price"], kde=True)
    plt.title("Distribuição de Preço")
    plt.tight_layout()
    fig_path = FIGURES_DIR / "dist_price.png"
    plt.savefig(fig_path)
    plt.close()

    # Correlação
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.select_dtypes("number").corr(), cmap="viridis")
    plt.title("Matriz de Correlação")
    plt.tight_layout()
    fig_path = FIGURES_DIR / "correlation_matrix.png"
    plt.savefig(fig_path)
    plt.close()


if __name__ == "__main__":
    df = load_processed_sales_data()
    basic_eda(df)
