import datetime

from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import base64
import os
import sys

import validation
from stats import compute_stats

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    title="FastalaVista"
)

navbar = dbc.Navbar(
    children=[
        # Left: App Title
        dbc.NavbarBrand("Data Viz", className="ms-2"),

        # Hamburger toggle for mobile
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

        # Collapsible menu items (right side)
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="#", className="nav-link")),
                    dbc.NavItem(dbc.NavLink("About", href="#", className="nav-link")),
                    dbc.NavItem(dbc.NavLink("GitHub", href="https://github.com/", target="_blank")),
                ],
                className="ms-auto",  # Push to right
                navbar=True,
            ),
            id="navbar-collapse",
            is_open=False,
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    sticky="top",

)


@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar(n, is_open):
    if n:
        return not is_open
    return is_open


footer = html.Div(
    [f"""
    Fasta Visualization Tool
    """,
     html.Br(),
     html.Hr(),
     f"{datetime.datetime.today().strftime("%Y-%m-%d")}"
        , html.Div("Contact:"),
     html.Div([
         html.A(html.I(className="fas fa-envelope"), href="mailto:sgvolpe@gmail.com", target="_blank"),
         html.A(html.I(className="fab fa-linkedin"), href="https://linkedin.com/in/santiago-gonzalez-volpe-22009a35",
                target="_blank"),
         html.A(html.I(className="fab fa-github"), href="https://github.com/sgvolpe", target="_blank")
     ], className="footer-links"),
     html.Div("Developed by SGV", className="footer-signature")

     ],
    className="footer"
)

app.layout = html.Div(
    children=[
        dcc.Store(id="stored-data"),
        navbar,
        html.Div(
            children=[
                dbc.Container(
                    [
                        dbc.Row(
                            html.H2(
                                "Fastalavista, sequence visualization Tool",
                                style={"textAlign": "center", "marginTop": "20px"}
                            ),
                        ),
                        dbc.Row(
                            children=[

                                dbc.Col(
                                    [  # Upload dashboard JSON
                                        dcc.Upload(
                                            id="upload-seq",
                                            children=html.Div(
                                                [
                                                    "Drag and Drop or ",
                                                    html.A("Select File")
                                                ]),
                                            style={
                                                "width": "100%", "height": "100px", "lineHeight": "100px",
                                                "borderWidth": "2px", "borderStyle": "dashed",
                                                "borderRadius": "10px", "textAlign": "center", "margin": "10px"},
                                            multiple=False
                                        )
                                    ]
                                )
                            ]
                        ),
                        dbc.Row(
                            html.Hr()
                        ),
                        html.Div(
                            id="file-info-div",
                            style={"fontWeight": "bold", "marginTop": "10px"}
                        ),

                        dbc.Row(
                            html.Hr(),

                        ),

                        dcc.Download(id="download-dashboard-json"),
                        html.Br(),

                    ],
                    fluid=True,
                    className="panel"
                ),
                dbc.Container(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.Div(id="sequences"),
                                    ]
                                )
                            ]
                        ),

                    ],
                    className="panel"
                )
            ],
            className="app-content"
        ),
        footer

    ]
)


def make_length_distribution_chart(length_dist: dict):
    """
    Convert a dict like {49: 1, 48: 2, 47: 1} into a Plotly bar chart
    that shows sequence/read length distribution.

    Parameters
    ----------
    length_dist : dict
        Keys = lengths (int), values = counts (int)

    Returns
    -------
    go.Figure
        Plotly figure suitable for Dash dcc.Graph
    """

    # Sort lengths numerically for a clean plot
    lengths = sorted(length_dist.keys())
    counts = [length_dist[l] for l in lengths]

    fig = go.Figure(
        data=[
            go.Bar(
                x=lengths,
                y=counts,
            )
        ]
    )

    fig.update_layout(
        title="Sequence Length Distribution",
        xaxis_title="Length (bp)",
        yaxis_title="Count",
        template="plotly_white",
        bargap=0.2,
        margin=dict(l=40, r=20, t=60, b=40),
    )

    return fig

@app.callback(
    Output("stored-data", "data"),
    Output("file-info-div", "children"),
    Input("upload-seq", "contents"),
    State("upload-seq", "filename")
)
def update_stored_data(contents, filename):
    if contents is None:
        return None, ""
    else:
        content_type, content_string = contents.split(',')
        text = base64.b64decode(content_string).decode("utf-8")
        format = validation.detect_format(text)

        result = validation.validate_sequence(text)
        sequences = result.sequence_records
        fmt = validation.detect_format(text)

        stats = compute_stats(
            text, fmt)
        info_text = f"File: {filename} | Format: {format} | Sequences: {len(sequences)} |Length: {len(text)} "
        histogram = make_length_distribution_chart(stats["length_distribution"])
        return {
            "result": [
                seq_rec.model_dump()
                for seq_rec in sequences
            ],
            "text": text,
        }, html.Div([
            html.P(info_text),
            dcc.Graph(figure=histogram)
        ])


@app.callback(
    Output("sequences", "children"),
    Input("stored-data", "data"),
)
def update_sequences(data):
    if data is None:
        return []
    sequences = html.Div(
        children=[]
    )


    for seq in data["result"]:
        gc_content = validation.gc_content(seq.get("seq", ""))
        sequences.children.extend(
            [
                html.Div(
                    children=[
                        html.H5(f"ID: {seq['id']}"),
                        html.P(f"Description: {seq['description']}"),
                        html.Pre(f"Sequence: {seq['seq']}"),
                        html.Pre(f"GC: {gc_content}"),
                        html.Hr()
                    ]
                )
            ]
        )

    print(data["result"])
    return sequences


if __name__ == "__main__":
    app.run(debug=True)
