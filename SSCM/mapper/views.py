from django.shortcuts import render,redirect
from django.utils.http import urlencode
from django.urls import reverse
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


coordinates_array = []

def newIndex(request):
  

   if request.method == 'POST':   
      data = json.loads(request.body.decode('utf-8'))
      coordinates = data.get('coordinates')     
      print(coordinates)
      if coordinates:
         base_url = reverse('map-page')
         return redirect(f"{base_url}?{urlencode({'coordinates': json.dumps(coordinates)})}")
   return render(request,'map.html')





def mapPage(request):
   coordinates = json.loads(request.GET.get('coordinates'))
   print("coordinate type :" , type(coordinates) ,f":{coordinates}")
   Map = geemap.Map()
   Map.set_center(35.0,1.1,12)
   ROI1 = ee.Geometry.Polygon(coordinates)
   #importing the image collection and filtering the date and cloud percentage and mapping the cloud filter function 
   S2 = ee.ImageCollection('COPERNICUS/S2').filterDate('2018-05-01','2018-05-30').map(maskS2clouds).filterBounds(ROI1)

   ndvi = S2.median().normalizedDifference(['B8','B4'])
   indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}
   Map.addLayer(ndvi,indecesVis,"ndviLayer")

   context ={
         'map': Map.to_html()
   }
   coordinates_array.append(context)
   print(coordinates_array)
   print('complete')
   print(context)
   return render(request,'map.html',context)


def mainPage(request):
   json_data = keys.json_data
   # Preparing values
   json_object = json.loads(json_data, strict=False)
   service_account = json_object['client_email']
   json_object = json.dumps(json_object)
   #Authorising the app
   credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
   ee.Initialize(credentials)    
   return render(request,'base.html',)




