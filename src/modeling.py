import xgboost as xgb
from sklearn.linear_model    import LogisticRegression
from sklearn.neighbors       import KNeighborsClassifier
from sklearn.tree            import DecisionTreeClassifier
from sklearn.ensemble        import RandomForestClassifier
from sklearn.svm             import SVC
from sklearn.metrics         import accuracy_score

def train_all_models(X_train, y_train, X_test, y_test) -> dict[str, float]:
    """
    Treina e avalia os 6 modelos no split fornecido.
    """
    models = {
        "Logistic Regression":    LogisticRegression(max_iter=2000),
        "K-Nearest Neighbors":    KNeighborsClassifier(n_neighbors=5),
        "Decision Tree":          DecisionTreeClassifier(random_state=42),
        "Random Forest":          RandomForestClassifier(n_estimators=100, random_state=42),
        "Support Vector Machine": SVC(kernel="linear", probability=True, random_state=42),
        "XGBoost":                xgb.XGBClassifier(eval_metric="mlogloss", random_state=42)
    }

    results = {}
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        results[name] = accuracy_score(y_test, preds)
    return results
