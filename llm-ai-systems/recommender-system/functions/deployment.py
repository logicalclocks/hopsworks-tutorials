import streamlit as st
import hopsworks

@st.cache_resource()
def get_deployment(_project):
    
    fs = _project.get_feature_store()
    ms = _project.get_model_serving()
    
    articles_fv = fs.get_feature_view(
        name="articles", 
        version=1,
    )

    recommender_deployment = ms.get_deployment("recommenderdeployment")
    
    recommender_deployment.start(await_running=180)
    
    return articles_fv, recommender_deployment