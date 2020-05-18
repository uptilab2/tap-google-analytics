# Google Analytics Json Schema Generation

############################################################################################
# Goals:                                                                                   #
# Research into the specific data types that will be needed for the json schema            #
# Generate metadata from 'field_infos' (field_exclusions, profile_id, metric or dimension) #
#                                                                                          #
# Expected Result:                                                                         #
# Have rough draft of code that generates a catalog, given field_infos                     #
############################################################################################

import re
import listing_custom_metrics_and_dimensions as listing
import discover_metrics_and_dimensions as discover
from singer import metadata
from singer.catalog import Catalog, CatalogEntry, Schema

standard_fields = discover.field_infos
custom_fields = listing.custom_metrics_and_dimensions

# What data types exist?
# ipdb> {i['dataType'] for i in standard_fields}
standard_fields_data_types = {'CURRENCY', 'STRING', 'PERCENT', 'TIME', 'INTEGER', 'FLOAT'}

# ipdb> {i['type'] for i in custom_fields}
custom_fields_data_types = {'CURRENCY', 'INTEGER', 'STRING', 'TIME'}

# How should we translate them?

def type_to_schema(ga_type):
    if ga_type == 'CURRENCY':
        # https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#ecomm
        return {"type": ["number", "null"]}
    elif ga_type == 'STRING':
        # TODO: What about date-time fields?
        return {"type": ["string", "null"]}
    elif ga_type == 'PERCENT':
        # TODO: Unclear whether these come back as "0.25%" or just "0.25"
        return {"type": ["number", "null"]}
    elif ga_type == 'TIME':
        return {"type": ["string", "null"]}
    elif ga_type == 'INTEGER':
        return {"type": ["integer", "null"]}
    elif ga_type == 'FLOAT':
        return {"type": ["number", "null"]}
    else:
        raise Exception("Unknown Google Analytics type: {}".format(ga_type))

# TODO: Trim the `ga:` here?
# TODO: Do we need to generate the `XX` fields schemas here somehow? e.g., 'ga:productCategoryLevel5' vs. 'ga:productCategoryLevelXX'
# - The numeric versions are in `ga_cubes.json`
field_schemas = {**{f["id"]: type_to_schema(f["dataType"]) for f in standard_fields},
                 **{f["id"]: type_to_schema(f["dataType"]) for f in custom_fields}}

# These are data types that we traditionally have used, compare them with those discovered
known_dimension_types = {"start-date": "DATETIME",
                         "end-date": "DATETIME",
                         "cohortNthWeek": "INTEGER",
                         "nthDay": "INTEGER",
                         "cohortNthDay": "INTEGER",
                         "screenDepth": "INTEGER",
                         "latitude": "FLOAT",
                         "visitCount": "INTEGER",
                         "visitsToTransaction": "INTEGER",
                         "daysSinceLastSession": "INTEGER",
                         "sessionsToTransaction": "INTEGER",
                         "longitude": "FLOAT",
                         "nthMonth": "INTEGER",
                         "nthHour": "INTEGER",
                         "subContinentCode": "INTEGER",
                         "pageDepth": "INTEGER",
                         "nthWeek": "INTEGER",
                         "daysSinceLastVisit": "INTEGER",
                         "sessionCount": "INTEGER",
                         "nthMinute": "INTEGER",
                         "dateHour": "DATETIME",
                         "date": "DATETIME",
                         "daysToTransaction": "INTEGER",
                         "cohortNthMonth": "INTEGER",
                         "visitLength": "INTEGER"}

