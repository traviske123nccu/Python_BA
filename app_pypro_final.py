# === Tech Summary ===
# This block imports all required libraries:
# - streamlit: for building web interfaces
# - requests: for making HTTP API calls
# - pandas: for tabular data handling using DataFrames
# - numpy: for numerical and array computations
# - matplotlib.pyplot: for static data visualization (e.g., charts)
# - json: for encoding and decoding JSON objects
# - os: for accessing the operating system’s file paths and environment
# =====================

import streamlit as st             # Build web-based front-end interface
import requests                    # Send HTTP requests (e.g., API calls)
import pandas as pd                # Handle tabular data (commonly with DataFrame)
import numpy as np                 # Numerical computing with array and matrix support

import matplotlib.pyplot as plt    # Plotting library for static visualizations
import json                        # Parse and store JSON data
import os                          # OS-level operations like file paths

API_KEY = "nqj9Kh3QVKwI4AFfuwGddoSOQznWReylbYLFynzU" # This is the API key to the USDA API

# === Tech Summary ===
# This function queries the USDA FoodData Central API to search for branded food items.
# It accepts a search keyword, an API key, and the max number of results to return (default: 100).
# If the API call is successful, it extracts and returns a list of FDC (FoodData Central) IDs.
# If the request fails (non-200 response), it logs the error and returns an empty list.
# =====================

def search_usda_foods(query, api_key, max_results=100):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"  # API endpoint for USDA food search

    params = {                              # Define query parameters
        "api_key": api_key,                 # API key for authentication
        "query": query,                     # Search keyword
        "pageSize": max_results,            # Max number of results to return
        "dataType": ["Branded"]             # Restrict to branded food items
    }

    response = requests.get(url, params=params)          # Make HTTP GET request

    if response.status_code != 200:                      # Handle failed request
        st.error(f"Search error {response.status_code}") # Display error in Streamlit UI
        return []                                        # Return empty list on failure

    return [food["fdcId"] for food in                   # Extract list of food IDs from JSON response
            response.json().get("foods", [])]

# === Tech Summary ===
# This function sends a POST request to the USDA API to fetch detailed information
# for a list of food items using their FDC IDs.
# It sets appropriate JSON headers, includes the FDC ID list in the request payload,
# and appends the API key as a parameter.
# On success (HTTP 200), it returns the parsed JSON response; otherwise, it returns an empty list.
# =====================

def fetch_multiple_foods(fdc_ids, api_key):
    
    url = "https://api.nal.usda.gov/fdc/v1/foods"              # API endpoint for batch food lookup

    headers = {"Content-Type": "application/json"}             # Specify JSON content in POST header
    payload = {"fdcIds": fdc_ids}                              # Payload includes list of food IDs
    params = {"api_key": api_key}                              # API key passed as URL parameter

    response = requests.post(                                  # Send POST request with payload & headers
        url, headers=headers, json=payload, params=params
    )

    return response.json() if response.status_code == 200 else []  # Return JSON data or empty list
    
# === Tech Summary ===
# This function extracts a standardized set of nutritional information from a list of food items.
# It converts USDA food records into a pandas DataFrame with key nutrient values.
# - It first maps USDA nutrient names to custom column labels (e.g., "Protein (g)", "Sodium (mg)").
# - For each food item, it extracts relevant nutrient values and fills in missing ones with 0.
# - Returns a structured DataFrame with rows representing food items and columns for nutrients.
# =====================

