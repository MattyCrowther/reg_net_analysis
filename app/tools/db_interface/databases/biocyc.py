import requests
from db_interface.databases.abstract_database import AbstractDatabase

class RegulonDB(AbstractDatabase):
    BASE_URL = "https://regulondb.ccg.unam.mx/graphql"

    def __init__(self):
        self.session = requests.Session()

    def _post(self, graphql_query: str):
        """Send a POST request with a GraphQL query to RegulonDB."""
        try:
            response = self.session.post(self.BASE_URL, json={"query": graphql_query}, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"GraphQL API call failed: {e}")

    def fetch_all(self):
        """Fetch all core biological entities."""
        genes =  self.fetch_all_genes(1)
        return
        operons = self.fetch_all_operons(1)
        regulons =  self.fetch_all_regulons(1)
        sigmulons = self.fetch_all_sigmulons(1)
        # Try to unify.

    def fetch_entity(self, name: str):
        """Fetch a single entity overview by name."""
        query = f"""
        {{
          getOverview(name: "{name}") {{
            name
            type
            id
            data
          }}
        }}
        """
        return self._post(query)
