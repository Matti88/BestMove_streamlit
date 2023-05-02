<img src="./assets/MyBestMove_logo.png"  width="30%" height="30%">

## The App

myBestMove is a web application that helps users to find the best place to live based on their preferred transportation method and travel time. It allows users to search for locations, select a transportation method, and generate isochrones, which are lines that connect all the points reachable within a certain time frame. 

Users can also upload a CSV file with a list of houses of interest, and the app will filter out all the locations that do not fall within the generated isochrones. Additionally, users can filter the list of houses by max price and minimum squared meters. 

## Installation

To use myBestMove, you will need to have a [geoAPIfy API key](https://www.geoapify.com/) and a CSV file with a list of houses of interest. Once you have these, you can clone this repository, install the required dependencies, and start the server.

```bash
> git clone https://github.com/your-username/myBestMove.git
> cd myBestMove
> pip install -r requirements.txt
> streamlit run streamlit_app.py
```

## Example

Here is an example of an isochrone generated using myBestMove:

![Example Isochrone](/assets/Example_Isochrones_with_Origin_Point_of_Interest.png "Example Isochrone")

## Commands for making it work on MacOS + M1

```bash
brew install pyenv
pyenv install 3.9
eval "$(command pyenv init -)"
eval "$(command pyenv init --path)"
pyenv global 3.9 
python3 --version
```

### modification on streamlit library
When running on python 3.11 as for April 2023 you will see the following error:

```bash
streamlit run streamlit_app.py
> /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/streamlit/elements/arrow.py
```
You can make it work with a simple modification on the streamlit library to target the right outdeted object:

- go to the file `/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/streamlit/elements/arrow.py`
- to change with the import from `collections` to  `collections.abc`
- run streamlit on Mac


## Command for Unit Test
```bash
python3 -m unittest ./bestMove/test_bestMove.py
```