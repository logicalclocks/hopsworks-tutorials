import streamlit as st
import hopsworks
from datetime import datetime

# Function to print a styled header
def print_header(text, font_size=22):
    res = f'<span style=" font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)

# Function to retrieve and start model deployments
@st.cache_resource()
def get_deployments():
    # Displaying a message indicating the process has started
    st.write("🚀 Retrieving and Starting Deployments...")

    # Logging into the Hopsworks project
    project = hopsworks.login()

    # Getting the model serving instance from the project
    ms = project.get_model_serving()

    # Retrieving deployments for the query model and ranking model
    query_model_deployment =  ms.get_deployment("querydeployment")
    ranking_deployment =  ms.get_deployment("rankingdeployment")

    # Starting the ranking deployment with a maximum waiting time of 180 seconds
    ranking_deployment.start(await_running=180)
    
    # Starting the query model deployment with a maximum waiting time of 180 seconds
    query_model_deployment.start(await_running=180)
    
    # Displaying a message indicating that deployments are ready
    st.write('✅ Deployments are ready!')

    # Returning deployment instances
    return ranking_deployment, query_model_deployment

st.title('👒 Fashion Items Recommender')

# Retrieve deployment instances
ranking_deployment, query_model_deployment = get_deployments()

# Dropdown to select a customer ID
option_customer = st.selectbox(
    'For which customer?',
    (
        '641e6f3ef3a2d537140aaa0a06055ae328a0dddf2c2c0dd6e60eb0563c7cbba0',
        '1fdadbb8aa9910222d9bc1e1bd6fb1bd9a02a108cb0e899b640780f32d8f7d83',
        '7b0621c12c65570bdc4eadd3fca73f081e2da5769f0d31585ac301cea58af53f',
        '675cd49509ef9692d793af738c08d9bce0856036b9e988cba4e26422944314d6',
        '895576481a1095ad66ab3279483f4323724e9d53d9f089b16f289a3f660c1101',
    )
)

# Get the current timestamp
option_time = datetime.now().isoformat()

# Display a message indicating the process has started
st.write('🔮 Getting recommendations...')

# Prepare input for the model deployment
deployment_input = {
    "instances": {
        "customer_id": option_customer, 
        "transaction_date": option_time,
    }
}

# Make a prediction using the query model deployment
prediction = query_model_deployment.predict(deployment_input)['predictions']['ranking']

# Display the top 3 recommendations
print_header('📝 Top 3 Recommendations:')
for recommendation in prediction[:3]:
    st.write(f'👔 Item ID: {recommendation[1]} 🎯 Score: {recommendation[0]}')

# Button to stop the Streamlit app and deployments
if st.button("Stop Streamlit"):
    st.write('⚙️ Stopping Deployments...')
    ranking_deployment.stop()
    query_model_deployment.stop()
    st.success('✅ App finished successfully!')
    st.stop()