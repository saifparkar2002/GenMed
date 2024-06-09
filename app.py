import os
import time
import json
import pandas as pd
import streamlit as st
from urllib.request import urlopen
from langchain_openai import OpenAI
from langchain_experimental.agents import create_csv_agent
# DONT SET TO ALWAYS RERUN THE SCRIPT AS IT WILL RELOAD THE AGENT EVERYTIME AND  USE MORE OPEN AI API CREDITS

def get_kendra_details(pincode):
    df = pd.read_csv('GPS_dataset.csv', encoding='latin-1')
    pin_df = df[df['Pincode'] == pincode]
    return pin_df['Kendra Address'].values[0], pin_df['Status'].values[0], pin_df['Store Code'].values[0], pin_df['District'].values[0], pin_df['State'].values[0]

def curr_location():
    url = "http://ipinfo.io/json"

    response = urlopen(url)
    data = json.load(response)

    return data

# data_addr = curr_location()
# st.write(data_addr)
get, search = st.tabs(["Search Medicine Price", "Search Kendra by Pincode"])

st.sidebar.markdown("**About MedBot**")
st.sidebar.info("This chatbot is designed for informational purposes. Always consult a doctor for medical advice. ")
st.sidebar.markdown("""
**Data Source:** 
1. Jan Aushadi Kendra Website : For Generic Medicine and Drug Information.
2. Tata 1mg Website: For Normal Medicine Name and Price.""")


def main():
    # tabs for 1 for searching medicine price and another for searching kendra by pincode
    # HIDE THIS IF WE ARE GOING TO DEPLOY
    OPENAI_API_KEY = "YOUR API KEY"
    
    with get:
        data = curr_location()
        st.header("GenMed - General Medical Chatbot 💊") 
        st.markdown("GenMed is a general medical chatbot that can answer questions about your medication. 😊")
        st.write("""
        Tasks it can perform:
        * Provide generic prices for common medications 💰
        """)
        main_df = pd.read_csv('data.csv')
        filtered_group = st.selectbox("Do you know your what your medicine is for? ", [None] + main_df["Group Name"].unique().tolist())
        filtered_group_df = main_df[main_df["Group Name"] == filtered_group]
        filtered_group_df.to_csv('filtered_group.csv', index=False)
        add_name , status, store_code, _, _ = get_kendra_details(int(data.get('postal')))
        
        if filtered_group == None: 
            data_csv = 'data.csv'
        else:
            data_csv = 'filtered_group.csv'

        agent = create_csv_agent(
            OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY),
            data_csv,
            verbose=True
        )

        user_question = st.text_input("Ask a question about your medication: ")

        if user_question: 
            start_time = time.time() # Record the start time
            with st.spinner(text="Consulting the medical database... 🧠"):
                response = agent.run(user_question)
                st.write(response)
            end_time = time.time() # Record the end time
            response_time = end_time - start_time # Calculate the response time
            st.write(f"Response Time: {response_time:.2f} seconds")
        
        if st.button("Get your nearest Kendra? 🏥"):
            st.subheader("**Your nearest Kendra**")
            st.write("Your current Pincode: ", data['postal'])
            st.error("Note this pincode is based on your current ip. so it may be incorrect if you know pincode then kindly search by pincode")
            st.info(f"**Nearest Kendra:** {add_name} ")
            st.write(f"**Status:** `{status}` ")

    with search:
        st.header("Search Kendra by Pincode 📍")
        st.write("Enter your pincode to find the nearest Jan Aushadi Kendra.")
        pincode = st.text_input("Enter your pincode")
        if st.button("Search"):
            add_name , status, store_code, district, state = get_kendra_details(int(pincode))
            st.write(f"**Nearest Kendra:** {add_name} ")
            st.write(f"**District:** ", district)
            st.write(f"**State:** ", state)
            st.write(f"**Status:** `{status}` ")
            st.write(f"**Store Code:** `{store_code}` ")


if __name__ == "__main__":
    main()