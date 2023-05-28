from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import pandas as pd


def get_results():
    """
    Site id is a parameter used in the eBay API to specify the eBay site to use for an API call.
    Each eBay marketplace (such as eBay.com, eBay.co.uk, eBay.de, etc.) has a unique site ID.
    The Site id  parameter is required for most eBay API calls, as it specifies the marketplace
    context in which the API call is made.


    The config_file parameter is an optional parameter used to specify the location of a configuration
    file that contains API credentials and other settings needed to authenticate and make API calls to eBay.
    This file typically contains information such as the eBay developer account credentials, the application ID,
    the certificate ID, the token expiration time, and other settings. By providing a config_file parameter,
    you can avoid having to specify these settings in each API call, which can make your code more manageable and
    easier to maintain.
    """

    payload = {
        'keywords': '12 string bass guitar',
        'categoryId': ['3858'],
        'itemFilter': [
            {'name': 'LocatedIn', 'value': 'GB'},
        ],
        'sortOrder': 'StartTimeNewest',
    }

    try:
        api = Finding(siteid='EBAY-GB', appid='APPLICATION_ID', config_file=None)
        response = api.execute('findItemsAdvanced', payload)
        return response.dict()
    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def get_total_pages():
    results = get_results()
    """Get the total number of pages from the results"""
    if results:
        return int(results.get('paginationOutput').get('totalPages'))
    else:
        raise


def search_ebay():
    """parse the response - results and concatentate to the dataframe"""
    results = get_results()
    total_pages = get_total_pages()
    items_list = results['searchResult']['item']

    i = 2
    while i <= total_pages:

        # payload['paginationInput'] = {'entriesPerPage': 100, 'pageNumber': i}
        results = get_results()
        items_list.extend(results['searchResult']['item'])
        i += 1

    df_items = pd.DataFrame(columns=['itemId', 'title', 'viewItemURL', 'galleryURL', 'location', 'postalCode',
                                     'paymentMethod''listingType', 'bestOfferEnabled', 'buyItNowAvailable',
                                     'currentPrice', 'bidCount', 'sellingState'])

    for item in items_list:
        row = {
            'itemId': item.get('itemId'),
            'title': item.get('title'),
            'viewItemURL': item.get('viewItemURL'),
            'galleryURL': item.get('galleryURL'),
            'location': item.get('location'),
            'postalCode': item.get('postalCode'),
            'paymentMethod': item.get('paymentMethod'),
            'listingType': item.get('listingInfo').get('listingType'),
            'bestOfferEnabled': item.get('listingInfo').get('bestOfferEnabled'),
            'buyItNowAvailable': item.get('listingInfo').get('buyItNowAvailable'),
            'currentPrice': item.get('sellingStatus').get('currentPrice').get('value'),
            'bidCount': item.get('bidCount'),
            'sellingState': item.get('sellingState'),
        }

        # Deprecation note - don't use append
        """https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.append.html"""

        new_df = pd.DataFrame([row])
        df_items = pd.concat([df_items, new_df], axis=0, ignore_index=True)

    return df_items
