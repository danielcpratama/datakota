# import libraries
import pandas as pd
import streamlit as st
import geopandas as gpd
from streamlit_folium import st_folium
import plotly.express as px
import time
from google.cloud import storage
import os
from st_files_connection import FilesConnection
# from streamlit_gsheets import GSheetsConnection
import datetime
import pages.kota as kota
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
import io

# set page config
st.set_page_config(
    page_title="Jobs Analysis",
    layout="wide", 
    page_icon= "🛠️", 
    initial_sidebar_state='collapsed'
)
# ------------------------------------------------------------------------------
st.image('logo/logo.png', width=80)
st.title('Jobs Analysis')
if st.button('< back'):
    st.switch_page('pages/datakota_explorer.py')
# ------------------------------------------------------------------------------
# SET UP SIDE BAR
with st.sidebar:
    kota.sign_in()
    st.subheader('Contact us!')
    st.markdown("""
    [twitter](https://twitter.com/danielcaesarp)  
    [instagram](https://instagram.com/datakota.app)  
    [email](hi.datakota@gmail.com)  
    [github](https://github.com/danielcpratama/datakota)

    """)
   
    

# ------------------------------------------------------------------------------

# connect to google cloud service
gcs_credentials = st.secrets.connections.gcs
storage_client = storage.Client.from_service_account_info(info=gcs_credentials)

# import base data
@st.cache_data
def get_cities(file_name):
    conn = st.connection('gcs', type=FilesConnection)
    df = conn.read(f"datakota-bucket/{file_name}", input_format="csv", ttl=600)
    return df

@st.cache_data
def get_geom(geom_URL):
    bucket_name = 'datakota-bucket'
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(geom_URL)
    # Download the file to a local temporary file
    with open('temp.geojson', 'wb') as temp_file:
        blob.download_to_file(temp_file, timeout=900)
    # Read the GeoJSON file using geopandas
    gdf = gpd.read_file('temp.geojson')
    # Don't forget to clean up the temporary file
    os.remove('temp.geojson')
    return gdf

base_df = get_cities("data/base.csv").drop(columns=['Unnamed: 0'])
data = 'jobs'
data_df = get_cities(f"data/{data}_df.csv").drop(columns=['Unnamed: 0','KODE_KECAMATAN', 'KODE_KAB_KOTA', 'KODE_PROVINSI'])
join_df = pd.merge(base_df, data_df, how='left', on='KODE_KEL_DESA')


# ------------------------------------------------------------------------------

col1, col2 = st.columns([0.3, 0.7], gap='medium')

with col1:
    # st.write('use the selectboxes below to do your analysis')
    # ---------------------------------------
    st.markdown('#### Units & Scale')
    
    # Selectbox for Extent subset
    extent_list = ['National-wide', 'Province-wide', 'City-wide']
    extent_analysis = st.selectbox('scale', options=extent_list, key='extent')
    
    # Selectbox for smallest unit
    if extent_analysis == 'National-wide':
        unit_list = ['PROVINSI', 'KAB_KOTA']
    elif extent_analysis == 'Province-wide':
        unit_list = ['KAB_KOTA', 'KECAMATAN']
    else: 
        unit_list = ['KECAMATAN', 'DESA_KELURAHAN']
    unit_analysis = st.selectbox('units of analysis', options=unit_list, key='units')
    # ---------------------------------------
    st.markdown('### Location')

    # Selectbox for Province subset
    if extent_analysis == 'National-wide':
        province_list = ['All Provinces']
    else:
        province_list = list(base_df.sort_values(by='NAMA_PROVINSI').NAMA_PROVINSI.unique())
    province_analysis = st.selectbox('province', options=province_list, key='province')

    # Selectbox for city subset
    if extent_analysis == 'City-wide':
        city_list = list(base_df[base_df.NAMA_PROVINSI == province_analysis].sort_values(by='NAMA_KAB_KOTA').NAMA_KAB_KOTA.unique())
    elif unit_analysis == 'KAB_KOTA':
        city_list = ['All Cities']
    else:
        city_list = ['All Cities'] + list(base_df[base_df.NAMA_PROVINSI == province_analysis].sort_values(by='NAMA_KAB_KOTA').NAMA_KAB_KOTA.unique())
    city_analysis = st.selectbox('cities', options=city_list, key='city')
    # ---------------------------------------
    st.markdown('### Analysis')

    # Selectbox for demographic analysis
    analysis_key = list(join_df.columns)[14:]
    sub_analysis = st.selectbox('sub-analysis', options=analysis_key, key='population')

    # Selectbox for demographic normalizer
    normalizer_list = [None, 'Per sqKM', 'Per Total Population', 'Per Household']
    normalizer = st.selectbox('normalize', options=normalizer_list, key='normalizer')
    # ---------------------------------------

    # getting the correct geometry address
    
    if extent_analysis == 'National-wide':
        geom_URL = f'geom/ALL_{unit_analysis}.geojson'
    else:
        geom_URL = f'geom/{unit_analysis}_BY_PROVINCE/{province_analysis}_{unit_analysis}.geojson'

    




