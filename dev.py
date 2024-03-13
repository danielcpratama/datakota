
# import libraries
import streamlit as st
from PIL import Image


# set page config
st.set_page_config(
    page_title="Home",
    layout="centered", 
    page_icon= ":house:", 
    menu_items= {'About':'Made by Daniel Caesar Pratama'}
)
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
# SET UP TITLE 
st.image('logo/logo.png')
st.title("Datakota")
st.subheader("Geospatial Insights of Indonesian Cities")
st.write("Datakota is your one-stop solution for integrated and granular geospatial data, backed by powerful no-code analytics tools, and intuitive spatial data visualization.")

# ------------------------------------------------------------------------------
# HERO

st.image("logo/hero.png", use_column_width=True)
st.subheader("start unlocking geospatial insights for free")
st.write('click one of the analysis options below')

col1, col2, col3 = st.columns([1,1,1])
with col1:
    with st.container(border=True):
        st.page_link("pages/1_👥_Population_Analysis.py", label= "population analysis", icon= "👥")
    with st.container( border=True):
        st.page_link("pages/2_🎓_Education_Analysis.py", label= "education analysis", icon= "🎓")
with col2:
    with st.container(border=True):
        st.page_link("pages/3_👶_Age_Analysis.py", label= "age analysis", icon= "👶")
    with st.container(border=True):
        st.page_link("pages/4_🕉️_Religion_Analysis.py", label= "religion analysis", icon= "🕉️")
with col3:
    with st.container(border=True):
        st.page_link("pages/5_👫🏻_Sex_Marriage_Analysis.py", label= "sex & marriage status", icon= "👫🏻")
    with st.container(border=True):
        st.page_link("pages/6_🛠️_Jobs_Analysis.py", label= "jobs analysis", icon= "🛠️")

# ------------------------------------------------------------------------------
# USE CASE
st.divider()
st.subheader('Potential Use Cases')

colA, colB = st.columns([1,1])
with colA: 
#st.markdown('###### Public Sector')
    with st.expander('Urban Planning'):
        st.markdown(
            """Utilize demographic datasets for informed urban planning decisions. 
            Analyze population size, density, age composition, and employment data 
            to optimize infrastructure projects and resource allocation."""
        )
    with st.expander('Public Health'):
        st.markdown(
            """Leverage demographic data to address health disparities. 
            Utilize age, gender, and education data to develop targeted interventions and improve public health outcomes."""
        )


    #st.markdown('###### Private Sector')
    with st.expander('Retail Site Selection'):
        st.markdown(
            """Optimize retail location decisions using demographic insights. 
            Analyze population characteristics, income levels, and employment data 
            to identify prime retail locations and attract target customers."""
        )
with colB: 
    with st.expander('Real Estate Market Analysis'):
        st.markdown(
            """Enhance real estate market insights with demographic data. 
            Incorporate age, education, and income demographics 
            to identify market trends and make informed investment decisions."""
        )

    # with colC: 
    # st.markdown('###### Academics')
    with st.expander('Social Science Research'):
        st.markdown(
            """Drive social research with demographic datasets. 
            Utilize age, gender, education, and income data 
            to explore migration patterns, household structures, and social disparities."""
        )
    with st.expander('Geographic Studies'):
        st.markdown(
            """Enhance geographic analyses with demographic insights. 
            Incorporate population density, age distribution, and employment data 
            to understand spatial population dynamics and urbanization trends."""
        )

# FAQ
st.divider()
st.subheader('FAQ')

with st.expander("Why choose datakota?"):
    st.write('We have prepared the analysis for you, so you can get to data-driven decision faster. Our platform offers a vast repository of geospatial data, covering every nook and cranny of Indonesia, up to kelurahan level.')

with st.expander("Who is datakota for?"):
    st.markdown(
        """
    Datakota is built for data-driven decision makers like you

    - Consultants & Researchers
    - City Governments
    - Business & Property Developers
"""
    )

st.subheader('Disclaimer')
st.write('-- First time initializing might take a couple minutes')
st.write('-- We are a small startup! Consider purchasing dataset to support our business')
st.write('-- If you have querys please send email to hi.datakota@gmail.com')


