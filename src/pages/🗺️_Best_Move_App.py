from __future__ import annotations
from streamlit_folium import st_folium
import folium
import folium.features
import pandas as pd
import requests
from typing import List, Tuple
import json
from streamlit_searchbox import st_searchbox
from folium.plugins import MarkerCluster
import bestMove.bestMove as bm
from bestMove.poiObject import PoiDefinition
from supabase import create_client, Client
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

dict_selection_mode =  { '🚶 Walking': 'walk', '🚗 Car' : 'drive', '🚆 Public Transport': 'transit'}
necessaryList = ["address", "lon", "lat", "price_num", "sqm_num","insertionpage", "thumbnail_image"]

#-----------------------------------STYLE-------------------------------------

st.markdown("""
            <style> 
            .block-container.css-z5fcl4 
            { padding: 1.5rem 1.2rem, 1.5rem !important; }
            </style>
            """,
             unsafe_allow_html=True)

#-----------------------------------FUNCTIONS----------------------------------
# searching for address with geoAPIfy
@st.cache_data
def search_Addresses(searchterm: str) -> List[Tuple[str, any]]:
    """
    function with list of tuples (label:str, value:any)
    """

    if 'geo_API_Key' in st.session_state:
        if st.session_state.geo_API_Key != "" and len(st.session_state.geo_API_Key) > 10:

            # you can use a nice default here
            if not searchterm:
                return []

            if len(searchterm)<3:
                return []
            
            # API call to get list of suggestions
            response = requests.get(
                f"https://api.geoapify.com/v1/geocode/autocomplete?text={searchterm}&format=json&apiKey={st.session_state.geo_API_Key}",
                timeout=100,
            ).json()

            solutions = response['results']

            # first element will be shown in search, second is returned from component
            return [
                (
                    suggestion["formatted"],
                    [suggestion["lon"],suggestion["lat"], suggestion["formatted"]]
                )
                for suggestion in solutions
            ]
        else:
            st.warning("Seems a wrong Key {st.session_state.geo_API_Key} please provide good one")

    else:
        st.warning("Missing API KEY for geoAPIfy - please provide one")

# getting the isolines
@st.cache_data
def isolineGet(lat, lon, mode, range_, API_KEY, type_research = 'time'):

    print("Running ISOline")
    isoline_search = f"https://api.geoapify.com/v1/isoline?type={type_research}&mode={mode}&range={range_}&lat={lat}&lon={lon}&apiKey={API_KEY}"

    # sending get request isochrones
    r = requests.get(url = isoline_search)

    # extracting data in json format
    GeoJSONAreaOfPOI = r.json() 
    return GeoJSONAreaOfPOI
    
# isoline insertion
def isolineInsertion(GeoJSONAreaOfPOI, m):
    geoJson_Poi_area = folium.GeoJson(json.dumps(GeoJSONAreaOfPOI), 
                                    name="geojson",  
                                    style_function=bm.style_function, 
                                    highlight_function=bm.highlight_function
                                    )
    geoJson_Poi_area.add_to(m)

# Utility for removing marker clusters
def removing_mk(m):
    list_mark_clust = []
    for key_ in m._children.keys():
        if 'marker_cluster' in key_:
            list_mark_clust.append(key_)
    for key_mk in list_mark_clust:
        del m._children[key_mk] 

# Utility for removing marker clusters
def removing_geoJson(m):

    list_geoJson = []
    for key_ in m._children.keys():
        if 'geo_json' in key_:
            list_geoJson.append(key_)
    for key_mk in list_geoJson:
        del m._children[key_mk]

# Define a function to load the data and create the map
@st.cache_resource
def load_map():
    # Create a map centered at a location
    m = folium.Map(location=[48.2087612, 16.3911373], zoom_start=12)
    return m

# delete single isochrone
def del_single_isochrone(index_iso):
    st.session_state.poi_details_list.pop(index_iso)
    print("================\nfrom DELETE Button")
    if 'housing_data' in st.session_state:    
        newmapUpdate("ISOCHRONES_MARKERS")
    else:
        newmapUpdate("ISOCHRONES")

# reset the map elements
def reset_map():
    removing_mk(st.session_state.map)
    st.session_state.poi_details_list = []
    newmapUpdate("ISOCHRONES")

# selecting a poi for house filtering
def poi_selection_switch(poi_index):
    st.session_state.poi_details_list[poi_index].filtered = not(st.session_state.poi_details_list[poi_index].filtered )
    print("================\nfrom SELECTION Switch")
    if len(st.session_state.poi_details_list) == 0:    
        newmapUpdate("ISOCHRONES_MARKERS")
    else:
        if 'housing_data' in st.session_state:
            newmapUpdate("MARKERS")

# prefilling checks
def prefiltering_checks():
    if 'housing_data' in st.session_state:
        newmapUpdate('MARKERS')
    else:
        st.warning("No Data Loaded Yet")
        
# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(table_name = "clean_insertions", sqm_num = "", price_num = ""):
    print(sqm_num, price_num)
    if sqm_num == "" and price_num == "":
        query_statement = 'insertionpage, agency ,   thumbnail_image, title, sqm_num, address, otherinfo, otherinfo_2,price_num, lat, lon'
        return supabase.table(table_name).select(query_statement).execute()
    else:
        query_statement = 'insertionpage, agency ,   thumbnail_image, title, sqm_num, address, otherinfo, otherinfo_2,price_num, lat, lon'
        return supabase.table(table_name).select(query_statement).gte('sqm_num',sqm_num).lte('price_num', price_num).execute()

# Macro Function:
# Will get the command for 3 things:
#     1) House refreshing:
#     2) Search and Print all the new Isochrones (Pois)
#     3) Delete existing POIs
def newmapUpdate(refreshENUM):

    print(f"REFRESHING TYPE: {refreshENUM}")

    refresh_dict = {"ISOCHRONES_MARKERS": [True,True], "ISOCHRONES": [True,False], "MARKERS": [False,True] }
    Isochrone_ = 0
    Markers_ = 1
    test_id_map_is_in_session_state = 'map' in st.session_state

    # ISOCHRONE Refreshing
    if refresh_dict[refreshENUM][Isochrone_] and test_id_map_is_in_session_state:

        removing_geoJson(st.session_state.map)

        for isoline_ in st.session_state.poi_details_list:
            isolineInsertion(isoline_.isolineObject, st.session_state.map)

    # MARKERS Refreshing
    if refresh_dict[refreshENUM][Markers_] and test_id_map_is_in_session_state:

        #st.session_state.map = removing_mk(st.session_state.map)
        removing_mk(st.session_state.map)

        allTheHouses = pd.DataFrame(run_query("clean_insertions", st.session_state.sqm_min ,st.session_state.price_max).data)

        if any(list(map(lambda x: x.filtered, st.session_state.poi_details_list ))):
            for poi_ in st.session_state.poi_details_list:
                if poi_.filtered:
                    allTheHouses = bm.add_poi_colum_selection(allTheHouses,  poi_.title ,  poi_.isolineObject )

        if allTheHouses.shape[0] >= 500:
            allTheHouses = allTheHouses.sample(n=500)
                    
        # Create a marker cluster layer
        marker_cluster = MarkerCluster(name="Markers")

        # Add some fake markers to the map
        for row_ in allTheHouses.iterrows():
            folium.Marker(
                location=[row_[1]['lat'],row_[1]['lon']],
                popup = f"Price: {row_[1]['price_num']} <br/> Sqm: {row_[1]['sqm_num']} <br/> <a href='http://www.willhaben.at{row_[1]['insertionpage']}' target='_blank'> <img src='{row_[1]['thumbnail_image']}' alt='Thumbnail' height='200' width='250'> </a> <br/> Link: <a href='http://www.willhaben.at{row_[1]['insertionpage']}' target='_blank'>Link to Listing</a>",
                icon=folium.Icon(icon="cloud"),
            ).add_to(marker_cluster)
        
        st.session_state.housing_data_filtered = allTheHouses
        marker_cluster.add_to(st.session_state.map)

