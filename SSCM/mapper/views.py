from django.shortcuts import render
import geemap.foliumap as geemap
import keys 
import ee 
import json 

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

    context= {
        'map': Map
    }
    return render(request,'base.html',context)
