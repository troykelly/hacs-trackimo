"""Constants for the Trackimo integration."""

DOMAIN = "trackimo"

INTEGRATION_VERSION = "0.0.21"

TRACKIMO_CLIENTID = "943f9b0f-73c8-4435-8801-0260db687f05"
TRACKIMO_CLIENTSECRET = "96ca64b0ae5f7005fd18387a28019615"

TRACKER_UPDATE = f"{DOMAIN}_tracker_update"

CONF_MAX_ACCURACY = "max_accuracy"
CONF_SKIP_ACCURACY_ON = "skip_accuracy_filter_on"

ATTR_ACCURACY = "accuracy"
ATTR_ADDRESS = "address"
ATTR_AGE = "age"
ATTR_COUNTRY = "country"
ATTR_CITY = "city"
ATTR_STATE = "state"
ATTR_REGION = "region"
ATTR_STREET = "street"
ATTR_ALTITUDE = "altitude"
ATTR_BATTERY = "batt"
ATTR_BEARING = "bearing"
ATTR_CATEGORY = "category"
ATTR_GEOFENCE = "geofence"
ATTR_ID = "id"
ATTR_LATITUDE = "lat"
ATTR_LONGITUDE = "lon"
ATTR_MOTION = "motion"
ATTR_SPEED = "speed"
ATTR_SPEEDMPS = "mps"
ATTR_STATUS = "status"
ATTR_TIMESTAMP = "timestamp"
ATTR_ATTRIBUTION = "attribution"

EVENT_DEVICE_MOVING = "device_moving"
EVENT_COMMAND_RESULT = "command_result"
EVENT_DEVICE_FUEL_DROP = "device_fuel_drop"
EVENT_GEOFENCE_ENTER = "geofence_enter"
EVENT_DEVICE_OFFLINE = "device_offline"
EVENT_GEOFENCE_EXIT = "geofence_exit"
EVENT_DEVICE_OVERSPEED = "device_overspeed"
EVENT_DEVICE_ONLINE = "device_online"
EVENT_DEVICE_STOPPED = "device_stopped"
EVENT_MAINTENANCE = "maintenance"
EVENT_ALARM = "alarm"
EVENT_TEXT_MESSAGE = "text_message"
EVENT_DEVICE_UNKNOWN = "device_unknown"
EVENT_ALL_EVENTS = "all_events"

MANUFACTURER = "trackimo"