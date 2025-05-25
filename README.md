# Nutrition Recommendation App - Pynut App

This is the final project for our Python-based business analytics course. The project involves building a nutrition scoring and recommendation app that uses nutritional data to assist users in making better food choices based on their fitness goals.

## Project Overview

Here is a video version of the Overview: [https://youtu.be/ET7IY8N7i4I](https://youtu.be/ET7IY8N7i4I)

The app allows users to:
1. Input personal information (age, gender, height, weight, activity level, and dietary goal).
2. Calculate their Total Energy Expenditure (TEE) based on official reference values.
3. Search for menu items or branded foods using the USDA API.
4. Score and visualize how well each food item aligns with the user’s dietary goals (e.g., fat loss, muscle gain).
5. Download and access the app using a QR code for easier sharing.

## Folder Structure

- `.devcontainer/`: Development environment configuration.
- `Code Lecture Notes in Markdown/`: Detailed Project notes in Markdown.
- `Code Lecture Notes in PDF/`: Detailed Project notes in LaTeX PDF.
- `Group Project Part 3_Group 02.ipynb`: Final Jupyter Notebook containing all logic and documentation.
- `app_pypro_final.py`: the `.py` file that Streamlit connects to and turn into a web app.
- `requirements.txt`: Python package dependencies for the app.
- `qrcode to download our app.png`: QR code for app.
- `README.md`: Project summary and user guide.

## Features

- **TEE Calculation**: Calculates users' energy needs based on demographic and activity data.
- **Food Search**: Leverages USDA API to fetch branded or restaurant menu items.
- **Scoring Algorithm**: Evaluates and ranks food items based on macronutrient targets.
- **Data Visualization**: Radar chart display to compare food items and dietary needs.
- **QR Code Sharing**: Provides a portable method to access and distribute the app.

## Disclaimer

In Section 1, we made an APP with this code! **Watch this video to find out how!**  [https://youtu.be/6gwox5OGmuE?si=0IlKHI2pz2bYLKn6](https://youtu.be/6gwox5OGmuE?si=0IlKHI2pz2bYLKn6) 

- We built the app with a Python Package called **Streamlit** which we highly recommend to include in the curriculum next year! 

- The final product(App) can be viewed through this link: [https://pyprofinal02.streamlit.app/](https://pyprofinal02.streamlit.app/)

<div class="alert alert-warning">
<b>Caution:</b> 
    
**Why our file doesn't work in `.ipynb`** and how you can run it **locally** (**please check out this video for clarification**): [https://youtube.com/live/1E-Adt9oS94?feature=share](https://youtube.com/live/1E-Adt9oS94?feature=share)

- This is, though may seem unecessary, is just an extra proof that our code works, just not on ipynb, and I explained it clearly why it doesn't.
</div>
