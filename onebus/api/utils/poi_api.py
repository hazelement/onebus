
import urllib
import json
import numpy as np
import pandas as pd
import multiprocessing
from multiprocessing.pool import ThreadPool
from functools import partial
import time

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import config as cf


class Timer:
    """
    Timer for profiling
    """
    def __init__(self, fnname):
        self.name = fnname

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        print(self.name + " took " + str(self.interval) + " sec.")



def _fetch_url(url):
    f = urllib.urlopen(url)
    response = json.loads(f.read())
    return response

def fs_loc_list(lat, lng, query):
    """
    Four square API
    :param lat:
    :param lng:
    :param query:
    :return:
    """
    print("using four square")

    fs_secret=cf.read_api_config('fs_secret')
    fs_client=cf.read_api_config('fs_client')

    srchquery="https://api.foursquare.com/v2/venues/search?near=calgary,ab&query="
    srchquery+=query
    srchquery+="&v=20150214&m=foursquare&client_secret=" + fs_secret + "&client_id=" + fs_client


    res = _fetch_url(srchquery)
    #print res

    loc_list = []
    name = []
    address = []
    for i in range(len(res['response']['venues'])):
        lat=res['response']['venues'][i]['location']['lat']
        lng=res['response']['venues'][i]['location']['lng']
        name.append(res['response']['venues'][i]['name'])
        loc_list.append([lat, lng])
        address.append(res['response']['venues'][i]['location']['formattedAddress'][0])

    gps_array = np.array(loc_list)
    name = np.array(name)
    address = np.array(address)
    return gps_array, name, address


def go_loc_list(lat, lng, query):
    """
    Google API
    :param lat:
    :param lng:
    :param query:
    :return:
    """
    # lat = 51.135494
    # lng = -114.158389
    # query = 'japanese restaurant'

    print("using google")

    query += " Calgary AB"

    loc_p = 'location'+str(lat)+','+str(lng)
    qry_list = query.strip().split(' ')
    qry_p = 'query=' + qry_list[0]
    for i in qry_list[1:]:
        qry_p += '+'
        qry_p += i
    rad_p = 'radius=10000'

    api_key = "key=" + cf.read_api_config('google')  # yyc Calgary key google places api web service


    srch = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
    srch += qry_p + '&'
    srch += loc_p + '&'
    srch += rad_p + '&'
    srch += api_key

    res = _fetch_url(srch)

    # return res

    # print(res)
    loc_list = []
    name = []
    address = []
    for loc in res['results']:
        lat = loc['geometry']['location']['lat']
        lng = loc['geometry']['location']['lng']
        loc_list.append([lat, lng])
        name.append(loc['name'])
        address.append(loc['formatted_address'])

    while('next_page_token' in res and len(name)<40):


        page_token = "pagetoken=" + res['next_page_token']
        srch = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
        # srch += qry_p + '&'
        srch += page_token +"&"
        srch += api_key

        res = _fetch_url(srch)

        for loc in res['results']:
            lat = loc['geometry']['location']['lat']
            lng = loc['geometry']['location']['lng']
            loc_list.append([lat, lng])
            name.append(loc['name'])
            address.append(loc['formatted_address'])


    gps_array = np.array(loc_list)
    name = np.array(name)
    address = np.array(address)

    # print name
    # print address
    return gps_array, name, address




def yelp_batch(lat_lng_pairs, query):
    """
    Yelp API
    :param lat_lng_pairs:
    :param query:
    :return:
    """
    print("using yelp")
    with Timer("yelp query"):
        partial_yelp = partial(_yelp_batch_indivitual, query=query)
        workers = multiprocessing.cpu_count()
        # p=multiprocessing.Pool(workers)
        p=ThreadPool(100)

        result = p.map(partial_yelp, lat_lng_pairs)

        p.close()
        p.join()

        df = pd.concat(result, ignore_index=True)
        df.drop_duplicates('name', inplace = True)


        print("Total no of raw results " + str(len(df)))
        return df


def _yelp_batch_indivitual(lat_lng, query):
    return yelp_loc_list(lat_lng[0], lat_lng[1], query)


