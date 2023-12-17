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

def maskS2clouds(image):
    return image.updateMask(image.select('QA60').eq(0))


def indexCalculator(S2,collection_with_indices,ROI1):
   dataframe = indeces.indexCalculation(S2,collection_with_indices,ROI1)
   formated_dataframe = dataframe.getDataFrames()
   return formated_dataframe 

coordinates_array = []

def newIndex(request):
  

   if request.method == 'POST':   
      data = json.loads(request.body.decode('utf-8'))
      coordinates = data.get('coordinates')     
      print(coordinates)
      if coordinates:
         base_url = reverse('map-page')
         print('reverse finished')
         return redirect(f"{base_url}?{urlencode({'coordinates': json.dumps(coordinates)})}")
   return render(request,'base.html')





def mapPage(request):
   print('map page view starts executing...')
   coordinates = json.loads(request.GET.get('coordinates'))
   print("coordinate type :" , type(coordinates) ,f":{coordinates}")
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
   ROI1 = ee.Geometry.Polygon(coordinates)    
   #importing the image collection and filtering the date and cloud percentage and mapping the cloud filter function 
   S2 = ee.ImageCollection('COPERNICUS/S2').filter(ee.Filter.calendarRange(2017,2021, 'year')).filter(ee.Filter.calendarRange(4, 7, 'month')).map(maskS2clouds).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)).filterBounds(ROI1)

   def computeIndices(image):
      # Compute SARVI
      sarvi = image.expression('(1 + L) * float(nir - red)/ (nir + red + L)', {
         'nir': image.select('B8'),
         'red': image.select('B4'),
         'L': 0.5
      }).rename('SARVI')

      # Compute GCI
      gci = image.expression('nir / green -1', {
         'green': image.select('B3'),
         'nir': image.select('B8')
      }).rename('GCI')

      # Compute NPCRI
      npcri = image.expression('((nir - red) / (nir + red)) / ((nir - blue) / (nir + blue))', {
         'nir': image.select('B8'),
         'red': image.select('B4'),
         'blue': image.select('B2')
      }).rename('NPCRI')

      # Compute RVI
      rvi = image.expression('red / nir', {
         'nir': image.select('B8'),
         'red': image.select('B4')
      }).rename('RVI')

      # Compute EVI
      evi = image.expression('2.5 * float(nir - red) / (nir + 6 * red - 7.5 * blue + 1)', {
         'nir': image.select('B8'),
         'red': image.select('B4'),
         'blue': image.select('B2')
      }).rename('EVI')

      # Compute NDVI
      ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

      # Return the image with computed indices
      return image.addBands([sarvi, gci, npcri, rvi, evi, ndvi])

   # Use .map() to apply the computeIndices function to each image in the collection
   collection_with_indices = S2.map(computeIndices)
   if collection_with_indices:
     indexCalculator(S2,collection_with_indices,ROI1)
   ndvi = S2.median().normalizedDifference(['B8','B4'])
   indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}

   Map.addLayer(ndvi.clip(ROI1),indecesVis,"ndviLayer")
   image = collection_with_indices.median().clip(ROI1)
   Map.addLayer(image.select('SARVI'),indecesVis,"SARVI")
   Map.addLayer(image.select('GCI'),indecesVis,"GCI")
   Map.addLayer(image.select('RVI'),indecesVis,"RVI")
   Map.addLayer(image.select('NPCRI'),indecesVis,"NPCRI")

   context ={
         'map': Map.to_html()
   }
   coordinates_array.append(context)
   print(coordinates_array)
   print('complete')
   print(context)
   return render(request,'map.html',context)


def mainPage(request):
   return render(request,'base.html',)




