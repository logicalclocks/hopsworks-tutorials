import streamlit as st
import hopsworks

@st.cache_resource()
def get_deployments(_project):
    
    fs = _project.get_feature_store()
    ms = _project.get_model_serving()
    
    articles_fv = fs.get_feature_view(
        name="articles", 
        version=1,
    )

    query_model_deployment = ms.get_deployment("querydeployment")
    ranking_deployment = ms.get_deployment("rankingdeployment")
    
    ranking_deployment.start(await_running=180)
    query_model_deployment.start(await_running=180)
    
    return articles_fv, ranking_deployment, query_model_deployment