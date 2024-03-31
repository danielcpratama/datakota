
# import libraries
import streamlit as st
from PIL import Image
from google.cloud import storage
import bcrypt
import datetime
from google.cloud import storage


# set page config
st.set_page_config(
    page_title="Home",
    layout="centered", 
    page_icon= ":house:", 
    menu_items= {'About':'Made by Daniel Caesar Pratama'}, 
    initial_sidebar_state= "collapsed"
)
# ------------------------------------------------------------------------------
# SET UP SIDEBAR
with st.sidebar:
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
st.title("Datakota")
st.subheader("Spatial Insights of Indonesian Cities")
st.write("Our curated spatial datasets and user-friendly analytic tools help businesses identify growth opportunities, optimize operations, and stay ahead of the competition.")
col_A, col_B = st.columns([1,2])
with col_A:
    if st.button('try datakota.explorer today', type='primary', use_container_width=True):
        st.switch_page("pages/datakota_explorer.py")
with col_B:
    st.caption('or scroll down to see our [other products](#our-products)')    


# ------------------------------------------------------------------------------
# Hero
st.image("logo/hero.png", use_column_width=True)
# ------------------------------------------------------------------------------
# Introducing datakota.explorer
with st.container(border=False):
    st.subheader('Introducing datakota.explorer')
    st.markdown("""
                Explore demographic insights visualized spatially:  
                age, jobs, religion, education level, gender, marital status, and more.
                """)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        with st.container(border=True, height=280):
            st.markdown('##### Comprehensive ')
            st.image('logo/comprehensive.png')
            st.markdown('We provide a wide selection of variables gathered from various sources')
        
    with col2:
        with st.container(border=True, height=280):
            st.markdown('##### Granular ')
            st.image('logo/granular.png')        
            st.markdown('We cover every nook & cranny of Indonesia up to Kelurahan level')
        
    with col3: 
        with st.container(border=True, height=280):
            st.markdown('##### Intuitive ')
            st.image('logo/intuitive.png')
            st.markdown('Get insights quickly with our interactive maps & charts')

    st.subheader('what they say about datakota.explorer')    

    st.markdown("👨🏽‍🦲      _datakota is cleaner & easier to use than government GIS geoportal!_ - twitter user")
    st.markdown("👧🏻      _datakota helped narrow down my research on informal economy!_ - Ms. KF")
    st.markdown("🙆🏽‍♂️      _I work in baby-care industry, and datakota helped me discover market potential in my province_ - Mr. FRB")
    st.markdown("""
    
    

    """)
if st.button('try datakota.explorer today', type='primary', use_container_width=False, key='trynow'):
        st.switch_page("pages/datakota_explorer.py")
st.markdown("""
    
    

    """)
# ------------------------------------------------------------------------------
# Product page
st.subheader('More Analytics Are Coming Soon', divider='grey', anchor='our-products')

col_l, col_r = st.columns([1,1])
# datakota.explorer

# datakota.retail
with col_l:
    with st.container(border=True, height=470):
        st.image("logo/kopi.png", use_column_width=True)
        st.subheader('🏪 datakota.retail', divider='grey')
        st.markdown("""
__Find the best location for your next restaurant, cafe, minimart and more using our location analysis tool__  
""")
        with st.expander("learn more:"):
            st.markdown("""
- Identify customer demographic profile within a catchment area  
- Analyse nearby competitors  
- Understand your location accessibility
""") 
        col_x, col_y = st.columns([1,1])
        with col_y:
            st.link_button('join waitlist',url='https://forms.gle/US1WirXFj5UNBx5GA', type='primary', use_container_width=True)

# datakota.housing
with col_r:
    with st.container(border=True, height=470):
        st.image("logo/house.png", use_column_width=True)
        st.subheader('🏠 datakota.housing', divider='grey')    
        st.markdown("""
__buying a house is likely your biggest purchase-of-a-lifetime, don't choose the wrong location__  
 
""")
        with st.expander("learn more:"):
            st.markdown("""                    
- compare comparable housing price in several locations 
- estimate living cost in the area  
- check disaster history
- check access to public transportation, school, healthcare, and parks
- check access to public service, i.e., water, electricity, internet                      
""")
        col_x, col_y = st.columns([1,1])
        with col_y:
            st.link_button('join waitlist', url= 'https://forms.gle/US1WirXFj5UNBx5GA', type='primary', use_container_width=True)

# datakota.enterprise

with st.container(border=True, height=540):
    st.image("logo/enterprise.png", use_column_width=True)
    st.subheader('💼 datakota.enterprise', divider='grey')
    st.markdown("""
__Customized spatial platform for your unique enterprise needs, from location intelligence, predictive analysis, and map visualization__  

""")
    with st.expander("explore sectoral potential:"):
        st.markdown("""
- real estate market assessment  
- healthcare analytics and facility planning  
- supply chain optimization through network analysis 
- geomarketing                        
""")
    col_x, col_y = st.columns([1,1])
    with col_y:
        st.link_button("let's talk", url = 'https://forms.gle/US1WirXFj5UNBx5GA', type='primary', use_container_width=True)


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

