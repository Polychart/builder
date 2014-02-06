"""
File containing parameters for Google Analytics as a data source connection.
"""
class GAParams:
  """
  Various parameters that are required for Google Analytics.

  Attribs:
    queryUrl: Endpoint for querying data from Google Analytics.
    managementUrl: Endpoint for querying user information from Google Analytics.
    metricTables: Static list of metrics and tables provided by Google Analytics.
  """
  def __init__(self):
    pass

  @staticmethod
  def getQueryUrl():
    """Returns Google Analytics Query URL"""
    return "https://www.googleapis.com/analytics/v3/data/ga?"

  @staticmethod
  def getManageUrl():
    """Returns Google Analytics Management URL"""
    return "https://www.googleapis.com/analytics/v3/management/accounts"

  @staticmethod
  def getTables():
    """Returns array for Google Analytics tables."""
    return [
      {
        'name': 'Visitor'
      , 'meta': {
          'visitorType': {'type': 'cat', 'ga': 'dimension'}
        , 'visitCount': {'type': 'num', 'ga': 'dimension'}
        , 'daysSinceLastVisit': {'type': 'num', 'ga': 'dimension'}
        , 'userDefinedValue': {'type': 'cat', 'ga': 'dimension'}
        , 'visitors': {'type': 'num', 'ga': 'metric'}
        , 'newVisits': {'type': 'num', 'ga': 'metric'}
        , 'percentNewVisits': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Session'
      , 'meta':{
          'visitLength': {'type': 'num', 'timerange': 'second', 'ga': 'dimension'}
        , 'visits': {'type': 'num', 'ga': 'metric'}
        , 'bounces': {'type': 'num', 'ga': 'metric'}
        , 'entranceBounceRate': {'type': 'num', 'ga': 'metric'}
        , 'visitBounceRate': {'type': 'num', 'ga': 'metric'}
        , 'timeOnSite': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'avgTimeOnSite': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Traffic Sources'
      , 'meta': {
          'referralPath': {'type': 'cat', 'ga': 'dimension'}
        , 'campaign': {'type': 'cat', 'ga': 'dimension'}
        , 'source': {'type': 'cat', 'ga': 'dimension'}
        , 'medium': {'type': 'cat', 'ga': 'dimension'}
        , 'keyword': {'type': 'cat', 'ga': 'dimension'}
        , 'adContent': {'type': 'cat', 'ga': 'dimension'}
        , 'socialNetwork': {'type': 'cat', 'ga': 'dimension'}
        , 'hasSocialSourceReferral': {'type': 'cat', 'ga': 'dimension'}
        , 'organicSearches': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'AdWords'
      , 'meta': {
          'adGroup': {'type': 'cat', 'ga': 'dimension'}
        , 'adSlot': {'type': 'cat', 'ga': 'dimension'}
        , 'adSlotPosition': {'type': 'cat', 'ga': 'dimension'}
        , 'adDistributionNetwork': {'type': 'cat', 'ga': 'dimension'}
        , 'adMatchType': {'type': 'cat', 'ga': 'dimension'}
        , 'adMatchedQuery': {'type': 'cat', 'ga': 'dimension'}
        , 'adPlacementDomain': {'type': 'cat', 'ga': 'dimension'}
        , 'adPlacementUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'adFormat': {'type': 'cat', 'ga': 'dimension'}
        , 'adTargetingType': {'type': 'cat', 'ga': 'dimension'}
        , 'adTargetingOption': {'type': 'cat', 'ga': 'dimension'}
        , 'adDisplayUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'adDestinationUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'adwordsCustomerID': {'type': 'cat', 'ga': 'dimension'}
        , 'adwordsCampaignID': {'type': 'cat', 'ga': 'dimension'}
        , 'adwordsCreativeID': {'type': 'cat', 'ga': 'dimension'}
        , 'adwordsCriterialID': {'type': 'cat', 'ga': 'dimension'}
        , 'impressions': {'type': 'num', 'ga': 'metric'}
        , 'adClicks': {'type': 'num', 'ga': 'metric'}
        , 'adCost': {'type': 'num', 'ga': 'metric'}
        , 'CPM': {'type': 'num', 'ga': 'metric'}
        , 'CPC': {'type': 'num', 'ga': 'metric'}
        , 'CTR': {'type': 'num', 'ga': 'metric'}
        , 'costPerTransaction': {'type': 'num', 'ga': 'metric'}
        , 'costPerGoalConversion': {'type': 'num', 'ga': 'metric'}
        , 'costPerConversion': {'type': 'num', 'ga': 'metric'}
        , 'RPC': {'type': 'num', 'ga': 'metric'}
        , 'ROI': {'type': 'num', 'ga': 'metric'}
        , 'margin': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Goal Conversions'
      , 'meta': {
          'goalStartsAll': {'type': 'num', 'ga': 'metric'}
        , 'goalCompletionsAll': {'type': 'num', 'ga': 'metric'}
        , 'goalValueAll': {'type': 'num', 'ga': 'metric'}
        , 'goalValueAllPerVisit': {'type': 'num', 'ga': 'metric'}
        , 'goalConversionRateAll': {'type': 'num', 'ga': 'metric'}
        , 'goalAbandonsAll': {'type': 'num', 'ga': 'metric'}
        , 'goalAbandonRateAll': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Platform / Device'
      , 'meta': {
          'browser': {'type': 'cat', 'ga': 'dimension'}
        , 'browserVersion': {'type': 'cat', 'ga': 'dimension'}
        , 'operatingSystem': {'type': 'cat', 'ga': 'dimension'}
        , 'operationSystemVersion': {'type': 'cat', 'ga': 'dimension'}
        , 'isMobile': {'type': 'cat', 'ga': 'dimension'}
        , 'mobileDeviceBranding': {'type': 'cat', 'ga': 'dimension'}
        , 'mobileDeviceModel': {'type': 'cat', 'ga': 'dimension'}
        , 'mobileInputSelector': {'type': 'cat', 'ga': 'dimension'}
        , 'mobileDeviceInfo': {'type': 'cat', 'ga': 'dimension'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        },
      }
    , {
        'name': 'Geo / Network'
      , 'meta': {
          'continent': {'type': 'cat', 'ga': 'dimension'}
        , 'subContinent': {'type': 'cat', 'ga': 'dimension'}
        , 'country': {'type': 'cat', 'ga': 'dimension'}
        , 'region': {'type': 'cat', 'ga': 'dimension'}
        , 'metro': {'type': 'cat', 'ga': 'dimension'}
        , 'city': {'type': 'cat', 'ga': 'dimension'}
        , 'latitiude': {'type': 'cat', 'ga': 'dimension'}
        , 'longitude': {'type': 'cat', 'ga': 'dimension'}
        , 'networkDomain': {'type': 'cat', 'ga': 'dimension'}
        , 'networkLocation': {'type': 'cat', 'ga': 'dimension'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'System',
        'meta': {
          'flashVersion': {'type': 'cat', 'ga': 'dimension'}
        , 'javaEnabled': {'type': 'cat', 'ga': 'dimension'}
        , 'language': {'type': 'cat', 'ga': 'dimension'}
        , 'screenColors': {'type': 'cat', 'ga': 'dimension'}
        , 'screenResolution': {'type': 'cat', 'ga': 'dimension'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Social Activities'
      , 'meta': {
          'socialActivityEndorsingUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityDisplayName': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityPost': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityTimestamp': {'type': 'num', 'ga': 'dimension'}
        , 'socialActivityUserHandler': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityUserPhotoUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityProfileUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityContentUrl': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityTagsSummary': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityAction': {'type': 'cat', 'ga': 'dimension'}
        , 'socialActivityNetworkAction': {'type': 'cat', 'ga': 'dimension'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Page Tracking'
      , 'meta': {
          'hostname': {'type': 'cat', 'ga': 'dimension'}
        , 'pagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'pagePathLevel1': {'type': 'cat', 'ga': 'dimension'}
        , 'pagePathLevel2': {'type': 'cat', 'ga': 'dimension'}
        , 'pagePathLevel3': {'type': 'cat', 'ga': 'dimension'}
        , 'pagePathLevel4': {'type': 'cat', 'ga': 'dimension'}
        , 'pageTitle': {'type': 'cat', 'ga': 'dimension'}
        , 'landingPagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'secondPagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'exitPagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'previousPagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'nextPagePath': {'type': 'cat', 'ga': 'dimension'}
        , 'pageDepth': {'type': 'num', 'ga': 'dimension'}
        , 'entrances': {'type': 'num', 'ga': 'metric'}
        , 'entranceRate': {'type': 'num', 'ga': 'metric'}
        , 'pageviews': {'type': 'num', 'ga': 'metric'}
        , 'pageviewsPerVisit': {'type': 'num', 'ga': 'metric'}
        , 'uniquePageviews': {'type': 'num', 'ga': 'metric'}
        , 'timeOnPage': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'avgTimeOnPage': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'exits': {'type': 'num', 'ga': 'metric'}
        , 'exitRate': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Internal Search'
      , 'meta': {
          'searchUsed': {'type': 'cat', 'ga': 'dimension'}
        , 'searchKeyword': {'type': 'cat', 'ga': 'dimension'}
        , 'searchKeywordRefinement': {'type': 'cat', 'ga': 'dimension'}
        , 'searchCategory': {'type': 'cat', 'ga': 'dimension'}
        , 'searchStartPage': {'type': 'cat', 'ga': 'dimension'}
        , 'searchDestinationPage': {'type': 'cat', 'ga': 'dimension'}
        , 'searchResultViews': {'type': 'num', 'ga': 'metric'}
        , 'searchUniques': {'type': 'num', 'ga': 'metric'}
        , 'avgSearchResultViews': {'type': 'num', 'ga': 'metric'}
        , 'searchVisits': {'type': 'num', 'ga': 'metric'}
        , 'percentVisitsWithSearch': {'type': 'num', 'ga': 'metric'}
        , 'searchDepth': {'type': 'num', 'ga': 'metric'}
        , 'avgSearchDepth': {'type': 'num', 'ga': 'metric'}
        , 'searchRefinements': {'type': 'num', 'ga': 'metric'}
        , 'searchDuration': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'avgSearchDuration': {'type': 'num', 'timerange': 'second', 'ga': 'metric'}
        , 'searchExits': {'type': 'num', 'ga': 'metric'}
        , 'searchExitRate': {'type': 'num', 'ga': 'metric'}
        , 'searchGoal(n)ConversionRate': {'type': 'num', 'ga': 'metric'}
        , 'searchGoalConversionRateAll': {'type': 'num', 'ga': 'metric'}
        , 'goalValueAllPerSearch': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Site Speed'
      , 'meta': {
          # Note that some of these times are typed numbers because they have
          # milliseconds as time range
          'pageLoadTime': {'type': 'num', 'ga': 'metric'}
        , 'pageLoadSample': {'type': 'num', 'ga': 'metric'}
        , 'avgPageLoadTime': {'type': 'num', 'ga': 'metric'}
        , 'domainLookupTime': {'type': 'num', 'ga': 'metric'}
        , 'avgDomainLookupTime': {'type': 'num', 'ga': 'metric'}
        , 'pageDownloadTime': {'type': 'num', 'ga': 'metric'}
        , 'redirectionTime': {'type': 'num', 'ga': 'metric'}
        , 'avgRedirectionTime': {'type': 'num', 'ga': 'metric'}
        , 'serverConnectionTime': {'type': 'num', 'ga': 'metric'}
        , 'avgServerConnectionTime': {'type': 'num', 'ga': 'metric'}
        , 'serverResponseTime': {'type': 'num', 'ga': 'metric'}
        , 'avgServerResponseTime': {'type': 'num', 'ga': 'metric'}
        , 'speedMetricsSample': {'type': 'num', 'ga': 'metric'}
        , 'domInteractiveTime': {'type': 'num', 'ga': 'metric'}
        , 'avgDomInteractiveTime': {'type': 'num', 'ga': 'metric'}
        , 'domContentLoadTime': {'type': 'num', 'ga': 'metric'}
        , 'avgDomContentLoadTime': {'type': 'num', 'ga': 'metric'}
        , 'domLatencyMetricsSample': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'App Tracking'
      , 'meta': {
          'appViews': {'type': 'num', 'ga': 'metric'}
        , 'uniqueAppViews': {'type': 'num', 'ga': 'metric'}
        , 'appviewsPerVisit': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Event Tracking'
      , 'meta': {
          'eventCategory': {'type': 'cat', 'ga': 'dimension'}
        , 'eventAction': {'type': 'cat', 'ga': 'dimension'}
        , 'eventLabel': {'type': 'cat', 'ga': 'dimension'}
        , 'totalEvents': {'type': 'num', 'ga': 'metric'}
        , 'uniqueEvents': {'type': 'num', 'ga': 'metric'}
        , 'eventValue': {'type': 'num', 'ga': 'metric'}
        , 'avgEventValue': {'type': 'num', 'ga': 'metric'}
        , 'visitsWithEvent': {'type': 'num', 'ga': 'metric'}
        , 'eventsPerVisitWithEvent': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Ecommerce'
      , 'meta': {
          'transactionId': {'type': 'cat', 'ga': 'dimension'}
        , 'affiliation': {'type': 'cat', 'ga': 'dimension'}
        , 'visitsToTransaction': {'type': 'num', 'ga': 'dimension'}
        , 'daysToTransaction': {'type': 'num', 'ga': 'dimension'}
        , 'productSku': {'type': 'cat', 'ga': 'dimension'}
        , 'productName': {'type': 'cat', 'ga': 'dimension'}
        , 'productCategory': {'type': 'cat', 'ga': 'dimension'}
        , 'transactions': {'type': 'num', 'ga': 'metric'}
        , 'transactionsPerVisit': {'type': 'num', 'ga': 'metric'}
        , 'transactionRevenue': {'type': 'num', 'ga': 'metric'}
        , 'revenuePerTransaction': {'type': 'num', 'ga': 'metric'}
        , 'transactionRevenuePerVisit': {'type': 'num', 'ga': 'metric'}
        , 'transactionShipping': {'type': 'num', 'ga': 'metric'}
        , 'transactionTax': {'type': 'num', 'ga': 'metric'}
        , 'totalValue': {'type': 'num', 'ga': 'metric'}
        , 'itemQuantity': {'type': 'num', 'ga': 'metric'}
        , 'uniquePurchaes': {'type': 'num', 'ga': 'metric'}
        , 'revenuePerItem': {'type': 'num', 'ga': 'metric'}
        , 'itemRevenue': {'type': 'num', 'ga': 'metric'}
        , 'itemsPerPurchase': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Social Interactions'
      , 'meta': {
          'socialInteractionNetwork': {'type': 'cat', 'ga': 'dimension'}
        , 'socialInteractionAction': {'type': 'cat', 'ga': 'dimension'}
        , 'socialInteractionNetworkAction': {'type': 'cat', 'ga': 'dimension'}
        , 'socialInteractionTarget': {'type': 'cat', 'ga': 'dimension'}
        , 'socialInteractions': {'type': 'num', 'ga': 'metric'}
        , 'uniqueSocialInteractions': {'type': 'num', 'ga': 'metric'}
        , 'socialInteractionsPerVisit': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'User Timings'
      , 'meta': {
          # Some times here are typed num because their time range is milliseconds
          'userTimingCategory': {'type': 'cat', 'ga': 'dimension'}
        , 'userTimingLabel': {'type': 'cat', 'ga': 'dimension'}
        , 'userTimingVariable': {'type': 'cat', 'ga': 'dimension'}
        , 'userTimingValue': {'type': 'num', 'ga': 'metric'}
        , 'userTimingSample': {'type': 'num', 'ga': 'metric'}
        , 'avgUserTimingValue': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    , {
        'name': 'Exception Tracking'
      , 'meta': {
          'exceptions': {'type': 'num', 'ga': 'metric'}
        , 'fatalExceptions': {'type': 'num', 'ga': 'metric'}
        , 'time': {'type': 'date', 'ga': 'dimension', 'format': 'unix'}
        }
      }
    ]
