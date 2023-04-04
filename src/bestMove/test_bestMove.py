import unittest
import pandas as pd
import numpy as np
from .bestMove import *

# Define a dummy PoiGeoJSON for testing
PoiGeoJSON = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
      },
      "properties": {
        "name": "Test Polygon"
      }
    }
  ]
}

class TestLibrary(unittest.TestCase):
    
    def setUp(self):
        self.df_houses = pd.DataFrame({
            'address': ['Wien, Austria', 'Berlin, Germany', 'Paris, France', 'London, UK'],
            'lat': [48.2082, 52.5200, 48.8566, 51.5072],
            'lon': [16.3738, 13.4050, 2.3522, -0.1276],
            'sqm': [50, 80, 100, 120],
            'price': ['€200,000', '€300,000', '€400,000', '€500,000']
        })
        self.ListOfShapes = [[(48.2082, 16.3738), (48.209, 16.378), (48.21, 16.375)], [(52.5200, 13.4050), (52.522, 13.409), (52.523, 13.406)]]
        self.PoiGeoJSON = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[(48.2082, 16.3738), (48.209, 16.378), (48.21, 16.375)], [(52.5200, 13.4050), (52.522, 13.409), (52.523, 13.406)]]
                }
            }]
        }

    def test_string_to_digit(self):
        self.df_houses['price'] = ['€200,000', '€300,000', '€400,000', '€500,000']
        result = string_to_digit(self.df_houses)
        self.assertTrue(np.issubdtype(result['price'].dtype, np.number))
        self.assertTrue(np.issubdtype(result['lat'].dtype, np.number))
        self.assertTrue(np.issubdtype(result['lon'].dtype, np.number))
        self.assertTrue(np.issubdtype(result['sqm'].dtype, np.number))

    def test_cleanUp_outlier(self):
        # test that the function removes outliers
        expected_output = pd.DataFrame({'address': ['Address D'], 'lat': [48.191912], 'lon': [16.378763], 'price': [650000], 'sqm': [78], 'year': [1980]})
        output = cleanUp_outlier(self.df_houses)
        pd.testing.assert_frame_equal(output, expected_output)

    def test_cleanUp_outlier_2(self):
        self.df_houses.loc[1, 'lat'] = np.nan
        self.df_houses.loc[2, 'lon'] = np.nan
        self.df_houses.loc[3, 'address'] = 'Wien,'
        result = cleanUp_outlier(self.df_houses)
        self.assertEqual(result.shape, (2, 5))
        self.assertTrue(result['lat'].notnull().all())
        self.assertTrue(result['lon'].notnull().all())
        self.assertTrue(result['address'].str.len().gt(len('Wien,')).all())

    def test_string_to_digit_2(self):
        # test that the function correctly transforms strings to digits
        expected_output = pd.DataFrame({'lon': [16.394506], 'lat': [48.209266], 'price': [400000], 'sqm': [85]})
        output = string_to_digit(self.df_houses[['lon', 'lat', 'price', 'sqm']])
        pd.testing.assert_frame_equal(output, expected_output)
    
    def test_ray_casting_method(self):
        # test that the function correctly identifies points inside and outside polygons
        poly = [[16.3663,48.2153],[16.3704,48.2072],[16.3844,48.2063],[16.3913,48.2128],[16.3799,48.2183],[16.3663,48.2153]]
        self.assertTrue(ray_casting_method(16.3735, 48.2105, poly))
        self.assertFalse(ray_casting_method(16.3977, 48.2181, poly))
    
    def test_check_house_in_reachable_area(self):
        # test that the function correctly identifies houses within reachable areas
        ListOfShapes = [[[16.3663,48.2153],[16.3704,48.2072],[16.3844,48.2063],[16.3913,48.2128],[16.3799,48.2183],[16.3663,48.2153]]]
        self.assertTrue(check_house_in_reachable_area(16.3735, 48.2105, ListOfShapes))
        self.assertFalse(check_house_in_reachable_area(16.3977, 48.2181, ListOfShapes))
    
    def test_filtering_by_PoI(self):
        # test that the function correctly filters a dataframe based on PoI columns
        array_pois = ['supermarket', 'restaurant']
        expected_output = pd.DataFrame({'lon': [16.394506], 'lat': [48.209266], 'price': [400000], 'sqm': [85], 'hash(supermarket)': [True], 'hash(restaurant)': [True]})
        output = filtering_by_PoI(self.df_houses, array_pois)
        pd.testing.assert_frame_equal(output, expected_output)

    def test_add_poi_colum_selection(self):
        # Create a sample dataframe with some test data
        df = pd.DataFrame({
            'address': ['Address 1', 'Address 2', 'Address 3'],
            'lat': [0.5, 1.5, 2.5],
            'lon': [0.5, 1.5, 2.5]
        })
        
        # Call the function to add the POI column
        df_result = add_poi_colum_selection(df, 'test_poi', PoiGeoJSON)
        
        # Check that the column was added and has the expected values
        assert 'test_poi' in df_result.columns
        assert df_result['test_poi'].tolist() == [True, False, False]
        
        # Check that only the rows with True values are retained
        assert len(df_result) == 1
        assert df_result.iloc[0]['address'] == 'Address 1'