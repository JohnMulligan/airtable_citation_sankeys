# Sankey diagram citation visualization scripts

2 scripts used to generate Sankey diagrams from citational data. Saved to github for reproducibility.

Noe: both of these rely on an airtable with a very particular structure, and need authentication keys saved in airtablekeys.json in order to run properly. Very loosely, that structure is one of unidirectional citations (one author--Foucault's--citations of a variety of texts). Texts in one table, citations between them in another. One author is privileged (here, Foucault). Author names are used to group texts cited by the privileged author. 

## Plotly

This runs a dashboard in Python3 and Plotly Dash.

1. It is ready for containerized deployment to plotly.
   1. Example at https://thawing-waters-20828.herokuapp.com/
   1. Using instructions here: https://dash.plotly.com/deployment
1. It runs the queries live
1. Downside: it auto-sorts the nodes, and this function cannot be disabled. So this graph is more tangled than it needs to be.

## d3

This runs on observable.

1. Easy peasy. With the airtable auth codes it pulls in a list of cited works, authors, and citations between them.
1. Generates diagrams ready for parsing in this notebook https://observablehq.com/@johnmulligan/sankey-diagram
1. Using a threshold of minimum citations as defined in the script.
