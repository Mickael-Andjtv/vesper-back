import webbrowser
import subprocess
import urllib.parse

from .audio_service import PlayMusic


def execute_vesper_action(action: str, action_data: str) -> str | PlayMusic:

    if action == "none":
        return "Aucune action requise."

    try:
        if action == "play_music":
            return PlayMusic(action_data)

        elif action == "web_search":
            query = urllib.parse.quote(action_data)
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Recherche Google ouverte pour : {action_data}"

        elif action == "start_timer":
            subprocess.run(
                [
                    "notify-send",
                    "Vesper Timer",
                    f"Minuteur lancé pour {action_data}",
                    "-i",
                    "alarm",
                ]
            )
            return f"Minuteur programmé pour : {action_data}"

        elif action == "show_code":
            return "Code prêt à être affiché."

        elif action == "get_weather":
            city = urllib.parse.quote(action_data) if action_data else ""
            url = f"https://wttr.in/{city}"
            webbrowser.open(url)
            return f"Météo affichée pour : {action_data or 'votre position'}"

        else:
            return f"Action '{action}' non reconnue par le système."

    except Exception as e:
        return f"Échec de l'exécution de l'action {action} : {str(e)}"