def yelp_rec_batch(rec_array, query):
    """
    yelp search batched rectangle
    :param rec_array: list rectanges to search on [[sw_lat, sw_lon, ne_lat, ne_lon], [sw_lat, sw_lon, ne_lat, ne_lon], ...]
    :param query:
    :return:
    """

    print("using yelp")

    with Timer("yelp query"):
        partial_yelp = partial(yelp_rec_api, query=query)
        workers = multiprocessing.cpu_count()
        # p=multiprocessing.Pool(workers)
        p=ThreadPool(workers)

        result = p.map(partial_yelp, rec_array)

        p.close()
        p.join()

        df = pd.concat(result, ignore_index=True)
        df.drop_duplicates('name', inplace = True)

        print("Total no of raw results " + str(len(df)))
        return df

def yelp_rec_api(rec, query):
    """
    return yelp results based on a rectangle given, search query
    :param query: list or numpy array as rectange coordinate, [sw_lat, sw_lon, ne_lat, ne_lon]
    :param query:
    :return: dataframe object, columns=['name', 'address', 'image_url', 'yelp_url', 'review_count', 'ratings_img_url', 'lat','lon']
    """

    def get_yelp(rectange):
        """
        get yelp result
        :param rectangle:  [sw_lat, sw_lon, ne_lat, ne_lon]
        :return: pandas dataframe
        """
        auth = Oauth1Authenticator( consumer_key=cf.read_api_config('yelp_consumer_key'),
                                consumer_secret=cf.read_api_config('yelp_consumer_secret'),
                                token=cf.read_api_config('yelp_token'),
                                token_secret=cf.read_api_config('yelp_token_secret'))
        client = Client(auth)

        df = pd.DataFrame(columns=['name', 'address', 'image_url', 'yelp_url', 'review_count', 'ratings_img_url', 'lat','lon'])

        response = client.search_by_bounding_box(rectange[0], rectange[1], rectange[2], rectange[3], term=query, limit='20', sort='0')
        # response = client.search_by_coordinates( lat, lng, accuracy=None, altitude=None,  altitude_accuracy=None, term=query, limit='20', radius_filter=radius_filter, sort='0', offset=str(i*20)) # meter
        for loc in response.businesses:
            df.loc[len(df)+1]=[loc.name,
                               ' '.join(loc.location.display_address),
                               loc.image_url, loc.url,
                               loc.review_count,
                               loc.rating_img_url,
                               loc.location.coordinate.latitude,
                               loc.location.coordinate.longitude]

        return df

    df = get_yelp(rec)

    df[['review_count']] = df[['review_count']].astype(int)

    print("no of raw results " + str(len(df)))
    return df


def yelp_loc_list(lat, lng, query):
    """
    return yelp results based on user lat and lng, search query
    :param lat:
    :param lng:
    :param query:
    :return: dataframe object, columns=['name', 'address', 'image_url', 'yelp_url', 'review_count', 'ratings_img_url', 'lat','lon']
    """
    auth = Oauth1Authenticator( consumer_key=cf.read_api_config('yelp_consumer_key'),
                                consumer_secret=cf.read_api_config('yelp_consumer_secret'),
                                token=cf.read_api_config('yelp_token'),
                                token_secret=cf.read_api_config('yelp_token_secret'))
    client = Client(auth)

    def get_yelp(radius_filter):
        df = pd.DataFrame(columns=['name', 'address', 'image_url', 'yelp_url', 'review_count', 'ratings_img_url', 'lat','lon'])

        for i in range(0, 2):
            if(len(df) < 20 and len(df) != 0):
                break
            response = client.search_by_coordinates( lat, lng, accuracy=None, altitude=None,  altitude_accuracy=None, term=query, limit='20', radius_filter=radius_filter, sort='0', offset=str(i*20)) # meter
            for loc in response.businesses:
                try:
                    df.loc[len(df)+1]=[loc.name,
                                       ' '.join(loc.location.display_address),
                                       loc.image_url, loc.url,
                                       loc.review_count,
                                       loc.rating_img_url,
                                       loc.location.coordinate.latitude,
                                       loc.location.coordinate.longitude]
                except Exception as e:
                    print(loc, e)

        # df.drop_duplicates('name', inplace = True)
        # print("no of raw results " + str(len(df)))
        return df

    df = get_yelp('3000')
    # if(len(df)<20):
    #     df = get_yelp('20000')

    df[['review_count']] = df[['review_count']].astype(int)

    # print("no of raw results " + str(len(df)))
    return df


if __name__=="__main__":
    lat = 51.0454027
    lng = -114.05651890000001
    query = "restaurant"
    # print(yelp_loc_list(lat, lng, query))
    print(yelp_rec_batch([[51.0454027, -114.05652, 51.0230, -114.123]], query))
    print(yelp_batch([[51.0454027, -114.05652], [51.0230, -114.123]], query))