import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(layout="wide")
st.title('Streaming services')


def read_data():
    content = pd.read_csv('sample/all_data.csv')

    # data cleaning
    content = content[['title', 'type','platform','averageRating', 'numVotes','description', 'year', 'release_year',
       'genre', 'age_certification', 'seasons', 'titleType', 'runtimeMinutes']]
    content.rename(columns={'title':'Title', 'type':'Type'}, inplace=True)

    content.release_year.fillna(content.year, inplace=True)
    content.drop(columns={'year'}, inplace = True)
    content.release_year = content.release_year.astype(int)
    content.numVotes = content.numVotes.astype(int)
    content.seasons = content.seasons.astype(str)

    content.Type.replace('movie', 'MOVIE', inplace=True)
    content.Type.replace('tv', 'TV SHOW', inplace=True)
    content.Type.replace('SHOW', 'TV SHOW', inplace=True)
    content.averageRating = [("%.2f" % x) for x in content.averageRating]   #limiting to 2 decimal places
    #content['release_year'] = [x.replace('.0', '') for x in content['release_year']]

    content.genre = [x.lower() for x in content.genre]
    content.genre = [x.replace("'", "") for x in content.genre]
    content.genre = [x.replace("[", "") for x in content.genre]
    content.genre = [x.replace("]", "") for x in content.genre]
    content.genre = [x.replace(" ", "") for x in content.genre]
    content.genre = [x.replace("documentation", "documentary") for x in content.genre]
    content.genre = [x.replace("scifi", "sci-fi") for x in content.genre]
    content.genre = [x.replace("sciencefiction", "sci-fi") for x in content.genre]
    content.genre = [x.replace("science", "sci-fi") for x in content.genre]
    content.genre = [x.replace("historical", "history") for x in content.genre]
    content.genre = [x.replace("musical", "music") for x in content.genre]
    return content

def sort_popular(content):
    sorted = content.sort_values(by='averageRating', ascending=False)
    sorted.reset_index(inplace=True, drop=True)
    return sorted

def select_type(content, c):
    
    type = c.radio('Select type of content (Movie/TV Show) :', ('All', 'MOVIE', 'TV SHOW'), key='type-radio')
    
    if (type=='All'):
        sorted_type = content.Type
    else:
        sorted_type = sort_popular(content[content.Type==type])
    
    return sorted_type

def select_platform(content, c):
    plat = c.radio('Select Platform :', ('All','Netflix', 'amazon prime', 'hotstar'),  key='plat_radio')
    if (plat=='All'):
        sorted_plat = sort_popular(content)
    else:
        sorted_plat = sort_popular(content[content.platform==plat])
    return sorted_plat

def select_genres(content, c):
    
    genres= content.genre.str.split(",").explode('genre').value_counts().index.tolist()
    genres.insert(0, 'All')
    selected_genre = c.selectbox('Select genre', (genres),  key='genre-radio')
    if (selected_genre=='All'):
        sorted_genre = sort_popular(content)
    else:
        sorted_genre = sort_popular(content[content.genre.str.contains(selected_genre)])
    return sorted_genre

def st_dataframe(df):
    st.dataframe(df)




content = read_data()
sorted = sort_popular(content)

def form_setup():
    form = st.form(key="filters")
    c1, c2, c3 = form.columns((2, 1, 1))

    type = c3.radio('Select type of content (Movie/TV Show) :', ('All', 'MOVIE', 'TV SHOW'), key='type-radio')
    plat = c2.radio('Select Platform :', ('All','Netflix', 'amazon prime', 'hotstar'),  key='plat_radio')
    genres= content.genre.str.split(",").explode('genre').value_counts().index.tolist()
    genres.insert(0, 'All')
    sel_genre = c1.selectbox('Select genre', (genres),  key='genre-radio')
    state = form.form_submit_button("Filter")
    fil1 = content
    if state:
        
        if type!='All':
            fil1= fil1[fil1.Type==type]

        if plat!='All':
            fil1 = fil1[fil1.platform==plat]

        if sel_genre!='All':
            fil1 = fil1[fil1.genre.str.contains(sel_genre)]
        
    st.dataframe(sort_popular(fil1))

form_setup()
#AwesomeTable(sorted)

