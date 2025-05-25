# Functions

## Disclaimer
1. This `.ipynb` file is not meant for the viewer to download directly and run the cells!
   
2. This is a seperate file to describe the lines of code building the Application. The purpose is to give the viewer or potential collaborator in the future a user manual of our code, and this very file is the first part of it.

3. We only import necessary packages and define functions that we are later going to use in the second seperate `.ipynb` file.

## Importing Necessary Packages

This block imports all the external libraries required for the application’s core functionality.

1. `streamlit` is used to build the **interactive web interface**. It allows for real-time updates, layout customization, and dynamic user interaction through input fields, buttons, and widgets.

2. `requests` is used to make **HTTP requests to external APIs**. In this project, it sends queries to the USDA FoodData Central API to retrieve nutritional information about branded food items.

3. `pandas` provides tools for **loading, organizing, and manipulating tabular data using DataFrames**. This is especially useful for storing nutrient values and computing scores across multiple food records.

4. `numpy` supports efficient **numerical computation**, such as calculating BMI or applying formulas to estimate TEE (Total Energy Expenditure).

5. `matplotlib.pyplot` is imported as `plt` and is used to generate **static visualizations**. The application uses it to draw radar charts comparing food nutrient values against reference targets.

6. `json` handles the encoding and decoding of data in JSON format. It is used for both **reading/writing the local user database (`user_db.json`) and parsing API responses**.

7. `os` is used for operating system-level tasks, such as checking if a file exists, building file paths, or saving data to disk.

8. `difflib` provides tools for computing string similarity, which can be useful for fuzzy matching—e.g., when a user enters a food keyword that doesn't exactly match database entries.

At the end of the block, `API_KEY` is defined as a string containing the USDA API key. This key is required to authenticate each request sent to the FoodData Central API and must be included in all API queries.


```python
import streamlit as st             # Build web-based front-end interface
import requests                    # Send HTTP requests (e.g., API calls)
import pandas as pd                # Handle tabular data (commonly with DataFrame)
import numpy as np                 # Numerical computing with array and matrix support
import matplotlib.pyplot as plt    # Plotting library for static visualizations
import json                        # Parse and store JSON data
import os                          # OS-level operations like file paths
import difflib                     # Compute string similarity (e.g., fuzzy matching)

API_KEY = "nqj9Kh3QVKwI4AFfuwGddoSOQznWReylbYLFynzU" # This is the API key to the USDA API
```

## Function 1. `search_usda_foods(query, api_key, max_results=100)`

### Code Explanation

This function `search_usda_foods(query, api_key, max_results=100)` sends a query to the USDA FoodData Central API and returns a list of matching food item IDs (`fdcId`s) based on a search keyword. It is a core utility for initiating branded food lookups based on user input.

1. The `url` variable defines the API endpoint for food search. This is a fixed URL from the USDA API that handles keyword-based food queries.

2. A dictionary named `params` is created to define the query parameters:
   - `api_key` is required for authentication and must be passed with each request.
   - `query` is the actual search keyword, which can be user-defined (e.g., "beef").
   - `pageSize` limits the number of returned results to `max_results`, defaulting to 100.
   - `dataType` is set to `"Branded"` to filter results to only branded food items (excluding generic or foundation foods).

3. A `GET` request is made using `requests.get()` with the URL and query parameters. The result is stored in the `response` object.

4. The function checks the HTTP response status code. If it is not `200` (indicating failure), an error message is shown in the Streamlit app using `st.error()`, and the function returns an empty list.

5. If the request is successful, the response is parsed as JSON, and a list comprehension extracts the `"fdcId"` value from each food item in the `"foods"` list. This list of IDs is returned to be used in downstream API calls for detailed nutrient information.

In summary, this function builds and sends a properly formatted query to the USDA food database, handles failure cases gracefully, and extracts only the minimal required output — the IDs of branded foods matching the user’s search.


```python
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
```

### Note

The `max_result` is set to 100 to improve the searching speed, because we are going to do many manipulations of the data afterwards. Trimming down the results is necessary for better user experience.

### Demo

The result below is the food IDs which can later be used to fetch nutritional facts. As you can see, this is the top 6 results that comes up when you search the keyword, butter, in the database.


```python
search_usda_foods("butter", API_KEY, max_results=6)
```




    [1920273, 2542726, 2103635, 1932883, 2094280, 2070614]



### Further Explanation of the Lines of Code that could be Confusing