def extract_nutrients_df(food_list):
    
    key_nutrients = {                                       # Map USDA nutrient names to display labels
        "Energy": "Calories",
        "Protein": "Protein (g)",
        "Total lipid (fat)": "Fat (g)",
        "Carbohydrate, by difference": "Carbs (g)",
        "Sugars, total including NLEA": "Sugar (g)",
        "Total Sugars": "Sugar (g)",
        "Fiber, total dietary": "Fiber (g)",
        "Sodium, Na": "Sodium (mg)"
    }

    radar_labels = [                                        # Nutrient labels to ensure column consistency
        "Calories", "Protein (g)", "Fat (g)", "Carbs (g)",
        "Sugar (g)", "Fiber (g)", "Sodium (mg)"
    ]

    records = []                                            # Initialize list to hold each row of data

    for food in food_list:
        row = {
            "Food": food.get("description", ""),            # Extract food name
            "FDC ID": food.get("fdcId", ""),                # Unique ID
            "Brand": food.get("brandOwner", "")             # Brand information
        }

        for item in food.get("foodNutrients", []):          # Loop through each nutrient in food item
            name = item.get("nutrient", {}).get("name", "") # Get nutrient name
            if name in key_nutrients:
                row[key_nutrients[name]] = float(item.get("amount", 0))  # Save amount if it's in key list

        for label in radar_labels:                          # Ensure all radar labels are present
            row.setdefault(label, 0.0)                       # Default to 0 if not extracted

        records.append(row)                                 # Append complete row to list

    return pd.DataFrame(records)        

# === Tech Summary ===
# This function estimates Total Energy Expenditure (TEE) using different formulas 
# based on gender, age group, and activity level.
# - For infants (age ≤ 2), simplified formulas are used.
# - For children and adults, age-specific equations (from USDA or academic references)
#   are used for each activity level: inactive, low active, and active.
# - The result is a daily TEE value in kcal/day.
# =====================

def calculate_tee(gender, age, height, weight, activity_level):
    if gender == 'male':
        if age <= 2:
            # Infant male TEE formula
            return -716.45 - (1.00 * age) + (17.82 * height) + (15.06 * weight)

        elif age < 19:
            # Boys aged 3–18, equations by activity level
            if activity_level == 'inactive':
                return -447.51 - 3.68 * age + 13.01 * height + 13.15 * weight
            elif activity_level == 'low active':
                return 19.12 + 3.68 * age + 8.62 * height + 20.28 * weight
            elif activity_level == 'active':
                return -388.19 + 3.68 * age + 12.66 * height + 20.46 * weight
            else:  # very active or unknown
                return -671.75 + 3.68 * age + 15.38 * height + 23.25 * weight

        else:
            # Adult male (≥19 years old), equations by activity level
            if activity_level == 'inactive':
                return 753.07 - 10.83 * age + 6.50 * height + 14.10 * weight
            elif activity_level == 'low active':
                return 581.47 - 10.83 * age + 8.30 * height + 14.94 * weight
            elif activity_level == 'active':
                return 1004.82 - 10.83 * age + 6.52 * height + 15.91 * weight
            else:
                return -517.88 - 10.83 * age + 15.61 * height + 19.11 * weight

    else:  # female
        if age <= 2:
            # Infant female TEE formula
            return -69.15 + 80.0 * age + 2.65 * height + 54.15 * weight

        elif age < 19:
            # Girls aged 3–18
            if activity_level == 'inactive':
                return 55.59 - 22.25 * age + 8.43 * height + 17.07 * weight
            elif activity_level == 'low active':
                return -297.54 - 22.25 * age + 12.77 * height + 14.73 * weight
            elif activity_level == 'active':
                return -189.55 - 22.25 * age + 11.74 * height + 18.34 * weight
            else:
                return -709.59 - 22.25 * age + 18.22 * height + 14.25 * weight

        else:
            # Adult female (≥19 years old)
            if activity_level == 'inactive':
                return 584.90 - 7.01 * age + 5.72 * height + 11.71 * weight
            elif activity_level == 'low active':
                return 575.77 - 7.01 * age + 6.60 * height + 12.14 * weight
            elif activity_level == 'active':
                return 710.25 - 7.01 * age + 6.54 * height + 12.34 * weight
            else:
                return 511.83 - 7.01 * age + 9.07 * height + 12.56 * weight
                
