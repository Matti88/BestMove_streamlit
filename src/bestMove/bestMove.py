import pandas as pd
import numpy as np
import scipy.stats as stats 
import random

# cleanupd outlier
def cleanUp_outlier(df_houses):
  
    df_houses_not_good = df_houses[df_houses.isna().any(axis=1)] # collecting housing options that have missing data
    df_houses_not_good = pd.concat( [ df_houses_not_good, df_houses[df_houses['address'].str.len() <= len("Wien,") ] ])
    df_houses_not_good =  pd.concat( [ df_houses_not_good, df_houses[(np.abs(stats.zscore(df_houses['lat'])) < 1.8)] ]) 
    df_houses_not_good =  pd.concat( [ df_houses_not_good, df_houses[(np.abs(stats.zscore(df_houses['lon'])) < 1.8)] ]) 
    return df_houses_not_good

# string to digit transform
def string_to_digit(df, cols_to_transform = ['lon','lat','sqm']):
    #  transform for these columns ['lon','lat','price','sqm']        
    # clean up the price column
    df['price'] = df['price'].str.replace(r'\D', '', regex=True).astype(int)

    for col in cols_to_transform:
        mask = pd.to_numeric(df [col], errors='coerce').isna()
        df  = df .loc[~mask]
        df [col] = df [col].astype(float) # or int
    return df

# Ray casting
def ray_casting_method(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


# Checking 1 house on the given polygon
def check_house_in_reachable_area(longitude, latitude, ListOfShapes ):

    for basicPolygons in ListOfShapes:
        for basicPolygon_ in basicPolygons:
            if ray_casting_method( longitude, latitude , basicPolygon_):
                return True
    return False

# given a dataframe and array filter for those values that are True given the list of columns in array_pois
def filtering_by_PoI(dataframe, array_pois):
    for poi_ in array_pois:
        dataframe = dataframe.loc[dataframe[str(hash(str(poi_)))] == True]
    return dataframe
 
# a function to generate the style of the isochrones
def style_function(feature):
    global base_color
    r = lambda: random.randint(0,255)
    while True:
        random_color = '#%02X%02X%02X' % (r(),r(),r())
        if "#ffaf00" == random_color:
            pass
        else:
            base_color = random_color
            break
    return {
        'border': '2px solid black',
        "fillColor": base_color, "color": "blue", "weight": 1.5, "dashArray": "5, 5"
    }
# a function to generate the style of the isochrones when "mouse over"
def highlight_function(feature):
    return {"fillColor": "#ffaf00", "color": "green", "weight": 3, "dashArray": "5, 5"}


def add_poi_colum_selection(df_houses, poi_name ,PoiGeoJSON):
    # Add database columns with boolean information on house in/out of the isoline
    
    df_houses[poi_name] = df_houses.apply(lambda row: check_house_in_reachable_area( row['lon'], row['lat'],PoiGeoJSON['features'][0]['geometry']['coordinates']) , axis=1)
    df_houses = df_houses[ df_houses[poi_name] == True ]
    return df_houses