with col2:
    tab1, tab2, tab3, tab4 = st.tabs(["maps", "charts", "metadata", "downloads"])
    with tab1:
        
        # calling and subsetting geodataframe
        with st.spinner('dicariin dulu ya...'):
            gdf = get_geom(geom_URL=geom_URL)
            if city_analysis == 'All Cities':
                gdf = get_geom(geom_URL=geom_URL)
            else: 
                gdf = get_geom(geom_URL=geom_URL)[gdf.NAMA_KAB_KOTA == city_analysis]     
        gdf.KODE_PROVINSI = gdf.KODE_PROVINSI.astype(str)

        # merging dataframe and geodataframe
        if unit_analysis == 'DESA_KELURAHAN':
            pivot_df = join_df[['KODE_KEL_DESA', 'POPULASI', 'JUMLAH_KK']+analysis_key]
            pivot_gdf = pd.merge(gdf,pivot_df, how='left', on='KODE_KEL_DESA').rename(columns={'NAMA_KEL_DESA':'NAMA_DESA_KELURAHAN'})
        elif unit_analysis == 'KECAMATAN':
            pivot_df = join_df.groupby(by=f'KODE_{unit_analysis}').sum()[analysis_key + ['POPULASI', 'JUMLAH_KK']]
            pivot_gdf = pd.merge(gdf.rename(columns = {'KODE_KEC':'KODE_KECAMATAN'}),pivot_df, how='left', on=f'KODE_KECAMATAN')
        elif unit_analysis == 'KAB_KOTA':
            pivot_df = join_df.groupby(by=f'KODE_{unit_analysis}').sum()[analysis_key+ ['POPULASI', 'JUMLAH_KK']]
            pivot_gdf = pd.merge(gdf,pivot_df, how='left', on=f'KODE_KAB_KOTA')
        else:
            pivot_df = join_df.groupby(by=f'NAMA_{unit_analysis}').sum()[analysis_key+ ['KODE_PROVINSI', 'POPULASI', 'JUMLAH_KK']].reset_index()
            pivot_df.KODE_PROVINSI = pivot_df.KODE_PROVINSI.astype(int).astype(str)
            pivot_gdf = pd.merge(gdf,pivot_df, how='left', on=f'NAMA_PROVINSI')

        # calculating normalization
        pivot_gdf['val'] = pivot_gdf[sub_analysis]
        pivot_gdf['RESULT'] = pivot_gdf['val'].round(2).astype(str) + f' {sub_analysis}'
        if normalizer == 'Per sqKM':
            pivot_gdf['val'] = pivot_gdf[sub_analysis]/pivot_gdf['LUAS_SQKM']
            pivot_gdf['RESULT'] = pivot_gdf['val'].round(2).astype(str) + f' {sub_analysis} {normalizer}'
            pivot_gdf = pivot_gdf.dropna()
        elif normalizer == 'Per Total Population':
            pivot_gdf['val'] = pivot_gdf[sub_analysis]/pivot_gdf['POPULASI']*100
            pivot_gdf['RESULT'] = pivot_gdf['val'].round(2).astype(str) + f'% {sub_analysis} {normalizer}'
            pivot_gdf = pivot_gdf.dropna()
        elif normalizer == 'Per Household':
            pivot_gdf['val'] = pivot_gdf[sub_analysis]/pivot_gdf['JUMLAH_KK']*100
            pivot_gdf['RESULT'] = pivot_gdf['val'].round(2).astype(str) + f'% {sub_analysis} {normalizer}'
            pivot_gdf = pivot_gdf.dropna()

        # draw map here
        with st.spinner('digambar dulu ya... '):            
            # map name
            if normalizer != None: 
                title = str.title(f'Map of {sub_analysis} {normalizer} distribution, by {unit_analysis} in {city_analysis}, {province_analysis} ')
                st.markdown(f'##### {title}')
            else: 
                title = str.title(f'Map of {sub_analysis} distribution, by {unit_analysis} in {city_analysis}, {province_analysis} ')
                st.markdown(f'##### {title}')

            cmap = 'plasma'
            map = pivot_gdf.explore(column = pivot_gdf['val'],
                                cmap = cmap,
                                tiles = 'CartoDB positron',
                                #tiles = map_tile,
                                attr = "mapbox",
                                color = 'white',
                                tooltip = [f'NAMA_{unit_analysis}', 'RESULT'],
                                scheme = 'EqualInterval', 
                                k = 10, 
                                highlight = True, 
                                popup = True,
                                legend = True,
                                style_kwds = {'stroke':0.5,
                                                'color' : 'black',
                                                'weight' : 0.5,
                                                'fillOpacity' : 0.8
                                                }, 
                                legend_kwds = {'colorbar': False, 'caption': title, 'fmt':'{:,.0f}'}
                                )
            
            with st.container(border=True, height= 550):
                st_folium(map, 
                    #center = (106.8,-6.8),
                    returned_objects= [],
                    #width= 1000, 
                    height = 500, 
                    use_container_width=True
                    )
            # MAKING LEGENDS
            # Create a separate plot just for the legend
            legend_fig, legend_ax = plt.subplots(figsize=(50, 3))  # Adjust figsize as needed
            
            pivot_gdf.plot(ax=legend_ax, column='val', cmap=cmap, legend=True, 
                           legend_kwds = {'orientation':'horizontal', 'fmt':'{:,.0f}'}, )
            
            #legend_ax.legend(loc= 'lower right')
            legend_ax.clear()
            legend_ax.axis('off')  # Turn off axis

            # Save the legend plot as a PNG image
            legend_png = BytesIO()
            legend_fig.savefig(legend_png, format='png', bbox_inches = 'tight', dpi = 150)
            plt.close(legend_fig)

            # Load the legend PNG image from BytesIO
            legend_png.seek(0)
            img = Image.open(legend_png)

            # Define the cropping parameters
            left = 0
            top = 300  # Adjust this value as needed to crop from the top
            right = img.width
            bottom = img.height

            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))

            # Convert the cropped image back to BytesIO
            cropped_png = io.BytesIO()
            cropped_img.save(cropped_png, format='PNG')

            col1, col2 = st.columns([0.3,0.7])
            #with col1:
                #st.download_button('Download Map', data=map._to_png(), file_name=f'{title}.png', mime='png')
            with col2:
                st.image(cropped_png,  use_column_width=True) #caption='Legend',

           

    with tab2: 
        with st.container(height=600, border=True):
            # make a education level composition dataframe
            plot_df_a = pd.DataFrame(pivot_gdf[analysis_key].sum()).reset_index().rename(columns={'index':'jobs', 0:'total'})
            plot_df_a = plot_df_a.sort_values(by='total', ascending=False)[:10].sort_values(by='total', ascending=True)
            
            # plot demographic composition
            fig_a = px.bar(plot_df_a, 
                    x='total', 
                    y="jobs", 
                    orientation='h',
                    hover_data=["jobs", "total"],
                    height=450,
                    title=f'Top 10 jobs in {city_analysis}, {province_analysis}'
                    )
            fig_a.update_traces(marker_color = '#FBB265')
            st.plotly_chart(fig_a)

            # make a top 10 unit analysis with highest analysis 
            place_list = pd.Series(['NAMA_DESA_KELURAHAN', 'NAMA_KECAMATAN', 'NAMA_KAB_KOTA', 'NAMA_PROVINSI'])
            place_list_indf = pd.Series(list(pivot_gdf.columns))
            place = list(place_list_indf[place_list_indf.isin(place_list)])
            plot_df_b = pivot_gdf[place + [ sub_analysis,'val', 'RESULT']].sort_values(by='val', ascending=False)
            plot_df_c = plot_df_b.sort_values(by= 'val', ascending = True).tail(10)

            # plot top 10 analysis
            if normalizer != None: 
                plot_title = f'Top 10 {unit_analysis}, {city_analysis}, {province_analysis} with highest {sub_analysis} {normalizer}'
                axis_label = f'% {sub_analysis} {normalizer}'
            else: 
                plot_title = f'Top 10 {unit_analysis}, {city_analysis}, {province_analysis} with highest {sub_analysis}'
                axis_label = f'{sub_analysis}'
            
            fig_b = px.bar(plot_df_c, 
                        x = 'val',
                        y = f'NAMA_{unit_analysis}',
                        hover_data= place + ['RESULT'], 
                        title= plot_title,
                        )
            fig_b.update_traces(marker_color = '#FBB265')
            fig_b.update_xaxes(title_text = axis_label)
            st.plotly_chart(fig_b)
    
    with tab3: 
        meta_df = pd.read_csv('metadata/metadata.csv')
        

        st.markdown("""
        
        ### Disclaimer: 
        
        The data provided on this platform is intended for visualization purposes only. 
        While we strive to present accurate information, we cannot guarantee the accuracy or completeness of the data. 
        Users are encouraged to independently verify any information before making decisions based on it. 
        We shall not be held responsible for any inaccuracies, errors, or omissions in the data provided.


        """)
        st.dataframe(meta_df)
        
    with tab4: 
         # generate downloadable dataframe
        download_df = pivot_gdf[place + [ sub_analysis, 'RESULT',  'LUAS_SQKM']]
        download_gdf = pivot_gdf[place + [ sub_analysis, 'RESULT',  'LUAS_SQKM', 'geometry']]
        
        # download buttons
        st.write('preview dataset:')
        st.write(download_df.head(5))


        st.download_button(
                label=f"Download CSV",
                data=download_df.to_csv(),
                file_name=f'{city_analysis}_{province_analysis}_{sub_analysis}.csv',
                mime='text/csv',
            )
        
        st.download_button(
                label=f"Download GeoJSON",
                data=download_gdf.to_json(),
                file_name=f'{city_analysis}_{province_analysis}_{sub_analysis}.geojson',
                )
# ---------------------------------------
st.caption('First time initializing might take a couple minutes, Press "R" to reload/refresh')
