import ee 
import pandas as pd 
class indexCalculation():
        '''
        create the dataframe and filter the data frame from the indeces provided. 
        
        '''
        def __init__(self, imageCollection,collection_with_indices,ROI1):
                self.S2 = imageCollection
                self.collection_with_indices = collection_with_indices
                self.ROI1 = ROI1
        def getDataFrames(self):  
                # Convert the Image Collection to a list
                image_list = self.collection_with_indices.toList(self.collection_with_indices.size())

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
                        filtered = filterCollectionByMonthYear(self.collection_with_indices, month, year)
                        image = filtered.median()
                        date = ee.Date.fromYMD(year, month, 1)
                        filteredCollection.append(image.set('system:time_start', date.millis()).set('month', month).set('year', year))

                # Create an image collection from the filtered images
                filteredimageCollection = ee.ImageCollection(filteredCollection)

                # filteredimageCollection
                filteredimage = filteredimageCollection.median()
                band_names = filteredimage.bandNames().getInfo()
                print("Band names in filteredimageCollection:", band_names)
                filteredimageCollection   
                def calculateMeans(imageCollection,date):
                        print("running .....")
                        date = ee.Date(date)
                        imageCollection = imageCollection.filterDate(date, date.advance(1, 'month')).median()
                # Compute mean vegetation indices
                        ndvi_mean = imageCollection.select('NDVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        sarvi_mean = imageCollection.select('SARVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        gci_mean = imageCollection.select('GCI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        npcri_mean = imageCollection.select('NPCRI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        rvi_mean = imageCollection.select('RVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)
                        evi_mean = imageCollection.select('EVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=self.ROI1, scale=10)

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
                dates = self.collection_with_indices.map(extract_and_format_date)

                # Get distinct dates
                distinct_dates = dates.distinct('date').aggregate_array('date')

                # Convert the resulting list of distinct dates to a Python list
                dates_list = distinct_dates.getInfo()


                print(dates_list)

                data = [calculateMeans(self.collection_with_indices,date)for date in dates_list]
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
                
                return df_filtered





