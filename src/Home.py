
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

st.markdown("""
            <style> 
            .block-container.css-z5fcl4 
            { padding: 1.5rem !important; }
            </style>
            """,
             unsafe_allow_html=True)


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

with st.expander("Privacy Policy"):
    st.markdown(
        """
        Privacy Policy

        Introduction

        This privacy policy (the "Policy") describes how "bestmove" (the "Company") collects, uses, and discloses your personal information when you use our website [bestmove.streamlit.app] (the "Website") or our app (the "App").

        Information We Collect

        We collect the following information from you when you use the Website or App:

        Personal information you provide us: We collect the personal information you provide us when you create an account, such as your name, email address, and password.
        Information about your usage of the Website or App: We collect information about how you use the Website or App, such as the pages you visit, the features you use, and the time and date of your visits.
        Information from third-party services: We may collect information from third-party services, such as Google Analytics, to help us understand how you use the Website or App.
        How We Use Your Information

        We use your information for the following purposes:

        To provide you with the Website or App: We use your information to provide you with the Website or App and to deliver the features and services you request.
        To improve the Website or App: We use your information to improve the Website or App and to develop new features and services.
        To communicate with you: We use your information to communicate with you about the Website or App, such as sending you emails about new features or updates.
        To market to you: We may use your information to market to you about our products and services.
        Disclosure of Your Information

        We may disclose your information to the following third parties:

        Our service providers: We may share your information with our service providers who help us operate the Website or App, such as hosting providers and email service providers.
        Advertising partners: We may share your information with our advertising partners who help us deliver targeted advertising to you.
        Legal authorities: We may disclose your information to legal authorities if we are required to do so by law.
        Your Rights

        You have the following rights with respect to your information:

        Access: You have the right to access your information that we collect.
        Correction: You have the right to correct any inaccurate or incomplete information that we collect about you.
        Deletion: You have the right to request that we delete your information.
        Objection: You have the right to object to our processing of your information.
        Withdrawal of consent: You have the right to withdraw your consent to our processing of your information at any time.
        How to Contact Us

        If you have any questions about this Policy, please contact us at matteo.montanari25@gmail.com .

        Changes to this Policy

        We may update this Policy from time to time. The most recent version of the Policy will always be posted on the Website.

        Effective Date

        This Policy is effective as of 27th July 2023.
        """
        )    