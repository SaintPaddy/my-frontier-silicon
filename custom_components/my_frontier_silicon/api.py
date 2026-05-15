"""API client for Frontier Silicon devices."""
import logging
from typing import Any, Optional
import xml.etree.ElementTree as ET
from urllib.parse import quote

import aiohttp
import asyncio

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
        
        # Build base URL without :80 if port is 80
        if port == 80:
            self.base_url = f"http://{host}/fsapi"
        else:
            self.base_url = f"http://{host}:{port}/fsapi"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, url: str, timeout: int = 5) -> tuple[Optional[ET.Element], str]:
        """Make HTTP request and parse XML response."""
        try:
            session = await self._get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                # Check response status
                if response.status != 200:
                    _LOGGER.debug("HTTP %d for %s", response.status, url)
                    return None, ""
                
                text = await response.text()
                
                # Check for empty response
                if not text or not text.strip():
                    _LOGGER.debug("Empty response from device")
                    return None, ""
                
                # Try to parse XML
                try:
                    root = ET.fromstring(text)
                    return root, text
                except ET.ParseError as err:
                    # Only log at debug level - this is common when radio is in standby
                    _LOGGER.debug("XML parse error: %s (response: %s)", err, text[:100])
                    return None, text
                    
        except asyncio.TimeoutError:
            _LOGGER.debug("Request timeout: %s", url)
            return None, ""
        except aiohttp.ClientError as err:
            _LOGGER.debug("Connection error: %s", err)
            return None, ""
        except Exception as err:
            # Only log unexpected errors at error level
            _LOGGER.error("Unexpected request error: %s", err)
            return None, ""

    def _get_status(self, root: Optional[ET.Element]) -> str:
        """Extract status from XML root."""
        if root is None:
            return "XML_PARSE_ERROR"
        status_elem = root.find("status")
        if status_elem is not None and status_elem.text:
            return status_elem.text.strip()
        return "UNKNOWN"

    async def create_session(self) -> Optional[str]:
        """Create a new API session."""
        url = f"{self.base_url}/CREATE_SESSION?pin={self.pin}"
        root, _ = await self._request(url)
        
        status = self._get_status(root)
        if status == "FS_OK" and root is not None:
            sid_elem = root.find("sessionId")
            if sid_elem is not None and sid_elem.text:
                self.session_id = sid_elem.text.strip()
                _LOGGER.debug("Session created: %s", self.session_id)
                return self.session_id
        
        _LOGGER.error("Failed to create session: %s", status)
        return None

    async def _ensure_session(self) -> bool:
        """Ensure we have a valid session."""
        if self.session_id:
            return True
        return await self.create_session() is not None

    async def get_value(self, path: str) -> tuple[Optional[str], str]:
        """GET a scalar value from the device."""
        if not await self._ensure_session():
            return None, "NO_SESSION"

        url = f"{self.base_url}/GET/{path}?pin={self.pin}&sid={self.session_id}"
        root, _ = await self._request(url)
        status = self._get_status(root)

        if root is None:
            return None, status

        # Extract value from various possible formats
        value_elem = root.find(".//value")
        if value_elem is not None:
            # Try child elements first (u8, u32, c8_array, etc.)
            for child in value_elem:
                if child.text is not None:
                    return child.text, status
            # Try direct text
            if value_elem.text:
                return value_elem.text, status

        return None, status

    async def set_value(self, path: str, value: str) -> str:
        """SET a value on the device."""
        if not await self._ensure_session():
            return "NO_SESSION"

        encoded_value = quote(str(value))
        url = f"{self.base_url}/SET/{path}?pin={self.pin}&sid={self.session_id}&value={encoded_value}"
        root, _ = await self._request(url)
        status = self._get_status(root)

        # Handle session expiration
        if status in ("FS_SESSION_TIMEOUT", "FS_INVALID_SID"):
            self.session_id = None
            if await self.create_session():
                url = f"{self.base_url}/SET/{path}?pin={self.pin}&sid={self.session_id}&value={encoded_value}"
                root, _ = await self._request(url)
                status = self._get_status(root)

        return status

    async def list_get_next(self, path: str, max_items: int = 100) -> list[dict[str, str]]:
        """Get a list of items from the device."""
        if not await self._ensure_session():
            return []

        url = f"{self.base_url}/LIST_GET_NEXT/{path}/-1?pin={self.pin}&sid={self.session_id}&maxItems={max_items}"
        root, _ = await self._request(url)

        if root is None:
            return []

        items = []
        for item in root.findall(".//item"):
            item_data = {}
            
            # Get key attribute
            item_key = item.get("key")
            if item_key is not None:
                item_data["key"] = item_key

            # Get field values
            for field in item.findall("field"):
                name = field.get("name", "")
                # Try different value types
                for value_type in ("c8_array", "u8", "u16", "u32", "s8", "s16", "s32"):
                    v = field.find(value_type)
                    if v is not None and v.text is not None:
                        item_data[name] = v.text
                        break

            items.append(item_data)

        return items

    async def get_device_info(self) -> dict[str, Any]:
        """Get device information."""
        info = {}
        info["name"], _ = await self.get_value("netRemote.sys.info.friendlyName")
        info["version"], _ = await self.get_value("netRemote.sys.info.version")
        info["radio_id"], _ = await self.get_value("netRemote.sys.info.radioId")
        return info

    async def get_modes(self) -> list[dict[str, str]]:
        """Get available modes/input sources."""
        return await self.list_get_next("netRemote.sys.caps.validModes")

    async def get_presets(self) -> list[dict[str, str]]:
        """Get saved presets/favorites."""
        # Navigate to preset list first (fixes FS_NODE_BLOCKED)
        _LOGGER.debug("Navigating to preset list")
        await self.set_value("netRemote.nav.state", "1")
        
        # Give radio time to update navigation state
        await asyncio.sleep(0.3)
        
        # Now fetch presets
        presets = await self.list_get_next("netRemote.nav.presets", max_items=40)
        
        _LOGGER.debug("Found %d presets", len(presets))
        return presets

    async def power_on(self) -> bool:
        """Turn device on."""
        status = await self.set_value("netRemote.sys.power", "1")
        return status == "FS_OK"

    async def power_off(self) -> bool:
        """Turn device off."""
        status = await self.set_value("netRemote.sys.power", "0")
        return status == "FS_OK"

    async def set_volume(self, level: int) -> bool:
        """Set volume level."""
        status = await self.set_value("netRemote.sys.audio.volume", str(level))
        return status == "FS_OK"

    async def mute(self) -> bool:
        """Mute the device."""
        status = await self.set_value("netRemote.sys.audio.mute", "1")
        return status == "FS_OK"

    async def unmute(self) -> bool:
        """Unmute the device."""
        status = await self.set_value("netRemote.sys.audio.mute", "0")
        return status == "FS_OK"

    async def set_mode(self, mode_id: str) -> bool:
        """Set input source mode."""
        status = await self.set_value("netRemote.sys.mode", mode_id)
        return status == "FS_OK"

    async def select_preset(self, preset_key: str) -> bool:
        """Select a preset/favorite."""
        status = await self.set_value("netRemote.nav.action.selectPreset", preset_key)
        return status == "FS_OK"

    async def play(self) -> bool:
        """Start playback."""
        status = await self.set_value("netRemote.play.control", "1")
        return status == "FS_OK"

    async def pause(self) -> bool:
        """Pause playback."""
        status = await self.set_value("netRemote.play.control", "2")
        return status == "FS_OK"

    async def stop(self) -> bool:
        """Stop playback."""
        status = await self.set_value("netRemote.play.control", "0")
        return status == "FS_OK"

    async def next_track(self) -> bool:
        """Skip to next track."""
        status = await self.set_value("netRemote.play.control", "3")
        return status == "FS_OK"

    async def previous_track(self) -> bool:
        """Skip to previous track."""
        status = await self.set_value("netRemote.play.control", "4")
        return status == "FS_OK"