known_metric_types = {"transactionsPerSession": "FLOAT",
                      "localTransactionRevenue": "FLOAT",
                      "internalPromotionViews": "INTEGER",
                      "uniqueSocialInteractions": "INTEGER",
                      "domainLookupTime": "INTEGER",
                      "adxImpressions": "INTEGER",
                      "socialInteractionsPerSession": "FLOAT",
                      "adxCoverage": "FLOAT",
                      "goalValuePerSession": "FLOAT",
                      "eventsPerSessionWithEvent": "FLOAT",
                      "visitsWithEvent": "INTEGER",
                      "productRemovesFromCart": "INTEGER",
                      "percentSearchRefinements": "FLOAT",
                      "serverResponseTime": "INTEGER",
                      "newVisits": "INTEGER",
                      "organicSearches": "INTEGER",
                      "goalValuePerVisit": "FLOAT",
                      "14dayUsers": "INTEGER",
                      "adsenseAdUnitsViewed": "INTEGER",
                      "totalValue": "FLOAT",
                      "quantityAddedToCart": "INTEGER",
                      "cohortRevenuePerUser": "FLOAT",
                      "cohortActiveUsers": "INTEGER",
                      "CTR": "FLOAT",
                      "adsenseCoverage": "FLOAT",
                      "searchUniques": "INTEGER",
                      "percentVisitsWithSearch": "FLOAT",
                      "avgPageDownloadTime": "FLOAT",
                      "quantityRemovedFromCart": "INTEGER",
                      "avgRedirectionTime": "FLOAT",
                      "avgSessionDuration": "FLOAT",
                      "searchGoalConversionRateAll": "FLOAT",
                      "revenuePerItem": "FLOAT",
                      "localTransactionTax": "FLOAT",
                      "goalXXCompletions": "INTEGER",
                      "cohortPageviewsPerUser": "FLOAT",
                      "productDetailViews": "INTEGER",
                      "pageviewsPerVisit": "FLOAT",
                      "domContentLoadedTime": "INTEGER",
                      "avgDomContentLoadedTime": "FLOAT",
                      "adClicks": "INTEGER",
                      "pageLoadTime": "INTEGER",
                      "uniqueScreenviews": "INTEGER",
                      "visitBounceRate": "FLOAT",
                      "revenuePerTransaction": "FLOAT",
                      "fatalExceptionsPerScreenview": "FLOAT",
                      "goalXXAbandons": "INTEGER",
                      "cohortSessionsPerUserWithLifetimeCriteria": "FLOAT",
                      "cohortRetentionRate": "FLOAT",
                      "hits": "INTEGER",
                      "dcmROI": "FLOAT",
                      "dcmFloodlightRevenue": "FLOAT",
                      "sessionDuration": "FLOAT",
                      "entrances": "INTEGER",
                      "CPM": "FLOAT",
                      "fatalExceptions": "INTEGER",
                      "adsenseRevenue": "FLOAT",
                      "cohortGoalCompletionsPerUserWithLifetimeCriteria": "FLOAT",
                      "productRefunds": "INTEGER",
                      "costPerTransaction": "FLOAT",
                      "queryProductQuantity": "INTEGER",
                      "contentGroupUniqueViewsXX": "INTEGER",
                      "quantityCheckedOut": "INTEGER",
                      "goalValueAll": "FLOAT",
                      "uniqueAppviews": "INTEGER",
                      "avgServerResponseTime": "FLOAT",
                      "cohortSessionDurationPerUser": "FLOAT",
                      "pageLoadSample": "INTEGER",
                      "exceptions": "INTEGER",
                      "bounceRate": "FLOAT",
                      "searchExitRate": "FLOAT",
                      "visits": "INTEGER",
                      "redirectionTime": "INTEGER",
                      "adxRevenuePer1000Sessions": "FLOAT",
                      "adxClicks": "INTEGER",
                      "impressions": "INTEGER",
                      "avgSearchResultViews": "FLOAT",
                      "cohortPageviewsPerUserWithLifetimeCriteria": "FLOAT",
                      "timeOnPage": "FLOAT",
                      "cohortSessionsPerUser": "FLOAT",
                      "RPC": "FLOAT",
                      "adsenseECPM": "FLOAT",
                      "productListClicks": "INTEGER",
                      "buyToDetailRate": "FLOAT",
                      "dcmClicks": "INTEGER",
                      "dcmMargin": "FLOAT",
                      "exits": "INTEGER",
                      "uniqueEvents": "INTEGER",
                      "adsenseAdsViewed": "INTEGER",
                      "productRevenuePerPurchase": "FLOAT",
                      "avgSearchDepth": "FLOAT",
                      "timeOnScreen": "FLOAT",
                      "metricXX": "INTEGER",
                      "adsensePageImpressions": "INTEGER",
                      "pageviewsPerSession": "FLOAT",
                      "goalXXValue": "FLOAT",
                      "dcmCPC": "FLOAT",
                      "speedMetricsSample": "INTEGER",
                      "dcmROAS": "FLOAT",
                      "sessionsWithEvent": "INTEGER",
                      "bounces": "INTEGER",
                      "dcmImpressions": "INTEGER",
                      "adsenseViewableImpressionPercent": "FLOAT",
                      "dcmCTR": "FLOAT",
                      "cohortSessionDurationPerUserWithLifetimeCriteria": "FLOAT",
                      "userTimingSample": "INTEGER",
                      "adxViewableImpressionsPercent": "FLOAT",
                      "avgTimeOnPage": "FLOAT",
                      "adxImpressionsPerSession": "FLOAT",
                      "transactionTax": "FLOAT",
                      "uniquePurchases": "INTEGER",
                      "uniquePageviews": "INTEGER",
                      "eventsPerVisitWithEvent": "FLOAT",
                      "cohortTotalUsers": "INTEGER",
                      "domInteractiveTime": "INTEGER",
                      "relatedProductQuantity": "INTEGER",
                      "adxRevenue": "FLOAT",
                      "goalXXStarts": "INTEGER",
                      "transactionsPerVisit": "FLOAT",
                      "productCheckouts": "INTEGER",
                      "productAddsToCart": "INTEGER",
                      "appviews": "INTEGER",
                      "pageviews": "INTEGER",
                      "timeOnSite": "FLOAT",
                      "adxECPM": "FLOAT",
                      "avgPageLoadTime": "FLOAT",
                      "users": "INTEGER",
                      "avgSearchDuration": "FLOAT",
                      "pageValue": "FLOAT",
                      "newUsers": "INTEGER",
                      "goalAbandonsAll": "INTEGER",
                      "7dayUsers": "INTEGER",
                      "cohortGoalCompletionsPerUser": "FLOAT",
                      "costPerGoalConversion": "FLOAT",
                      "percentNewVisits": "FLOAT",
                      "totalEvents": "INTEGER",
                      "transactionRevenue": "FLOAT",
                      "30dayUsers": "INTEGER",
                      "ROI": "FLOAT",
                      "margin": "FLOAT",
                      "cohortRevenuePerUserWithLifetimeCriteria": "FLOAT",
                      "screenviews": "INTEGER",
                      "adsenseCTR": "FLOAT",
                      "searchExits": "INTEGER",
                      "transactionShipping": "FLOAT",
                      "domLatencyMetricsSample": "INTEGER",
                      "localItemRevenue": "FLOAT",
                      "dcmFloodlightQuantity": "INTEGER",
                      "percentNewSessions": "FLOAT",
                      "itemsPerPurchase": "FLOAT",
                      "socialActivities": "INTEGER",
                      "dcmRPC": "FLOAT",
                      "productListCTR": "FLOAT",
                      "internalPromotionClicks": "INTEGER",
                      "entranceRate": "FLOAT",
                      "cohortTotalUsersWithLifetimeCriteria": "INTEGER",
                      "adsenseExits": "INTEGER",
                      "localProductRefundAmount": "FLOAT",
                      "searchResultViews": "INTEGER",
                      "exceptionsPerScreenview": "FLOAT",
                      "productRefundAmount": "FLOAT",
                      "avgEventValue": "FLOAT",
                      "searchGoalXXConversionRate": "FLOAT",
                      "totalRefunds": "INTEGER",
                      "adxCTR": "FLOAT",
                      "avgServerConnectionTime": "FLOAT",
                      "correlationScore": "FLOAT",
                      "sessions": "INTEGER",
                      "transactionRevenuePerSession": "FLOAT",
                      "itemQuantity": "INTEGER",
                      "avgUserTimingValue": "FLOAT",
                      "avgDomainLookupTime": "FLOAT",
                      "entranceBounceRate": "FLOAT",
                      "goalCompletionsAll": "INTEGER",
                      "socialInteractionsPerVisit": "FLOAT",
                      "goalValueAllPerSearch": "FLOAT",
                      "adCost": "FLOAT",
                      "goalXXAbandonRate": "FLOAT",
                      "ROAS": "FLOAT",
                      "percentSessionsWithSearch": "FLOAT",
                      "appviewsPerVisit": "FLOAT",
                      "screenviewsPerSession": "FLOAT",
                      "goalAbandonRateAll": "FLOAT",
                      "cartToDetailRate": "FLOAT",
                      "revenuePerUser": "FLOAT",
                      "socialInteractions": "INTEGER",
                      "adxMonetizedPageviews": "INTEGER",
                      "avgDomInteractiveTime": "FLOAT",
                      "visitors": "INTEGER",
                      "quantityRefunded": "INTEGER",
                      "searchRefinements": "INTEGER",
                      "localTransactionShipping": "FLOAT",
                      "searchDuration": "FLOAT",
                      "searchDepth": "INTEGER",
                      "goalConversionRateAll": "FLOAT",
                      "cohortAppviewsPerUserWithLifetimeCriteria": "FLOAT",
                      "exitRate": "FLOAT",
                      "transactions": "INTEGER",
                      "goalXXConversionRate": "FLOAT",
                      "serverConnectionTime": "INTEGER",
                      "costPerConversion": "FLOAT",
                      "internalPromotionCTR": "FLOAT",
                      "goalStartsAll": "INTEGER",
                      "pageDownloadTime": "INTEGER",
                      "localRefundAmount": "FLOAT",
                      "avgTimeOnSite": "FLOAT",
                      "dcmCost": "FLOAT",
                      "itemRevenue": "FLOAT",
                      "transactionsPerUser": "FLOAT",
                      "transactionRevenuePerVisit": "FLOAT",
                      "searchVisits": "INTEGER",
                      "avgScreenviewDuration": "FLOAT",
                      "productListViews": "INTEGER",
                      "searchSessions": "INTEGER",
                      "sessionsPerUser": "FLOAT",
                      "1dayUsers": "INTEGER",
                      "eventValue": "INTEGER",
                      "refundAmount": "FLOAT",
                      "cohortAppviewsPerUser": "FLOAT",
                      "adsenseAdsClicks": "INTEGER",
                      "userTimingValue": "INTEGER",
                      "CPC": "FLOAT"}

