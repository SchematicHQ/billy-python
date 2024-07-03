# Schematic Sample App for an Image Search Project

A demo using Schematic to implement packaging in an application.

This app is an image search engine using the Flickr API. It:
- Implements metered packaging model
- [Checks for feature access based on the current subscription](https://github.com/SchematicHQ/billy-python/blob/e03d3bb35b87925eb4151842894b784585330d77/vendors/schematic_python.py#L24)
- [Reports usage of a feature](https://github.com/SchematicHQ/billy-python/blob/e03d3bb35b87925eb4151842894b784585330d77/vendors/schematic_python.py#L132)
- [Manages the subscription lifecycle using Schematic](https://github.com/SchematicHQ/billy-python/blob/e03d3bb35b87925eb4151842894b784585330d77/main.py#L96)

## Why Schematic?
We believe that B2B businesses should not reinvent the wheel to support pricing and packaging, and that a single platform, not a collection of disconnected code, tools, and processes, should support customers from purchase to feature delivery and ultimately billing.

Schematic decouples billing and entitlements logic from application code. With it, you can launch, package, meter, and monitor features without needing to restructure your app or introduce breaking changes.

## Getting started with the Billy app
1. Create and activate a virtualenv

```
python3 -m venv venv
. venv/bin/activate
```

2. Clone the repo:

```
git clone https://github.com/SchematicHQ/billy-python.git
```

3. Install all requirements:

```
pip install -r requirements.txt
npm install
```

npm is used as a task runner and to support TailwindCSS.

4. Initialize the .env file by copying the example file:

```
cp .env.example .env
```

5. Populate your .env file
- Generate Flickr API keys here (to fill in FLICKR_API_KEY, FLICKR_SECRET_KEY): https://www.flickr.com/services/apps/create/
- Generate Schematic API keys in your account here (to fill in SCHEMATIC_API_KEY): https://docs.schematichq.com/quickstart#setting-up-dev-and-prod-environments

## Getting started with the Schematic app

1. Log into your Schematic account
2. Run the following to seed your Schematic environment with flags, features, and plans for Billy (make sure your .env file has a valid Schematic API key first):

```
npm run populate-schematic
```

3. Run the Billy app locally

## Running locally

Run the following command:

```
npm start run
```

Open the app locally at http://127.0.0.1:5000/register.

## Resources

- [How to implement metered features with Scehmatic](https://github.com/SchematicHQ/billy-python/blob/e03d3bb35b87925eb4151842894b784585330d77/main.py#L96)
- [Sending usage events to Schematic](https://docs.schematichq.com/quickstart#sending-track-and-identify-calls)
- [Evaluating company entitlements with Schematic](https://docs.schematichq.com/quickstart#evaluating-entitlements)