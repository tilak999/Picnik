from typing import Any

from geopy.geocoders import Nominatim
from pydantic import BaseModel

from app.internal.helper.base_service import BaseServiceClass


class GPS(BaseModel):
    GPSLatitudeRef: str
    GPSLatitude: tuple
    GPSLongitudeRef: str
    GPSLongitude: tuple


class LocationService(BaseServiceClass):
    def __init__(self) -> None:
        super().__init__(name=__name__)

    def _convert_to_degrees(self, value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def parse(self, gps_tags: dict[str, float]):
        if "GPSInfo" in gps_tags.keys():
            gps = GPS.model_validate(gps_tags["GPSInfo"])
            gps_latitude = gps.GPSLatitude
            gps_latitude_ref = gps.GPSLatitudeRef
            gps_longitude = gps.GPSLongitude
            gps_longitude_ref = gps.GPSLongitudeRef
            lat = self._convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat *= -1
            lon = self._convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon *= -1
            return {"lat": lat, "long": lon}
        return None

    async def get_address(self, exif: dict) -> dict[str, Any]:
        geolocator = Nominatim(user_agent="picnik")
        lat_lon = self.parse(exif)
        out = {}
        if lat_lon is not None:
            lat = lat_lon["lat"]
            lon = lat_lon["long"]
            result = geolocator.reverse(f"{lat}, {lon}")
            location = result.raw  # type: ignore
            out = location["address"] if "address" in location.keys() else {}
        self.logger.debug("address: %s", out)
        return out