# === Tech Summary ===
# This function calculates the target intake (in grams) of macronutrients
# per meal based on total daily energy expenditure (TEE).
# Assumptions:
# - 40% of calories from protein, 30% from fat, 30% from carbs
# - Protein and carbs: 4 kcal/g; fat: 9 kcal/g
# - Daily intake is divided equally into 3 meals
# =====================

def compute_target_macros_per_meal(tee):
    return {
        "Protein (g)": tee * 0.4 / 4 / 3,   # 40% of calories → divide by 4 kcal/g → 3 meals
        "Fat (g)":     tee * 0.3 / 9 / 3,   # 30% of calories → divide by 9 kcal/g → 3 meals
        "Carbs (g)":   tee * 0.3 / 4 / 3    # 30% of calories → divide by 4 kcal/g → 3 meals
    }
    
# === Tech Summary ===
# This function scores food records in a DataFrame based on how closely they match
# the target macro and calorie goals for one meal.
# - Each nutrient has its own scoring function:
#   - Calories/Fat/Carbs: penalized if over target
#   - Protein: capped at 1 when exceeding target
# - Weights for total score depend on the selected goal (muscle_gain or fat_loss)
# - Final output is the same DataFrame with added score columns, sorted by Total Score
# =====================

def score_menu(df, targets, tee, goal):
    # Helper: score = x / t if under target, else penalize
    def bounded_score(x, t): return min(x / t, 1)

    # Penalize over-target macros with a decreasing function (2 - x/t), min 0
    def penalized_score(x, t): return max(0, 2 - x / t) if x > t else x / t

    # Individual nutrient scores
    df["Calories Score"] = df["Calories"].apply(lambda x: penalized_score(x, tee))
    df["Protein Score"]  = df["Protein (g)"].apply(lambda x: bounded_score(x, targets["Protein (g)"]))
    df["Fat Score"]      = df["Fat (g)"].apply(lambda x: penalized_score(x, targets["Fat (g)"]))
    df["Carbs Score"]    = df["Carbs (g)"].apply(lambda x: penalized_score(x, targets["Carbs (g)"]))

    # Different weights for different goals
    weights = {
        "muscle_gain": [0.2, 0.4, 0.2, 0.2],  # Emphasize protein for bulking
        "fat_loss":    [0.3, 0.4, 0.3, 0.2]   # Balance between calorie and protein
    }[goal]

    # Weighted total score = sum of nutrient scores × weights
    df["Total Score"] = (
        df["Calories Score"] * weights[0] +
        df["Protein Score"]  * weights[1] +
        df["Fat Score"]      * weights[2] +
        df["Carbs Score"]    * weights[3]
    )

    return df.sort_values("Total Score", ascending=False)  # Highest score first

# === Tech Summary ===
# This function plots a radar chart for a single food item's nutrient values.
# Each nutrient is normalized against standard daily values (DV) for adults.
# - Uses matplotlib to draw a circular radar chart with 7 nutrients
# - Scales values between 0 and 1 (as % of daily recommended intake)
# - Fills the area to show nutrient density at a glance
# - Outputs the plot directly into Streamlit via st.pyplot()
# =====================

def plot_radar_chart(row):
    labels = [                                       # Nutrients to include in the radar chart
        "Calories", "Protein (g)", "Fat (g)", "Carbs (g)",
        "Sugar (g)", "Fiber (g)", "Sodium (mg)"
    ]

    daily = {                                        # Daily recommended values for each nutrient
        "Calories": 2000, "Protein (g)": 50, "Fat (g)": 78,
        "Carbs (g)": 300, "Sugar (g)": 50, "Fiber (g)": 28, "Sodium (mg)": 2300
    }

    values = [row[l] / daily[l] for l in labels]     # Normalize each nutrient by daily value
    values += [values[0]]                            # Close the radar shape by repeating the first value

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist() + [0]  # Radar chart angles

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))  # Create polar (radar) plot
    ax.plot(angles, values)                          # Draw the outline
    ax.fill(angles, values, alpha=0.25)              # Fill the area with transparency

    ax.set_xticks(angles[:-1])                       # Set axis ticks
    ax.set_xticklabels(labels, fontsize=8)           # Set tick labels (nutrients)
    ax.set_ylim(0, 1)                                # Set radial axis from 0 to 100% of DV
    ax.set_title(row["Food"], y=1.1)                 # Title = food name

    st.pyplot(fig)                                   # Render plot in Streamlit

