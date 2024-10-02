import streamlit as st
import pickle
import pandas as pd
import requests


# CSS to center elements and style buttons
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    return None


# Function to fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return {
        'title': data.get('title'),
        'overview': data.get('overview'),
        'release_date': data.get('release_date'),
        'vote_average': data.get('vote_average'),
        'runtime': data.get('runtime'),
        'genres': ', '.join([genre['name'] for genre in data.get('genres', [])])
    }


# Function to recommend similar movies based on user input
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids


# Load movie data and similarity matrix
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('cosine_sim.pkl', 'rb'))

# Apply custom CSS for better styling
local_css("styles.css")

# Streamlit UI
st.title('🎬 Movie Recommender System🎥')

# Add a header image or banner
st.image("movie-trendy-banner-vector.jpg", use_column_width=True)  # Add your banner image path

# Add a dropdown for selecting a movie
selected_movie_name = st.selectbox(
    'Search for a movie to get recommendations:', movies['title'].values
)

# Button to show recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie_name)
    st.session_state['recommended_movie_names'] = recommended_movie_names
    st.session_state['recommended_movie_posters'] = recommended_movie_posters
    st.session_state['recommended_movie_ids'] = recommended_movie_ids

# Display the movie recommendations
if 'recommended_movie_names' in st.session_state:
    st.subheader(f"Recommended Movies for {selected_movie_name}")
    recommended_movie_names = st.session_state['recommended_movie_names']
    recommended_movie_posters = st.session_state['recommended_movie_posters']
    recommended_movie_ids = st.session_state['recommended_movie_ids']

    # Create columns for displaying movies
    for i in range(len(recommended_movie_names)):
        cols = st.columns(4)
        for i, col in enumerate(cols):
            with col:
                st.image(recommended_movie_posters[i], use_column_width=True)
                st.markdown(f"**{recommended_movie_names[i]}**")
                if st.button(f'Show details for {recommended_movie_names[i]}', key=f'details_{i}'):
                    movie_details = fetch_movie_details(recommended_movie_ids[i])
                    st.write(f"**Title**: {movie_details['title']}")
                    st.write(f"**Overview**: {movie_details['overview']}")
                    st.write(f"**Release Date**: {movie_details['release_date']}")
                    st.write(f"**Rating**: {movie_details['vote_average']}")
                    st.write(f"**Runtime**: {movie_details['runtime']} minutes")
                    st.write(f"**Genres**: {movie_details['genres']}")
