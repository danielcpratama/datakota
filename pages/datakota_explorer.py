import streamlit as st
from google.cloud import storage
import bcrypt
import datetime
from google.cloud import storage
import pages.kota as kota


# set page config
st.set_page_config(
    page_title="datakota.explorer",
    layout="centered", 
    page_icon= ":map:", 
    menu_items= {'About':'Made by Daniel Caesar Pratama'}, 
    initial_sidebar_state="expanded"
)


# ------------------------------------------------------------------------------
# SET UP SIDE BARS

# set up side bar
with st.sidebar:
    st.subheader('Account Set Up', anchor='set-up')
    tab1, tab2 = st.tabs(['Sign In', 'Sign Up'])
    with tab1:
        kota.sign_in()
        st.caption('please SIGN UP if you don\'t have an account')
        
    with tab2: 
        kota.sign_up()
        
    
    st.divider()
    st.subheader('Contact us!')
    st.markdown("""
    [twitter](https://twitter.com/danielcaesarp)  
    [instagram](https://instagram.com/datakota.app)  
    [email](hi.datakota@gmail.com)  
    [github](https://github.com/danielcpratama/datakota)

    """)
    
    

# ------------------------------------------------------------------------------
# SET UP TITLE 

st.image('logo/logo.png')
st.title("datakota.explorer")
if st.button('< Home', type='secondary', use_container_width=False):
        st.switch_page("Home.py")
# st.image("logo/hero.png", use_column_width=True)

# ------------------------------------------------------------------------------
# PRICING PLAN
st.subheader("👈 Sign In/Sign Up To Get Your Pass")
col1, col2, col3 = st.columns([1,1,1])
with col1: 
    with st.container(border=True, height=420):
        st.image('logo/free.png')
        st.markdown('##### free pass')
        st.markdown('Explore Indonesian city data for free—exclusively for students, educators, academics, and NGO/non-profit movers and shakers!')
with col2: 
    with st.container(border=True, height=420):
        st.image('logo/daily.png')
        st.markdown('##### daily pass @IDR15k')
        st.markdown('make data-driven decisions today at a price of a coffee to get insights from all over Indonesia—empowering you to seize opportunities and stay ahead')
with col3: 
    with st.container(border=True, height=420):
        st.image('logo/weekly.png')
        st.markdown('##### weekly pass @IDR50k')
        st.markdown('Dive deep into your research and analysis with a full week of uninterrupted access—unlocking the insights you need to fuel innovation')

# ------------------------------------------------------------------------------
st.subheader("Demographic Spatial Dataset, Province to Kelurahan Level")
st.write("source: Dukcapil Kemendagri, 2019")
st.write('Population analysis is free for you to try! __Sign in__ to unlock more analysis, charts, maps, and raw dataset.')

col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("👥 population [FREE TRY!]", use_container_width=True, disabled=False, type = 'primary', 
                 help="population, household, and density"):
        st.switch_page("pages/1_👥_Population_Analysis.py")
    if st.button( "🎓 education analysis", use_container_width=True, disabled=st.session_state["disabled_status"],
                 help="total population by latest attained education level"):
        st.switch_page("pages/2_🎓_Education_Analysis.py")
with col2:
    if st.button("👶 age analysis", use_container_width=True, disabled=st.session_state["disabled_status"], 
                 help=" total population by age distribution, toddler, school age, productive age, and elder"):
        st.switch_page("pages/3_👶_Age_Analysis.py")
    if st.button( "🕉️ religion analysis", use_container_width=True, disabled=st.session_state["disabled_status"],
                 help=" total population by religion, including traditional belief"):
        st.switch_page("pages/4_🕉️_Religion_Analysis.py")
with col3:
    if st.button("👫🏻 sex & marriage analysis", use_container_width=True, disabled=st.session_state["disabled_status"],
                 help=" total population by gender and marriage status"):
        st.switch_page("pages/5_👫🏻_Sex_Marriage_Analysis.py")
    if st.button( "🛠️ jobs analysis", use_container_width=True, disabled=st.session_state["disabled_status"],
                 help=" total population by jobs"):
        st.switch_page("pages/6_🛠️_Jobs_Analysis.py")


# ------------------------------------------------------------------------------
st.divider()
st.subheader("Coming soon")
st.write('We believe in data fusion: merging public government dataset with open sources data. Here are available dataset in our pipeline')

col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.button("Data Potensi Desa 2018, by Kelurahan", use_container_width=True, disabled=True)
    st.button( "Survey Ekonomi Nasional, 2018-2022, by Kota", use_container_width=True, disabled=True)
    st.button( "Street Network, OSM", use_container_width=True, disabled=True)
    st.button( "Land Surface Temperature, Sentinel-2", use_container_width=True, disabled=True)
with col2:
    st.button("Fiscal & Fiscal Indicators, Time Series, by Kota", use_container_width=True, disabled=True)
    st.button( "Economics Indicators, Time Series, by Kota", use_container_width=True, disabled=True)
    st.button( "Building footprint, Google Open Building", use_container_width=True, disabled=True)
    st.button( "Built-Up Index, Sentinel-2", use_container_width=True, disabled=True)
with col3:
    st.button("Infrastructure Indicators, Time Series, by Kota", use_container_width=True, disabled=True)
    st.button( "Tax Revenue, Time Series, by Kota", use_container_width=True, disabled=True)
    st.button( "Places PoI, OSM & Google Maps", use_container_width=True, disabled=True)
    st.button( "NDVI, Sentinel-2", use_container_width=True, disabled=True)

# ------------------------------------------------------------------------------
st.divider()
st.subheader("Did not find what you're looking for?")
st.write("Request dataset by sending us an email at hi.datakota@gmail.com")

# ------------------------------------------------------------------------------
st.divider()
st.subheader("Contribute High-Quality Dataset for a Lifetime Access!")
st.write("Contact us at hi.datakota@gmail.com with 'dataset contribution' as a subject if you'd like to make dataset contribution")


# ------------------------------------------------------------------------------
# Footer
st.divider()
st.subheader('Support Us!')
colA, colB = st.columns([2,1])
with colA:
    st.markdown('''
                - we are accepting donation through QRIS payment!  
                - contribute a high quality dataset that you'd like the public to see! send us an email  
                - follow us on social media & let us know how we are doing!  
                ''')
    st.markdown("""
          
          
                
        [twitter](https://twitter.com/danielcaesarp) | [instagram](https://instagram.com/datakota.app)  | [email](hi.datakota@gmail.com)  | [github](https://github.com/danielcpratama/datakota)

        """)
    st.caption('&copy;datakota | datakota is a solo venture by Daniel Caesar Pratama')

with colB:
    st.image("logo/QRIS_small.jpg", width=200)