# === Tech Summary ===
# This function estimates an individual's average speed (in km/h or mph) for a given activity,
# adjusted based on their BMI and age.
# - A base speed is defined for each activity type.
# - If BMI > 25 (overweight), speed is reduced by 10%.
# - If age > 40, speed is further reduced by 5%.
# - Returns the adjusted speed rounded to 2 decimal places.
# =====================

def estimate_speed_bmi_age(activity, bmi, age):
    base_speeds = {                        # Define default speeds by activity type
        "Running": 9.0,
        "Swimming": 3.0,
        "Cycling": 15.0,
        "Walking": 5.0
    }

    speed = base_speeds.get(activity, 5.0) # Use default of 5.0 if activity is unknown

    if bmi > 25:                           # Reduce speed by 10% if overweight
        speed *= 0.9

    if age > 40:                           # Reduce speed by 5% if older
        speed *= 0.95

    return round(speed, 2)                # Round final result to 2 decimal places
    
# === Tech Summary ===
# This function estimates how long and how far a person needs to exercise to burn a given number of calories,
# considering BMI and age adjustments.
# - Takes in a calorie target, user's BMI, and age.
# - For each activity, computes:
#   - Time required (in minutes)
#   - Estimated speed (adjusted for BMI and age)
#   - Total distance covered in km
# - Returns a dictionary mapping each activity to its estimated time, distance, and speed.
# =====================

def calories_to_exercise_with_distance(calories, bmi, age):
    activities = {                            # Activity name and estimated kcal burned per minute
        "Running": 10,
        "Swimming": 14,
        "Cycling": 8,
        "Walking": 4
    }

    result = {}

    for activity, kcal_per_min in activities.items():
        minutes = calories / kcal_per_min     # Time needed to burn target calories
        speed = estimate_speed_bmi_age(activity, bmi, age)  # Adjusted speed (km/h)
        distance = (minutes / 60) * speed     # Convert time to hours × speed = distance

        result[activity] = {
            "time_min": round(minutes),       # Time in minutes
            "distance_km": round(distance, 2),# Distance in km, rounded to 2 decimals
            "speed_kmh": speed                # Raw speed value
        }

    return result
    
# === Tech Summary ===
# This function calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation.
# BMR represents the number of calories required to maintain basic bodily functions at rest.
# Formula:
# - Male:    10 × weight + 6.25 × height − 5 × age + 5
# - Female:  10 × weight + 6.25 × height − 5 × age − 161
# Units:
# - weight: in kilograms (kg)
# - height: in centimeters (cm)
# - age: in years
# =====================

def calculate_bmr(gender, age, height, weight):
    if gender.lower() == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)


# ======================== Streamlit Section ========================

# --- Logo Link ---
logo_url = "https://cdn-icons-png.flaticon.com/512/590/590685.png"  # Logo URL used in Streamlit header

# --- File path for user DB persistence ---
USER_DB_PATH = "user_db.json"  # Local file to persist user data

# --- Load user DB from file if exists ---
if os.path.exists(USER_DB_PATH):
    with open(USER_DB_PATH, "r") as f:
        USER_DB = json.load(f)             # Load user data from JSON file
