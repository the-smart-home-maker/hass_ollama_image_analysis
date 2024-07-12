"""AI image analysis integration"""

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

DOMAIN = "ai_image_analysis"

AI_IMAGE_ANALYSIS_SERVICE_NAME = "ai_image_analysis"
AI_IMAGE_ANALYSIS_SCHEMA = vol.Schema(
    {
        vol.Required("prompt"): str,
        vol.Required("model"): str,
        vol.Required("image_path"): str,
    }
)


async def read_binary_file(file_name):
    try:
        async with aiofiles.open(file_name, "r") as f:
            return await f.read()
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Setup up a config entry."""

    async def ai_image_analysis(call: ServiceCall) -> ServiceResponse:
        config_dict = config.as_dict()

        # load the call parameters
        prompt = call.data["prompt"]
        image_path = call.data["image_path"]
        model = call.data.get("model", "llava")

        host = config_dict["data"]["host"]

        client = AsyncClient(host=host)

        binary_image = await read_binary_file("/workspaces/hass_core" + image_path)

        # b64encoded_binary_image = await pybase64.b64encode(binary_image)

        # make the call to ollama
        response = await client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "image": binary_image,
                },
            ],
        )

        print("Rückmeldung von Modell: ", response["message"]["content"])

        return {
            "items": [
                {
                    "result": response["message"]["content"],
                }
            ],
        }

    hass.services.async_register(
        DOMAIN,
        AI_IMAGE_ANALYSIS_SERVICE_NAME,
        ai_image_analysis,
        schema=AI_IMAGE_ANALYSIS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    return True