# These are the fields whose datatype is different from the sets above,
# and are not handled in other ways -- 'CURRENCY' or 'PERCENT'
all_datatype_discrepancies = {f["id"].split(":")[1]: {**known_dimension_types, **known_metric_types}[f["id"].split(":")[1]]
                              for f in standard_fields
                              if f["id"].split(":")[1] in {**known_dimension_types, **known_metric_types}
                              and f['dataType'] not in ['CURRENCY', 'PERCENT']
                              and f["dataType"] != {**known_dimension_types, **known_metric_types}[f["id"].split(":")[1]]}

# ipdb> pp {f["id"]: {**known_dimension_types, **known_metric_types}[f["id"]] for f in standard_fields if f["id"] in {**known_dimension_types, **known_metric_types} and f["dataType"] != {**known_dimension_types, **known_metric_types}[f["id"]] and f["dataType"] == "STRING"}

integer_field_overrides = {'cohortNthDay',
                           'cohortNthMonth',
                           'cohortNthWeek',
                           'daysSinceLastSession',
                           'daysToTransaction',
                           'nthDay',
                           'nthHour',
                           'nthMinute',
                           'nthMonth',
                           'nthWeek',
                           'pageDepth',
                           'screenDepth',
                           'sessionCount',
                           'sessionsToTransaction',
                           'subContinentCode',
                           'visitCount',
                           'visitLength',
                           'visitsToTransaction'}

