import json
from pickle import load, dump
import numpy.random as rd
import folium
import pandas as pd
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import BANFrance
from streamlit_folium import folium_static
# from tqdm import tqdm

# tqdm.pandas()  # use tqdm with pandas

# *** DATA PRE-PROCESSING ***
# load adress coords dict
try:
    with open('adress_coords.pickle', 'rb') as f:
        adress_coords = load(f)
except FileNotFoundError:
    adress_coords = {}

# get coordinates from adresses
try:
    df = pd.read_csv('cartes_interactives_COORD.csv')
except FileNotFoundError:
    try:
        df = pd.read_csv('cartes_interactives.csv')

        # geolocator = Nominatim(user_agent="Alexandre Raufast")
        geolocator = BANFrance()
        # ArcGIS (inscription)
        # BANFrance
        # DataBC
        # GeoNames (inscription)
        # HERE
        # Photon
        # LiveAddress

        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=.2, error_wait_seconds=5)

        # max_retries=1 ???

        def lat_long(row):
            address = f"{row['Ville']} France"
            if address in adress_coords:
                # address already exists in dict, add some noise and return
                lat, lon = adress_coords[address]
                return lat + rd.normal(scale=1e-3), lon + rd.normal(scale=1e-3)  # differential privacy
            else:
                location = geocode(address)
                if location:
                    adress_coords[address] = (location.latitude, location.longitude)
                    return location.latitude, location.longitude
                else:
                    return 0, 0


        # https://stackoverflow.com/a/29550458/14960480
        # df[['lat', 'lon']] = df_multi_core(df=df, df_f_name='progress_apply', subset=['village', 'departement'], njobs=-1,
        #                                    func=lat_long, axis=1)
        df[['lat', 'lon']] = pd.DataFrame(df.progress_apply(lat_long, axis=1).tolist(), index=df.index)

        df = df.fillna('?')

        df.to_csv('cartes_interactives_COORD.csv', index=False)
    finally:
        with open('adress_coords.pickle', 'wb') as f:
            dump(adress_coords, f)


@st.cache
def read_csv(path):
    return pd.read_csv(path)


df = df[['Noms', 'Ville', 'Mail']]

# st.sidebar.markdown("### Villes des invit??s pour covoiturage")
# st.sidebar.markdown("...Instructions ici...")
st.title("Villes des invit??s pour covoiturage")
st.markdown("""Cette carte donne les villes des invit??s au mariage, pour les covoiturages.
Elle n'est pas reli??e au site covoitribu, c'est juste une carte que j'ai fait ?? c??t??.

Utilisez cette carte interactive pour trouver des invit??s qui habitent proche de chez vous, et demandez leur direct s'ils peuvent vous prendre : chaque point bleu est une famille d'invit??s, les coordonn??es s'affichent quand vous passez la souris dessus.

POUR CEUX QUI ONT UNE VOITURE : n'oubliez pas d'ajouter votre trajet sur le lien covoitribu, les invit??s sans voitures doivent s'y prendre tr??s ?? l'avance pour r??server leurs trains si pas de covoit !
- Lien de covoiturage pour le 13 (chez vous <--> Clermont) : https://www.covoitribu.fr/poll/24072_HZWw6rImtYGUIq
- Lien de covoiturage pour Anschald (repas) : https://www.covoitribu.fr/poll/30021_bxx9TXsOuq63mq
""")


m = folium.Map(location=[46, 2], zoom_start=5, tiles=None)
folium.TileLayer('CartoDB positron', name="Light Map", control=False).add_to(m)

geojson1 = folium.features.GeoJson(
    data=json.load(open('cartes_interactives_COORD.geojson')),
    smooth_factor=2,
    style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['Ville', 'Noms', 'Mail'],
        aliases=["Ville :", "Noms :", "Mail :"],
        localize=True,
        sticky=False,
        style="""
                       background-color: #F0EFEF;
                       border: 2px solid black;
                       border-radius: 3px;
                       box-shadow: 3px;
                   """,
        max_width=800, ),
    highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
).add_to(m)

folium_static(m)


# *** FILTERS ***
col1, _ = st.columns(2)

with col1:
    cities_list = df["Ville"].unique().tolist()
    cities_list.sort()
    city = st.selectbox("Ville", cities_list, index=1, help='S??lectionner une ville pour afficher les invit??s.')

df = df[df["Ville"] == city]

st.write(df)
# *********
