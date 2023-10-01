# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import fiona
from PIL import Image

st.set_page_config(layout="wide")


# import all dataset
#base_df = pd.read_csv('data/base_df.csv')
@st.cache_data
def load_data(location):
    base_df = gpd.read_file(location)
    return base_df

base_df = load_data('https://storage.googleapis.com/datakota/data/base_gdf2.geojson')

# list of analysis keys
population_list_key = ['POPULASI', 'JUMLAH_KK', 'LUAS_WILAYAH', 'KEPADATAN']
religion_list_key = ['ISLAM', 'KRISTEN', 'KATOLIK', 'HINDU', 'BUDDHA', 'KONGHUCU', 'KEPERCAYAAN']
sex_list_key = ['PRIA', 'WANITA', 'BELUM_KAWIN', 'KAWIN', 'CERAI_HIDUP', 'CERAI_MATI']
education_list_key = ['Tidak/Belum Sekolah',
                    'Belum Tamat SD/Sederajat',
                    'Tamat SD/Sederajat',
                    'SMP/Sederajat',
                    'SMA/Sederajat',
                    'Diploma I/II',
                    'Akademi/Diploma III/S. Muda',
                    'Diploma IV/Strata I',
                    'Strata II',
                    'Strata III',]
age_list_key = ['U0',
                'U5',
                'U10',
                'U15',
                'U20',
                'U25',
                'U30',
                'U35',
                'U40',
                'U45',
                'U50',
                'U55',
                'U60',
                'U65',
                'U70',
                'U75',
                'usia_balita', 
                'usia_sekolah',
                'usia_produktif', 
                'usia_lansia']
job_list_key = list(gpd.read_file('https://storage.googleapis.com/datakota/data/jobs_df.geojson').columns)[5:-2]


with st.sidebar:
    
    with st.container():
        image = Image.open('logo/Artboard 2.png')
        st.image(image)
        st.title('kotadata')
        st.subheader('Geospatial Insights of Indonesian Cities')
        st.write('use the selectboxes below to do your analysis')
        
        # Selectbox for province subset
        st.header('location')
        province_list = list(base_df.sort_values(by='PROVINSI').PROVINSI.unique())
        province_analysis = st.selectbox('province', options=province_list, key='province')

        # Selectbox for city subset
        city_list = ['All Cities'] + list(base_df[base_df.PROVINSI == province_analysis].sort_values(by='KAB_KOTA').KAB_KOTA.unique())
        city_analysis = st.selectbox('cities', options=city_list, key='city')

        # import geodataframe
        if city_analysis == 'All Cities':
            gdf = base_df[base_df.PROVINSI == province_analysis]
        else: 
            gdf = base_df[base_df.KAB_KOTA == city_analysis]
        
        gdf['KODE_DESA']=gdf['KODE_DESA'].astype(int)


        # Selectbox for demographic analysis
        st.header('demographics')
        demo_list = ['population', 'religion', 'sex', 'education', 'age', 'jobs']
        demo_analysis = st.selectbox('analysis', options=demo_list, key='demographics')
    
        # generate lists of sub_analysis
        if demo_analysis == 'population':
            sub_list = population_list_key
        elif demo_analysis == 'religion':
            sub_list = religion_list_key
        elif demo_analysis == 'sex':
            sub_list = sex_list_key
        elif demo_analysis == 'age':
            sub_list = age_list_key
        elif demo_analysis == 'education':
            sub_list = education_list_key
        else:
            sub_list = job_list_key
        
        
        # Selectbox for demographic sub analysis
        demo_sub_analysis = st.selectbox('sub-analysis', options=sub_list, key='demographic2')

        # import dataset according to selection
        
        df_join = pd.read_csv(f'https://storage.googleapis.com/datakota/data/{demo_analysis}_df.csv', usecols= ['KODE_DESA'] + [demo_sub_analysis])
        df_join['KODE_DESA']=df_join['KODE_DESA'].astype(int)
        df = pd.merge(gdf, df_join, how='left', on='KODE_DESA')

        # Selectbox for demographic normalizer
        normalizer_list = [None, 'Per sqKM', 'Per Total Population']
        normalizer = st.selectbox('normalize', options=normalizer_list, key='normalizer')
        df['val'] = df[demo_sub_analysis]
        df['RESULT'] = df['val'].round(2).astype(str) + f' {demo_sub_analysis}'
        if normalizer == 'Per sqKM':
            df['val'] = df[demo_sub_analysis]/df['LUAS_WILAYAH']
            df['RESULT'] = df['val'].round(2).astype(str) + f' {demo_sub_analysis} {normalizer}'
        elif normalizer == 'Per Total Population':
            df['val'] = df[demo_sub_analysis]/df['total']
            df['RESULT'] = df['val'].round(2).astype(str) + f' {demo_sub_analysis} {normalizer}'

        

        # Selectbox for mapping color tools
        st.header('mapping')
        color_list = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                      'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
        color_select = st.selectbox('color', options=color_list, key='colors')
        
        # Selectbox for color binning schemes
        scheme_list = [None, 'NaturalBreaks', 'Quantiles', 'Percentiles', 'StdMean']
        scheme_select = st.selectbox('schemes', options=scheme_list, key='schemes')



#st.write(df.sample(5))
map = df.explore(column = df['val'],
                    cmap = color_select,
                    tiles = 'CartoDB positron',
                    tooltip = ['PROVINSI', 'KAB_KOTA', 'KECAMATAN', 'DESA_KELURAHAN', 'RESULT'],
                    scheme = scheme_select, 
                    highlight = True, 
                    popup = False, 
                    style_kwds = {  #'stroke':0.1,
                                    'weight' : 0.5,
                                    'fillOpacity' : 0.8}, 
                    )

st_folium(map, 
        #center = (106.8,-6.8),
        returned_objects= [],
        width= 1000, 
        height = 800
        )




