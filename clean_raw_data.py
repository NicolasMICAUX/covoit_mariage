"""clean RAW data."""
import os

import pandas as pd

df = pd.read_excel('Adresses pour faire-parts mariage.xlsx')

# garder seulement ceux qui n'ont pas dis qu'ils ne venaient pas
df = df[df['Présence'] != 0]

# garder seulement là où adresses renseignées
df = df.dropna(subset=['Adresse'])

# remove all things inside parentheses in the column
df['Noms'] = df['Noms'].str.replace(r'\(.*\)', '')

# Export to CSV
df.to_csv('cartes_interactives.csv', index=False)

# delete 'cartes_interactives_COORD.csv'
if 'cartes_interactives_COORD.csv' in os.listdir():
    os.remove('cartes_interactives_COORD.csv')
