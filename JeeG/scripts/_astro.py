"""Sunrise/sunset and moon phase maths (no internet). Not a task."""
import datetime
import math

PLACES = {  # name: (latitude, longitude, time zone)
    "delhi": (28.6139, 77.2090, "Asia/Kolkata"), "new delhi": (28.6139, 77.2090, "Asia/Kolkata"),
    "mumbai": (19.0760, 72.8777, "Asia/Kolkata"), "kolkata": (22.5726, 88.3639, "Asia/Kolkata"),
    "chennai": (13.0827, 80.2707, "Asia/Kolkata"), "bangalore": (12.9716, 77.5946, "Asia/Kolkata"),
    "bengaluru": (12.9716, 77.5946, "Asia/Kolkata"), "hyderabad": (17.3850, 78.4867, "Asia/Kolkata"),
    "pune": (18.5204, 73.8567, "Asia/Kolkata"), "ahmedabad": (23.0225, 72.5714, "Asia/Kolkata"),
    "jaipur": (26.9124, 75.7873, "Asia/Kolkata"), "lucknow": (26.8467, 80.9462, "Asia/Kolkata"),
    "patna": (25.5941, 85.1376, "Asia/Kolkata"), "bhopal": (23.2599, 77.4126, "Asia/Kolkata"),
    "chandigarh": (30.7333, 76.7794, "Asia/Kolkata"), "kochi": (9.9312, 76.2673, "Asia/Kolkata"),
    "guwahati": (26.1445, 91.7362, "Asia/Kolkata"), "varanasi": (25.3176, 82.9739, "Asia/Kolkata"),
    "london": (51.5074, -0.1278, "Europe/London"), "paris": (48.8566, 2.3522, "Europe/Paris"),
    "dubai": (25.2048, 55.2708, "Asia/Dubai"), "singapore": (1.3521, 103.8198, "Asia/Singapore"),
    "tokyo": (35.6762, 139.6503, "Asia/Tokyo"), "sydney": (-33.8688, 151.2093, "Australia/Sydney"),
    "new york": (40.7128, -74.0060, "America/New_York"), "los angeles": (34.0522, -118.2437, "America/Los_Angeles"),
    "san francisco": (37.7749, -122.4194, "America/Los_Angeles"), "toronto": (43.6532, -79.3832, "America/Toronto"),
    "karachi": (24.8607, 67.0011, "Asia/Karachi"), "dhaka": (23.8103, 90.4125, "Asia/Dhaka"),
    "kathmandu": (27.7172, 85.3240, "Asia/Kathmandu"), "colombo": (6.9271, 79.8612, "Asia/Colombo"),
    "moscow": (55.7558, 37.6173, "Europe/Moscow"), "berlin": (52.5200, 13.4050, "Europe/Berlin"),
}


def sun_times(date, lat, lon):
    """(sunrise_utc, sunset_utc) as datetimes, or (None, 'polar day'/'polar night')."""
    n = (date.toordinal() - datetime.date(2000, 1, 1).toordinal()) + 0.0008        # days since J2000 (noon UTC, 2000-01-01)
    jstar = n - lon / 360.0
    m = math.radians((357.5291 + 0.98560028 * jstar) % 360)
    c = 1.9148 * math.sin(m) + 0.0200 * math.sin(2 * m) + 0.0003 * math.sin(3 * m)
    lam = math.radians((math.degrees(m) + c + 180 + 102.9372) % 360)
    transit = jstar + 0.0053 * math.sin(m) - 0.0069 * math.sin(2 * lam)
    sin_dec = math.sin(lam) * math.sin(math.radians(23.4397))
    dec = math.asin(sin_dec)
    phi = math.radians(lat)
    cosw = (math.sin(math.radians(-0.833)) - math.sin(phi) * sin_dec) / (math.cos(phi) * math.cos(dec))
    if cosw > 1:
        return None, "polar night"
    if cosw < -1:
        return None, "polar day"
    w0 = math.degrees(math.acos(cosw))
    base = datetime.datetime(2000, 1, 1, 12, tzinfo=datetime.timezone.utc)
    return (base + datetime.timedelta(days=transit - w0 / 360.0),
            base + datetime.timedelta(days=transit + w0 / 360.0))


SYNODIC = 29.530588853
NEW_MOON_REF = datetime.datetime(2000, 1, 6, 18, 14, tzinfo=datetime.timezone.utc)


def moon_age(when_utc):
    return ((when_utc - NEW_MOON_REF).total_seconds() / 86400.0) % SYNODIC


def moon_info(when_utc):
    age = moon_age(when_utc)
    illum = (1 - math.cos(2 * math.pi * age / SYNODIC)) / 2
    names = [(1.85, "New moon"), (7.38, "Waxing crescent"), (9.23, "First quarter"), (13.84, "Waxing gibbous"),
             (15.69, "Full moon"), (20.30, "Waning gibbous"), (22.15, "Last quarter"), (27.68, "Waning crescent"), (99, "New moon")]
    name = next(n for lim, n in names if age < lim)
    return age, illum, name


def next_phase(when_utc, target_age):
    """Next time the moon reaches target_age (0 = new, ~14.77 = full), approximately."""
    age = moon_age(when_utc)
    d = (target_age - age) % SYNODIC
    return when_utc + datetime.timedelta(days=d)
