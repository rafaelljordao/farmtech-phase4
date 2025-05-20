import matplotlib.pyplot as plt
import seaborn as sns

def plot_distributions(df):
    plt.figure(figsize=(12,5))
    sns.boxplot(data=df.select_dtypes("number"))
    plt.title("Boxplot das Variáveis Numéricas")
    plt.xticks(rotation=45)
    plt.show()

def plot_correlation(df):
    nums = df.select_dtypes("number")
    corr = nums.corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", linewidths=.5)
    plt.title("Matriz de Correlação")
    plt.show()

def plot_profile(profile_df):
    ax = profile_df.plot(kind="bar", figsize=(10,6))
    ax.set_ylabel("Média")
    ax.set_ylim(0, profile_df.values.max() * 1.1)
    plt.title("Perfil Ideal vs. Fertilizantes Selecionados")
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(1.0, 1.0))
    plt.show()

def plot_model_comparison(results: dict[str, float]):
    df = (
        sns
        .barplot(x=list(results.keys()), y=list(results.values()))
    )
    plt.ylim(0,1)
    plt.ylabel("Accuracy")
    plt.title("Comparação de Acurácias dos Modelos")
    plt.xticks(rotation=45, ha="right")
    plt.show()
