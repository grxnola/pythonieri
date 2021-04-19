# Pythonieri
An API-compatible clone of [Falconieri](https://github.com/nethesis/falconieri/).

Pythonieri allows you to store a phone's provisioning URL in a provider's RPS.
Currently, only Yealink is supported. Yealink have a JSON api which is nice,
except it's designer is insane. 

## Requirements
Python 3.8
Flask >= 1.1.2
Requests >= 2.25.1

## Usage
Install the dependencies with `pipenv install` (or install Flask and Requests using
your preferred solution) and run with:
```
python ./pythonieri.py
```
though it's recommended you write an init script to manage it.

## Configuration
The only configuration in Pythonieri is secrets.py. Example configuration:
```
yealink = {
  api_key: blipblop,
  api_secret: bingbong
}
```

## Thanks
Special thanks to [Nethesis](https://www.nethesis.it/) for the original Falconieri.

## Notes
Please don't read the source in the providers files yet.
