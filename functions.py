def calculate_daily_consumption(power_rating, usage_hours):
    return power_rating * usage_hours / 1000


def get_monthly_consumption(total_daily_units):
    return total_daily_units * 30


rate_per_unit = 50


def get_cost(monthly_units):
    return monthly_units * rate_per_unit


def give_advice(monthly_units):

    if monthly_units <= 50:
        return "Low consumption"

    elif monthly_units <= 100:
        return "Medium consumption"

    else:
        return "High consumption"


def find_highest_consuming_appliance(appliances):

    if not appliances:
        return None, 0, "No appliances found."

    high = 0
    high_appliance = ""

    for appliance in appliances:

        daily = appliance.daily_units

        if daily > high:
            high = daily
            high_appliance = appliance.appliance

    threshold = 8

    if high > threshold:
        advice = "is consuming unusually high energy."

    else:
        advice = "consumption is within a reasonable range."

    return high_appliance, high, advice