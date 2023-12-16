# import ee 
# import pandas as pd 
# class indexCalculation():
#                 def __init__(self,roi,imageCollection):
#                      self.ROI1 = roi
#                      self.S2 = imageCollection
#                 def computeIndices(self,image):
#                         # Compute SARVI
#                         sarvi = image.expression('(1 + L) * float(nir - red)/ (nir + red + L)', {
#                                 'nir': image.select('B8'),
#                                 'red': image.select('B4'),
#                                 'L': 0.5
#                         }).rename('SARVI')

#                         # Compute GCI
#                         gci = image.expression('nir / green -1', {
#                                 'green': image.select('B3'),
#                                 'nir': image.select('B8')
#                         }).rename('GCI')


#                         # Compute NPCRI
#                         npcri = image.expression('((nir - red) / (nir + red)) / ((nir - blue) / (nir + blue))', {
#                                 'nir': image.select('B8'),
#                                 'red': image.select('B4'),
#                                 'blue': image.select('B2')
#                         }).rename('NPCRI')

#                         # Compute RVI
#                         rvi = image.expression('red / nir', {
#                                 'nir': image.select('B8'),
#                                 'red': image.select('B4')
#                         }).rename('RVI')

#                         # Compute EVI
#                         evi = image.expression('2.5 * float(nir - red) / (nir + 6 * red - 7.5 * blue + 1)', {
#                                 'nir': image.select('B8'),
#                                 'red': image.select('B4'),
#                                 'blue': image.select('B2')
#                         }).rename('EVI')

#                         # Compute NDVI
#                         ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

#                         # Return the image with computed indices
#                         return image.addBands([sarvi, gci, npcri, rvi, evi, ndvi])

#                 # Use .map() to apply the computeIndices function to each image in the collection
#                 collection_with_indices = S2.map(computeIndices)
#                 # Convert the Image Collection to a list
#                 image_list = collection_with_indices.toList(collection_with_indices.size())

#                 # Convert the Earth Engine List to a Python list
#                 image_list = image_list.getInfo()

#                 # Now, image_list is a Python list containing all the images
#                 # print('The image list is ', image_list)


#                 def filterCollectionByMonthYear(collection, month, year):
#                         start = ee.Date.fromYMD(year, month, 1)
#                         end = start.advance(1, 'month')
#                         filteredCollection = collection.filterDate(start, end)
#                         return filteredCollection

#                 # Select months (April, June, and July) and a range of years
#                 months = [4, 6, 7]  # April, June, and July
#                 years = list(range(2017, 2021))  # All years from 2015 to 2022

#                 # Filter the collection for selected months and years
#                 filteredCollection = []
#                 for year in years:
#                         for month in months:
#                                 print(year)
#                                 filtered = filterCollectionByMonthYear(collection_with_indices, month, year)
#                                 image = filtered.median()
#                                 date = ee.Date.fromYMD(year, month, 1)
#                                 filteredCollection.append(image.set('system:time_start', date.millis()).set('month', month).set('year', year))

#                 # Create an image collection from the filtered images
#                 filteredimageCollection = ee.ImageCollection(filteredCollection)

#                 # filteredimageCollection
#                 filteredimage = filteredimageCollection.median()
#                 band_names = filteredimage.bandNames().getInfo()
#                 print("Band names in filteredimageCollection:", band_names)
#                 # S2.median().bandNames().getInfo()
#                 def calculateMeans(self,imageCollection,date):
#                         date = ee.Date(date)
#                         imageCollection = imageCollection.filterDate(date, date.advance(1, 'month')).median()
#                         # Compute mean vegetation indices
#                         ndvi_mean = imageCollection.select('NDVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
#                         sarvi_mean = imageCollection.select('SARVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
#                         gci_mean = imageCollection.select('GCI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
#                         npcri_mean = imageCollection.select('NPCRI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
#                         rvi_mean = imageCollection.select('RVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
#                         evi_mean = imageCollection.select('EVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        
#                         mean_ndvi = ee.Number(ndvi_mean.get('NDVI')).float().getInfo()
#                         mean_sarvi = ee.Number(sarvi_mean.get('SARVI')).float().getInfo()
#                         mean_gci = ee.Number(gci_mean.get('GCI')).float().getInfo()
#                         mean_npcri = ee.Number(npcri_mean.get('NPCRI')).float().getInfo()
#                         mean_rvi = ee.Number(rvi_mean.get('RVI')).float().getInfo()
#                         mean_evi = ee.Number(evi_mean.get('EVI')).float().getInfo()
#                         print(mean_ndvi)
#                         return {'date': date.format('YYYY-MM-dd').getInfo(), 'mean_ndvi': mean_ndvi,'mean_sarvi':mean_sarvi,'mean_gci': mean_gci,'mean_npcri': mean_npcri,'mean_rvi':mean_rvi,'mean_evi':mean_evi}
#                 # Map function to extract and format the dates
#                 def extract_and_format_date(self,image):
#                         date = image.date().format('YYYY-MM-dd')
#                         return ee.Feature(None, {'date': date})
#                 # Map the function over the collection
#                 dates = collection_with_indices.map(extract_and_format_date)

#                 # Get distinct dates
#                 distinct_dates = dates.distinct('date').aggregate_array('date')

#                 # Convert the resulting list of distinct dates to a Python list
#                 dates_list = distinct_dates.getInfo()


#                 print(dates_list)
                
#                 def getDataFrame(self):
#                         data = [self.calculateMeans(self.collection_with_indices,date)for date in self.dates_list]
#                         df_all = pd.DataFrame(data).set_index('date')
#                         indecesVis = {'min': 0 ,"max": 1, 'palette': ['red','white','green']}
                        
#                         image = self.collection_with_indices.filterBounds(self.ROI1).median()
#                         self.Map.addLayer(image.select('SARVI'),indecesVis,"SARVI")
#                         self.Map.addLayer(image.select('GCI'),indecesVis,"GCI")
#                         self.Map.addLayer(image.select('RVI'),indecesVis,"RVI")
#                         self.Map.addLayer(image.select('NPCRI'),indecesVis,"NPCRI")

#                 getDataFrame()






