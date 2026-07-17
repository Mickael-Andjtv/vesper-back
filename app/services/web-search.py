import requests
from ddgs import DDGS


class WebSearch:
    def get_context(self, query: str) -> str:
        try:
            result = DDGS().text(query, region="fr-fr", max_results=5)[0]
            return requests.get(f"https://r.jina.ai/{result.get('href')}").text
        except Exception as e:
            raise RuntimeError(f"Error:{str(e)}")

    