datetime_field_overrides = {'date',
                            'dateHour'}

float_field_overrides = {'latitude',
                         'longitude',
                         'avgScreenviewDuration',
                         'avgSearchDuration',
                         'avgSessionDuration',
                         'avgTimeOnPage',
                         'cohortSessionDurationPerUser',
                         'cohortSessionDurationPerUserWithLifetimeCriteria',
                         'searchDuration',
                         'sessionDuration',
                         'timeOnPage',
                         'timeOnScreen'}

def revised_type_to_schema(ga_type, field_id):
    field_id = field_id.split(":")[1]
    if field_id in datetime_field_overrides:
        return {"type": ["string", "null"], "format": "date-time"}
    elif ga_type == 'CURRENCY':
        # https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#ecomm
        return {"type": ["number", "null"]}
    elif ga_type == 'PERCENT':
        # TODO: Unclear whether these come back as "0.25%" or just "0.25"
        return {"type": ["number", "null"]}
    elif ga_type == 'TIME':
        return {"type": ["string", "null"]}
    elif ga_type == 'INTEGER' or field_id in integer_field_overrides:
        return {"type": ["integer", "null"]}
    elif ga_type == 'FLOAT' or field_id in float_field_overrides:
        return {"type": ["number", "null"]}
    elif ga_type == 'STRING':
        # TODO: What about date-time fields?
        return {"type": ["string", "null"]}
    else:
        raise Exception("Unknown Google Analytics type: {}".format(ga_type))

