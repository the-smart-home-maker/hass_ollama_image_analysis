"""Ollama (local AI models) image analysis integration"""

import voluptuous as vol

from homeassistant.core import (
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
import aiohttp

DOMAIN = "ollama_image_analysis"

OLLAMA_IMAGE_ANALYSIS_SERVICE_NAME = "ollama_image_analysis"
OLLAMA_IMAGE_ANALYSIS_SCHEMA = vol.Schema(
    {
        vol.Required("prompt"): str,
        vol.Required("model"): str,
        vol.Required("image_paths"): [str],
    }
)

# Used to determine if a path is an url or a path.
def is_url(path):

    # Check if the path starts with common URL patterns
    if path.startswith("http://") or path.startswith("https://"):
        return True
    else:
        return False

async def read_binary_file(file_name: str) -> bytes:
    try:
        async with aiofiles.open(file_name, "rb") as f:
            return await f.read()
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def fetch_image_from_url(url: str) -> bytes:
    """Fetches an image from a URL and returns it in binary format."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Failed to fetch image from {url}. Status code: {response.status}")
    except Exception as e:
        print(f"An error occurred while fetching the image from {url}: {e}")

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
        image_paths = call.data["image_paths"]
        model = call.data.get("model", "llava")

        host = config_dict["data"]["host"]
        client = AsyncClient(host=host)

        # Will store the b64 encoded images after they're been read
        b64encoded_images = []

        for image_path in image_paths:
            # Determine if the image path is a url or an image path.
            if not is_url(image_path):

                # Read the file as bytes
                image_bytes = await read_binary_file(image_path)
                b64encoded_images.append(await convert_to_base64(image_bytes))
            
            # Otherwise, get the image url
            else:

                # Read the url as bytes
                image_bytes = await fetch_image_from_url(image_path)
                b64encoded_images.append(await convert_to_base64(image_bytes))

        # make the call to ollama
        response = await client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": b64encoded_images,
                },
            ],
        )

        return { "result": response["message"]["content"] }
        

    hass.services.async_register(
        DOMAIN,
        OLLAMA_IMAGE_ANALYSIS_SERVICE_NAME,
        ollama_image_analysis,
        schema=OLLAMA_IMAGE_ANALYSIS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    return True
