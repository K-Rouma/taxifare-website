import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import folium
from streamlit_folium import st_folium
import requests

# -------------------------------
# Print a Folium map correctly
# -------------------------------
def print_map(longitude, latitude):
    longitude = float(longitude)
    latitude = float(latitude)

    m = folium.Map(location=[latitude, longitude], zoom_start=15)

    folium.Marker(
        [latitude, longitude],
        tooltip="Position"
    ).add_to(m)

    st_folium(m, width=700, height=500)


# Helper to convert inputs
def to_float(val):
    try:
        return float(val)
    except:
        return None


# -------------------------------
# SIDEBARsss
# -------------------------------


st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a, black);
            color: white;
            padding-top: 20px;
            border-radius : 10px 0px 0px 10px;,
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #0f172a, black);
            padding: 10px;
        }

        /* Conteneur principal du contenu */
        .main > div {
            background-color: grey !important;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        [data-testid="stHeader"] {
            background: linear-gradient(90deg, #0f172a);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)



url = 'https://taxifare.lewagon.ai/predict'


# -------------------------------
# PICKUP LOCATION
# -------------------------------
st.subheader("Pickup Geolocation")
with st.container(border=True):

    st.markdown("#### Autodetect")

    location = streamlit_geolocation()
    auto_longitude = location.get("longitude")
    auto_latitude = location.get("latitude")

    if auto_longitude and auto_latitude:
        st.success(f"Autodetected longitude: {auto_longitude}")
        st.success(f"Autodetected latitude: {auto_latitude}")
    else:
        st.info("Click the button above to detect your position.")

    st.markdown("---")
    st.markdown("#### Manual input")
    with st.expander("### Select coordinate manually"):
        manual_lon_input = st.text_input("Enter pickup longitude manually", width=220)
        manual_lat_input = st.text_input("Enter pickup latitude manually", width=220)

        apply_pickup_manual = st.button("Apply manual pickup coordinates")

    # Store applied values in session_state
    if "pickup_manual_lon" not in st.session_state:
        st.session_state.pickup_manual_lon = None
        st.session_state.pickup_manual_lat = None

    if apply_pickup_manual:
        st.session_state.pickup_manual_lon = to_float(manual_lon_input)
        st.session_state.pickup_manual_lat = to_float(manual_lat_input)
        if st.session_state.pickup_manual_lon and st.session_state.pickup_manual_lat:
            st.success("✓ Manual pickup coordinates applied!")
        else:
            st.error("Invalid manual coordinates")

    st.markdown("---")


    # Priority: auto → manual applied
    pickup_lon = auto_longitude or st.session_state.pickup_manual_lon
    pickup_lat = auto_latitude or st.session_state.pickup_manual_lat

    if pickup_lon is None or pickup_lat is None:
        st.checkbox("Verify my pickup position", key=1, disabled=True)
    else:
        if st.checkbox("Verify my pickup position", key=2):
            print_map(pickup_lon, pickup_lat)



# -------------------------------
# DROPOFF LOCATION
# -------------------------------
st.subheader("Dropoff Geolocation")
with st.container(border=True):

    drop_lon_input = st.text_input("Enter dropoff longitude manually", width=220)
    drop_lat_input = st.text_input("Enter dropoff latitude manually", width=220)

    apply_dropoff_manual = st.button("Apply manual dropoff coordinates")

    # Store applied values
    if "dropoff_manual_lon" not in st.session_state:
        st.session_state.dropoff_manual_lon = None
        st.session_state.dropoff_manual_lat = None

    if apply_dropoff_manual:
        st.session_state.dropoff_manual_lon = to_float(drop_lon_input)
        st.session_state.dropoff_manual_lat = to_float(drop_lat_input)
        if st.session_state.dropoff_manual_lon and st.session_state.dropoff_manual_lat:
            st.success("✓ Manual dropoff coordinates applied!")
        else:
            st.error("Invalid manual coordinates")

    # Dropoff logic
    dropoff_lon = st.session_state.dropoff_manual_lon
    dropoff_lat = st.session_state.dropoff_manual_lat

    if dropoff_lon is None or dropoff_lat is None:
        st.checkbox("Verify my destination position", key=3, disabled=True)
    else:
        if st.checkbox("Verify my destination position", key=4):
            print_map(dropoff_lon, dropoff_lat)






with st.sidebar:
    st.subheader("Date & Time")
    with st.container(border=True):

        with st.container(horizontal=True):
            date = st.date_input("Date", width=100)
            time = st.time_input("Time", width=100, step=60)

        st.write(f"Date & Time selected : {date} at {time}")

    st.subheader("Passenger's details")
    with st.container(border=True):
        passenger_count = st.slider("Select passenger number", min_value=1, max_value=10)
# Bouton pour lancer la prédiction
    st.markdown("---")
    st.subheader("💸 Fare Prediction")
    if st.button("Get my prediction fare"):

        # --- Vérifications minimales ---
        if pickup_lon is None or pickup_lat is None:
            st.error("❌ Pickup coordinates missing.")
        elif dropoff_lon is None or dropoff_lat is None:
            st.error("❌ Dropoff coordinates missing.")
        else:
            st.info("⏳ Requesting fare prediction...")

            # Paramètres du GET
            params = {
                "pickup_datetime": f"{date} {time}",
                "pickup_longitude": pickup_lon,
                "pickup_latitude": pickup_lat,
                "dropoff_longitude": dropoff_lon,
                "dropoff_latitude": dropoff_lat,
                "passenger_count": passenger_count
            }

            try:
                response = requests.get(url, params=params)

                if response.status_code == 200:
                    result = response.json()

                    # On suppose que l'API renvoie {"prediction": value}
                    predicted_fare = result.get("fare")

                    if predicted_fare is not None:
                        st.success(f"💰 Estimated Fare: **{round(predicted_fare, 2)} $**")
                    else:
                        st.warning("⚠️ API responded but no 'prediction' field was found.")
                else:
                    st.error(f"❌ API error: {response.status_code}")
                    st.json(response.json())

            except Exception as e:
                st.error(f"❌ Request failed: {e}")
