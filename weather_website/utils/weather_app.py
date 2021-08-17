# Initial Config
import requests
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime


def ordinal(n: int):
    """
    Returns the ordinal word based on the numeral provided.
    """
    return str(n) + (
        "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )


# Functions for retrieving data via the OpenWeather API - https://openweathermap.org/api
class CurrentWeather:
    """
    Class gets the current weather for today's date.

    """

    def __init__(self, api_key: str):
        """
        In order to make API calls with the OpenWeather API, we need a relevant API key.

        Parameters
        ----------
        api_key: str, the api key from OpenWeather.

        """
        self.api_key = api_key

    def get_current_weather(self, city_name: str) -> dict:
        """
        Gets the current weather (for today's date) and returns in a dictionary format.

        Parameters
        ----------
        city_name: str, the name of the city to get weather.

        Returns
        -------
         A dictionary of information of the latest weather.

        """
        # Setting the current weather url
        current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={self.api_key}"

        # Setting the params to get data in a metric format
        params = {"units": "metric"}

        # Make the request
        r = requests.get(url=current_weather_url, params=params)
        current_weather_dict = r.json()

        return current_weather_dict

    @staticmethod
    def get_country(current_weather_dict: dict) -> str:
        """
        Returns the country of the city specified using the latitude and longitude from the
        current_weather_dict.

        Parameters
        ----------
        current_weather_dict: dict, the current weather dict created using the func: get_current_weather.

        Returns
        -------
        A string of the country of the city specified to get the current weather.

        """
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")

        # Get the latitude & longitude
        longitude = str(current_weather_dict["coord"]["lon"])
        latitude = str(current_weather_dict["coord"]["lat"])

        # Get the location
        location = geolocator.reverse(latitude + "," + longitude)

        return location.raw["address"]["country"]

    @staticmethod
    def get_current_date() -> str:
        now = datetime.now()
        day = int(now.strftime("%d"))

        return now.strftime(f"%A {ordinal(day)} %B")


class Forecast(CurrentWeather):
    """
    Class contains functions to retrieve a weather forecast for a given, specified city. This is a subclass
    of CurrentWeather as the both need the param api_key to function.

    """

    def __init__(self, api_key: str):
        """
        In order to make API calls with the OpenWeather API, we need a relevant API key.

        Parameters
        ----------
        api_key: str, the api key from OpenWeather.

        """
        super().__init__(api_key)

    def get_forecast_dict(self, city_name: str):
        """
        Gets the weather forecasted for a given city.

        Parameters
        ----------
        city_name: str, the name of the city to get weather.

        Returns
        -------
        A dictionary of the forecasted weather for the given city.

        """
        # Set the forecasted url
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={self.api_key}"

        # Setting the params to get data in a metric format
        params = {"units": "metric"}

        # Make the request
        r = requests.get(url=forecast_url, params=params)

        return r.json()

    @staticmethod
    def get_forecast_dict_list(forecast_dict: dict) -> list:
        """
        Returns a list of forecasts based on the forecast_dict param provided.

        Parameters
        ----------
        forecast_dict: dict, created from the func get_forecast_dict.

        Returns
        -------
        A list of forecasts

        """
        return forecast_dict["list"]

    @staticmethod
    def get_dt_text(forecast_dict_list: list, item: int, _format: str):
        """
        Retrieves the datetime value of the 'dt_txt' from the forecast_dict param created
        from the func get_forecast_dict.

        Parameters
        ----------
        forecast_dict_list: list, created from the func get_forecast_dict_list.
        item: int, the item number in the forecast_dict to get data for.
        _format: str, the format to return, eg '%d' or '%A'.

        Returns
        -------
        A datetime object with the dt text for a given item number

        """
        return datetime.fromisoformat(forecast_dict_list[item]["dt_txt"]).strftime(
            _format
        )

    @staticmethod
    def obtain_range_list(forecast_dict_list: list):
        """
        Obtains a list of integers that are the indicies of each unique date in the forecast_dict_list param.

        Parameters
        ----------
        forecast_dict_list

        Returns
        -------

        """
        days = []
        indicies = []

        for index, item in enumerate(forecast_dict_list):
            day, index_val = (
                Forecast.get_dt_text(
                    forecast_dict_list=forecast_dict_list,
                    item=index,
                    _format="%d-%m-%Y",
                ),
                index,
            )

            days.append(day)
            indicies.append(index_val)

        days_index_dict = dict(zip(days, indicies))
        return list(days_index_dict.values())

    @staticmethod
    def get_forecast_dataframe(forecast_dict_list: list):
        # Create range_list
        range_list = Forecast.obtain_range_list(forecast_dict_list=forecast_dict_list)

        # Initialise the lists needed to store data
        days = []
        descriptions = []
        temperatures = []
        temperatures_mins = []
        temperatures_maxs = []
        humidities = []

        for item in range_list:
            # Obtain the date
            day = int(Forecast.get_dt_text(forecast_dict_list, item, _format="%d"))
            date = Forecast.get_dt_text(
                forecast_dict_list, item, _format=f"%A {ordinal(day)} %B"
            )
            days.append(date)

            # Obtain the descriptions
            desc = forecast_dict_list[item]["weather"][0]["description"]
            descriptions.append(desc)

            # Obtain the temperature
            temp = forecast_dict_list[item]["main"]["temp"]
            temperatures.append(temp)

            # Obtain the minimum temperatures
            min_temp = forecast_dict_list[item]["main"]["temp_min"]
            temperatures_mins.append(min_temp)

            # Obtain the maximum temperatures
            max_temp = forecast_dict_list[item]["main"]["temp_max"]
            temperatures_maxs.append(max_temp)

            # Obtain the humidity
            humidity = forecast_dict_list[item]["main"]["humidity"]
            humidities.append(humidity)

        # Construct the dataframe
        df = pd.DataFrame(
            columns=["Date", "Description", "Temp", "Min_Temp", "Max_Temp", "Humidity"]
        )

        # Populate the columns
        df["Date"] = days
        df["Description"] = descriptions
        df["Temp"] = temperatures
        df["Min_Temp"] = temperatures_mins
        df["Max_Temp"] = temperatures_maxs
        df["Humidity"] = humidities

        return df
