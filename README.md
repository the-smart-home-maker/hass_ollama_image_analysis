# Local (in your network) AI image analysis with Ollama AI models from within Home Assistant

## Introduction

This Home Assistant custom component allows you to locally call your local Ollama instance and infer AI models locally. The component especially focusses on AI image analysis. You can pass in an image, for example from your security camera, to analyze it. The component provides a Home Assistant service that you can include in your automations.

## Installation

### Installing Ollama

Before installing the custom component in Home Assistant, you should have an Ollama instance running in your local network serving the Ollama REST API. Also, you should have already downloaded the model you want to use (e.g. llava). 

One thing is important: As the Ollama instance will most likely not run on the same machine as Home Assistant, you need to make sure that the Ollama API can be accessed not only via localhost but also via IP address. On Mac OS, for example, you have to set an environment variable to do so. This environment variable needs to be set BEFORE you start Ollama, i.e. if you have already started Ollama please make sure to close it, set the environment variable and then open it again.

```
launchctl setenv OLLAMA_HOST 0.0.0.0:11434
```

Once you have installed Ollama and configured the environment variable, you can just run for example to run Ollama with llava as a model:

```
ollama run llava
```
More details can be found here: https://github.com/ollama/ollama

### Installing the custom component in Home Assistant

The easiest way to install this Home Assistant custom component is to use HACS. 

Open Home Assistant, go to HACS, then click on the three dots on the upper right corner to add a custom repository. Then add the url to this repository. After adding the custom repository, you should be able to find the custom component by searching in HACS. 

Once you have installed the custom component via HACS, you need to restart Home Assistant. 

After the Home Assistant restart, you can go to "Settings" > "Devices & Services" > "Add integration" and then search for "Ollama (local AI models) image analysis". During the setup, you have to pass in the address of your local Ollama instance including the port. The standard port used is 11434. So the host could for example be http://192.168.178.20:11434. Make sure to use http as a protocol (not https).

The component is now ready for use.

## Usage

After the component has been successfully installed and set up, you will find a new service in Home Assistant which you can include in your automations.

For testing the service, you can go to "Developer Tools" > "Services" and then select "Ollama (local AI models) image analysis: Analyze camera image with local AI based upon Ollama" from the Dropdown list.

You should now be provided with different fields to fill out:

1. Prompt: The prompt tells your model what you want to know. For example "What do you see in this image?", "Do you see my glasses on this image?", "Is there something suspicious in this image?".
2. Image path: The path to an image in your Home Assistant file system. Depends on where you store the images to be analyzed. For example "/share/camera_images/latest.jpg".
3. Model: Here you can define, which model Ollama should use for analyzing the image with the given prompt. You should select a model that is multi model, i.e. can handle image and prompt as an input. Be aware that you need to download the model once to Ollama (see installation) before you can use it via this Home Assistant service. For example "llava".

Once you have filled out the fields, you can excute the service and you should be prompted with the result below the box in which you defined the input parameters. Be aware that depending on the performance / hardware config of the machine you are running Ollama on and depending on the complexity of the prompt, resolution of the image as well as on the selected AI model, it can take some seconds or even minutes to receive a response.

If everything works as expected, you can start creating your first automation using the new service "Ollama (local AI models) image analysis: Analyze camera image with local AI based upon Ollama". This works pretty much the same as described above. Just create a new automation or open an existing automation and add the service "Ollama (local AI models) image analysis: Analyze camera image with local AI based upon Ollama" as an action to your automation. In the automation you have to also define a "response variable" as an additional field. This response variable will be filled with the response of the service and can be used in the following steps to send the data to another service, for example for creating a push notification with the result.
