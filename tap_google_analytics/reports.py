PREMADE_REPORTS = [
    {
        "name": "audience_overview",
        "metrics": [
            "users",
            "newUsers",
            "sessions",
            "sessionsPerUser",
            "pageviews",
            "pageviewsPerSession",
            "avgSessionDuration",
            "bounceRate"
        ],
        "dimensions": [
            "date",
            "language",
            "country",
            "city",
            "browser",
            "operatingSystem",
            "screnResolution",
            "year",
            "month",
            "hour",
        ],
        "default_dimensions": [
            "date"
        ]
    },
    {
        "name": "audience_geo_location",
        "metrics": [
            "users",
            "newUsers",
            "sessions",
            "pageviewsPerSession",
            "avgSessionDuration",
            "bounceRate"
        ],
        "dimensions": [
            "date",
            "year",
            "month",
            "hour",
            "country",
            "city",
            "continent",
            "subContinent"
        ],
        "default_dimensions": [
            "date",
            "country",
            "city",
            "continent",
            "subContinent"
        ]
    },
    {
        "name": "audience_technology",
        "metrics": [
            "users",
            "newUsers",
            "sessions",
            "pageviewsPerSession",
            "avgSessionDuration",
            "bounceRate"
        ],
        "dimensions": [
            "date",
            "year",
            "month",
            "hour",
            "browser",
            "operatingSystem",
            "screenResolution",
            "screenColors",
            "flashVersion",
            "javaEnabled",
            "hostname"
        ],
        "default_dimensions": [
            "date",
            "browser",
            "operatingSystem",
        ]
    },
    {
        "name": "acquisition_overview",
        "metrics": [
            "sessions",
            "pageviewsPerSession",
            "avgSessionDuration",
            "bounceRate"
        ],
        "dimensions": [
            'acquisitionMedium',
            'acquisitionSource',
            'acquisitionSourceMedium',
            'acquisitionTrafficChannel'
        ],
        "default_dimensions": [
            "acquisitionTrafficChannel",
            "acquisitionSource",
            "acquisitionSourceMedium",
            "acquisitionMedium",
        ]
    },
    {
        "name": "behavior_overview",
        "metrics": [
            "pageviews",
            "uniquePageviews",
            "avgTimeOnPage",
            "bounceRate",
            "exitRate",
            "exits"
        ],
        "dimensions": [
            "date",
            "year",
            "month",
            "hour",
            "pagePath",
            "pageTitle",
            "searchKeyword",
            "eventCategory"
        ],
        "default_dimensions": [
            "date",
            "pagePath",
            "pageTitle",
            "searchKeyword"
        ]
    },
    {
        "name": "ecommerce_overview",
        "metrics": ["transactions"],
        "dimensions": [
            "transactionId",
            "campaign",
            "source",
            "medium",
            "keyword",
            "socialNetwork"
        ],
        "default_dimensions": [
            "transactionId",
            "campaign",
            "source",
            "medium",
            "keyword",
            "socialNetwork"
        ]
    }
]
