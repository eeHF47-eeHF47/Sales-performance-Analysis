import threading
import time
from flask import Flask, request, jsonify
import pandas as pd
import openai
import os
import streamlit as st
import requests
from PIL import Image

# Load environment variables from.env file
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv(),override=True)
# Flask app configuration
app = Flask(__name__)

# Load the sales data from the CSV file
try:
    sales_data = pd.read_csv('sales_performance_data.csv')
    print("Columns in sales data:", sales_data.columns)  # Print columns for verification
except FileNotFoundError:
    print("Error: The file 'sales_performance_data.csv' was not found.")
    exit(1)

def get_llm_feedback(prompt):
    """
    Use OpenAI's GPT to generate feedback based on the prompt.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for faster responses
            messages=[
                {"role": "system", "content": "You are an assistant providing sales analysis feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,  # Limit the max tokens for a shorter response
            temperature=0.7,
            request_timeout=10  # Set a timeout of 10 seconds
        )
        # Extract the complete response text
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating feedback: {e}"

# Flask API Endpoints
@app.route('/api/rep_performance', methods=['GET'])
def rep_performance():
    rep_id = request.args.get('rep_id')
    if not rep_id:
        return jsonify({"error": "No representative ID provided"}), 400
    # Simulate fetching representative performance data (replace with actual logic)
    performance_data = {"rep_id": rep_id, "sales": 1000, "performance": "Good"}
    return jsonify(performance_data)

@app.route('/api/team_performance', methods=['GET'])
def team_performance():
    # Simulate team performance analysis (replace with actual logic)
    feedback = "The overall team is performing well with an upward sales trend."
    return jsonify({"feedback": feedback})

@app.route('/api/performance_trends', methods=['GET'])
def performance_trends():
    time_period = request.args.get('time_period')
    if not time_period:
        return jsonify({"error": "Time period not specified"}), 400
    # Simulate analysis (replace with actual logic)
    trends_feedback = f"Sales trends analysis for {time_period}: steady growth."
    return jsonify({"feedback": trends_feedback})

# Function to run Flask in a separate thread
def run_flask():
    app.run(port=5000, debug=True, use_reloader=False)

# Streamlit frontend with enhanced styling
def run_streamlit():
    # Set page configuration
    st.set_page_config(page_title="Sales Performance Analysis", page_icon="📊", layout="wide")

    # Add a title with an emoji and some styling
    st.markdown("<h1 style='text-align: center; color: blue;'>📊 Sales Performance Analysis Dashboard</h1>", unsafe_allow_html=True)

   # Load the image using Streamlit's st.image function

    # Open the image file
    image = Image.open("C:/Users/eshaa/Desktop/today/sales_performance/sales.jpg")


    # Display the image with st.image and use custom styling for centralization
    st.markdown(
        """
        <style>
        .centered-image {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the image with a custom CSS class for central alignment
    st.image(image, use_column_width=True, caption="Sales Performance Dashboard", output_format="auto")

    # Display the first 10 rows of the sales data with a colored header
    st.markdown("<h2 style='color: green;'>First 10 Rows of Sales Data</h2>", unsafe_allow_html=True)
    st.dataframe(sales_data.head(10), height=300)

    # Individual Sales Representative Performance
    st.markdown("<h2 style='color: orange;'>Individual Sales Representative Performance</h2>", unsafe_allow_html=True)
    rep_id = st.text_input("Enter Sales Representative ID:")

    if st.button("Analyze Representative Performance"):
        if rep_id:
            try:
                response = requests.get(f"http://127.0.0.1:5000/api/rep_performance?rep_id={rep_id}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        st.success(f"Performance Data for Representative ID {rep_id}:")
                        st.json(data)
                    except requests.exceptions.JSONDecodeError:
                        st.error("Error: The server returned a non-JSON response.")
                        st.write(response.text)  # Output the raw response for debugging
                else:
                    st.error(response.json().get('error', 'Error fetching data'))
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
        else:
            st.warning("Please enter a Sales Representative ID.")

    # Overall Team Performance Analysis
    st.markdown("<h2 style='color: purple;'>Overall Team Performance</h2>", unsafe_allow_html=True)
    if st.button("Analyze Team Performance"):
        try:
            response = requests.get("http://127.0.0.1:5000/api/team_performance")
            if response.status_code == 200:
                try:
                    feedback = response.json().get("feedback", "No feedback available.")
                    st.success("Team Performance Feedback:")
                    st.markdown(f"<div style='background-color: #e0f7fa; padding: 10px;'>{feedback}</div>", unsafe_allow_html=True)
                except requests.exceptions.JSONDecodeError:
                    st.error("Error: The server returned a non-JSON response.")
                    st.write(response.text)  # Output the raw response for debugging
            else:
                st.error(response.json().get('error', 'Error fetching data'))
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    # Sales Performance Trends
    st.markdown("<h2 style='color: teal;'>Sales Performance Trends and Forecasting</h2>", unsafe_allow_html=True)
    time_period = st.selectbox("Select Time Period:", ["monthly", "quarterly", "yearly"])

    if st.button("Analyze Trends"):
        try:
            response = requests.get(f"http://127.0.0.1:5000/api/performance_trends?time_period={time_period}")
            if response.status_code == 200:
                try:
                    feedback = response.json().get("feedback", "No feedback available.")
                    st.success("Performance Trends Feedback:")
                    st.markdown(f"<div style='background-color: #fce4ec; padding: 10px;'>{feedback}</div>", unsafe_allow_html=True)
                except requests.exceptions.JSONDecodeError:
                    st.error("Error: The server returned a non-JSON response.")
                    st.write(response.text)  # Output the raw response for debugging
            else:
                st.error(response.json().get('error', 'Error fetching data'))
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

# Run both Flask and Streamlit
if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Delay to ensure Flask starts before Streamlit
    time.sleep(2)

    # Run the Streamlit app
    run_streamlit()
