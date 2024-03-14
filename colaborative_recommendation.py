import pandas as pd
import seaborn as sns
from surprise import Reader, Dataset, SVD
from surprise.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
sns.set_style("ticks")

#COLABORATIVE FILTERING SCRIPT
reader = Reader(rating_scale=(1,10))
df_title = pd.read_csv('C:/mangas.csv')
df_title.set_index('id', inplace = True)
df = pd.read_csv('C:/reviews.csv') 
print(df.size)

#gera objeto Dataset da biblioteca com o relacionamento de usuarios e mangas
data = Dataset.load_from_df(df[['user_id', 'manga_id', 'rating']], reader)
svd = SVD()
#aplica o treinamento com uma parte do dataset
trainset, testset = train_test_split(data, test_size=0.2)
svd.fit(trainset)
predictions = svd.test(testset)
#realiza medição das métricas de desempenho
y_true = [pred.r_ui for pred in predictions]
y_pred = [pred.est for pred in predictions]
mae_svd = mean_absolute_error(y_true, y_pred)
rmse_svd = np.sqrt(mean_squared_error(y_true, y_pred))
print(f"MAE for SVD: {mae_svd:.4f}")
print(f"RMSE for SVD: {rmse_svd:.4f}")

#checa as obras do perfil para quem será realizado recomendação
df_1 = df[(df['user_id'] == 1)]
df_1 = df_1.set_index('manga_id')
df_1 = df_1.join(df_title)[['title','rating','genres']]
print(df_1)
print("")

#realiza predição para o usuario pelo id
pd.set_option('display.max_rows', 1000)

user_1 = df_title.copy()
user_1 = user_1.reset_index()
user_1['estimate_score'] = user_1['id'].apply(lambda x: svd.predict(1, x).est)
user_1 = user_1.drop('id', axis=1)
user_1 = user_1.sort_values('estimate_score', ascending=False)
user_1 = user_1[user_1['genres'] != "[]"]

# Limita a quantidade de caracteres do 'title' para 11
user_1['title'] = user_1['title'].apply(lambda x: x[:11])
#print(user_1[['title', 'type', 'genres', 'estimate_score']].head(300))



#PEARSONS' R CORRELATION SCRIPT
print("PEARSONS' R CORRELATION:")

#cria um dataframe que representa as relações entre obras e usuários
df_p = pd.pivot_table(df,values='rating',index='user_id',columns='manga_id')
#print(df_p[2].head())
def recommend(title_id, min_count):
    print("Mangá ({})".format(df_title.loc[title_id,"title"][:11]))
    print("- Top 10 obras recomendadas baseado em correlação de Pearson - ")
    target = df_p[title_id] #obtem a obra alvo
    #realiza calculo de correlação entre linhas e colunas
    similar_to_target = df_p.corrwith(target)
    #gera um dataframe com os valores de correlação em uma coluna
    corr_target = pd.DataFrame(similar_to_target, columns = ['PearsonR'])
    corr_target.dropna(inplace = True)
    corr_target = corr_target.sort_values('PearsonR', ascending = False)
    corr_target.index = corr_target.index.map(int)
    f = ['count','mean']
    #adiciona atributos do dataframe original para o dataframe gerado
    df_title_summary = df.groupby('manga_id')['rating'].agg(f)
    df_title_summary.index = df_title_summary.index.map(int)
    corr_target = corr_target.join(df_title).join(df_title_summary)[['PearsonR', 'title', 'genres', 'count', 'mean']]
    # Limita a quantidade de caracteres do 'title' para 11 e inclui o campo 'genres'
    corr_target['title'] = corr_target['title'].apply(lambda x: x[:11])
    corr_target = corr_target[corr_target['genres'] != "[]"]
    print(corr_target[corr_target['count']>min_count][['title', 'genres', 'PearsonR', 'count', 'mean']].sort_values('PearsonR', ascending = False).to_string(index=False))

#executa o método escolhendo a obra de base e qtd. minima de avaliações
recommend(2, 0)