# Function to create and display the distribution plot
def plot_distribution(column_data, plotTitle="Distribution Plot", plotVariable="Column Values"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(column_data, kde=True, ax=ax)  # You can use different plots like sns.distplot for older versions
    ax.set_xlabel(plotVariable)
    ax.set_ylabel('Frequency')
    ax.set_title(plotTitle)
    st.pyplot(fig)

# loading data into dataframe and then into session
supabase = init_connection()
rows = run_query()
if "housing_data_filtered" not in st.session_state:
    st.session_state["housing_data_filtered"] = pd.DataFrame(rows.data)  

if "housing_data" not in st.session_state:
    st.session_state["housing_data"] = pd.DataFrame(rows.data)

if "sqm_min" not in st.session_state:
    st.session_state["sqm_min"] = 40

if "price_max" not in st.session_state:
    st.session_state["price_max"] = 150000

# initialize session state authenticated
if 'authenticated' not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
 
    # #-----------------------------------STRUCTURE-------------------------------------
    st.subheader("Selectors")
    with st.expander("Point Of Interests"):
        
        address = st_searchbox(
            search_function=search_Addresses,
            placeholder="Address",
            label="Search Point of Interest Address",
            default="lon and lat",
            clear_on_submit=False,
            clearable=True,
            key="searching_Address"
        )

        with st.form("poi_form"):

            title = st.text_input("Title of your Point of Interest")
            mode_of_transport = st.selectbox("Choose mode of transport", options=['🚶 Walking', '🚗 Car', '🚆 Public Transport'])
            minutes_table = st.selectbox("Select time interval in minutes", options=[5, 10, 15, 20, 30, 45, 60])
        
            if st.form_submit_button("Add Poi Isochrone", use_container_width=True):
                # checking if the title is present
                if title == "":
                    st.error(f"Title is missing! 🚨")
                elif address == "lon and lat":
                    st.error(f"POI Coordinates missing! 🚨")
                elif title in list(map(lambda x: x.title, st.session_state.poi_details_list)):
                    st.error(f"There is already a POI with same title! 🚨")                
                else:
                    print("-----The key------")
                    # Store the selected options in the session state 
                    isolineObject = isolineGet(address[1], address[0],dict_selection_mode[mode_of_transport], minutes_table*60, st.session_state.geo_API_Key )
                    poi_instnace = PoiDefinition(title, mode_of_transport , minutes_table, address, isolineObject, False)

                    st.session_state.poi_details_list.append( poi_instnace )
                    newmapUpdate("ISOCHRONES")        

    with st.expander("Filters"):
        # prices and squared meters
        with st.form("price_sqm_form"):
            st.subheader("Price and Space filtering")
            st.session_state.price_max = st.number_input("Max Price", min_value=100000, max_value=3000000, step=1 , value=150000, disabled=False, label_visibility="visible")
            st.session_state.sqm_min = st.number_input("Min m\u00B2 space ", min_value=10, max_value=200 , step=1 , value=40, disabled=False, label_visibility="visible")
            st.form_submit_button("Filter", use_container_width=True, on_click=prefiltering_checks)

    left_main , right_main  = st.columns([8,2])
    
    
    # loading MAp
    if 'map' in st.session_state :
        if st.session_state.map == "":
            st.session_state.map = load_map()

    # Display the POIs
    with left_main:
        st.subheader("Map")
        st_folium(
            st.session_state.map, 
            key="old",
            height=700,
            width=1200,
            returned_objects=[]
            )
        
    # Display the map
    with right_main:
        # display the current to-do list
        if len(st.session_state.poi_details_list) > 0:
            st.write('### Point of Interests:')
            st.markdown(f"<hr />", unsafe_allow_html=True)
            for i, item in enumerate(st.session_state.poi_details_list):
                container_ = st.container()
                with container_:
                    left , right  = st.columns([4,3])
                    # add an item card
                    left.markdown(f"**Poi Title**: {item.title}")
                    left.markdown(f"**Mode of Transportation**: {item.mode_of_transport}")
                    left.markdown(f"**Time Range**: {item.minutes_table} minutes")
                    left.markdown(f"**Address**: {item.address[2]}")

                    # add a button to delete the item
                    right.button(f'Delete 🗑️ #{i+1}', on_click=del_single_isochrone, args=(i,), use_container_width =True)

                    # Filter markers by POI
                    right.checkbox(f'Keep listings in this area: #{i+1}', value=item.filtered, on_change=poi_selection_switch, args=(i,))
                
                st.markdown(f"<hr />", unsafe_allow_html=True)
                
        else:
            st.write('No Point of Interest searched and loaded')

    st.subheader("Listings")
    if 'housing_data_filtered' in st.session_state:
        #col1, col2, col3, col4, col5= st.columns(5)
        col1, col2, col3, col4, col5 = st.columns([1,1,2,1,2])
        housing_df = st.session_state.housing_data_filtered
        CountOfOffers = housing_df.shape[0]
        MedianPrice = round(housing_df['price_num'].median(),0)
        MinPrice, MaxPrice = round(housing_df['price_num'].min(),0), round(housing_df['price_num'].max(),0)
        MedianSqm = round(housing_df['sqm_num'].median(),0)

        col1.metric("Number of Listings", f"{CountOfOffers}")
        col2.metric("Median Price", f"{MedianPrice}€")
        with col3:
            plot_distribution(housing_df['price_num'], "Price Distribution", "Price")
        col4.metric("Median Squared Meters", f"{MedianSqm}m\u00B2")
        with col5:
            plot_distribution(housing_df['sqm_num'], "m\u00b2 Distribution", "Squared Meters")

        # Displaying 
        st.dataframe(
            st.session_state.housing_data_filtered,
            column_config={
                "price_num": st.column_config.ProgressColumn(
                    "Price",
                    help="Price",
                    format="$%f",
                    min_value=MinPrice,
                    max_value=MaxPrice,
                    ),
                "thumbnail_image": st.column_config.ImageColumn(
                    "House Image", help="Streamlit app preview screenshots"
                ),
 
        },
        hide_index=True,
        column_order=["thumbnail_image", "title", "address","sqm_num","price_num","otherinfo","otherinfo_2", "insertionpage"]
        )

 

else:

    st.markdown(
        """
        ## Access Restricted
        
        You do not have permission to access this page. Please log in to view the content.
        
        To log in, enter your username and password in the login section on the left side of the app.
        """
    )
