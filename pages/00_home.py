import solara


@solara.component
def Page():
    with solara.Column(align="center"):
        markdown = """
        ## A Solara web app for DuckDB
        This is a Solara web app for DuckDB. Click on the menu above to see the different examples.
        <br>
        Source code: <https://github.com/opengeos/duckdb-solara>
        ![](https://github.com/user-attachments/assets/216789ff-7e9d-46df-8bb0-9fbaca531a39)
        """

        solara.Markdown(markdown)