else:
    USER_DB = {                            # If file doesn't exist, initialize in-memory user DB
        "alice": {
            "password": "1234",            # Simple password (not secure for real apps)
            "gender": "female",
            "age": 28,
            "height": 160,                 # in cm
            "weight": 55,                  # in kg
            "activity_level": "active",    # User-reported activity level
            "goal": "fat_loss"             # Goal: either "fat_loss" or "muscle_gain"
        },
        "bob": {
            "password": "5678",
            "gender": "male",
            "age": 30,
            "height": 175,
            "weight": 70,
            "activity_level": "inactive",
            "goal": "muscle_gain"
        }
    }

# --- Streamlit page setup ---
st.set_page_config(layout="centered")  # Set layout to centered (better visual balance)

# --- Header with logo aligned to title ---
col_logo, col_title = st.columns([2, 6])  # Two columns: logo (1/4 width), title (3/4 width)

with col_logo:
    st.image(logo_url, width=150)  # Display logo image at defined width

with col_title:
    st.markdown("## Nutrition App 2.5.5 Final")  # Main title (Markdown style)
    st.caption("Your personalized guide to smarter food choices!")  # Subtitle or tagline
    st.caption("A Python Project Created by Group 02 with Python and Streamlit")  # Credit line

# --- Track login state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False  # Initialize login state

# --- Show login/register form if not logged in ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 Member Access")
    auth_mode = st.radio("Choose action", ["Login", "Register"])

    # --- Login form ---
    if auth_mode == "Login": # What shows if user choose the Login action
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"): # What happens next if user hits the Login button
            if username in USER_DB and USER_DB[username]["password"] == password:
                st.session_state.logged_in = True # Change the session state from not logged in to logged in
                st.session_state.user_profile = USER_DB[username]  # Load full user data
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    # --- Registration form ---
    elif auth_mode == "Register": # What shows if user choose the Register action
        new_user = st.text_input("Choose a username(at least 3 characters)")
        new_pass = st.text_input("Create a password(at least 4 characters)", type="password")
        confirm_pass = st.text_input("Confirm password(at least 4 characters)", type="password")

        # Profile information fields
        st.markdown("### 📋 Profile Info")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Biological Sex", ["male", "female"])
            age = st.number_input("Age", 1, 99, 25)
            height = st.number_input("Height (cm)", 100, 250, 165)
        with col2:
            weight = st.number_input("Weight (kg)", 30, 150, 60)
            activity_level = st.selectbox("Activity level", ["inactive", "low active", "active", "very active"])
            goal = st.selectbox("Goal", ["muscle_gain", "fat_loss"])

        # Validation and account creation
        if st.button("Register"):
            if new_user in USER_DB: # Username has to be unique
                st.error("❌ Username already taken.")
            elif new_pass != confirm_pass: # Password must match to confirm the user correctly typed in his/her desired password
                st.error("❌ Passwords do not match.")
            elif len(new_user) < 3 or len(new_pass) < 4: 
                st.warning("⚠️ Username must be 3+ characters, password 4+.")
            else:
                # Save new user data by updating the previous user database
                USER_DB[new_user] = {
                    "password": new_pass,
                    "gender": gender,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "activity_level": activity_level,
                    "goal": goal
                }

                try:
                    with open(USER_DB_PATH, "w") as f:
                        json.dump(USER_DB, f, indent=4)
                        print("✅ Saved USER_DB")
                except Exception as e:
                    st.error(f"⚠️ Error saving user: {e}")
                    

                st.session_state.logged_in = True # Change the session state from not logged in to logged in
                st.session_state.user_profile = USER_DB[new_user] # Log in with the new user's profile
                st.session_state.username = new_user
                st.success("✅ Registration successful! Logging you in...")
                st.rerun()

    st.stop()  # Prevent rendering other UI before login

# --- Sidebar logout ---
if st.session_state.get("logged_in") and st.session_state.get("username"):
    st.sidebar.success(f"👋 Logged in as {st.session_state.username}")  # Welcome message
    st.sidebar.button(
        "📜 Logout", 
        on_click=lambda: st.session_state.clear()  # Clear session on logout
    )

