import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

# Load the correlation data
df_correlation = pd.read_csv("CountryCorrelationStats.csv")

# Load the Female Labour Force Participation data
df_female_participation = pd.read_csv("FemaleParticipationStats.csv")

# Load the CO2 Emission data
df_emission = pd.read_csv("EmissionStats.csv")

# Create the choropleth map using the correlation data
fig = px.choropleth(
    df_correlation,
    locations="Code", 
    color="CorrelationCoefficient",  
    hover_name="CountryName",  
    color_continuous_scale=px.colors.diverging.RdYlBu, 
    range_color=(-1, 1)  
)

# Initialize the Dash app and set the external Bootstrap stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container(
    [
        # Add the title at the top of the page
        html.H1(
            "Correlation between CO2 Emission and Female Labour Force Participation",
            style={"text-align": "center", "margin-top": "20px", "margin-bottom": "20px"}
        ),
        
        # The Choropleth Map
        dcc.Graph(id="choropleth", figure=fig, style={"height": "60vh", "margin-left": "40px", "margin-right": "40px"}),

        # Modal for displaying country details
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
                dbc.ModalBody(
                    [
                        dcc.Graph(id="participation-graph"),
                        dcc.Graph(id="emission-graph")
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal",
            is_open=False,
            size="xl",  # Make the modal large enough to display both graphs
        ),

        html.P(
    """
    The graph maps the correlation coefficient of the graphs of CO2 Emission (tons) and Female Labour Force Participation (%) over time (1991 - 2022). 
    This process was done by collecting and filtering open-source verified data and plotting the graphs of year  to Labour Force Participation and CO2 emissions relation. 
    The correlation coefficient was determined in MATLAB and the results are mapped on this interactive SVG choropleth model, with the scale ranging from -1 to 1, to uncover if certain regions follow a trend.
    By clicking on a country, you are able to view the individual graphs to visually examine their correlation, and their corresponding higher-degree regressive mathematical model.
    A 3D Multivariable graph is also available along with its multivariable equation and the corresponding axes: 
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),
html.P(
    """
    X = Date range (1991 to 2022)
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),

html.P(
    """
    Y = Female Labour Force Participation (%) 
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),

html.P(
    """
    Z = CO2 Emission (tons)
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),



html.P(
    """
    A multivariable graph is useful in determining the projected trends by finding the partial derivative with respect to the required value, or by simply pluggung .... elaborate more  
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),
html.B(
    """
    Open Sourced Data: 
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px",
        "margin-top": "400px",
}
),
html.P(
    """
    Global Carbon Budget (2023) – with major processing by Our World in Data. “Annual CO₂ emissions – GCB” [dataset]. 
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),

html.P(
    """
    International Labour Organization. “ILO Modelled Estimates and Projections Database (ILOEST)” ILOSTAT. Accessed February 06, 2024. https://ilostat.ilo.org/data/.
    """,
    style={"text-align": "left",
        "margin-left": "200px",
        "margin-right": "200px"}
),

    ],
    fluid=True,
)

# Callback to open the modal with country data and graphs when a country is clicked
@app.callback(
    [Output("modal", "is_open"),
     Output("modal-title", "children"),
     Output("participation-graph", "figure"),
     Output("emission-graph", "figure")],
    [Input("choropleth", "clickData"),
     Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(clickData, n_clicks_close, is_open):
    if n_clicks_close and is_open:
        return False, "", go.Figure(), go.Figure()  # Close modal

    if clickData:
        country_code = clickData['points'][0]['location']
        country_name = clickData['points'][0]['hovertext']
        
        # Filter Female Labour Participation data for the selected country
        country_data_female = df_female_participation[
            (df_female_participation['Code'] == country_code) & 
            (df_female_participation['Year'] >= 1991) & 
            (df_female_participation['Year'] <= 2022)
        ]

        # Create the plot for Female Labour Force Participation over time
        participation_fig = go.Figure()
        participation_fig.add_trace(go.Scatter(
            x=country_data_female['Year'],
            y=country_data_female['Value'],
            mode='lines+markers',
            name='Participation Rate'
        ))

        # Customize the participation graph
        participation_fig.update_layout(
            title=f"Female Labour Force Participation in {country_name}",
            xaxis_title="Year",
            yaxis_title="Labour Force Participation Rate (%)",
            yaxis=dict(range=[0, 100]),
            xaxis=dict(range=[1991, 2022]),
            height=400
        )

        # Filter CO2 Emission data for the selected country
        country_data_emission = df_emission[
            (df_emission['Code'] == country_code) & 
            (df_emission['Year'] >= 1991) & 
            (df_emission['Year'] <= 2022)
        ]

        # Create the plot for CO2 Emissions over time
        emission_fig = go.Figure()
        emission_fig.add_trace(go.Scatter(
            x=country_data_emission['Year'],
            y=country_data_emission['AnnualCO_Emissions'],
            mode='lines+markers',
            name='CO2 Emissions'
        ))

        # Customize the emission graph
        emission_fig.update_layout(
            title=f"CO2 Emissions in {country_name}",
            xaxis_title="Year",
            yaxis_title="CO2 Emissions (tons)",
            yaxis=dict(range=[country_data_emission['AnnualCO_Emissions'].min(), country_data_emission['AnnualCO_Emissions'].max()]),
            xaxis=dict(range=[1991, 2022]),
            height=400
        )

        # Return the modal data
        return True, f"Country: {country_name} (Code: {country_code})", participation_fig, emission_fig

    return is_open, "", go.Figure(), go.Figure()  # Keep modal state unchanged if no click

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
