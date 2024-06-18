# Schematic Sample App for an Image Search App

A demo of using Schematic to implement packaging in an application.

This app is an image search engine using the Flickr API. It implements a metered packaging model, checks for feature access based on their current subscription, reports usage of a feature, and manages the subscription lifecycle using Schematic.

## Why Schematic?
We believe that B2B businesses should not reinvent the wheel to support pricing and packaging, and that a single platform, not a collection of disconnected code, tools, and processes, should support customers from purchase to feature delivery and ultimately billing.

Schematic decouples billing and entitlements logic from application code. With it, you can launch, package, meter, and monitor features without needing to restructure your app or concern yourself with breaking changes.

## Getting started with the Billy app
1. Clone the repo:

```
git clone https://github.com/SchematicHQ/billy-python.git
```

2. Install all requirements:

```
pip install -r requirements.txt
npm install
```

3. Initialize the .env file:

```
cp .env.example .env
```

4. Populate your .env file
- Generate Flickr keys here: https://www.flickr.com/services/apps/create/
- Generate a Schematic API key: https://docs.schematichq.com/quickstart#setting-up-dev-and-prod-environments

## Getting started with the Schematic app

1. Log into your Schematic account
2. Run the following to seed your Schematic environment with Billy data (make sure your .env file has a valid Schematic API key first)

```
 npm run populate-schematic
```

3. Run the Billy app locally

## Running locally

Run the following command

```
npm start run
```

Open the app locally at http://127.0.0.1:5000/register.