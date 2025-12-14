"""Constants for the My Frontier Silicon integration."""

DOMAIN = "my_frontier_silicon"
DEFAULT_PORT = 80
DEFAULT_PIN = "1234"
DEFAULT_NAME = "Frontier Silicon Radio"

# Config flow
CONF_PIN = "pin"

# Update intervals
SCAN_INTERVAL = 30  # seconds
SESSION_REFRESH_INTERVAL = 540  # 9 minutes (sessions last ~10 min)

# Endpoints
ENDPOINT_CREATE_SESSION = "CREATE_SESSION"
ENDPOINT_POWER = "netRemote.sys.power"
ENDPOINT_MODE = "netRemote.sys.mode"
ENDPOINT_VOLUME = "netRemote.sys.audio.volume"
ENDPOINT_MUTE = "netRemote.sys.audio.mute"
ENDPOINT_PLAY_CONTROL = "netRemote.play.control"
ENDPOINT_PLAY_STATUS = "netRemote.play.status"
ENDPOINT_PLAY_INFO_NAME = "netRemote.play.info.name"
ENDPOINT_PLAY_INFO_TEXT = "netRemote.play.info.text"
ENDPOINT_PLAY_INFO_ARTIST = "netRemote.play.info.artist"
ENDPOINT_PLAY_INFO_ALBUM = "netRemote.play.info.album"
ENDPOINT_PLAY_INFO_GRAPHIC = "netRemote.play.info.graphicUri"
ENDPOINT_DEVICE_NAME = "netRemote.sys.info.friendlyName"
ENDPOINT_DEVICE_VERSION = "netRemote.sys.info.version"
ENDPOINT_VALID_MODES = "netRemote.sys.caps.validModes"
ENDPOINT_VOLUME_STEPS = "netRemote.sys.caps.volumeSteps"
ENDPOINT_PRESETS = "netRemote.nav.presets"
ENDPOINT_SELECT_PRESET = "netRemote.nav.action.selectPreset"
ENDPOINT_EQ_PRESET = "netRemote.sys.audio.eqPreset"
ENDPOINT_SLEEP = "netRemote.sys.sleep"
ENDPOINT_NAV_LIST = "netRemote.nav.list"

# Play control values
PLAY_CONTROL_STOP = "0"
PLAY_CONTROL_PLAY = "1"
PLAY_CONTROL_PAUSE = "2"
PLAY_CONTROL_NEXT = "3"
PLAY_CONTROL_PREV = "4"

# Play status values
PLAY_STATUS_STOPPED = "0"
PLAY_STATUS_BUFFERING = "1"
PLAY_STATUS_PLAYING = "2"
PLAY_STATUS_PAUSED = "3"

# Mode IDs (common across Frontier Silicon devices)
MODE_INTERNET_RADIO = "0"
MODE_PODCASTS = "1"
MODE_SPOTIFY = "2"
MODE_DAB = "3"
MODE_FM = "4"
MODE_BLUETOOTH = "5"
MODE_CD = "6"
MODE_USB = "7"
MODE_AUX = "8"

# Attribute names
ATTR_STATION = "station"
ATTR_MODE = "mode"
ATTR_PRESETS = "presets"
ATTR_EQ_PRESET = "eq_preset"
