# -&bull;- coding: utf-8 -&bull;-
"""
Created on Wed May 20 10:29:08 2026

@author: Mirian Ojer
"""
import sys
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import requests
import geopandas as gpd
from io import StringIO
import os
from pathlib import Path

#  Paths base (repo)
#BASE_DIR = Path(__file__).resolve().parent
BASE_DIR =Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"

print(BASE_DIR)
print(RAW_DIR)
print(OUT_DIR)

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(">>> INICIO DEL SCRIPT")
'''
# Detectar la carpeta real donde está el .py o el .exe
if getattr(sys, 'frozen', False):
    # Si está congelado en exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si está en .py normal
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
'''

# basandome en https://www.lexnavarra.navarra.es/detalle.asp?r=37630  Capitulo 2 Articulo 6
#Descarga de capas
url = (
    "https://inspire.navarra.es/services/riesgoIncendios/wfs/"
    "?service=WFS"
    "&version=2.0.0"
    "&request=GetFeature"
    "&typeNames=riesgoIncendios:vw_riesgomunicipiod0"
    "&outputFormat=application/json"
)

gdf = gpd.read_file(url)
gdf.to_file(RAW_DIR / "vw_riesgometeoalertad0.shp")
url = (
    "https://inspire.navarra.es/services/riesgoIncendios/wfs/"
    "?service=WFS"
    "&version=2.0.0"
    "&request=GetFeature"
    "&typeNames=riesgoIncendios:vw_riesgometeoalertad0lg"
    "&outputFormat=application/json"
)

gdf = gpd.read_file(url)
gdf.to_file(RAW_DIR / "vw_riesgomunicipiod0.shp")


#Este es el de Sina viso que aparece de [Sin aviso, Verde, Amarillo, Naranja, Rojo]
Riesgo_de_incendio = gpd.read_file(RAW_DIR+"vw_riesgometeoalertad0.shp")

#Este es el de Sina viso que aparece de [Bajo, Moderado, Alto, Muy Alto, Extremo]
Aviso_Temp_Extrema = gpd.read_file(RAW_DIR+"vw_riesgomunicipiod0.shp")

now = datetime.now()
current_time = now.strftime("%H_%M_%S")

lista_Riesgo_de_incendio = ['Sin aviso', 'Verde', 'Amarillo', 'Naranja', 'Rojo']
lista_Aviso_Temp_Extrema = ['Bajo', 'Moderado', 'Alto', 'Muy Alto', 'Extremo']

gdf_merge = Riesgo_de_incendio.merge(
    Aviso_Temp_Extrema[['Municipio', 'Alerta']],
    on='Municipio',
    how='left'   # mantiene todas las filas de gdf1
)

#gdf_merge['Labores']= np.nan 
gdf_merge['Labores'] = None

#Generar casos aleatorios
gdf_merge['Alerta_x'] = np.random.choice(['Sin aviso', 'Verde', 'Amarillo', 'Naranja', 'Rojo'],len(gdf_merge))
gdf_merge['Alerta_y'] = np.random.choice(['Bajo', 'Moderado', 'Alto', 'Muy Alto', 'Extremo'],len(gdf_merge))

for i in range(len(gdf_merge)):
    if gdf_merge.loc[i, 'Alerta_y'] in ['Bajo', 'Moderado', 'Alto']:
        gdf_merge.loc[i, 'Labores'] = 'Permitidas'
        
    elif gdf_merge.loc[i, 'Alerta_x'] == 'Amarillo' and gdf_merge.loc[i, 'Alerta_y'] in ['Muy Alto', 'Extremo']:        
        gdf_merge.loc[i, 'Labores'] = 'Permitidas condicional'
        
    elif gdf_merge.loc[i, 'Alerta_x'] == 'Naranja' and gdf_merge.loc[i, 'Alerta_y'] in ['Muy Alto', 'Extremo']:    
        gdf_merge.loc[i, 'Labores'] =  'Permitidas condicional estricta'

    elif gdf_merge.loc[i, 'Alerta_x'] == 'Rojo' and gdf_merge.loc[i, 'Alerta_y'] in ['Muy Alto', 'Extremo']:    
        gdf_merge.loc[i, 'Labores'] =  'Prohibidas completamente'
    
    elif pd.isnull(gdf_merge.loc[i, 'Labores']):
        gdf_merge.loc[i, 'Labores'] =  'Permitidas'

# PDF
colores = {
    'Permitidas': 'green',
    'Permitidas condicional': 'yellow',
    'Permitidas condicional estricta': 'orange',
    'Prohibidas completamente': 'red'
}

gdf_merge['color'] = gdf_merge['Labores'].map(colores)

gdf_merge.to_file(OUT_DIR +"/AA_Mapa_Incendio_Unificado.shp", driver="ESRI Shapefile")
gdf_merge.to_file(OUT_DIR +"/incendios_unificados.geojson", driver="GeoJSON")

