import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# gráfico de barras mangás por ano
df = pd.read_csv('C:/mangas.csv')

def extract_year(date_str):
    if 'to' in date_str:
        start_date = date_str.split('to')[0].strip()
    else:
        start_date = date_str.strip()
    try:
        return datetime.strptime(start_date, '%b %d, %Y').year
    except ValueError:
        try:
            return datetime.strptime(start_date, '%b %Y').year
        except ValueError:
            return None

df['year_started'] = df['published'].apply(extract_year)

current_year = datetime.now().year
df_filtered = df[df['year_started'] >= current_year - 10]

manga_counts = df_filtered['year_started'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
manga_counts.plot(kind='bar', color=plt.cm.tab20(range(len(manga_counts))))

plt.xlabel('Ano de Lançamento')
plt.ylabel('Quantidade de Mangás')
plt.title('Quantidade de Mangás Lançados por Ano nos Últimos 10 Anos')
plt.xticks(rotation=45)

for i, value in enumerate(manga_counts):
    plt.text(i, value + 0.05, str(value), ha='center')

plt.tight_layout()
plt.show()
