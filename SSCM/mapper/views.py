from django.shortcuts import render
import geemap.foliumap as geemap
from . import keys 
import ee 
import json 
from . import indeces


# Create your views here.

def index(request):
    json_data = keys.json_data
    # Preparing values
    json_object = json.loads(json_data, strict=False)
    service_account = json_object['client_email']
    json_object = json.dumps(json_object)
    #Authorising the app
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
    ee.Initialize(credentials)
    
    Map = geemap.Map()
    Map.set_center(35.0,1.1,12)
    ROI1=ee.FeatureCollection('users/muthamijohn/kwanza_constituency')
    #cloud mask function
    def maskS2clouds(image):
        return image.updateMask(image.select('QA60').eq(0))

    # #importing the image collection and filtering the date and cloud percentage and mapping the cloud filter function 
    S2=ee.ImageCollection('COPERNICUS/S2_SR').filter(ee.Filter.calendarRange(2017,2021, 'year')).filter(ee.Filter.calendarRange(7, 9, 'month')).map(maskS2clouds).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5))
    #creating a single image from the sentinel 2 image collection 
    image=S2.first().clip(ROI1)
    S2image=ee.ImageCollection('COPERNICUS/S2_SR').filterDate('2017-01-01','2022-12-30').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15)).median().clip(ROI1)
    Map.addLayer(S2.select('B4','B3','B2').filterBounds(ROI1).median(),{'min': 0 ,"max": 3000},"sentinel image 1")
    Map.addLayer(S2image.select('B4','B3','B2'),{'min': 0 ,"max": 3000},"sentinel image")
   
    print(image.bandNames().getInfo())
    print(image.select('B4'))
    
    indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}
    indexImages = indeces.indexCalculation(S2,'B3','B4','B8','B2')
    image = indexImages.get_indeces(S2.filterBounds(ROI1).median())
    Map.addLayer(image.select('SARVI'),indecesVis,"SARVI")

    context= {
        'map': Map.to_html()
    }
    return render(request,'base.html',context)
