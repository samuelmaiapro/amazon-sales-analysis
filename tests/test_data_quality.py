import pandas as pd
from src.config import PROCESSED_DATA_DIR


def test_processed_data_exists():
    path = PROCESSED_DATA_DIR / "amazon_sales_clean.csv"
    assert path.exists(), "Arquivo de dados processados não existe."


def test_no_all_null_columns():
    path = PROCESSED_DATA_DIR / "amazon_sales_clean.csv"
    df = pd.read_csv(path)
    null_cols = [c for c in df.columns if df[c].isna().all()]
    assert len(null_cols) == 0, f"Colunas totalmente nulas encontradas: {null_cols}"
