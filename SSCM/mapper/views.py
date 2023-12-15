from django.shortcuts import render
import geemap.foliumap as geemap
from django.http import JsonResponse
from . import keys 
import ee 
import json 
from . import indeces
import pandas as pd 
import plotly.express as px 
from django.views.decorators.csrf import csrf_exempt

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
    if Map.draw_features:
       ROI1 = ee.FeatureCollection(Map.draw_features)  
    # Map.draw_last_feature
    # ROI1 = ee.FeatureCollection(Map.draw_features)
    else:
       ROI1 = ee.FeatureCollection('users/muthamijohn/kwanza_constituency')
    datafunc = indeces.indexCalculation(ROI1,Map)
    datafunc.main()
    # Map.remove_drawn_features()
    context ={
        'map': Map.to_html()
    }
    return render(request,'base.html',context)



def newIndex(request):
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

   if request.method == 'POST':   
      data = json.loads(request.body.decode('utf-8'))
      coordinates = data.get('coordinates')     
      print(coordinates)
      if coordinates:
            ROI1 = ee.Geometry.Polygon(coordinates)
            #importing the image collection and filtering the date and cloud percentage and mapping the cloud filter function 
            S2 = ee.ImageCollection('COPERNICUS/S2').filterDate('2018-05-01','2018-05-30').filterBounds(ROI1)
            print(list(S2.getInfo()))
            # print(S2.getInfo())
            # print(S2.median().getBandInfo())
            ndvi = S2.median().normalizedDifference(['B8','B4'])
            indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}
            Map.addLayer(ndvi,indecesVis,"ndviLayer")
            context ={
                  'map': Map.to_html()
            }
            print('complete')
            print(context)
            # return render(request,'map.html',context)
            return JsonResponse(context)
      else:
              return render(request,'map.html')
def mainPage(request):
       return render(request,'base.html')




