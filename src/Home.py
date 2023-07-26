
from __future__ import annotations
import streamlit as st  
from streamlit_supabase_auth import login_form, logout_button
from supabase import create_client, Client
import supabase

#-----------------------------------CONFIG-------------------------------------
# page configurations
st.set_page_config(
    page_title="BestMove App",
    page_icon="🗺️",
    layout="wide",
)

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()
 
# initialize session state with an empty list for the to-do items
if 'poi_details_list' not in st.session_state:
    st.session_state.poi_details_list = [] 

# initialize session state with an empty list for the to-do items
if 'price_max' not in st.session_state:
    st.session_state.price_max = 90000

# initialize session state with an empty list for the to-do items
if 'sqm_min' not in st.session_state:
    st.session_state.sqm_min = 0

# Load the map
if 'map' not in st.session_state:
    st.session_state.map = ""

# initialize session state with an empty list for the to-do items
if 'Houses_count' not in st.session_state:
    st.session_state.price_max = 90000

# initialize session state with an empty list for the to-do items
if 'sqm_min' not in st.session_state:
    st.session_state.sqm_min = 0

# initialize session state with geoAPIfy key
API_k = st.secrets["GEOAPIFY_KEY"]
st.session_state.geo_API_Key = API_k

# initialize session state with geoAPIfy key
st.session_state["SUPABASE_URL"] = st.secrets["SUPABASE_URL"]
st.session_state["SUPABASE_KEY"] = st.secrets["SUPABASE_KEY"]

# initialize session state authenticated
if 'authenticated' not in st.session_state:
    st.session_state["authenticated"] = False

#-----------------------------------STYLE-------------------------------------
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


#-----------------------------------CONTENT-------------------------------------

def main():
    st.title("Best Move App 🗺️")
    session = login_form()
    #st.write(session)
    if not session:
        st.session_state["authenticated"] = False 
        return
    #st.experimental_set_query_params(page=["success"])
    with st.sidebar:
        st.write(f"Welcome {session['user']['email']}")
        st.session_state["authenticated"] = True
        logout_button()


if __name__ == "__main__":
    main()