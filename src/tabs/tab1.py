import pandas as pd
from PIL import Image
from dash import dcc, html, Input, Output
import dash_daq as daq
import plotly.express as px
import dash_bootstrap_components as dbc
from utils.styles import *
from utils.functions import create_annotations, create_boxplot
from dash import callback

# Tab 1
# Read the data
df_brands = pd.read_csv("data/tab1/df_brands_aggregated.csv",delimiter=";")


# Set dropdown-menu options
renamed_columns = {"Social Perception Score Eco-Friendliness": "SPS Eco", "Survey Score Eco-Friendliness": "Survey Eco", 
               "Social Perception Score Luxury": "SPS Luxury", "Survey Score Luxury": "Survey Luxury", 
               "Social Perception Score Nutrition": "SPS Nutrition", "Survey Score Nutrition": "Survey Nutrition"}
df_brands.rename(columns=renamed_columns, inplace=True)
dropdown_options = df_brands.columns[1:-3].tolist()
dropdown_options_xaxis = dropdown_options
dropdown_options_yaxis = dropdown_options

# Rename the columns to make them more readable
df_brands["Sector"].replace({"apparel":"Apparel", "car":"Car", "food":"Food & Beverage", "personal_care":"Personal Care"}, inplace=True)
sectors_list = df_brands["Sector"].unique()
color_discrete_map = {"Apparel":"#636EFA", "Car":"#EF553B", "Food and Beverage":"#00CC96", "Personal Care":"#038764 "}

# Load the Brand Logos
brand_logos = {}
for i, row in df_brands.iterrows():
    brand = row["Brand Name"]
    brand_logos[brand] = Image.open(f"assets/Brand Logos/{brand}.png")

# Images for the dropdown menus
perceptions_images = {}
perceptions_list = ["Eco", "Luxury", "Nutrition","Survey","SPS"]
for i in perceptions_list:
    perceptions_images[i] = Image.open(f"assets/{i}.png")

sector_images = {}
for i in sectors_list:
    sector_images[i] = Image.open(f"assets/{i}.png")

# Begin content of sidebar in Tab 1
switch_1 =  html.Div(
            [
            html.P("Show Brand Names",style = SWITCH_NAME),
            daq.BooleanSwitch(id='brand-names-switch',
                              on=True,
                              style = SWITCH)
            ],
            style = {"height":"40px","margin-top":"25px"}
)

switch_2 =  html.Div(
            [
            html.P("Show Trendline",style = SWITCH_NAME),
            daq.BooleanSwitch(id='trendline-switch',on=True,style = SWITCH)
            ]
            ,style ={"height":"40px"}
)

switch_3 =  html.Div(
            [
            html.P("Show Brand Logos",style = SWITCH_NAME),
            daq.BooleanSwitch(id='logo-switch',on=False,style = SWITCH)
            ]
            ,style ={"height":"40px"}
)


sidebar_1 = [
        html.H3("Filters", style={"textAlign": "center",}),
        html.Hr(style={"margin-top":"24px"}),
        dbc.Nav
        (
            [
                html.Label('Select X-Axis'),
                dcc.Dropdown(dropdown_options_xaxis, 'Survey Eco', id='xaxis-column',clearable=False,style={"margin-bottom":"10px"}),
                
                html.Img(id='xaxis-column-image-1',src=perceptions_images["Survey"],style={"width":"45%","height":"50px","object-fit":"contain","float":"left"}),
                html.Img(id='xaxis-column-image-2',src=perceptions_images["Eco"],style={"width":"45%","height":"50px","object-fit":"contain","float":"right"}),
                
                html.Label('Select Y-Axis'),
                dcc.Dropdown(dropdown_options_yaxis,'SPS Eco',id='yaxis-column',clearable=False,style={"margin-bottom":"10px"}),
                html.Img(id='yaxis-column-image-1',src=perceptions_images["SPS"],style={"width":"45%","height":"50px","object-fit":"contain","float":"left"}),
                html.Img(id='yaxis-column-image-2',src=perceptions_images["Eco"],style={"width":"45%","height":"50px","object-fit":"contain","float":"right"}),
                
                html.Label('Select Sector(s)'),
                html.Div(
                    [
                    dcc.Dropdown(sectors_list,['Car'],multi=True, id="sector-dropdown",placeholder="Select Sector(s)",style={"height":"75px"})
                    ],style={"font-size":"14px"}
                ),
                html.Div(id = "sector-dropdown-images",children = [],style={"width":"100%","height":"50px"}),
                switch_1,
                switch_2,
                switch_3,
                
            ],
            vertical=True,
            pills=True,
        ),
    ]
# End of content of sidebar in Tab 1

# Begin content of main content in Tab 1
content_first_row = html.Div(
    [
        dcc.Graph(
            id='brand_perception_culotta',
            style={
                "border": "1px solid #e0e0e0",
                "width": "99.9%",
                "float": "left",
                "margin-top": "10px",
                "border-radius": "10px",
                "background-color": "white"
            },
            config=GRAPH_CONFIG
        ),
    ]
)

content_second_row = html.Div([
    dcc.Graph(id='brand_perception_culotta_boxplot_x', style=GRAPH, config=GRAPH_CONFIG), 
    dcc.Graph(id='brand_perception_culotta_boxplot_y', style=GRAPH, config=GRAPH_CONFIG)
], className="tab-1-boxplot-row")

content_tab1 = [content_first_row, content_second_row]
# End of content of main content in Tab 1


# Remove selected value from dropdown options
@callback(Output("xaxis-column","options"),
              Output("yaxis-column","options"),
              Input("xaxis-column","value"),
              Input("yaxis-column","value")
              )
