from src.data_ingestion import download_amazon_sales_dataset
from src.data_preprocessing import load_raw_sales_data, clean_sales_data, save_processed_data
from src.eda import basic_eda
from src.visualization import sales_trend_over_time, top_categories_by_sales


def main():
    # 1. Download / ingestão
    download_amazon_sales_dataset()

    # 2. Carregar dados brutos
    raw_df = load_raw_sales_data()

    # 3. Limpeza
    clean_df = clean_sales_data(raw_df)
    save_processed_data(clean_df)

    # 4. EDA básica
    basic_eda(clean_df)

    # 5. Visualizações específicas
    sales_trend_over_time(clean_df)
    top_categories_by_sales(clean_df)


if __name__ == "__main__":
    main()
