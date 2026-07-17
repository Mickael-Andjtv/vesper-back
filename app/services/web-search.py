import requests
from ddgs import DDGS


class WebSearch:
    def _get_content(self, query: str) -> str:
        try:
            result = DDGS().text("Film Michael 2026", region="fr-fr", max_results=5)[0]
            return requests.get(f"https://r.jina.ai/{result.get('href')}").text
        except Exception as e:
            raise RuntimeError(f"Error:{str(e)}")

    def get_search(self, query: str, request: str):
        content = self._get_content(query)
