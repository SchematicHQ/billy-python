import os
import xmltodict
import flickr_api
from flickr_api.api import flickr

flickr_api.set_keys(api_key = os.environ.get("FLICKR_API_KEY"), api_secret=os.environ.get("FLICKR_SECRET_KEY"))

###
# Flickr integration
###
def retrieve_images_by_keyword(search):
    photo_array = {}

    photos = xmltodict.parse(flickr.photos.search(text = search, per_page = 20, page = 1, safe_search = 1))

    for photo in photos['rsp']['photos']['photo']:
        photo_array[photo['@id']] = {"owner" : photo['@owner'], "id" : photo['@id'], "url" : "https://live.staticflickr.com/"+photo['@server']+"/"+photo["@id"]+"_"+photo['@secret']+".jpg"}
    
    return photo_array

def retrieve_images_by_photo_id(photos):
    photo_array = {}
    
    for photo in photos:
        if photo.photo_id:
            photo_metadata = xmltodict.parse(flickr.photos.getInfo(photo_id = photo.photo_id))
            photo_metadata = photo_metadata['rsp']['photo']
            photo_array[photo_metadata['@id']] = {"owner" : photo_metadata['owner']['@nsid'], "id" : photo_metadata['@id'], "url" : "https://live.staticflickr.com/"+photo_metadata['@server']+"/"+photo_metadata["@id"]+"_"+photo_metadata['@secret']+".jpg"}
    
    return photo_array