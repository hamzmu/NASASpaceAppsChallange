import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go

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

app.layout = dbc.Container(
    [
        html.H1("Correlation between CO2 Emission and Female Labour Force Participation",
            style={"text-align": "center", "margin-top": "20px", "margin-bottom": "20px"}),
        dcc.Graph(id="choropleth", figure=choropleth_fig, style={"height": "60vh"}),
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


@app.callback(
    [Output("modal", "is_open"),
     Output("modal-title", "children"),
     Output("modal-body", "children")],
    [Input("choropleth", "clickData"),
     Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)

#gpt assisted code
def toggle_modal(clickData, n_clicks_close, is_open):
    if n_clicks_close and is_open:
        return False, "", ""  

    # If user clicks on a country in the choropleth
    if clickData:
        country_info = clickData['points'][0]
        country_name = country_info['hovertext']
        country_code = country_info['location']
        

        female_country_data = female_data[female_data['Code'] == country_code]
        emission_country_data = emission_data[emission_data['Code'] == country_code]

        # Merge the datasets on Year and ensure the lengths are the same
        merged_data = pd.merge(
            female_country_data[['Year', 'Value']],
            emission_country_data[['Year', 'AnnualCO_Emissions']],
            on='Year'
        ).dropna()  

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

        #setup and calculate the higher degree regression model to get multivariable equation
        #prompted AI assisted tool to setup 
        year_grid, female_grid = np.meshgrid(np.linspace(years.min(), years.max(), 20), np.linspace(female_participation.min(), female_participation.max(), 20))
        co2_fit = (
            model.intercept_
            + model.coef_[0] * year_grid
            + model.coef_[1] * female_grid
            + model.coef_[2] * (year_grid ** 2)
            + model.coef_[3] * (female_grid ** 2)
            + model.coef_[4] * (year_grid * female_grid)
        )
        
        # Create 3D **Scatter** plot
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
            title="3D Scatter Plot of Year, Female Participation, and CO2 Emissions",
            
        )
        
        # Combine all the graphs in the modal body
        modal_body = html.Div([
            html.P(f"For Z = CO2, X = Year, and Y = FemaleParticipation"),
            html.P(f"Quadratic Regression Equation: z = {model.intercept_:.2f} + {model.coef_[0]:.2f}y + {model.coef_[1]:.2f}x + {model.coef_[2]:.2f}y^2 + {model.coef_[3]:.2f}x^2 + {model.coef_[4]:.2f}xy"),
            dcc.Graph(
                figure=scatter_3d_fig,
                style={"height": "80vh"}  # Set a larger height for the 3D graph
                ),
            dcc.Graph(figure=female_participation_fig),
            dcc.Graph(figure=emission_fig)
        ])

        # Modal title
        title = f"Country: {country_name} (Code: {country_code})"
        return True, title, modal_body  # Open modal with data

    return is_open, "", ""  # Keep modal state unchanged
### - gpt assisted code end for using ploty


if __name__ == '__main__':
    app.run_server(debug=True)
