"""API client for Frontier Silicon devices."""
import asyncio
import logging
from typing import Any, Optional
import xml.etree.ElementTree as ET
from urllib.parse import quote

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FrontierSiliconAPI:
    """API client for Frontier Silicon devices."""

    def __init__(self, host: str, port: int, pin: str) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.pin = pin
        self.session_id: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

        if port == 80:
            self.base_url = f"http://{host}/fsapi"
        else:
            self.base_url = f"http://{host}:{port}/fsapi"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            _LOGGER.debug("Creating aiohttp ClientSession")
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def clear_session(self, context: str = "clear_session") -> None:
        """Forget the FSAPI session id without closing the HTTP client."""
        if self.session_id:
            _LOGGER.info("Clearing FSAPI session; context=%s", context)
        self.session_id = None

    def _mask_url(self, url: str) -> str:
        """Mask pin and sid in logs."""
        masked = url.replace(f"pin={self.pin}", "pin=****")
        if self.session_id:
            masked = masked.replace(f"sid={self.session_id}", f"sid={self.session_id}")
        return masked

    async def _request(self, url: str, timeout: int = 5, context: str = "request") -> tuple[Optional[ET.Element], str]:
        """Make HTTP request and parse XML response."""
        try:
            session = await self._get_session()
            _LOGGER.debug("FSAPI request [%s]: %s", context, self._mask_url(url))
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status != 200:
                    _LOGGER.debug("FSAPI HTTP %d [%s]", response.status, context)
                    return None, ""

                text = await response.text()
                if not text or not text.strip():
                    _LOGGER.debug("FSAPI empty response [%s]", context)
                    return None, ""

                try:
                    root = ET.fromstring(text)
                    _LOGGER.debug("FSAPI XML OK [%s]", context)
                    return root, text
                except ET.ParseError as err:
                    _LOGGER.debug("FSAPI XML parse error [%s]: %s; response=%s", context, err, text[:120])
                    return None, text

        except asyncio.TimeoutError:
            _LOGGER.debug("FSAPI timeout [%s]", context)
            return None, ""
        except aiohttp.ClientError as err:
            _LOGGER.debug("FSAPI connection error [%s]: %s", context, err)
            return None, ""
        except Exception as err:
            _LOGGER.error("FSAPI unexpected request error [%s]: %s", context, err)
            return None, ""

    def _get_status(self, root: Optional[ET.Element]) -> str:
        """Extract status from XML root."""
        if root is None:
            return "XML_PARSE_ERROR"
        status_elem = root.find("status")
        if status_elem is not None and status_elem.text:
            return status_elem.text.strip()
        return "UNKNOWN"

    async def create_session(self, context: str = "create_session") -> Optional[str]:
        """Create a new API session."""
        _LOGGER.warning(
            "FSAPI CREATE_SESSION requested; context=%s. If radio wakes now, this is the trigger.",
            context,
        )
        url = f"{self.base_url}/CREATE_SESSION?pin={self.pin}"
        root, _ = await self._request(url, context=f"CREATE_SESSION:{context}")

        status = self._get_status(root)
        if status == "FS_OK" and root is not None:
            sid_elem = root.find("sessionId")
            if sid_elem is not None and sid_elem.text:
                self.session_id = sid_elem.text.strip()
                _LOGGER.info("FSAPI session created successfully; context=%s", context)
                return self.session_id

        _LOGGER.warning("Failed to create FSAPI session: status=%s; context=%s", status, context)
        return None

    async def _ensure_session(self, allow_create: bool = True, context: str = "ensure_session") -> bool:
        """Ensure we have a valid session."""
        if self.session_id:
            return True
        if not allow_create:
            _LOGGER.debug("No FSAPI session and session creation not allowed; context=%s", context)
            return False
        return await self.create_session(context=context) is not None

    async def get_value(self, path: str, *, allow_session_create: bool = True, context: str = "get_value") -> tuple[Optional[str], str]:
        """GET a scalar value from the device."""
        if not await self._ensure_session(allow_create=allow_session_create, context=context):
            return None, "NO_SESSION"

        url = f"{self.base_url}/GET/{path}?pin={self.pin}&sid={self.session_id}"
        root, _ = await self._request(url, context=context)
        status = self._get_status(root)

        if root is None:
            return None, status

        value_elem = root.find(".//value")
        if value_elem is not None:
            for child in value_elem:
                if child.text is not None:
                    _LOGGER.debug("FSAPI GET %s => %s; status=%s; context=%s", path, child.text, status, context)
                    return child.text, status
            if value_elem.text:
                _LOGGER.debug("FSAPI GET %s => %s; status=%s; context=%s", path, value_elem.text, status, context)
                return value_elem.text, status

        _LOGGER.debug("FSAPI GET %s returned no value; status=%s; context=%s", path, status, context)
        return None, status

    async def set_value(self, path: str, value: str, *, context: str = "set_value") -> str:
        """SET a value on the device."""
        if not await self._ensure_session(allow_create=True, context=context):
            return "NO_SESSION"

        _LOGGER.warning("FSAPI SET %s=%s; context=%s", path, value, context)
        encoded_value = quote(str(value))
        url = f"{self.base_url}/SET/{path}?pin={self.pin}&sid={self.session_id}&value={encoded_value}"
        root, _ = await self._request(url, context=context)
        status = self._get_status(root)

        if status in ("FS_SESSION_TIMEOUT", "FS_INVALID_SID"):
            self.session_id = None
            if await self.create_session(context=f"{context}:retry"):
                url = f"{self.base_url}/SET/{path}?pin={self.pin}&sid={self.session_id}&value={encoded_value}"
                root, _ = await self._request(url, context=f"{context}:retry")
                status = self._get_status(root)

        _LOGGER.info("FSAPI SET result %s=%s; status=%s; context=%s", path, value, status, context)
        return status

    async def list_get_next(self, path: str, max_items: int = 100, *, context: str = "list_get_next") -> list[dict[str, str]]:
        """Get a list of items from the device."""
        if not await self._ensure_session(allow_create=True, context=context):
            return []

        _LOGGER.info("FSAPI LIST_GET_NEXT %s; max_items=%s; context=%s", path, max_items, context)
        url = f"{self.base_url}/LIST_GET_NEXT/{path}/-1?pin={self.pin}&sid={self.session_id}&maxItems={max_items}"
        root, _ = await self._request(url, context=context)

        if root is None:
            return []

        items = []
        for item in root.findall(".//item"):
            item_data = {}
            item_key = item.get("key")
            if item_key is not None:
                item_data["key"] = item_key

            for field in item.findall("field"):
                name = field.get("name", "")
                for value_type in ("c8_array", "u8", "u16", "u32", "s8", "s16", "s32"):
                    v = field.find(value_type)
                    if v is not None and v.text is not None:
                        item_data[name] = v.text
                        break
            items.append(item_data)

        _LOGGER.info("FSAPI LIST_GET_NEXT %s returned %d items; context=%s", path, len(items), context)
        return items

    async def get_device_info(self) -> dict[str, Any]:
        """Get device information."""
        info = {}
        info["name"], _ = await self.get_value("netRemote.sys.info.friendlyName", context="device_info:name")
        info["version"], _ = await self.get_value("netRemote.sys.info.version", context="device_info:version")
        info["radio_id"], _ = await self.get_value("netRemote.sys.info.radioId", context="device_info:radio_id")
        return info

    async def get_modes(self) -> list[dict[str, str]]:
        """Get available modes/input sources."""
        return await self.list_get_next("netRemote.sys.caps.validModes", context="get_modes")

    async def get_presets(self) -> list[dict[str, str]]:
        """Get saved presets/favorites for the current mode."""
        _LOGGER.warning("FSAPI preset read changes navigation state first; this may wake/change some radios")
        await self.set_value("netRemote.nav.state", "1", context="get_presets:navigate")
        await asyncio.sleep(0.3)
        presets = await self.list_get_next("netRemote.nav.presets", max_items=40, context="get_presets:list")
        _LOGGER.info("Found %d presets", len(presets))
        return presets

    async def power_on(self) -> bool:
        """Turn device on."""
        status = await self.set_value("netRemote.sys.power", "1", context="power_on")
        return status == "FS_OK"

    async def power_off(self) -> bool:
        """Turn device off."""
        status = await self.set_value("netRemote.sys.power", "0", context="power_off")
        if status == "FS_OK":
            await self.clear_session(context="power_off")
        return status == "FS_OK"

    async def set_volume(self, level: int) -> bool:
        status = await self.set_value("netRemote.sys.audio.volume", str(level), context=f"set_volume:{level}")
        return status == "FS_OK"

    async def mute(self) -> bool:
        status = await self.set_value("netRemote.sys.audio.mute", "1", context="mute")
        return status == "FS_OK"

    async def unmute(self) -> bool:
        status = await self.set_value("netRemote.sys.audio.mute", "0", context="unmute")
        return status == "FS_OK"

    async def set_mode(self, mode_id: str) -> bool:
        status = await self.set_value("netRemote.sys.mode", mode_id, context=f"set_mode:{mode_id}")
        return status == "FS_OK"

    async def select_preset(self, preset_key: str) -> bool:
        status = await self.set_value("netRemote.nav.action.selectPreset", preset_key, context=f"select_preset:{preset_key}")
        return status == "FS_OK"

    async def play(self) -> bool:
        status = await self.set_value("netRemote.play.control", "1", context="play")
        return status == "FS_OK"

    async def pause(self) -> bool:
        status = await self.set_value("netRemote.play.control", "2", context="pause")
        return status == "FS_OK"

    async def stop(self) -> bool:
        status = await self.set_value("netRemote.play.control", "0", context="stop")
        return status == "FS_OK"

    async def next_track(self) -> bool:
        status = await self.set_value("netRemote.play.control", "3", context="next_track")
        return status == "FS_OK"

    async def previous_track(self) -> bool:
        status = await self.set_value("netRemote.play.control", "4", context="previous_track")
        return status == "FS_OK"
