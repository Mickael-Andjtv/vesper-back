import requests
from ddgs import DDGS


class WebSearch:
    def get_context(self, query: str) -> str:
        try:
            results = list(DDGS().text(query, region="fr-fr", max_results=5))
            if not results:
                return "Aucun résultat trouvé sur le web."

            first_result = results[0]
            url = first_result.get("href")
            raw_text = requests.get(f"https://r.jina.ai/{url}", timeout=10).text

            max_characters = 6000
            if len(raw_text) > max_characters:
                return (
                    raw_text[:max_characters]
                    + "\n\n[... Contenu tronqué pour économiser les tokens ...]"
                )

            return raw_text

        except Exception as e:
            raise RuntimeError(f"Error: {str(e)}")
