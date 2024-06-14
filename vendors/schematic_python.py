from schematic.client import Schematic, SchematicConfig, LocalCache, EventBodyIdentifyCompany
import config
import os
import json

# configure SDK cache & set flag defaults in case there is service interruption
cache_size_bytes = 1000000
cache_ttl = 1000  # in milliseconds
sch_config = SchematicConfig(
    cache_providers=[LocalCache[bool](cache_size_bytes, cache_ttl)],
    flag_defaults={"some-flag-key": True} # update later
)

# initiatlize client & pass updated config
client = Schematic(os.environ.get("SCHEMATIC_API_KEY"), sch_config)

######
# Schematic Flag Check - retrieve flag value for given company
######
def check_flag(organization_id, flag_key):
    # set company context to reference company
    company = {
        "organization_id" : str(organization_id)
    }

    # set flag key to evaluate
    key = flag_key

    # retrieve flag value from schematic)
    # if value is not available in local cache, Schematic client will submit network request
    response = client.features.check_flag(
        key = key,
        company=company
        )
    
    return response.data.value

######
# Schematic User Upsert - create and update user
######
def user_create_update(current_user, **kwargs):
    name = str(current_user.username)

    user = {
        "user_id" : current_user.id
    }

    company = {
        "organization_id" : current_user.company.id
    }

    print(user)
    print(company)

    traits = {}
    for key, value in kwargs.items():
        traits[key] = value

    response  = client.companies.upsert_user(
      company = company,
      keys = user,
      name = name,
      traits = traits
    )

    return response

######
# Schematic Company Upsert - create and update company
######
def company_create_update(current_user, **kwargs):
    name = str(current_user.company.company)
    
    company = {}
    company["organization_id"] = current_user.company.id

    traits = {}
    for key, value in kwargs.items():
        traits[key] = value

    response = client.companies.upsert_company(
        keys = company,
        name = name,
        traits = traits
    )

    return response

######
# Schematic Get Metadata - get trait metadata from schematic
######
def get_company(current_user):
    company = {}
    company["organization_id"] = current_user.company.id

    response = client.companies.lookup_company(
        keys = company
    )

    print(json.dumps(json.loads(response.json()), sort_keys=True, indent=4, separators=(",", ": ")))
    
    return response.json()

######
# Schematic Identify Event - send updated user information to Schematic
######
def send_identify_event(current_user, **kwargs):
    name = current_user.username

    user = {}
    user["user_id"] = current_user.id

    company = {}
    company["organization_id"] = current_user.company.id

    traits = {}
    for key, value in kwargs.items():
        traits[key] = value

    response = client.identify(
        keys=user,
        name=name,
        company=EventBodyIdentifyCompany(
            keys=company,
        ),
        traits=traits
    )

    return response

######
# Schematic Track Event - send usage to Schematic
######
def send_track_event(current_user, event_name):
    user = {}
    user["user_id"] = current_user.id

    company = {}
    company["organization_id"] = current_user.company.id

    response = client.track(
        event=event_name,
        user=user,
        company=company,
    )

    return response