# TODO: Trim the `ga:` here?
# TODO: Do we need to generate the `XX` fields schemas here somehow? e.g., 'ga:productCategoryLevel5' vs. 'ga:productCategoryLevelXX'
# - The numeric versions are in `ga_cubes.json`
revised_field_schemas = {**{f["id"].split(':')[1]: type_to_schema(f["dataType"]) for f in standard_fields},
                         **{f["id"].split(':')[1]: type_to_schema(f["dataType"]) for f in custom_fields}}

# Expand Out standard XX fields into their numeric counterparts
# This will give us all of the fields that exist, including the actual names of standard `XX` fields
field_exclusions = discover.generate_exclusions_lookup()

# Translate the known standard `XX` fields to their numeric counterparts
# NOTE: This should probably happen before generating schemas, that way we get one for each.
xx_fields = [f for f in standard_fields if 'XX' in f['id']]
xx_field_regexes = {f['id'].split(':')[1].replace('XX', r'\d\d?'): f for f in xx_fields}
numeric_xx_fields = [{**field_info, **{"id": numeric_field_id}}
                     for regex, field_info in xx_field_regexes.items()
                     for numeric_field_id in field_exclusions.keys() if re.match(regex, numeric_field_id)]

# Some did not get captured by this search
# - Mainly entries with `XX` in the middle of the id
# ipdb> pp [f['id'] for f in standard_fields if 'XX' in f['id']]
['goalXXStarts',
 'goalXXCompletions',
 'goalXXValue',
 'goalXXConversionRate',
 'goalXXAbandons',
 'goalXXAbandonRate',
 'searchGoalXXConversionRate',
 'contentGroupUniqueViewsXX', # Matched
 'dimensionXX', # Custom, ignore
 'customVarNameXX', # Custom, ignore
 'metricXX', # Custom, ignore
 'customVarValueXX', # Custom, ignore
 'landingContentGroupXX', # Matched
 'previousContentGroupXX', # Matched
 'contentGroupXX', # Matched
 'productCategoryLevelXX' # Matched
]

# These are the ones that matched (e.g., have constant numeric definitions)
# ipdb> pp {field_info["id"] for regex, field_info in xx_field_regexes.items() for f in field_exclusions.keys() if re.match(regex, f)}
{'contentGroupUniqueViewsXX',
 'contentGroupXX',
 'landingContentGroupXX',
 'previousContentGroupXX',
 'productCategoryLevelXX'}

# Looks like the only other standard fields we don't have are goals.
# Goals could be discovered through the data mangement API, if we have access
# - https://developers.google.com/analytics/devguides/config/mgmt/v3/data-management
# - https://developers.google.com/analytics/devguides/config/mgmt/v3/mgmtReference/management/goals/list

