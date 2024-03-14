import pandas as pd
import matplotlib.pyplot as plt

# gráfico de barras tipos de obras
df = pd.read_csv('C:/mangas.csv')

type_counts = df['type'].value_counts()

plt.figure(figsize=(10, 8))
type_counts.plot(kind='bar', color=plt.cm.Paired(range(len(type_counts))))

plt.xlabel('Tipo')
plt.ylabel('Quantidade')
plt.title('Quantidade por Tipo')
plt.xticks(rotation=45)

for i, value in enumerate(type_counts):
    plt.text(i, value + 0.05, str(value), ha='center')

# Exibir o gráfico
plt.tight_layout()
plt.show()