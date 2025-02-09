from framework.tool_calling import openai_function_wrapper
import random
import math
from typing import List, Dict, Optional
from datetime import datetime, timedelta


@openai_function_wrapper(
    funct_descript="Get the weather forecast for a specific location and day",
    param_descript={
        "day": "The day to check the weather for",
        "location": "The location to check the weather for"
    }
)
def weather(day: str, location: str) -> str:
    """Simulated weather forecast"""
    conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy", "snowy"]
    temps = range(0, 35)
    return f"The weather on {day} in {location} will be {random.choice(conditions)} with a temperature of {random.choice(temps)}°C"


@openai_function_wrapper(
    funct_descript="Convert between different units of measurement",
    param_descript={
        "value": "The numeric value to convert",
        "from_unit": "The unit to convert from (e.g., km, mi, kg, lb, c, f)",
        "to_unit": "The unit to convert to (e.g., km, mi, kg, lb, c, f)"
    },
    enum_parameters={
        "from_unit": ["km", "mi", "kg", "lb", "c", "f"],
        "to_unit": ["km", "mi", "kg", "lb", "c", "f"]
    }
)
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between different units of measurement"""
    conversions = {
        ("km", "mi"): lambda x: x * 0.621371,
        ("mi", "km"): lambda x: x * 1.60934,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x * 0.453592,
        ("c", "f"): lambda x: (x * 9 / 5) + 32,
        ("f", "c"): lambda x: (x - 32) * 5 / 9
    }

    if (from_unit, to_unit) in conversions:
        result = conversions[(from_unit, to_unit)](value)
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    else:
        return f"Conversion from {from_unit} to {to_unit} is not supported"


@openai_function_wrapper(
    funct_descript="Calculate trip duration and estimated arrival time",
    param_descript={
        "distance": "Distance in kilometers",
        "speed": "Average speed in km/h",
        "start_time": "Start time in HH:MM format",
        "breaks": "Number of 15-minute breaks to take (optional)",
    }
)
def calculate_trip(distance: float, speed: float, start_time: str, breaks: int = 0) -> str:
    """Calculate trip duration and arrival time"""
    try:
        # Calculate base duration in hours
        duration_hours = distance / speed

        # Add break time
        total_break_time = breaks * 0.25  # Convert 15-minute breaks to hours
        total_duration = duration_hours + total_break_time

        # Calculate arrival time
        start_dt = datetime.strptime(start_time, "%H:%M")
        duration_td = timedelta(hours=total_duration)
        arrival_dt = start_dt + duration_td

        # Format results
        duration_hrs = math.floor(total_duration)
        duration_mins = round((total_duration - duration_hrs) * 60)

        return (f"Trip Summary:\n"
                f"- Distance: {distance:.1f} km\n"
                f"- Average Speed: {speed} km/h\n"
                f"- Number of breaks: {breaks} ({breaks * 15} minutes total)\n"
                f"- Duration: {duration_hrs} hours and {duration_mins} minutes\n"
                f"- Start Time: {start_time}\n"
                f"- Estimated Arrival: {arrival_dt.strftime('%H:%M')}")
    except ValueError:
        return "Error: Please provide time in HH:MM format"


@openai_function_wrapper(
    funct_descript="Analyze text and provide statistics",
    param_descript={
        "text": "The text to analyze",
        "include_word_count": "Whether to include word count in analysis",
        "include_char_count": "Whether to include character count in analysis",
        "include_sentence_count": "Whether to include sentence count in analysis"
    }
)
def analyze_text(
        text: str,
        include_word_count: bool = True,
        include_char_count: bool = True,
        include_sentence_count: bool = True
) -> str:
    """Analyze text and provide various statistics"""
    results = []

    if include_word_count:
        words = len(text.split())
        results.append(f"Word count: {words}")

    if include_char_count:
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))
        results.append(f"Character count: {chars} (without spaces: {chars_no_spaces})")

    if include_sentence_count:
        # Simple sentence counting - splits on ., ! and ?
        sentences = len([s for s in text.split('.') if s.strip()])
        results.append(f"Approximate sentence count: {sentences}")

    return "\n".join(results)
