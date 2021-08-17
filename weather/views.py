from django.shortcuts import render
import sys

sys.path.append('..')

from utils import config, weather_app
import json


# Create your views here.
def home(request):
    # Handle the city name config
    city_name = request.POST.get('city-name')
    if city_name is None:
        city = config.CITY_NAME
    else:
        city = city_name

    # Obtain the current weather dict
    current_weather_dict = weather_app.CurrentWeather(
        api_key=config.API_KEY
    ).get_current_weather(city_name=city)

    # Obtain the country
    country = weather_app.CurrentWeather(api_key=config.API_KEY).get_country(
        current_weather_dict=current_weather_dict
    )

    # Obtain the current date
    current_date = weather_app.CurrentWeather.get_current_date()

    # Store the results in a dict to be accessed later
    weather = {
        "current_date": current_date,
        "city": city,
        "country": country,
        "temperature": current_weather_dict["main"]["temp"],
        "temp_min": current_weather_dict["main"]["temp_min"],
        "temp_max": current_weather_dict["main"]["temp_max"],
        "description": current_weather_dict["weather"][0]["description"],
        "icon": current_weather_dict["weather"][0]["icon"],
    }

    # Handle the weather forecast dataframe
    # Create the forecast dict
    forecast_dict = weather_app.Forecast(api_key=config.API_KEY).get_forecast_dict(
        city_name=city
    )

    # Create the forecast dict list
    forecast_dict_list = weather_app.Forecast.get_forecast_dict_list(
        forecast_dict=forecast_dict
    )

    # Create the forecast dataframe
    df = weather_app.Forecast.get_forecast_dataframe(
        forecast_dict_list=forecast_dict_list
    )

    # Parse the records into a json format
    json_records = df.reset_index().to_json(orient="records")
    data = json.loads(json_records)

    # Place the weather dict and data dict into context
    context = {"weather": weather, "data": data}

    return render(request, "weather/home.html", context)


def about(request):
    return render(request, "weather/about.html")
