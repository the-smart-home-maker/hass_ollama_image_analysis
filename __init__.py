"""Ollama (local AI models) image analysis integration"""

import voluptuous as vol

from homeassistant.core import (
    Config,
    HomeAssistant,
    ServiceCall,
    SupportsResponse,
    ServiceResponse,
)

from homeassistant.config_entries import ConfigEntry

from ollama import AsyncClient

import pybase64
import aiofiles
import asyncio

DOMAIN = "ollama_image_analysis"

OLLAMA_IMAGE_ANALYSIS_SERVICE_NAME = "ollama_image_analysis"
OLLAMA_IMAGE_ANALYSIS_SCHEMA = vol.Schema(
    {
        vol.Required("prompt"): str,
        vol.Required("model"): str,
        vol.Required("image_path"): str,
    }
)


async def read_binary_file(file_name: str) -> bytes:
    try:
        async with aiofiles.open(file_name, "rb") as f:
            return await f.read()
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def convert_to_base64(input_bytes: bytes) -> str:
    # Simulate an asynchronous operation
    await asyncio.sleep(0)

    # Encode the bytes to Base64
    base64_bytes = pybase64.b64encode(input_bytes)

    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Setup up a config entry."""

    async def ollama_image_analysis(call: ServiceCall) -> ServiceResponse:
        config_dict = config.as_dict()

        # load the call parameters
        prompt = call.data["prompt"]
        image_path = call.data["image_path"]
        model = call.data.get("model", "llava")

        host = config_dict["data"]["host"]

        client = AsyncClient(host=host)

        image_bytes = await read_binary_file("/workspaces/hass_core" + image_path)

        b64encoded_image = await convert_to_base64(image_bytes)

        # make the call to ollama
        response = await client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [b64encoded_image],
                },
            ],
        )

        return {
            "items": [
                {
                    "result": response["message"]["content"],
                }
            ],
        }

    hass.services.async_register(
        DOMAIN,
        OLLAMA_IMAGE_ANALYSIS_SERVICE_NAME,
        ollama_image_analysis,
        schema=OLLAMA_IMAGE_ANALYSIS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    return True