def remove_options_tab(xaxis_column_value,yaxis_column_value):
    options_xaxis = [x for x in dropdown_options_xaxis if x != yaxis_column_value]
    options_yaxis = [x for x in dropdown_options_yaxis if x != xaxis_column_value]
    return options_xaxis, options_yaxis


@callback(
    Output('brand_perception_culotta', 'figure'),
    Output('brand_perception_culotta_boxplot_x', 'figure'),
    Output('brand_perception_culotta_boxplot_y', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('sector-dropdown', 'value'),
    Input('brand-names-switch', 'on'),
    Input('trendline-switch', 'on'),
    Input('logo-switch', 'on'),
    )

def update_graphs_1(xaxis_column_name, yaxis_column_name,sector_dropdown_name, brand_names, trendline_switch,logo_switch):
    df_filtered = df_brands[df_brands["Sector"].isin(sector_dropdown_name)]
    # dots_size = df_filtered[yaxis_column_name].fillna(0) + df_filtered[xaxis_column_name].fillna(0)
    df_filtered["dots_size"] = 1
    # Create the Scatter Plot
    fig = px.scatter(
                        df_filtered, x=xaxis_column_name, y=yaxis_column_name, color="Sector",hover_name="Brand Name", size = "dots_size", size_max=15,
                        height=550, color_discrete_map=color_discrete_map, hover_data={"dots_size":False,xaxis_column_name :":.2f", yaxis_column_name :":.3f"},
                        trendline="ols" if trendline_switch else None,
                        template = "simple_white"
                    )
    title = "Scatterplot of " + xaxis_column_name + " vs " + yaxis_column_name
    annotations = create_annotations(df_filtered, xaxis_column_name, yaxis_column_name)
    fig.update_layout(  
                        margin={'l': 40, 'b': 40, 't': 30, 'r': 180}, hovermode='closest',
                        hoverlabel=dict(bgcolor="white"),
                        uirevision="Don't change",
                        # Make the background transparent
                        paper_bgcolor='rgba(0,0,0,0)',
                        # scene=dict(annotations=annotations)
                        # legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.99)
                        # legend=dict(
                        #         orientation="h",
                        #         yanchor="bottom",
                        #         y=0.95,
                        #         xanchor="right",
                        #         x=0.99
                        #         ),
                    
                        # transition_duration=250   
                        title={
                        'text': title,
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'} 
                    )

    # fig.update_traces(hovertemplate = xaxis_column_name + " %{x}" + "<br>%{y:.2f}")
    fig.update_xaxes(title = xaxis_column_name)
    fig.update_yaxes(title = yaxis_column_name)
    
    # fig.update_traces(textposition='top center',textfont_size=12)
    # fig.update_traces(marker={'size': 15})
    
    fig.update_layout(annotations=annotations if brand_names else [])
    
    # Create the Boxplots
    boxplot_x = create_boxplot(df_filtered, xaxis_column_name, xaxis_column_name, color_discrete_map)
    boxplot_y = create_boxplot(df_filtered, yaxis_column_name, yaxis_column_name, color_discrete_map)
    

    # fig.update_traces(marker_color="rgba(0,0,0,0)")
    if logo_switch:
        fig.update_traces(marker={'size': 1})
        xaxis_max = df_filtered[xaxis_column_name].max()
        yaxis_max = df_filtered[yaxis_column_name].max()
        x_size = xaxis_max*0.09
        y_size = yaxis_max*0.09
        if yaxis_column_name == "Survey Eco" and "Apparel" in sector_dropdown_name:
            x_size = xaxis_max*0.06
            y_size = yaxis_max*0.06
        
        for i, row in df_filtered.iterrows():
            brand = row["Brand Name"]
            fig.add_layout_image(
                dict(
                    source= brand_logos[brand],
                    xref= "x",
                    yref= "y",
                    xanchor="center",
                    yanchor="middle",
                    x=row[xaxis_column_name],
                    y=row[yaxis_column_name],
                    sizex= x_size,
                    sizey= y_size,
                    sizing="contain",
                    opacity=1,
                    layer="above"
                )
            )

    return fig, boxplot_x, boxplot_y

# Update the Images shown below the dropdowns
@callback(Output("xaxis-column-image-1","src"),
              Output("xaxis-column-image-2","src"),
              Output("yaxis-column-image-1","src"),
              Output("yaxis-column-image-2","src"),
              Input("xaxis-column","value"),
              Input("yaxis-column","value"),
              )
def update_dropdown_images(xaxis_column_name, yaxis_column_name):
    xaxis_column_string = xaxis_column_name.split(" ")
    yaxis_column_string = yaxis_column_name.split(" ")
    return perceptions_images[xaxis_column_string[0]], perceptions_images[xaxis_column_string[1]], perceptions_images[yaxis_column_string[0]], perceptions_images[yaxis_column_string[1]]
              
# Update the Images shown below the sector dropdown
@callback(Output("sector-dropdown-images","children"),
              Input("sector-dropdown","value"),
              )
def update_sector_dropdown_images(sector_dropdown_list):
    return [html.Img(src=sector_images[sector], style={"height":"50px", "width":"auto", "margin":"10px"}) for sector in sector_dropdown_list]
    

# Turn Brand Names Off when Brand Logos are turned ON
@callback(
    Output('brand-names-switch',"on"),
    Output('brand-names-switch',"disabled"), 
    Input('logo-switch', 'on'))
def update_brand_names(logo_switch):
    if logo_switch:
        return False, True
    else:
        return True, False