# This could be called during discovery to generate goal-related schemas for each one that's defined
# NOTE: Goals are not necessarily defined in 1, 2, 3, 4... order. We defined one at 17 for fun.
def get_goals_for_profile(access_token, account_id, web_property_id, profile_id):
    """
    Gets all goal IDs for profile to generate goal-related metric schemas.
    """
    profiles_url = 'https://www.googleapis.com/analytics/v3/management/accounts/{accountId}/webproperties/{webPropertyId}/profiles/{profileId}/goals'
    goals_response = requests.get(profiles_url.format(accountId=account_id,
                                                         webPropertyId=web_property_id,
                                                         profileId=profile_id),
                                              headers={'Authorization' : 'Bearer ' + access_token},
                                              params={"quotaUser": quota_user})
    return [g["id"] for g in goals_response.json()['items']]

# Generate Metadata - Use the "standard_fields" and "custom_fields" to do this
# 1. Standard, non XX fields
# 2. Standard, Goal XX fields -- still XX in exclusions map
# 3. Standard, Non-Goal XX fields -- In numeric form in exclusions map
# 4. Custom Fields (ga:metricXX and ga:dimensionXX for now)

# Algo:
# generate ALL the schemas
#    - generate metadata for each schema and case above
# Profit!

def is_static_XX_field(field_id, field_exclusions):
    """
    GA has fields that are documented using a placeholder of `XX`, where
    the `XX` is replaced with a number in practice.

    Some of these are standard fields with constant numeric
    representations. These must be handled differently from other field,
    so this function will detect this case using the information we have
    gleaned in our field_exclusions values.

    If the field_exclusions map does NOT have the `XX` version in it, this
    function assumes that it has only the numeric versions.
    """
    return 'XX' in field_id and field_id not in field_exclusions

def is_dynamic_XX_field(field_id, field_exclusions):
    """
    GA has fields that are documented using a placeholder of `XX`, where
    the `XX` is replaced with a number in practice.

    Some of these are standard fields that are generated based on other
    artifacts defined for the profile (e.g., goals). These must be handled
    differently from other fields as well, since the IDs must be
    discovered through their own means.

    If the field_exclusions map DOES have the `XX` version in it, this
    function assumes that the field is dynamically discovered.
    """
    return 'XX' in field_id and field_id in field_exclusions

def handle_static_XX_field(field, field_exclusions):
    """
    Uses a regex of the `XX` field's ID to discover which numeric versions
    of a given `XX` field name we have exclusions for.

    Generates a schema entry and metadata for each.
    Returns:
    - Sub Schemas  {"<numeric_field_id>": {...field schema}, ...}
    - Sub Metadata {"numeric_field_id>": {...exclusions metadata value}, ...}
    """
    regex_matcher = field['id'].replace("XX", r'\d\d?')
    matching_exclusions = {field_id: field_exclusions[field_id]
                           for field_id in field_exclusions.keys()
                           if re.match(regex_matcher, field_id)}

    sub_schemas = {field_id: revised_type_to_schema(field["dataType"], field["id"])
                     for field_id in matching_exclusions.keys()}
    sub_metadata = matching_exclusions

    return sub_schemas, sub_metadata

def get_dynamic_field_names(client, field):
    # TODO: This is mocked, do the real thing as we discover cases, please
    # TODO: This should throw if the field name is not known, to determine all known fields over time
    return [field['id'].replace('XX',str(i)) for i in range(1,5)]

def handle_dynamic_XX_field(client, field, field_exclusions):
    """
    Discovers dynamic names of a given XX field using `client` with
    `get_dynamic_field_names` and matches them with the exclusions known
    for the `XX` version of the name.

    Generates a schema entry and metadata for each.
    Returns:
    - Sub Schemas  {"<numeric_field_id>": {...field schema}, ...}
    - Sub Metadata {"numeric_field_id>": {...exclusions metadata value}, ...}
    """
    dynamic_field_names = get_dynamic_field_names(client, field)

    sub_schemas = {d: revised_type_to_schema(field["dataType"],field["id"])
                   for d in dynamic_field_names}

    sub_metadata = {r: field_exclusions[field['id']]
                    for r in dynamic_field_names}
    return sub_schemas, sub_metadata

