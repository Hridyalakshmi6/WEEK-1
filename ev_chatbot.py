import streamlit as st
import pandas as pd

# Set page title
st.title("EV Charging Data Chatbot")

# Load the cleaned dataset (adjust the file path if needed)
df = pd.read_csv('cleaned_ev_charging_patterns.csv')

# Convert datetime columns if necessary
df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'])
df['Charging End Time'] = pd.to_datetime(df['Charging End Time'])

# Display a brief intro
st.write("This is a simple chatbot for querying the cleaned EV charging dataset. Ask questions like 'What is the average energy consumed?' or 'Show average cost by user type'.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        else:
            # If it's a DataFrame, display as table
            st.dataframe(message["content"])

# Get user input
prompt = st.chat_input("Ask a question about the EV charging data:")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response based on user prompt (simple keyword-based logic)
    response = None
    response_df = None

    try:
        lower_prompt = prompt.lower()

        if "average energy" in lower_prompt or "mean energy" in lower_prompt:
            avg_energy = df['Energy Consumed (kWh)'].mean()
            response = f"The average energy consumed is {avg_energy:.2f} kWh."

        elif "average cost" in lower_prompt or "mean cost" in lower_prompt:
            if "by user type" in lower_prompt:
                avg_cost_by_user = df.groupby('User Type')['Charging Cost (USD)'].mean().sort_values()
                response = "Average Charging Cost by User Type:"
                response_df = avg_cost_by_user
            else:
                avg_cost = df['Charging Cost (USD)'].mean()
                response = f"The average charging cost is {avg_cost:.2f} USD."

        elif "average rate" in lower_prompt or "mean rate" in lower_prompt:
            if "by charger type" in lower_prompt:
                avg_rate_by_charger = df.groupby('Charger Type')['Charging Rate (kW)'].mean().sort_values()
                response = "Average Charging Rate by Charger Type:"
                response_df = avg_rate_by_charger
            else:
                avg_rate = df['Charging Rate (kW)'].mean()
                response = f"The average charging rate is {avg_rate:.2f} kW."

        elif "charges by day" in lower_prompt:
            charges_by_day = df['Day of Week'].value_counts()
            response = "Number of Charges by Day of Week:"
            response_df = charges_by_day

        elif "average energy by location" in lower_prompt:
            avg_by_location = df.groupby('Charging Station Location')['Energy Consumed (kWh)'].mean().sort_values()
            response = "Average Energy Consumed by Location:"
            response_df = avg_by_location

        elif "summary" in lower_prompt or "describe" in lower_prompt:
            summary = df.describe()
            response = "Summary Statistics of Numerical Columns:"
            response_df = summary

        elif "head" in lower_prompt or "preview" in lower_prompt:
            head_df = df.head(5)
            response = "Preview of the first 5 rows:"
            response_df = head_df

        elif "correlation" in lower_prompt:
            numerical_cols = ['Energy Consumed (kWh)', 'Charging Duration (hours)', 'Charging Rate (kW)', 
                              'Charging Cost (USD)', 'State of Charge (Start %)', 'State of Charge (End %)', 
                              'Distance Driven (since last charge) (km)', 'Temperature (°C)', 'Vehicle Age (years)', 
                              'Calculated Duration (hours)']
            corr_matrix = df[numerical_cols].corr()
            response = "Correlation Matrix:"
            response_df = corr_matrix

        else:
            response = "Sorry, I didn't understand your question. Try asking about averages, summaries, or correlations in the dataset."

    except Exception as e:
        response = f"An error occurred: {str(e)}"

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
        if response_df is not None:
            st.dataframe(response_df)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response if response_df is None else response_df})