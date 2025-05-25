# Nutrition Recommendation App - Pynut App

This is the final project for our Python-based business analytics course. The project involves building a nutrition scoring and recommendation app that uses nutritional data to assist users in making better food choices based on their fitness goals.

## Project Overview

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
