import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go

# Load the datasets
female_data = pd.read_csv('FemaleParticipationStats.csv')
emission_data = pd.read_csv('EmissionStats.csv')
correlation_data = pd.read_csv('CountryCorrelationStats.csv')

# Create the base choropleth map
choropleth_fig = px.choropleth(
    correlation_data,
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
        dcc.Graph(id="choropleth", figure=choropleth_fig, style={"height": "60vh"}),

        # Modal for displaying country details and the graphs
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal",
            is_open=False,
            size="xl"
        ),

        html.P(
            """
            The graph maps the correlation coefficient of the graphs of CO2 Emmission(tons) and Female Labour force participation(%) over time (1991 - 2022).
            This process was done by collected and filtered Open source verified data and plotting the graphs of year relation to Labour force participation and Co2 emissions.
            The correlation coefficient was determined in MATLAB and results are mapped on this interactive SVG choropleth model, with a scale from -1 to 1, to uncover if certain regions follow a trend.
            """,
            style={"text-align": "center", "margin-top": "11px", "margin-bottom": "20px"}
        ),
    ],
    fluid=True,
)

# Callback to open the modal with country data when a country is clicked
@app.callback(
    [Output("modal", "is_open"),
     Output("modal-title", "children"),
     Output("modal-body", "children")],
    [Input("choropleth", "clickData"),
     Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(clickData, n_clicks_close, is_open):
    # Check if the modal is already open and if the user clicked "close"
    if n_clicks_close and is_open:
        return False, "", ""  # Close modal

    # If user clicks on a country in the choropleth
    if clickData:
        country_info = clickData['points'][0]
        country_name = country_info['hovertext']
        country_code = country_info['location']
        
        # Filter data for selected country
        female_country_data = female_data[female_data['Code'] == country_code]
        emission_country_data = emission_data[emission_data['Code'] == country_code]

        # Merge the datasets on Year and ensure the lengths are the same
        merged_data = pd.merge(
            female_country_data[['Year', 'Value']],
            emission_country_data[['Year', 'AnnualCO_Emissions']],
            on='Year'
        ).dropna()  # Drop rows with missing values if any

        # Create the two 2D graphs (Female Participation and CO2 Emissions)
        female_participation_fig = px.line(merged_data, x="Year", y="Value", title="Female Labour Force Participation")
        emission_fig = px.line(merged_data, x="Year", y="AnnualCO_Emissions", title="CO2 Emissions")

        # 3D Scatter Plot
        years = merged_data['Year'].values
        female_participation = merged_data['Value'].values
        co2_emissions = merged_data['AnnualCO_Emissions'].values
        
        X = np.column_stack((years, female_participation))
        X_poly = np.column_stack((X, years**2, female_participation**2, years*female_participation))
        
        # Fit a quadratic regression model
        model = LinearRegression()
        model.fit(X_poly, co2_emissions)
        
        # Generate predictions for the regression plane
        year_grid, female_grid = np.meshgrid(np.linspace(years.min(), years.max(), 20), np.linspace(female_participation.min(), female_participation.max(), 20))
        co2_fit = (
            model.intercept_
            + model.coef_[0] * year_grid
            + model.coef_[1] * female_grid
            + model.coef_[2] * (year_grid ** 2)
            + model.coef_[3] * (female_grid ** 2)
            + model.coef_[4] * (year_grid * female_grid)
        )
        
        # Create 3D Scatter plot
        scatter_3d_fig = go.Figure(data=[
            go.Scatter3d(x=years, y=female_participation, z=co2_emissions, mode='markers', marker=dict(size=5)),
            go.Surface(x=year_grid, y=female_grid, z=co2_fit, opacity=0.5)
        ])
        scatter_3d_fig.update_layout(
            scene=dict(
                xaxis_title='Year',
                yaxis_title='Female Labour Force Participation (%)',
                zaxis_title='CO2 Emissions (tons)',
            ),
            title="3D Scatter Plot of Year, Female Participation, and CO2 Emissions"
        )
        
        # Combine all the graphs in the modal body
        modal_body = html.Div([
            dcc.Graph(figure=female_participation_fig),
            dcc.Graph(figure=emission_fig),
            dcc.Graph(figure=scatter_3d_fig),
            html.P(f"Quadratic Regression Equation: CO2 = {model.intercept_:.2f} + {model.coef_[0]:.2f}*Year + {model.coef_[1]:.2f}*FemaleParticipation + {model.coef_[2]:.2f}*Year^2 + {model.coef_[3]:.2f}*FemaleParticipation^2 + {model.coef_[4]:.2f}*Year*FemaleParticipation")
        ])

        # Modal title
        title = f"Country: {country_name} (Code: {country_code})"

        return True, title, modal_body  # Open modal with data

    return is_open, "", ""  # Keep modal state unchanged

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
