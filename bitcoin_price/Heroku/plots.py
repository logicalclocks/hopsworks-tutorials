import plotly.graph_objs as go

def get_price_plot(data):
    fig = go.Figure()
    trace1 = go.Scatter(
        x = data.reset_index()['date'],
        y = data['close'].astype(float),
        mode = 'lines',
        name = 'Close'
    )

    layout = dict(
        title = 'Historical Bitcoin Prices',
     xaxis = dict(
         rangeslider=dict(visible = True), type='date'
       )
    )
    fig.add_trace(trace1)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate = 'Data: %{x} <br>Price: %{y}') 
    fig.update_yaxes(fixedrange=False)

    return fig


def get_volume_plot(data):
    fig = go.Figure()
    trace1 = go.Scatter(
        x = data.reset_index()['date'],
       y = data['volume'],
       mode = 'lines',
       name = 'Bitcoin Volume'
    )
    
    layout = dict(
        title = 'Historical Bitcoin Volume',
        xaxis = dict(
           rangeslider=dict(
               visible = True
            ),
            type='date'
     )
    )

    fig.add_trace(trace1)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate = 'Data: %{x} <br>Volume: %{y}') 

    return fig