# --- Input Section (for logged-in users only) ---
if "user_profile" in st.session_state:
    profile = st.session_state.user_profile

    # Extract personal info from session state
    gender = profile["gender"]
    age = profile["age"]
    height = profile["height"]
    weight = profile["weight"]
    activity_level = profile["activity_level"]
    goal = profile["goal"]

    # --- Sidebar: Display user profile and metrics ---
    st.sidebar.markdown("### 👤 Your Profile")
    st.sidebar.write(f"**👫 Gender:** {gender}")
    st.sidebar.write(f"**🎂 Age:** {age} years")
    st.sidebar.write(f"**📏 Height:** {height} cm")
    st.sidebar.write(f"**⚖️ Weight:** {weight} kg")
    st.sidebar.write(f"**🏃‍♂️ Activity Level:** {activity_level}")
    st.sidebar.write(f"**🎯 Goal:** {goal.replace('_', ' ').title()}")

    # This is later added just for the demo, it shows the usernames registered.
    st.sidebar.markdown("### 🔐 Show Registered Users (Dev Only)")
    st.sidebar.write("Registered usernames:")
    st.sidebar.write(list(USER_DB.keys()))

    # Calculate energy needs and activity equivalents
    tee = calculate_tee(gender, age, height, weight, activity_level)      # Total Energy Expenditure
    bmi = weight / ((height / 100) ** 2)                                   # Body Mass Index
    burn_data = calories_to_exercise_with_distance(tee / 3, bmi, age)     # Burn 1 meal worth of kcal

    bmr = calculate_bmr(gender, age, height, weight)                      # Basal Metabolic Rate

    # --- Sidebar: Display BMR and TEE results ---
    st.sidebar.markdown("### 🔥 Daily Energy Estimates")
    st.sidebar.write(f"**💤 BMR:** **{round(bmr)}** kcal/day")
    st.sidebar.write(f"**🔥 TEE:** **{round(tee)}** kcal/day")

    # --- Sidebar: Display burn estimates for 1/3 TEE ---
    st.sidebar.markdown("### 🏃 Burn 1 Meal (~⅓ TEE):")
    for activity, stats in burn_data.items():
        st.sidebar.write(f"**{activity}**: {stats['time_min']} min ≈ {stats['distance_km']} km")

    # --- Main panel: search bar ---
    st.markdown("### 🔍 Search Food by Keyword")
    keyword = st.text_input("Search food keyword", value="beef")  # default = "beef"
    submitted = st.button("🔎 Find Foods")

    # --- Search logic begins ---
    if submitted:
        # Step 1: Search fdcIds by keyword
        fdc_ids = search_usda_foods(keyword, API_KEY)

        # Step 2: Fetch nutrient data by fdcIds
        foods = fetch_multiple_foods(fdc_ids, API_KEY)

        # Step 3: Convert to structured dataframe
        df = extract_nutrients_df(foods)

        # Step 4: (Optional) Estimate how much effort needed to burn average food calories
        if "Calories" in df.columns:
            avg_calories = df["Calories"].mean()
            bmi = weight / ((height / 100) ** 2)
            exercise_data = calories_to_exercise_with_distance(avg_calories, bmi, age)

        # Step 5: Score food based on user profile
        tee = calculate_tee(gender, age, height, weight, activity_level)
        targets = compute_target_macros_per_meal(tee)
        scored = score_menu(df, targets, tee, goal)

        # --- Output ranked results ---
        st.subheader(
            f"🏆 Top Foods for '{keyword}' (Goal: {goal.replace('_', ' ').title()})"
        )
        st.dataframe(scored.head(20))  # Show table with ranking

        # --- Show radar charts for each food item ---
        cols = st.columns(2)  # Two-column layout for radar charts
        for i, (_, row) in enumerate(scored.head(20).iterrows()):
            with cols[i % 2]:
                st.markdown(f"#### 🥗 {row['Food']} – {row['Brand']}")
                plot_radar_chart(row)
