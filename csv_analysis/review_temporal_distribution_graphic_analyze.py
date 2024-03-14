import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Gráfico de área temporal reviews
df = pd.read_csv('C:/reviews.csv')

df['date'] = pd.to_datetime(df['date'], errors='coerce')

reviews_per_day = df.groupby(df['date'].dt.date).size()

plt.figure(figsize=(12, 6))
plt.fill_between(reviews_per_day.index, reviews_per_day.values, color='skyblue', alpha=0.4)
plt.plot(reviews_per_day.index, reviews_per_day.values, color='Slateblue', alpha=0.6, linewidth=2)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator())

plt.xlabel('Data')
plt.ylabel('Quantidade de Avaliações')
plt.title('Quantidade de Avaliações de Mangá ao Longo do Tempo')
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()