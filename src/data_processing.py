import pandas as pd

def load_and_clean(path: str) -> pd.DataFrame:
    """
    Carrega o CSV e aplica limpeza básica (ex.: strip em colunas,
    remoção de duplicatas, tratar missing, etc).
    """
    df = pd.read_csv(path)
    # remover espaços em nomes de coluna
    df.columns = df.columns.str.strip()
    # checar e eliminar duplicatas
    df = df.drop_duplicates()
    # … (qualquer outra limpeza) …
    return df

def prepare_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o perfil ideal (média de todas as features numéricas)
    e retorna um DataFrame com índice 'Ideal Geral'.
    """
    numeric_cols = ['Temperature', 'Humidity', 'Moisture',
                    'Nitrogen', 'Potassium', 'Phosphorous']
    perfil = (
        df[numeric_cols]
        .mean()
        .rename('Ideal Geral')
        .to_frame()
        .T
    )
    return perfil
