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
   print('map page view starts executing...')
   coordinates = json.loads(request.GET.get('coordinates'))
   print("coordinate type :" , type(coordinates) ,f":{coordinates}")
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
   # Convert the Image Collection to a list
   image_list = collection_with_indices.toList(collection_with_indices.size())

   # Convert the Earth Engine List to a Python list
   image_list = image_list.getInfo()

   # Now, image_list is a Python list containing all the images
   print('The image list is ', image_list)


   def filterCollectionByMonthYear(collection, month, year):
      start = ee.Date.fromYMD(year, month, 1)
      end = start.advance(1, 'month')
      filteredCollection = collection.filterDate(start, end)
      return filteredCollection

   # Select months (April, June, and July) and a range of years
   months = [4, 6, 7]  # April, June, and July
   years = list(range(2017, 2021))  # All years from 2015 to 2022

   # Filter the collection for selected months and years
   filteredCollection = []
   for year in years:
      for month in months:
         filtered = filterCollectionByMonthYear(collection_with_indices, month, year)
         image = filtered.median()
         date = ee.Date.fromYMD(year, month, 1)
         filteredCollection.append(image.set('system:time_start', date.millis()).set('month', month).set('year', year))

   # Create an image collection from the filtered images
   filteredimageCollection = ee.ImageCollection(filteredCollection)

   # filteredimageCollection
   filteredimage = filteredimageCollection.median()
   band_names = filteredimage.bandNames().getInfo()
   print("Band names in filteredimageCollection:", band_names)
   S2.median().bandNames().getInfo()
   filteredimageCollection   
   def calculateMeans(imageCollection,date):
         date = ee.Date(date)
         imageCollection = imageCollection.filterDate(date, date.advance(1, 'month')).median()
      # Compute mean vegetation indices
         ndvi_mean = imageCollection.select('NDVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
         sarvi_mean = imageCollection.select('SARVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
         gci_mean = imageCollection.select('GCI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
         npcri_mean = imageCollection.select('NPCRI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
         rvi_mean = imageCollection.select('RVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
         evi_mean = imageCollection.select('EVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)

         mean_ndvi = ee.Number(ndvi_mean.get('NDVI')).float().getInfo()
         mean_sarvi = ee.Number(sarvi_mean.get('SARVI')).float().getInfo()
         mean_gci = ee.Number(gci_mean.get('GCI')).float().getInfo()
         mean_npcri = ee.Number(npcri_mean.get('NPCRI')).float().getInfo()
         mean_rvi = ee.Number(rvi_mean.get('RVI')).float().getInfo()
         mean_evi = ee.Number(evi_mean.get('EVI')).float().getInfo()

         return {'date': date.format('YYYY-MM-dd').getInfo(), 'mean_ndvi': mean_ndvi,'mean_sarvi':mean_sarvi,'mean_gci': mean_gci,'mean_npcri': mean_npcri,'mean_rvi':mean_rvi,'mean_evi':mean_evi}
   
   
      # Map function to extract and format the dates
   def extract_and_format_date(image):
      date = image.date().format('YYYY-MM-dd')
      return ee.Feature(None, {'date': date})
   # Map the function over the collection
   dates = collection_with_indices.map(extract_and_format_date)

   # Get distinct dates
   distinct_dates = dates.distinct('date').aggregate_array('date')

   # Convert the resulting list of distinct dates to a Python list
   dates_list = distinct_dates.getInfo()


   print(dates_list)

   data = [calculateMeans(collection_with_indices,date)for date in dates_list]
   df_all = pd.DataFrame(data).set_index('date')

   df = df_all
   df= df.reset_index()
   # Extract the year from the 'date' column and create a new 'year' column
   df['year'] = pd.to_datetime(df['date']).dt.year

   # Group by 'year' and calculate the mean for desired columns
   mean_df = df.groupby('year').agg({
      'mean_ndvi': 'mean',
      'mean_sarvi': 'mean',
      'mean_gci': 'mean',
      'mean_npcri': 'mean',
      'mean_rvi': 'mean',
      'mean_evi': 'mean'
   }).reset_index()

   # Convert the result to a list of dictionaries
   result = mean_df.to_dict(orient='records')

   # Print the result
   print(result)

   df_filtered = pd.DataFrame(result)
   df_filtered[['year','mean_ndvi', 'mean_sarvi', 'mean_npcri','mean_rvi','mean_gci']]
   df_filtered.set_index('year')
   print(df_filtered)
   ndvi = S2.median().normalizedDifference(['B8','B4'])
   indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}

   Map.addLayer(ndvi.clip(ROI1),indecesVis,"ndviLayer")
   image = S2.median().clip(ROI1)
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
   json_data = keys.json_data
   # Preparing values
   json_object = json.loads(json_data, strict=False)
   service_account = json_object['client_email']
   json_object = json.dumps(json_object)
   #Authorising the app
   credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
   ee.Initialize(credentials)    

   return render(request,'base.html',)




