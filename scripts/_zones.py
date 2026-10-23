"""City and time zone names shared by time tasks. Not a task."""
CITY = {"london": "Europe/London", "paris": "Europe/Paris", "berlin": "Europe/Berlin", "madrid": "Europe/Madrid", "rome": "Europe/Rome",
        "moscow": "Europe/Moscow", "istanbul": "Europe/Istanbul", "dubai": "Asia/Dubai", "abu dhabi": "Asia/Dubai", "riyadh": "Asia/Riyadh",
        "mumbai": "Asia/Kolkata", "delhi": "Asia/Kolkata", "new delhi": "Asia/Kolkata", "kolkata": "Asia/Kolkata", "bangalore": "Asia/Kolkata",
        "bengaluru": "Asia/Kolkata", "chennai": "Asia/Kolkata", "hyderabad": "Asia/Kolkata", "pune": "Asia/Kolkata", "india": "Asia/Kolkata",
        "ist": "Asia/Kolkata", "karachi": "Asia/Karachi", "dhaka": "Asia/Dhaka", "kathmandu": "Asia/Kathmandu", "colombo": "Asia/Colombo",
        "bangkok": "Asia/Bangkok", "singapore": "Asia/Singapore", "hong kong": "Asia/Hong_Kong", "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai", "tokyo": "Asia/Tokyo", "japan": "Asia/Tokyo", "seoul": "Asia/Seoul", "sydney": "Australia/Sydney",
        "melbourne": "Australia/Melbourne", "auckland": "Pacific/Auckland", "cairo": "Africa/Cairo", "nairobi": "Africa/Nairobi",
        "lagos": "Africa/Lagos", "johannesburg": "Africa/Johannesburg", "new york": "America/New_York", "washington": "America/New_York",
        "toronto": "America/Toronto", "chicago": "America/Chicago", "denver": "America/Denver", "los angeles": "America/Los_Angeles",
        "san francisco": "America/Los_Angeles", "seattle": "America/Los_Angeles", "mexico city": "America/Mexico_City",
        "sao paulo": "America/Sao_Paulo", "utc": "UTC", "gmt": "UTC"}


def zone_name(text):
    t = " ".join(text.lower().split())
    if t in CITY:
        return CITY[t]
    if "/" in t:
        return "/".join(p.title() if p.lower() != "utc" else "UTC" for p in t.replace(" ", "_").split("/"))
    return None
