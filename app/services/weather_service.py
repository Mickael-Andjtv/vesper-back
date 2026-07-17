import requests


class WeatherError(RuntimeError): ...


class Weather:
    def get_weather(self, city: str):
        try:
            url = f"https://wttr.in/{city}?lang=fr&format=j1"
            headers = {"User-Agent": "curl/7.81.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                raise WeatherError("Error fetching weather data.")

            data = response.json()
            current = data["current_condition"][0]
            return current
        except Exception as e:
            raise WeatherError(f"Erreur inattendue : {str(e)}")
