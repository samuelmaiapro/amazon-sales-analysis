import shutil
from pathlib import Path

import kagglehub
from .config import RAW_DATA_DIR, KAGGLE_DATASET


def download_amazon_sales_dataset() -> Path:
    """
    Faz o download da última versão do dataset de vendas da Amazon
    via kagglehub e copia os arquivos para data/raw.
    Retorna o caminho local do diretório em data/raw.
    """
    print(f"Baixando dataset '{KAGGLE_DATASET}' via kagglehub...")
    path = kagglehub.dataset_download(KAGGLE_DATASET)
    source_path = Path(path)

    target_dir = RAW_DATA_DIR / "amazon_sales"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copia todos os arquivos do download para data/raw/amazon_sales
    for item in source_path.iterdir():
        dest = target_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    print("Download concluído.")
    print("Arquivos copiados para:", target_dir)

    return target_dir


if __name__ == "__main__":
    download_amazon_sales_dataset()
