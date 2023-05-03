
from __future__ import annotations
import streamlit as st
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


dict_selection_mode =  { '🚶 Walking': 'walk', '🚗 Car' : 'drive', '🚆 Public Transport': 'transit'}



# Docs:
# 1) session states: poi_details_list
# 2) session states: map


 
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

# initialize session state with an empty geoAPIfy key

 

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
                timeout=5,
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



def prefiltering_checks():
    if 'housing_data' in st.session_state:
        newmapUpdate('MARKERS')
    else:
        st.warning("No Data Loaded Yet")
        


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

        allTheHouses = st.session_state.housing_data
        allTheHouses = allTheHouses[allTheHouses['price']<=st.session_state.price_max]

        print("\n----after price filtering-----")
        print(allTheHouses.shape)
        
        allTheHouses = allTheHouses[allTheHouses['sqm']>=st.session_state.sqm_min]
        print("\n----after sqm filtering-----")
        print(allTheHouses.shape)

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
                popup = f"Price: {row_[1]['price']} <br/> Sqm: {row_[1]['sqm']} Link: <a href='https://www.willhaben.at{row_[1]['link']}' target='_blank'>{row_[1]['link']}</a>",
                icon=folium.Icon(icon="cloud"),
            ).add_to(marker_cluster)
        
        # print("----after all filtering-----")
        # print(allTheHouses.head())

        st.session_state.housing_data_filtered = allTheHouses
        marker_cluster.add_to(st.session_state.map)


 
#-----------------------------------STRUCTURE-------------------------------------


# sidebar controls
with st.sidebar:    

    # prices and squared meters
    with st.form("price_sqm_form"):
        st.subheader("Price and Space filtering")
        st.session_state.price_max = st.number_input("Max Rental Price", min_value=400, max_value=3000, step=1 , value=800, disabled=False, label_visibility="visible")
        st.session_state.sqm_min = st.number_input("Min m\u00B2 space ", min_value=10, max_value=200 , step=1 , value=40, disabled=False, label_visibility="visible")
        st.form_submit_button("Filter", use_container_width=True, on_click=prefiltering_checks)
        
    st.markdown(f"<hr />", unsafe_allow_html=True) 

    # poin of interests section
    st.subheader("Point Of Interests")
    

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
    
        if st.form_submit_button("Submit Poi Map", use_container_width=True):
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

    #separate the areas
    st.markdown(f"<hr />", unsafe_allow_html=True)
    # Listing Controls
    st.subheader("Listing Controls") 
    st.button('Reset Map',  on_click=reset_map, use_container_width =True)
    st.markdown(f"<hr />", unsafe_allow_html=True)    

tab1, tab2, tab3, = st.tabs(["Map And Point of Interests", "Data", "API Key"])

with tab1:

    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">"""
                ,unsafe_allow_html=True)

    st.markdown("# BestMove")
    
    left_main , right_main  = st.columns([5,2])

    # loading MAp
    if 'map' in st.session_state :
        if st.session_state.map == "":
            st.session_state.map = load_map()

    # Display the POIs
    with left_main:
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
                print(item)
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

    if 'housing_data_filtered' in st.session_state:
        col1, col2, col3 = st.columns(3)
        housing_df = st.session_state.housing_data_filtered
        CountOfOffers = housing_df.shape[0]
        MedianPrice = housing_df['price'].median()
        MedianSqm = housing_df['sqm'].median()

        col1.metric("Number of Listings", f"{CountOfOffers}")
        col2.metric("Median Price", f"{MedianPrice}€")
        col3.metric("Median Squared Meters", f"{MedianSqm}m\u00B2")

        # edited_df = st.experimental_data_editor(st.session_state.housing_data, height=800)

        edited_df = st.experimental_data_editor(st.session_state.housing_data_filtered, height=800)



with tab2:
    st.subheader("Data")

    uploaded_file = st.file_uploader("Upload your hosing data")
    necessaryList = ["address", "lon", "lat", "price", "sqm","link"]

    if uploaded_file is not None:
        # Can be used wherever a "file-like" object is accepted:
        housesPoints = pd.read_csv(uploaded_file, sep=",")
        housesPoints.columns = housesPoints.columns.str.lower()
        boolean_check_list = list(map(lambda x : x in housesPoints.columns, necessaryList))


        if all(boolean_check_list):

            ## TODO - REMAKE the loading work and decide 
            ##       - XLSX or CSV, and which type of CSV
            # Replace commas with dots in the specified columns

            housesPoints = pd.DataFrame(housesPoints).dropna(subset=['lon','lat','price','sqm'])
            
            housesPoints = bm.string_to_digit(housesPoints)
            
            # print(housesPoints[['lon','lat','price','sqm']])

            st.session_state.housing_data = housesPoints
            st.success("Successful Data Load")
            st.experimental_show(housesPoints)
        else:
            missing_headers = [] 
            for i, value in  enumerate(boolean_check_list):
                if not(value):
                    missing_headers.append(necessaryList[i])
            st.warning("Missing the headers: " + " - ".join(missing_headers))
 


with tab3:
   st.header("API Key")
   API_k =  st.text_input("Insert here your geoAPIfy API KEY")
   if API_k:
       st.session_state.geo_API_Key = API_k


