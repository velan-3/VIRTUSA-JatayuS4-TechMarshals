# import streamlit as st
# from streamlit_geolocation import streamlit_geolocation
# import pandas as pd
import requests
# import folium
# from streamlit_folium import folium_static

def get_nearby_venues(latitude, longitude, radius, keyword, place_type):
    """
    Get nearby venues from the RapidAPI endpoint.
    """
    url = "https://google-map-places.p.rapidapi.com/maps/api/place/nearbysearch/json"

    querystring = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": keyword,
        "type": place_type
    }
    headers = {
    'x-rapidapi-key': "fb87524ac1msh25340f913b14344p10f764jsn7c399ee9b066",
    'x-rapidapi-host': "google-map-places.p.rapidapi.com"
    }
    # response =conn.request("GET", "/maps/api/geocode/json?address=1600%20Amphitheatre%2BParkway%2C%20Mountain%20View%2C%20CA&language=en&region=en&result_type=administrative_area_level_1&location_type=APPROXIMATE", headers=headers)
    response = requests.get(url, headers=headers, params=querystring)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        venues = []
        for result in data.get("results", [])[:10]:  # Limiting to 5 results
            venue = {
                "name": result["name"],
                "latitude": result["geometry"]["location"]["lat"],
                "longitude": result["geometry"]["location"]["lng"],
                "rating": result.get("rating", None),
                "address": result.get("vicinity", "")
            }
            venues.append(venue)
        # print(venues)
        return venues
    else:
        # st.error("Failed to fetch nearby venues.")
        return []
        
def locate():
    st.title("Find Nearby Veterinary Clinics")
    st.write("Recommended to use Edge browser")
    # Get user's location
    # Get user's location
    location = streamlit_geolocation()
    if location:
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        if latitude is not None and longitude is not None:
            st.write(f"Your current location: Latitude {latitude}, Longitude {longitude}")

            # Fetch nearby places using RapidAPI
            radius = 5000  # meters
            keyword = "veterinary"
            place_type = "veterinary_clinic"

            nearby_places = get_nearby_venues(latitude, longitude, radius, keyword, place_type)

            # Create a DataFrame with nearby places
            places_df = pd.DataFrame(nearby_places)
            print(places_df)

            # Add dropdown to select clinic
            selected_clinic = st.selectbox("Select a clinic:", places_df["name"])

            # Get the location of the selected clinic
            selected_clinic_location = places_df[places_df["name"] == selected_clinic]
            selected_clinic_latitude = selected_clinic_location.iloc[0]["latitude"]
            selected_clinic_longitude = selected_clinic_location.iloc[0]["longitude"]

            # Display selected clinic details
            st.write("Selected Clinic Details:")
            selected_clinic_details = {
                "Name": selected_clinic,
                "Rating": selected_clinic_location.iloc[0]["rating"],
                "Address": selected_clinic_location.iloc[0]["address"]
            }
            st.dataframe(pd.DataFrame(selected_clinic_details, index=[1]))

            # Create a map with user's location, nearby places, and selected clinic
            start_location = [latitude, longitude]
            end_location = [selected_clinic_latitude, selected_clinic_longitude]

            # Create a map centered on the start location
            m = folium.Map(location=start_location, zoom_start=15)

            path = folium.PolyLine([start_location, end_location], color='red', weight=5, opacity=0.5)
            path.add_to(m)

            # Create a Marker to represent the car
            car_marker = folium.Marker(location=start_location)
            car_marker.add_to(m)
            cm = folium.Marker(location=end_location)
            cm.add_to(m)

            
            st.components.v1.html(m._repr_html_(), height=500)

        else:
            st.write("Unable to retrieve latitude and longitude.")
    else:
        st.write("Unable to retrieve location.")
