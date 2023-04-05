import unittest
import pandas as pd
import numpy as np
from .bestMove import *
import json
import os

"""
- test_string_to_digit
test_string_to_digit: This test ensures that the function string_to_digit correctly transforms the string values in the price column of df_houses to numeric values. 
The test modifies the price column of df_houses to contain strings with different formats of numbers and calls the function on this modified DataFrame. 
The test then checks if the price, lat, lon, and sqm columns of the resulting DataFrame have data types that are numeric.

- test_string_to_digit_2
test_string_to_digit_2: This test checks if string_to_digit correctly transforms the string values of a subset of columns in df_houses to numeric values.
It creates an expected output DataFrame by manually computing the transformed values and then calls the function on a subset of df_houses. 
Finally, it checks if the output of the function matches the expected output.

- test_ray_casting_method
test_ray_casting_method: This test checks if ray_casting_method correctly identifies points inside and outside a polygon. 
It extracts a polygon from PoiGeoJSON, and checks if the function returns True for a point inside the polygon and False for a point outside the polygon.

- test_check_house_in_reachable_area
test_check_house_in_reachable_area: This test checks if check_house_in_reachable_area correctly identifies houses within reachable areas. 
It extracts a polygon from PoiGeoJSON and checks if the function returns True for a point inside the polygon and False for a point outside the polygon.

- test_add_poi_colum_selection
test_add_poi_colum_selection: This test checks if add_poi_colum_selection correctly adds a column with Boolean values indicating whether a house is within a reachable area. 
It creates a sample DataFrame with some test data and calls the function on this DataFrame, passing the test_poi string as the name of the new column. 
The test checks if the new column was added to the DataFrame, has the expected values, and retains only the rows with True values.

# The setUp method is used to initialize the data required by the tests. 
Specifically, it loads a JSON file called test_isochrone.json into a variable called PoiGeoJSON and creates a Pandas DataFrame called df_houses.

"""


class TestLibrary(unittest.TestCase):
    
    def setUp(self):
        # Get the path to the directory containing the test file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the JSON file
        json_path = os.path.join(test_dir, 'test_isochrone.json')
        
        # Open the file in read mode
        with open(json_path, 'r') as f:
            # Load the JSON data from the file
            self.PoiGeoJSON = json.load(f)

        self.df_houses = pd.DataFrame({
            'address': ['Wien, Austria', 'Berlin, Germany', 'Paris, France', 'London, UK'],
            'lat': [48.2082, 52.5200, 48.8566, 51.5072],
            'lon': [16.3738, 13.4050, 2.3522, -0.1276],
            'sqm': [50, 80, 100, 120],
            'price': ['€200,000', '€300,000', '€400,000', '€500,000']
        })

    def test_string_to_digit(self):
        self.df_houses['price'] = ['€200,000', '€ 300,000', '€400.000', '€500,000']
        result = string_to_digit(self.df_houses)
        self.assertTrue(np.issubdtype(result['price'].dtypes, np.number))
        self.assertTrue(np.issubdtype(result['lat'].dtypes, np.number))
        self.assertTrue(np.issubdtype(result['lon'].dtypes, np.number))
        self.assertTrue(np.issubdtype(result['sqm'].dtypes, np.number))


    def test_string_to_digit_2(self):
        # test that the function correctly transforms strings to digits
        expected_output = pd.DataFrame({
            'lon': [16.3738, 13.4050, 2.3522, -0.1276],
            'lat': [48.2082, 52.5200, 48.8566, 51.5072],
            'price': [200000,300000,400000,500000],
            'sqm': [50.0, 80.0, 100.0, 120.0]
        })        
        output = string_to_digit(self.df_houses[['lon', 'lat', 'price', 'sqm']])
        pd.testing.assert_frame_equal(output, expected_output)
    
    def test_ray_casting_method(self):
        # test that the function correctly identifies points inside and outside polygons
        poly = self.PoiGeoJSON['features'][0]['geometry']['coordinates'][0][0]
        self.assertTrue(ray_casting_method(16.368565, 48.218754, poly))
        self.assertFalse(ray_casting_method(16.3977, 48.2181, poly))
    

    def test_check_house_in_reachable_area(self):
        # test that the function correctly identifies houses within reachable areas
        self.assertTrue(check_house_in_reachable_area(16.368565,48.218754, self.PoiGeoJSON['features'][0]['geometry']['coordinates']))
        self.assertFalse(check_house_in_reachable_area(16.3977, 48.2181, self.PoiGeoJSON['features'][0]['geometry']['coordinates']))

    def test_add_poi_colum_selection(self):
        # Create a sample dataframe with some test data
        df = pd.DataFrame({
            'address': ['Address 1', 'Address 2', 'Address 3'],
            'lat': [48.218754,  52.5200, 48.8566],
            'lon': [16.368565, 13.4050,  16.368565],
        })
        
        # Call the function to add the POI column
        df_result = add_poi_colum_selection(df, 'test_poi', self.PoiGeoJSON)
        
        # Check that the column was added and has the expected values
        assert 'test_poi' in df_result.columns
        assert df_result['test_poi'].tolist() == [True]
        
        # Check that only the rows with True values are retained
        assert len(df_result) == 1
        assert df_result.iloc[0]['address'] == 'Address 1'