The last two lines of code can be very confusing to introductory learners of Python. 
```
food["fdcId"] for food in response.json().get("foods", []) # Extract list of food IDs from JSON response
```
In brief, the line of code above is the equivalent to the one below.
```
fdc_ids = []
for food in response.json().get("foods", []):
    fdc_ids.append(food["fdcId"])
```

## Function 2. `fetch_multiple_foods(fdc_ids, api_key)`

### Code Explanation

The `fetch_multiple_foods(fdc_ids, api_key)` function sends a batch request to the USDA FoodData Central API to retrieve detailed information about multiple food items, based on their `fdcId`s.

1. The `url` variable stores the endpoint for batch food lookup. This endpoint supports POST requests for fetching information on multiple food IDs at once.

2. A `headers` dictionary is defined to specify the content type as JSON. This tells the server that the request body is formatted as JSON data.

3. The `payload` dictionary contains the key `"fdcIds"` with a list of food item IDs as its value. This is the body of the POST request and indicates which specific items the app wants to retrieve.

4. The `params` dictionary includes the API key under the `"api_key"` field. This is required to authenticate the request and is passed in the URL.

5. A `POST` request is sent using `requests.post()`, which includes the URL, headers, JSON-formatted payload, and the authentication parameters.

6. The function then checks whether the response was successful (`status_code == 200`). If so, it returns the parsed JSON content. If not, it returns an empty list.

This function is essential for efficiently retrieving data about several food items in a single API call, rather than querying each one individually.


```python
def fetch_multiple_foods(fdc_ids, api_key):
    
    url = "https://api.nal.usda.gov/fdc/v1/foods"              # API endpoint for batch food lookup

    headers = {"Content-Type": "application/json"}             # Specify JSON content in POST header
    payload = {"fdcIds": fdc_ids}                              # Payload includes list of food IDs
    params = {"api_key": api_key}                              # API key passed as URL parameter

    response = requests.post(                                  # Send POST request with payload & headers
        url, headers=headers, json=payload, params=params
    )

    return response.json() if response.status_code == 200 else []  # Return JSON data or empty list
```

### How this function work with other functions

The difference between function 1 and 2 is that function 1 returns a list of food IDs while function 2 returns multiple foods complete details based on a list of food IDs.

The demo for this code is omitted as it returns in a long json data, including food IDs, nutrient IDs, and so many more extra information about the food that we aren't going to used further down the line. The data is so long, I don't even want to put it in this file. However, I still copied and pasted it in a word document, here is the link to the PDF. 

