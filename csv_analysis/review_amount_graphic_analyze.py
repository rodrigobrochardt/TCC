import pandas as pd
import matplotlib.pyplot as plt

# gráfico de dispersão reviews
df = pd.read_csv('C:/reviews.csv')

review_counts = df['manga_id'].value_counts().sort_values(ascending=False)

plot_data = pd.DataFrame({
    'manga_id': review_counts.index,
    'reviews': review_counts.values
})

plt.figure(figsize=(10, 6))
plt.scatter(plot_data['manga_id'], plot_data['reviews'])

plt.xlabel('Manga ID')
plt.ylabel('Quantidade de Avaliações')
plt.title('Quantidade de Avaliações por Manga ID (Ordem Decrescente)')
plt.grid(True)

plt.tight_layout()
plt.show()