def write_metadata(mdata, field, exclusions):
    """ Translate a field_info object and its exclusions into its metadata, and write it. """
    mdata = metadata.write(mdata, ("properties", field["id"]), "inclusion", "available")
    mdata = metadata.write(mdata, ("properties", field["id"]), "fieldExclusions", list(exclusions))
    mdata = metadata.write(mdata, ("properties", field["id"]), "behavior", field["type"])

    # TODO: What other pieces of metadata do we need? probably tap_google_analytics.ga_name, tap_google_analytics.profile_id, etc?
    # - Also, metric/dimension needs to be in metadata for the UI (refer to adwords for key) 'behavior'

    return mdata

def generate_catalog_entry(client, standard_fields, custom_fields, field_exclusions):
    schema = {"type": "object", "properties": {"_sdc_record_hash": {"type": "string"}}}
    mdata = metadata.get_standard_metadata(schema=schema, key_properties=["_sdc_record_hash"])
    mdata = metadata.to_map(mdata)

    LOGGER.info("debug generate catalog entry")
    LOGGER.info(standard_fields)
    for standard_field in standard_fields:
        LOGGER.info("ENTRY : ")
        LOGGER.info(standard_field)
        if standard_field['status'] == 'DEPRECATED':
            continue
        matching_fields = []
        if is_static_XX_field(standard_field["id"], field_exclusions):
            sub_schemas, sub_mdata = handle_static_XX_field(standard_field, field_exclusions)
            schema["properties"].update(sub_schemas)
            for calculated_id, exclusions in sub_mdata.items():
                specific_field = {**standard_field, **{"id": calculated_id}}
                mdata = write_metadata(mdata, specific_field, exclusions)
        elif is_dynamic_XX_field(standard_field["id"], field_exclusions):
            sub_schemas, sub_mdata = handle_dynamic_XX_field(client, standard_field, field_exclusions)
            schema["properties"].update(sub_schemas)
            for calculated_id, exclusions in sub_mdata.items():
                specific_field = {**standard_field, **{"id": calculated_id}}
                mdata = write_metadata(mdata, specific_field, exclusions)
        else:
            schema["properties"][standard_field["id"]] = revised_type_to_schema(standard_field["dataType"],
                                                                                 standard_field["id"])
            mdata = write_metadata(mdata, standard_field, field_exclusions[standard_field["id"]])

    for custom_field in custom_fields:
        if custom_field["kind"] == 'analytics#customDimension':
            exclusion_lookup_name = 'ga:dimensionXX'
        elif custom_field["kind"] == 'analytics#customMetric':
            exclusion_lookup_name = 'ga:metricXX'
        else:
            raise Exception('Unknown custom field "kind": {}'.format(custom_field["kind"]))

        exclusions = field_exclusions[exclusion_lookup_name]
        mdata = write_metadata(mdata, custom_field, exclusions)
        schema["properties"][custom_field["id"]] = revised_type_to_schema(custom_field["dataType"],
                                                                          custom_field["id"])
    return schema, mdata

# TODO: Not using a client, but will need one for dynamic standard fields
client = {}
generate_catalog_entry(client, standard_fields, custom_fields, field_exclusions)

# TODO: DESIGN - It occurs during this research that the `ga:` version of
# fields wouldn't be best, so we may want to write metadata with the `ga:`
# name and instead use the friendly name in the schema (this should appear
# on the `field_infos` objects in standard_Fields and custom_fields)

# Rough draft of catalog code

# Take the previous function and use it to create a singer catalog with Catalog, CatalogEntry, and Schema
def generate_catalog(client, standard_fields, custom_fields, exclusions):
    schema, mdata = generate_catalog_entry(client, standard_fields, custom_fields, field_exclusions)
    # Do the thing to generate the thing
    catalog_entry = CatalogEntry(schema=Schema.from_dict(schema),
                                 key_properties=['_sdc_record_hash'],
                                 stream='report',
                                 tap_stream_id='report',
                                 metadata=metadata.to_list(mdata))
    return Catalog([catalog_entry])


#CatalogEntry(schema=Schema.from_dict(schema), key_properties=['_sdc_record_hash'], stream='report', tap_stream_id='report', metadata=mdata)