[External Link: https://drive.google.com/file/d/1_d3IaOdPC57q5NA8358fQuqYYzQbiYIz/view?usp=sharing](https://drive.google.com/file/d/1_d3IaOdPC57q5NA8358fQuqYYzQbiYIz/view?usp=sharing)


We'll need function 3 to extract the necessary data (nutrients, brand name, etc.) and to make it into a Pandas DataFrame.

## Function 3. `extract_nutrients_df(food_list)`

### Code Explanation

The `extract_nutrients_df(food_list)` function processes a list of food item dictionaries (typically from the USDA API) and extracts selected nutrient values into a structured `pandas` DataFrame.

1. The dictionary `key_nutrients` maps the USDA nutrient names to cleaner display labels used as column headers. This helps standardize nutrient names despite the complexity of the original API naming.

2. The list `radar_labels` contains the target nutrient columns that should appear in every row. These labels match the values of `key_nutrients` and ensure consistency in the output DataFrame.

3. An empty list `records` is initialized to hold the nutrient data for each food item.

4. The outer `for` loop iterates through each food item in `food_list`. For each food, a new dictionary `row` is initialized containing basic information: the food's description, FDC ID, and brand owner (if available).

5. The inner `for` loop iterates over the list of nutrients in the `"foodNutrients"` field of each food item. For each nutrient, it tries to retrieve the nutrient's name. If the name is found in `key_nutrients`, its corresponding amount is added to the `row` dictionary using the mapped display label.

6. After processing the available nutrients, the loop over `radar_labels` ensures that all expected nutrient fields are present in the `row`. If a nutrient was not extracted, `setdefault()` fills in a value of `0.0`.

7. The fully populated `row` is appended to the `records` list, which accumulates the structured data for each food.

8. Finally, the list of dictionaries is converted into a `pandas` DataFrame using `pd.DataFrame(records)`. This structured table is returned and is ready for further scoring or visualization.

This function plays a key role in transforming raw USDA API responses into clean, uniform tabular data for analysis and charting.


```python
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
```

## Function 4. `calculate_tee(gender, age, height, weight, activity_level)`

### Code Explanation

The `calculate_tee(gender, age, height, weight, activity_level)` function estimates Total Energy Expenditure (TEE) in kilocalories per day, based on a person's physical attributes and activity level. It applies different equations depending on age group, gender, and activity.

1. The function first checks the `gender`. If `gender == 'male'`, it applies formulas specifically for males; otherwise, it uses female-specific formulas.

2. For males:
   - If `age <= 2`, the function uses an infant-specific TEE formula for boys that incorporates age, height, and weight in a linear equation.
   - If `age < 19`, the function treats the individual as a boy aged 3 to 18. The equation used depends on the `activity_level`, which can be `'inactive'`, `'low active'`, or `'active'`. If the activity level does not match any of these, a fallback formula is applied (often interpreted as "very active" or unspecified).
   - If `age >= 19`, the individual is treated as an adult male. Again, different formulas are applied based on the declared `activity_level`. The constants and coefficients in each case are empirically derived and differ by activity level.

3. For females:
   - If `age <= 2`, a separate infant TEE formula for girls is used, with a different set of coefficients from the male version.
   - If `age < 19`, the function applies formulas for girls aged 3–18. Like the male counterpart, it distinguishes among `inactive`, `low active`, and `active` activity levels, with a fallback formula for other inputs.
   - If `age >= 19`, adult women are handled with yet another set of formulas, each tailored to a different activity level.

4. Each return statement calculates the TEE as a weighted linear combination of age, height, and weight, using different coefficients. These coefficients originate from nutritional science literature and are used to approximate metabolic requirements under various activity conditions.

This function ensures a flexible and detailed estimation of daily caloric needs by accommodating a broad range of demographics and lifestyles. Its output feeds directly into downstream processes, such as macronutrient target calculations and personalized food scoring.



```python
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
```

### Reference

Our source for the TEE calculation method can be found in this site: [https://nap.nationalacademies.org/read/26818/chapter/7#83](https://nap.nationalacademies.org/read/26818/chapter/7#83)

Reference:
National Academies of Sciences, Engineering, and Medicine. (2023). Applications of the Dietary Reference Intakes for Energy. *In Dietary reference intakes for energy* (Chapter 5, pp. 84–85). The National Academies Press. [https://doi.org/10.17226/26818](https://doi.org/10.17226/26818)

## Function 5. `compute_target_macros_per_meal(tee)`

The `compute_target_macros_per_meal(tee)` function calculates the target intake (in grams) of protein, fat, and carbohydrates per meal, based on a person's Total Energy Expenditure (TEE). It uses fixed macronutrient ratios and standard energy conversion factors.

1. The function assumes a macronutrient distribution of:
   - 40% of total calories from protein,
   - 30% from fat,
   - 30% from carbohydrates.

2. For protein:
   - Calories from protein = `TEE * 0.4`
   - Since each gram of protein provides 4 kcal, divide by 4 to convert to grams.
   - Assuming 3 meals per day, divide again by 3 to get per-meal target.
   - Formula: `tee * 0.4 / 4 / 3`

3. For fat:
   - Calories from fat = `TEE * 0.3`
   - Fat has 9 kcal per gram, so divide by 9 to get grams.
   - Divide by 3 to get the per-meal target.
   - Formula: `tee * 0.3 / 9 / 3`

4. For carbohydrates:
   - Calories from carbs = `TEE * 0.3`
   - Carbs also provide 4 kcal per gram, so divide by 4.
   - Divide by 3 for per-meal distribution.
   - Formula: `tee * 0.3 / 4 / 3`

The function returns a dictionary with keys `"Protein (g)"`, `"Fat (g)"`, and `"Carbs (g)"`, each containing the computed gram-based per-meal recommendation. This output can then be used to score food items against personalized nutritional targets.


```python
def compute_target_macros_per_meal(tee):
    return {
        "Protein (g)": tee * 0.4 / 4 / 3,   # 40% of calories → divide by 4 kcal/g → 3 meals
        "Fat (g)":     tee * 0.3 / 9 / 3,   # 30% of calories → divide by 9 kcal/g → 3 meals
        "Carbs (g)":   tee * 0.3 / 4 / 3    # 30% of calories → divide by 4 kcal/g → 3 meals
    }
```

### Reference
The 433-rule is set by our teammate, Jian-Hao Lin. He got dietary advices from multiple fitness coaches and discovered that their advices for daily nutrients intake can be funneled down to this rule.

## Function 6. `score_menu(df, targets, tee, goal)`

The `score_menu(df, targets, tee, goal)` function scores each food item in a DataFrame against personalized nutritional targets. It uses different scoring logic and goal-specific weights to compute a final ranking for food selection.

1. Two helper functions are defined:
   - `bounded_score(x, t)` computes a linear score where the maximum score is `1` if the actual value `x` is at or above the target `t`. Otherwise, it returns a fraction `x/t`, giving partial credit for under-target values.
   - `penalized_score(x, t)` is designed to penalize overconsumption. It returns a decreasing score from `2 - x/t` when `x > t`, with a lower bound of 0. When under or on target, it behaves like `x/t`.

2. The function calculates individual nutrient scores for each row in the DataFrame:
   - `"Calories Score"` uses `penalized_score`, since excess calories are typically undesirable.
   - `"Protein Score"` uses `bounded_score`, rewarding high protein intake up to the target.
   - `"Fat Score"` and `"Carbs Score"` both use `penalized_score`, discouraging excessive intake relative to the target.

3. A `weights` dictionary is defined to assign different importance to each nutrient based on the user’s `goal`:
   - `"muscle_gain"` gives highest weight to protein (0.4), while balancing calories, fat, and carbs equally at 0.2.
   - `"fat_loss"` emphasizes both calorie control and protein (0.3 and 0.4 respectively), with moderate attention to fat and carbs.

4. A new column `"Total Score"` is calculated as the weighted sum of the four nutrient scores:
   - Each nutrient score is multiplied by its corresponding weight, and the results are summed to yield the final score.

5. The DataFrame is sorted by `"Total Score"` in descending order using `df.sort_values()`, so that the top-ranked foods (those closest to the dietary goal) appear first.

This function operationalizes the trade-offs between nutrient intake and dietary objectives, converting raw nutrition data into an actionable ranking system tailored to the user’s TEE and macro needs.


```python
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
```

### Reference
The scoring system is founded by our team-mates, Jian-Hao Lin, Ming-Chian Tsiang, and Bo-Yu Chuang. They just came up with this scoring system that gives a macro score to the food based on the consumer's fitness goal and the food's nutrients. 

## Function 7. `plot_radar_chart(row)`

The `plot_radar_chart(row)` function generates a radar chart (also known as a spider chart) to visually compare a food item's nutrient content with standard daily recommended values. This visualization helps assess how well a food meets nutritional goals across multiple dimensions.

1. A list called `labels` defines the nutrients to be visualized on the radar chart. These include `"Calories"`, `"Protein (g)"`, `"Fat (g)"`, `"Carbs (g)"`, `"Sugar (g)"`, `"Fiber (g)"`, and `"Sodium (mg)"`.

2. The dictionary `daily` specifies standard daily recommended values for each of these nutrients. These serve as the normalization baselines:
   - e.g., 2000 kcal for calories, 50g for protein and sugar, 70g for fat, etc.

3. The `values` list is constructed by dividing each nutrient value from `row` by its corresponding daily value. This normalizes each nutrient so that a value of `1.0` means the food meets 100% of the recommended daily amount. The first value is appended again to `values` to close the radar chart loop and form a complete shape.

4. The `angles` variable creates evenly spaced angle coordinates for the radar plot using `np.linspace`. It spans from `0` to `2π`, evenly dividing the circle by the number of nutrient categories. The starting point is repeated at the end to complete the shape.

5. A radar chart is initialized with `plt.subplots()` using the `polar=True` argument, which specifies the use of a polar coordinate system.

6. The data is plotted as a filled polygon:
   - `ax.plot(angles, values)` draws the outline.
   - `ax.fill(angles, values, alpha=0.25)` adds a translucent fill to visually emphasize the area.

7. Plot styling is handled as follows:
   - `ax.set_xticks()` and `ax.set_xticklabels()` set the axis ticks and nutrient labels around the circle.
   - `ax.set_ylim(0, 1)` scales all radial axes from 0 to 1 (i.e., from 0% to 100% of daily value).
   - `ax.set_title()` sets the food name as the chart title.

8. Finally, `st.pyplot(fig)` renders the chart in the Streamlit interface.

This function transforms raw nutrition data into an intuitive and comparable visual, allowing users to instantly see how a food item measures up against standard nutrient benchmarks.



```python
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
```

### Reference
U.S. Food and Drug Administration. (2022, July 25). *Daily value on the nutrition and supplement facts labels.* FDA. [https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels](https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels)

## Function 8. `estimate_speed_bmi_age(activity, bmi, age)`

The `estimate_speed_bmi_age(activity, bmi, age)` function estimates a person's average exercise speed in km/h based on their selected activity type, Body Mass Index (BMI), and age. The function returns a value rounded to two decimal places and incorporates realistic adjustments for weight and age.

1. A dictionary called `base_speeds` is defined to associate each activity with a default average speed in kilometers per hour:
   - `"Running"`: 9.0 km/h  
   - `"Swimming"`: 3.0 km/h  
   - `"Cycling"`: 15.0 km/h  
   - `"Walking"`: 5.0 km/h  

2. The function retrieves the base speed for the given `activity` using `base_speeds.get(activity, 5.0)`. If the input activity is not found in the dictionary, a default value of 5.0 km/h is used.

3. A conditional adjustment is applied if the user is overweight. If `bmi > 25`, the base speed is reduced by 10% by multiplying the speed by `0.9`.

4. A second conditional adjustment is made if the user is above the age of 40. If `age > 40`, the speed is further reduced by 5% by multiplying by `0.95`.

5. The function concludes by rounding the final result to two decimal places using `round(speed, 2)` and returns the adjusted estimate.

This function is particularly useful for estimating exercise duration or distance in other parts of the app where calorie burn is converted into real-world physical activity.


```python
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
```

### Reference
The estimated speeds for different exercises and for people with different BMI is just a rough gauge of how the speed varies.

## Function 9. `calories_to_exercise_with_distance(calories, bmi, age)`

The `calories_to_exercise_with_distance(calories, bmi, age)` function estimates the amount of time and distance required to burn a given number of calories for different physical activities, taking into account the user’s BMI and age to adjust movement speed.

1. A dictionary named `activities` is defined, which maps four types of physical activity to their estimated energy expenditure rate (in kcal per minute):
   - `"Running"`: 10 kcal/min
   - `"Swimming"`: 14 kcal/min
   - `"Cycling"`: 8 kcal/min
   - `"Walking"`: 4 kcal/min

2. An empty dictionary called `result` is initialized to store output for each activity.

3. A `for` loop iterates through each `(activity, kcal_per_min)` pair in the `activities` dictionary.

4. For each activity:
   - The number of minutes needed to burn the given `calories` is calculated using the formula:  
     `minutes = calories / kcal_per_min`.
   - The effective movement speed (in km/h) is estimated using the helper function `estimate_speed_bmi_age(activity, bmi, age)`, which adjusts for weight and age.
   - The corresponding distance (in kilometers) is computed using:  
     `distance = (minutes / 60) * speed`,  
     which converts minutes to hours and then applies the speed.

5. The output for each activity is stored in the `result` dictionary, with three fields:
   - `"time_min"`: Rounded number of minutes required to burn the calories.
   - `"distance_km"`: Rounded distance (in kilometers), up to 2 decimal places.
   - `"speed_kmh"`: Raw adjusted speed in km/h.

6. The function finally returns the complete `result` dictionary, providing a summary of duration, distance, and speed per activity based on caloric burn.



```python
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
```

### Reference
The estimated calorie-burns for different exercises and for people with different BMI is just a rough gauge.

## Function 10. `calculate_bmr(gender, age, height, weight)`

The `calculate_bmr(gender, age, height, weight)` function calculates the Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation. BMR estimates the number of calories a person burns at rest, and it varies based on gender, age, height, and weight.

1. The function starts by evaluating the `gender` input using `gender.lower()` to make the comparison case-insensitive. This allows inputs like `"Male"` or `"MALE"` to be treated the same as `"male"`.

2. If the gender is `"male"`, the function uses the male-specific BMR formula:
   ```
   BMR = 10 * weight + 6.25 * height - 5 * age + 5
   ```
   This formula assumes weight in kilograms, height in centimeters, and age in years.

3. If the gender is anything other than `"male"` (implicitly assuming `"female"`), the function uses the female-specific formula:
   ```
   BMR = 10 * weight + 6.25 * height - 5 * age - 161
   ```
   The structure is the same, but the constant at the end changes from `+5` (for males) to `-161` (for females), reflecting the physiological difference in metabolic rates.

4. The use of `return` ensures that the function immediately exits and provides the computed BMR value for use in downstream calculations, such as TEE (Total Energy Expenditure).

This function encapsulates gender-based BMR logic in a compact and efficient manner, enabling it to plug seamlessly into energy and nutrition tracking workflows.



```python
def calculate_bmr(gender, age, height, weight):
    if gender.lower() == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
```

### Reference
Garnet Health. (2016, July 1). *Basal metabolic rate calculator.* [https://www.garnethealth.org/news/basal-metabolic-rate-calculator](https://www.garnethealth.org/news/basal-metabolic-rate-calculator)
