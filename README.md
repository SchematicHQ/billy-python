## Getting started
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

## Running locally

Run the following command

```
npm start run     
```

Open the app locally at http://127.0.0.1:5000. Navigate to `/register` route to create a new user account.