from datetime import timedelta, datetime
from random import sample

import pandas as pd
import streamlit as st
import hopsworks
import plotly.express as px
import altair as alt

from functions import decode_features, get_model


def fancy_header(text, font_size=24):
    res = f'<span style="color:#ff5f27; font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True )


st.title('🚲 Citibike Usage Prediction 🚲')


st.write(36 * "-")
fancy_header('\n📡 Connecting to Hopsworks Feature Store...')

st.write("Logging... ")
# (Attention! If the app has stopped at this step,
# please enter your Hopsworks API Key in the commmand prompt.)
project = hopsworks.login()
fs = project.get_feature_store()


@st.cache(allow_output_mutation=True)
def get_feature_view():
    feature_view = fs.get_feature_view(
        name = 'citibike_feature_view',
        version = 1
    )
    feature_view.init_batch_scoring()

    return feature_view


st.write("Getting the Feature View...")
feature_view = get_feature_view()
st.write("Successfully connected!✔️")

st.write(36 * "-")
fancy_header('\n🪝 Retriving some useful data from Feature Store...')
# I have to use @st.cache to cache retrieved data and
# do not connect and download it every time
@st.cache(allow_output_mutation=True)
def get_data_from_feature_groups():
    citibike_stations_info_fg = fs.get_or_create_feature_group(
        name="citibike_stations_info",
        version=1
        )
    stations_info_df = citibike_stations_info_fg.read()

    meteorological_measurements_fg = fs.get_or_create_feature_group(
        name="meteorological_measurements",
        version=1
        )
    last_date_in_df = meteorological_measurements_fg.read()["date"].max()

    return stations_info_df, last_date_in_df


stations_info_df, last_date_in_df = get_data_from_feature_groups()

st.write("✅ Done!")

st.write(36 * "-")
fancy_header('\n☁️ Getting batch data from Feature Store...')

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_batch_data(last_date_in_df):
    start_date = datetime.strptime(last_date_in_df, "%Y-%m-%d") - timedelta(days=7)
    start_time = int(start_date.timestamp()) * 1000
    df_batch = feature_view.get_batch_data(start_time=start_time)

    return df_batch


df_batch = get_batch_data(last_date_in_df=last_date_in_df)
st.write("✅ Done!")


st.write(36 * "-")
fancy_header('\n🔬 Decoding our features...')
table_df = decode_features(df_batch[["date", "users_count", "station_id"]],
                           feature_view)
st.write("✅ Done!")
# all_stations_list = ['6389.09', '6401.01', '6569.07', '6578.01', '6605.08', '6670.03',
#                  '5238.05', '5303.08', '5484.09', '5539.06', '5561.06', '5752.07',
#                  '5755.09', '6004.06', '6089.07', '6432.11', '6679.11', '6747.06',
#                  '6873.01', '6923.20', '6960.10', '7003.03', '7023.04', '7059.08',
#                  '7098.05', '7393.09', '7450.05', '7580.01', '5623.03', '5626.15',
#                  '5659.05', '5755.14', '5788.13', '5847.01', '5905.12', '5938.11',
#                  '5955.12', '5964.01', '6089.08', '6137.04', '6203.02', '6257.03',
#                  '6306.01', '6422.09', '6450.12', '5820.08', '5838.09', '5847.08',
#                  '5854.09', '5938.01', '5977.01', '6055.08', '6072.06', '6072.14',
#                  '6098.10', '6115.06', '6140.05', '6206.08']

st.write(36 * "-")
# stations_list = sample(all_stations_list, 25)
# idk why but streamlit doesnt work when I use code above
stations_list = ['7450.05', '7580.01', '5623.03', '5626.15',
                '5659.05', '5755.14', '5788.13', '5847.01', '5905.12', '5938.11',
                '5955.12', '5964.01', '6089.08', '6137.04', '6203.02', '6257.03',
                '6306.01', '6422.09', '6450.12', '5820.08', '5838.09', '5847.08',
                '5854.09', '5938.01', '5977.01', '6055.08',]

stations_info_dict_1 = stations_info_df.set_index("station_id").to_dict()
stations_info_dict_2 = stations_info_df.set_index("station_name").to_dict()
stations_list_names = list(map(lambda x: stations_info_dict_1["station_name"][x], stations_list))
st.write("✅ Done!")

fancy_header('\n🏙 Please select citibike stations to process...')
with st.form("stations_selection"):
   selected_stations_names = st.multiselect('Choose any number of stations.', stations_list_names)
   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")

selected_stations = list(map(lambda x: stations_info_dict_2["station_id"][x], selected_stations_names))

table_df = table_df[table_df.station_id.isin(selected_stations)]
stations_info_df = stations_info_df[stations_info_df.station_id.isin(selected_stations)]


st.write(36 * "-")
fancy_header('\n🗺 You have selected these stations...')
def get_map(stations_info_df):
    fig = px.scatter_mapbox(stations_info_df,
                            lat="lat",
                            lon="long",
                            zoom=11.5,
                            hover_name="station_name",
                            size=[10] * len(selected_stations)
                            # height=600,
                            # width=700
                            )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

st.plotly_chart(get_map(stations_info_df))

st.write(36 * "-")
fancy_header('\n 🤖 Getting the model...')
model = get_model(project=project, model_name="citibike_mlp_model")
st.write("✅ Done!")

st.write(36 * "-")
fancy_header('\n 🧠 Predicting...')
df_for_model = df_batch.loc[table_df.index].drop(columns=["date", "station_id", "users_count_next_day"])

model.predict(df_for_model)

temp_df = pd.DataFrame()
temp_df["users_count_next_day"] = model.predict(df_for_model)
temp_df = decode_features(temp_df, feature_view)
st.write("✅ Done!")

st.write(36 * "-")
fancy_header('\n📈 Plotting our results...')
table_df["users_count_next_day"] = temp_df["users_count_next_day"].apply(lambda x:int(max(0, x))).values
table_df = table_df.sort_values("date")

table_date_max = table_df["date"].max()

for station in selected_stations:
    try:
        pred_value = table_df[(table_df.date == table_date_max) & (table_df.station_id == station)]\
                             ["users_count_next_day"].tolist()[0]
    except IndexError:
        pred_value = 0

    new_row = {"date": "Tomorrow (Prediction)",
               "users_count": pred_value,
               "station_id": station,
               "users_count_next_day": -1}
    table_df = table_df.append(new_row, ignore_index=True)


table_df.station_id = table_df.station_id.apply(lambda x: stations_info_dict_1["station_name"][x])
table_df = table_df.rename(columns={"station_id": "Station address",
                                    "users_count": "# of usecases",
                                     "date": "Date"})

alt.renderers.enable('altair_viewer')

rect = alt.Chart(table_df).mark_rect().encode(alt.X('Station address'),
                                              alt.Y('Date'),
                                              alt.Color('# of usecases')
                                             )
text = rect.mark_text(baseline='middle').encode(text='# of usecases', color=alt.value('red'))

layer = alt.layer(
    rect, text
)

# layer.show()
st.altair_chart(layer, use_container_width=True)

st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')
st.button("Re-run")
