from schematic import Schematic, CreateOrUpdateConditionGroupRequestBody, CreateOrUpdateConditionRequestBody
import config
import os
import json

# define pricing schema
data = {
            'plans' : {
                'basic' : {
                    'plan_type': 'pricing_plan',
                    'description': 'Our entry-level plan for new users',
                    'name': 'basic',
                    'features' : {
                        'search-queries' : {
                            'key' : 'search-queries',
                            'value_type' : 'Numeric',
                            'limit' : 1,
                            'period' : 'current_month'
                        },
                        'favorites' : {
                            'key' : 'favorites',
                            'value_type' : 'Numeric',
                            'limit' : 1,
                            'period' : None
                        }
                    }
                },
                'standard' : {
                    'plan_type': 'pricing_plan',
                    'description': 'Our mid-level plan for advanced users',
                    'name': 'standard',
                    'features' : {
                        'search-queries' : {
                            'key' : 'search-queries',
                            'value_type' : 'Numeric',
                            'limit' : 5,
                            'period' : 'current_month'
                        },
                        'favorites' : {
                            'key' : 'favorites',
                            'value_type' : 'Numeric',
                            'limit' : 5,
                            'period' : None
                        }
                    }
                },
                'pro' : {
                    'plan_type': 'pricing_plan',
                    'description': 'Our highest-level plan for expert users',
                    'name': 'pro',
                    'features' : {
                        'search-queries' : {
                            'key' : 'search-queries',
                            'value_type' : 'Unlimited',
                            'limit' : None,
                            'period' : 'current_month'
                        },
                        'favorites' : {
                            'key' : 'favorites',
                            'value_type' : 'Unlimited',
                            'limit' : None,
                            'period' : None
                        }
                    }
                }
            },
            'features' : {
                'search-queries' : {
                    'name' : 'Search Queries',
                    'description' : 'Meters search queries by user in Billy',
                    'feature_type' : 'event',
                    'trait_id' : None,
                    'event_subtype' : 'search-query',
                    'flag' : {
                        'default_value' : True,
                        'description' : None,
                        'flag_type' : 'boolean',
                        'key' : 'search-queries',
                        'name' : 'Search Queries'
                    }
                },
                'favorites' : {
                    'name' : 'Favorites',
                    'description' : 'Meters favorites for users in Billy',
                    'feature_type' : 'trait',
                    'trait_id' : 'favorite_count',
                    'event_subtype' : None,
                    'flag' : {
                        'default_value' : True,
                        'description' : None,
                        'flag_type' : 'boolean',
                        'key' : 'favorites',
                        'name' : 'Favorites'
                    }
                }
            }
        }

# initiatlize client
client = Schematic(os.environ.get("SCHEMATIC_API_KEY"))

#print(data)

def populate_schematic(data):
    print(data)

    features = data['features']
    plans = data['plans']

    company_response = create_company()
#    print(company_response)
#    print(json.dumps(json.loads(company_response.json())))
    company_response = json.loads(company_response.json())

#    print(company_response['data'])

    trait_response_plan = upsert_trait('plan', company_response['data'])
    json_trait_response_plan = json.loads(trait_response_plan.json())
    plan_trait_id = json_trait_response_plan['data']['entity_traits'][0]['definition']['id']

    trait_response_favorite = upsert_trait('favorite_count', company_response['data'])
    trait_response = json.loads(trait_response_favorite.json())

#    print(features)
#    print(plans)

    # create features
    feature_ids = {}
    for feature in features:
        feature_data = features[feature]
        # replace trait with id
        if feature_data['trait_id'] == 'favorite_count':
            feature_data['trait_id'] = trait_response['data']['entity_traits'][0]['definition']['id']
        response = create_feature(feature_data)
        feature_ids[feature_data['flag']['key']] = response.data.id

    # create plans
    plan_ids = {}
    for plan in plans:
        plan_data = plans[plan]
        response = create_plan(plan_data)
        plan_ids[plan_data['name']] = response.data.id

    # create entitlements
    for plan in plans:
        response = create_entitlements(plans[plan], plan_ids[plan], feature_ids)

    # create plan audiences
    for plan in plans:
       response = create_audiences(plans[plan], plan_ids[plan], plan_trait_id)

    delete_company(company_response['data']['id'])

    return 'Done seeding Schematic'

def create_feature(feature):
    response = client.features.create_feature(
        description = feature['description'],
        feature_type = feature['feature_type'],
        name = feature['name'],
        event_subtype = feature['event_subtype'],
        trait_id = feature['trait_id'],
        flag={
            "default_value" : feature['flag']['default_value'],
            "description" : None,
            "flag_type" : feature['flag']['flag_type'],
            "key" : feature['flag']['key'],
            "name" : feature['flag']['name']
        }
    )

    return response

def create_plan(plan):
    print(plan)
    response = client.plans.create_plan(
        description = plan['description'],
        plan_type = plan['plan_type'],
        name = plan['name']
    )

    return response

def create_audiences(plan, plan_id, plan_trait_id):
    client.plans.update_audience(
        plan_audience_id=plan_id,
        condition_groups = [
            CreateOrUpdateConditionGroupRequestBody(
                conditions=[
                    CreateOrUpdateConditionRequestBody(
                        condition_type="trait",
                        operator="eq",
                        trait_id =plan_trait_id,
                        trait_value=plan['name'],
                        metric_value=0,
                        resource_ids=[]
                    )
                ]
            )
        ],
        conditions=[]
    )

    return "audience created"

def create_entitlements(plan, plan_id, feature_ids):

    for feature in plan['features']:
        feature_data = plan['features'][feature]
        client.entitlements.create_plan_entitlement(
            feature_id = feature_ids[feature_data['key']],
            plan_id = plan_id,
            metric_period = feature_data['period'], 
            value_type = feature_data['value_type'],
            value_numeric=  feature_data['limit']
        )

    return 'entitlements created'

def create_company():
    response = client.companies.upsert_company(
        keys = {
            'org_id' : '123'
        },
        traits = {
            'favorite_count' : 1
        }
    )

    return response

def delete_company(id):
    client.companies.delete_company(
        company_id = id
    )

    return "deleted"

# create trait
def upsert_trait(trait, company):
    response = client.companies.upsert_company_trait(
        keys = {
            company['keys'][0]['key'] : company['keys'][0]['value']
        },
        trait  = trait,
        incr = 1
    )

    return response

response = populate_schematic(data)
print(response)