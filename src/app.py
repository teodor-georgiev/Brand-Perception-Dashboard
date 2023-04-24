from dash import Dash, dcc, html, Input, Output
from utils.styles import *
from tabs.tab1 import content_tab1, sidebar_1
from tabs.tab2 import content_tab2, sidebar_2
# from tabs.render_content import *
# dash_bootstrap_components.themes



           


# Define the Main Bar
dashboard_name = html.Div(
    html.H3('Brand Perception Dashboard',
            style={"textAlign": "left", "width":"550px","padding-left" : "25px"}),
    style=TEXT_DASHBOARD_NAME
)

tabs = html.Div(
                [
                dcc.Tabs(id="tabs", 
                        value='tab_2', 
                        children=[
                    dcc.Tab(label='Mining Brand Perceptions from Twitter', 
                            value='tab_1',
                            style = {'borderBottom': '0px solid #d6d6d6',"borderLeft": "0px solid #e0e0e0","background-color": "#ffffff","borderTop": "0px solid #e0e0e0"},
                            selected_style = {"borderLeft": "0px solid #e0e0e0"}),
                    dcc.Tab(label="Brand Perceptions' effect on Stock Price",
                            value='tab_2',
                            style = {'borderBottom': '0px solid #d6d6d6',"background-color": "#ffffff","borderTop": "0px solid #e0e0e0","borderRight": "0px solid #d6d6d6",
                                     "border-radius": "0px 10px 10px 0px"},
                            selected_style = {"borderRight": "0px solid #e0e0e0","border-radius": "0px 10px 10px 0px"}),
                    ])
                ],
                style=TAB
)

# Define the layout of the sidebar
sidebar_panel = html.Div(id = "sidebar_panel",
                         children = [],
                         style = SIDEBAR)





# Define the layout of the main content
content = html.Div(id="content", children=[],
    style=CONTENT
)






dashboard_main = html.Div(
    [
        dashboard_name,
        tabs,
    ],
    style=CONTENT
)




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets.append(dbc.themes.BOOTSTRAP)

app = Dash(__name__,external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

# Create server variable with Flask server object for use with gunicorn
server = app.server

# Create app layout
app.layout = html.Div(children=[dashboard_main,sidebar_panel,content])

# Render the content of the tabs
@app.callback(Output("content", "children"),
              Output("content", "style"), 
              Input("tabs", "value"))
def render_content(tab):
    if tab == "tab_1":
        return content_tab1 , CONTENT
    elif tab == "tab_2":
        CONTENT_2 = CONTENT.copy()
        # CONTENT_2.update({"margin-left":"13px"})
        return content_tab2, CONTENT_2

# Render the content of the sidebar    
@app.callback(Output("sidebar_panel", "children"),
              Output("sidebar_panel", "style"),
              Input("tabs", "value"))
def render_sidebar(tab):
    if tab == "tab_1":
        return sidebar_1 , SIDEBAR
    elif tab == "tab_2":
        SIDEBAR_2 = SIDEBAR.copy()
        SIDEBAR_2.update({"height":"528px"})
        return sidebar_2 , SIDEBAR_2


           
if __name__ == "__main__":
	app.run_server(port='8080',debug=False)