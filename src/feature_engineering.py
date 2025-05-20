import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split

def prepare_features(df: pd.DataFrame):
    # 1) Separa X e y
    X = df.drop('Fertilizer Name', axis=1)
    y = df['Fertilizer Name']

    # 2) Label encode do target
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # 3) One-hot encode nas variáveis categóricas
    cat_cols = ['Soil Type', 'Crop Type']
    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_cat = pd.DataFrame(
        ohe.fit_transform(X[cat_cols]),
        columns=ohe.get_feature_names_out(cat_cols),
        index=X.index
    )
    X_num = X.drop(cat_cols, axis=1)
    X_prepared = pd.concat([X_num, X_cat], axis=1)

    # 4) Split treino/teste com stratify para manter proporções
    X_train, X_test, y_train, y_test = train_test_split(
        X_prepared,
        y_enc,
        test_size=0.2,
        random_state=42,
        stratify=y_enc
    )

    # 5) Normaliza as variáveis numéricas
    num_cols = X_num.columns
    scaler = MinMaxScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols]  = scaler.transform(X_test[num_cols])

    return X_train, X_test, y_train, y_test
