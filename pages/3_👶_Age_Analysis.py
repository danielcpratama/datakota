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
from streamlit_gsheets import GSheetsConnection
import datetime

# set page config
st.set_page_config(
    page_title="Age Analysis",
    layout="wide", 
    page_icon= "👶"
)
# ------------------------------------------------------------------------------
st.image('logo/logo.png', width=80)
st.title('Age Analysis')
# ------------------------------------------------------------------------------
# SET UP SIDE BAR
with st.sidebar:
    st.subheader('Contact us!')
    st.markdown("""
    [twitter](https://twitter.com/danielcaesarp)  
    [instagram](https://instagram.com/datakota.app)  
    [email](hi.datakota@gmail.com)  
    [github](https://github.com/danielcpratama/datakota)

    """)
    st.subheader('We are accepting donation!')
    st.write('you can donate through QRIS below')
    st.image("logo/QRIS_small.jpg", width=250)
    

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
data = 'age'
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
        # st.write(f'data taken from data/{data}_df.csv')
        # st.write(f'geom taken from {geom_URL}')
        
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
            map = pivot_gdf.explore(column = pivot_gdf['val'],
                                cmap = 'viridis',
                                tiles = 'CartoDB positron',
                                #tiles = map_tile,
                                attr = "mapbox",
                                color = 'white',
                                tooltip = [f'NAMA_{unit_analysis}', 'RESULT'],
                                scheme = 'EqualInterval', 
                                k = 10, 
                                highlight = True, 
                                popup = True,
                                style_kwds = {'stroke':0.5,
                                                'color' : 'black',
                                                'weight' : 0.5,
                                                'fillOpacity' : 0.8
                                                }, 
                                )
            
            
            st_folium(map, 
                #center = (106.8,-6.8),
                returned_objects= [],
                width= 1000, 
                height = 600, 
                )

    with tab2: 
        with st.container(height=600, border=True):
            # make a education level composition dataframe
            plot_df_a = pd.DataFrame(pivot_gdf[analysis_key].sum()).reset_index().rename(columns={'index':'age_level', 0:'total'})[:-4]
            
            # plot demographic composition
            fig_a = px.bar(plot_df_a, 
                    x='total', 
                    y="age_level", 
                    orientation='h',
                    hover_data=["age_level", "total"],
                    height=550,
                    title=f'Demographic composition of {city_analysis}, {province_analysis} based on age composition'
                    )
            fig_a.update_traces(marker_color = '#6A3576')
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
            fig_b.update_traces(marker_color = '#6A3576')
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
        # establish connection with GSHEETS
        conn_gsheets = st.connection("gsheets", type=GSheetsConnection)
        existing_data = conn_gsheets.read(worksheet='download', usecols = list(range(11)),ttl=5)
        
        # generate downloadable dataframe
        download_df = pivot_gdf[place + [ sub_analysis, 'RESULT',  'LUAS_SQKM']]
        download_gdf = pivot_gdf[place + [ sub_analysis, 'RESULT',  'LUAS_SQKM', 'geometry']]
        @st.cache_data
        def convert_df(_dataframe):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return _dataframe.to_csv().encode('utf-8')

        csv = convert_df(download_df)

        # download forms
        st.subheader(f"Download Forms")
        with st.form(key='download_form'):
            colA, colB = st.columns([0.4,0.6])
            with colA:
                # QRIS
                st.write(f'scan QRIS and pay IDR {len(download_df)*200:,}')
                st.image('logo/QRIS_small.jpg', width = 300)
            with colB:
                # data preview
                st.write('Preview of randomly sampled data:')
                st.dataframe(download_df.sample(5, random_state=911))
                st.write(f'you will download {len(download_df)} rows of data')

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            email = st.text_input(label="email address*")
            phone = st.text_input(label="phone number")
            ref_no = st.text_input(label="last four digit of QRIS payment reference number*", max_chars=4)

            st.caption("** mandatory field")
            st.caption("you will receive a Download Key after we confirm your payment")

            submit_button = st.form_submit_button('Submit my payment!')

        # confirming payment
        pass_num = download_df[sub_analysis].max().astype(int)
        paid = True
        # generate new dataframe to upload to google sheets
        download_form_data = pd.DataFrame([{"timestamp" : timestamp,
                                            "email" : email,
                                            "phone" : phone, 
                                            "ref_no" : ref_no,
                                            "extent_analysis" : extent_analysis,
                                            "unit_analysis" : unit_analysis,
                                            "province_analysis" : province_analysis,
                                            "city_analysis" : city_analysis,
                                            "sub_analysis" : sub_analysis,
                                            "normalizer" : normalizer,
                                            "price" : len(download_df)*200
                                            }])

        if submit_button:
            if not email or not ref_no:
                st.warning("please fill out all mandatory field")
                st.stop()
            else:
                
                # update google sheets
                updated_df = pd.concat([existing_data, download_form_data])
                conn_gsheets.update(worksheet='download', data=updated_df)
                with st.spinner('Confirming your payment...'):
                    time.sleep(10)
                    st.success("your payment is confirmed")
                    st.write(f'download key is {st.secrets.DOWNLOAD_PASSWORD}_{pass_num}')
                
                # generating download password
        
        
        # fill out download key
        data_container = st.empty()
        data_pwd = data_container.text_input(
        f"insert download key here", type='password')
        if data_pwd == f"{st.secrets.DOWNLOAD_PASSWORD}_{pass_num}":
            st.success('you can download using buttons below')    
            paid = False
        else:
            st.warning("Wrong password!")
        
        # download buttons
        st.download_button(
                label=f"Download CSV",
                data=csv,
                file_name=f'{city_analysis}_{province_analysis}_{sub_analysis}.csv',
                disabled= paid,
                mime='text/csv',
            )
        
        st.download_button(
                label=f"Download GeoJSON",
                data=download_gdf.to_json(),
                file_name=f'{city_analysis}_{province_analysis}_{sub_analysis}.geojson',
                disabled= paid,
                )
# ---------------------------------------
st.caption('First time initializing might take a couple minutes, Press "R" to reload/refresh')