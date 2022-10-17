import csv

from requests import session
import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; color: #e4e8f3; font-size:55px '>STREAMING WARS : INDIA </h1>", unsafe_allow_html=True)
st.markdown("<p><p>", unsafe_allow_html=True)
d1,d2,d3 = st.columns((1,4,1))
d2.image('resources/streaming2.jpg', use_column_width=True, clamp=True)
CURRENT_THEME = "red"
IS_DARK_THEME = True

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

if 'flag' not in st.session_state:
    st.session_state.flag = False

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

content = read_data()
sorted = sort_popular(content)

if 'df' not in st.session_state:
    st.session_state.df = sorted

def form_setup():
    form = st.form(key="filters")
    c1, c2, c3 = form.columns((2, 1, 1))

    type = c3.radio('Select type of content (Movie/TV Show) :', ('All', 'MOVIE', 'TV SHOW'), key='type-radio')
    plat = c2.radio('Select Platform :', ('All','Netflix', 'amazon prime', 'hotstar'),  key='plat_radio')
    genres= content.genre.str.split(",").explode('genre').value_counts().index.tolist()
    genres.insert(0, 'All')
    sel_genre = c1.selectbox('Select genre', (genres),  key='genre-radio')
    c4, c5,c6 = form.columns((2,2,1))
    state = c5.form_submit_button("Filter")
    
    search = st.text_input("Search Titles", "")
    def watchlist():
        titles = form.multiselect("Select Titles for watchlist", st.session_state.df)
        st.session_state.watchlist.append(titles)
        submit = form.form_submit_button("Submit!")
        if submit:
            st.write("Your list is :", st.session_state.watchlist)
            #st.session_state.flag=0
    fil1 = content
    if state:
        
        if type!='All':
            fil1= fil1[fil1.Type==type]

        if plat!='All':
            fil1 = fil1[fil1.platform==plat]

        if sel_genre!='All':
            fil1 = fil1[fil1.genre.str.contains(sel_genre, case=False)]

    if search:
        fil1 = content[content.Title.str.contains(search, case=False)] 


    pop = sort_popular(fil1)
    st.session_state.df = pop
    form.write("Create a watchlist :")
    
    st.dataframe(st.session_state.df)

form_setup()

def watchlist_form():
    form2 = st.form(key="watch")
    
    def sub():  
        #st.session_state.listname = "temp"
        form2.write("Your list is :")
        df2 = content[content.Title.isin(st.session_state.multiselects)].reset_index()
        form2.table(df2)

        
        form2.write("Name your watchlist and save it : ")
        name = form2.text_input("Name of Watchlist", key="listname")

        def saved():
            print(st.session_state.listname)
            df2 = content[content.Title.isin(st.session_state.multiselects)].reset_index()
            st.session_state.multiselects = []

            df2['Name'] = st.session_state.listname
            try:
                csv_file = pd.read_csv('resources/watchlists.csv')
            except pd.errors.EmptyDataError:
                csv_file= df2

            else:
                #df2 = df2.apply(pd.to_numeric, errors='coerce')
                df2.averageRating = pd.to_numeric(df2.averageRating, errors='coerce')
                df2.runtimeMinutes = pd.to_numeric(df2.runtimeMinutes, errors='coerce')
                df2.seasons = pd.to_numeric(df2.seasons, errors='coerce')
                csv_file = csv_file.append(df2)
            #form2.write(csv_file)
            csv_file.to_csv('resources/watchlists.csv', index=False)
        #print(st.session_state.name_watchlist)
        
        save = form2.form_submit_button("Save", on_click=saved)


    col= form2.columns((2,1))
    titles = col[0].multiselect("Select Titles for watchlist", content, key = "multiselects")

    st.session_state.watchlist.append(titles)
    #st.session_state
    submit = col[1].form_submit_button("Submit!", on_click=sub)

watchlist_form()
        

def view_lists():
    check = st.checkbox("View saved watchlists")
    if check:
        try:
            csv_file = pd.read_csv('resources/watchlists.csv')
        except pd.errors.EmptyDataError:
            st.write("No saved lists yet")
        else:
            names = csv_file['Name'].unique()
        for n in names:
            with st.expander(n):
                st.write(csv_file[csv_file.Name==n])
view_lists()
#watchlist()
#AwesomeTable(sorted)


    
