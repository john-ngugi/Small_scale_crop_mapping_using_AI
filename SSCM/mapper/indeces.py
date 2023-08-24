import ee 

class indexCalculation:

    def __init__(self,imageCollection,band3,band4,band8,band2):
        self.imageCollection = imageCollection
        self.band3 = band3
        self.band4 = band4
        self.band8 = band8
        self.band2 = band2

    def get_indeces(self,image):
        # Compute SARVI
        sarvi = image.expression('(1 + L) * float(nir - red)/ (nir + red + L)', {
                'nir': image.select('B8'),
                'red': image.select('B4'),
                'L': 0.5}).rename('SARVI')
        
        # Compute GCI
        gci = image.expression('green - red / green + red', {
                'green': image.select('B3'),
                'red': image.select('B4')}).rename('GCI')
        
        # Compute NPCRI
        npcri = image.expression('((nir - red) / (nir + red)) / ((nir - blue) / (nir + blue))', {
            'nir': image.select('B8'),
            'red': image.select('B4'),
            'blue': image.select('B2')
        }).rename('NPCRI')
        
        # Compute RVI
        rvi = image.expression('red / nir', {
                'nir': image.select('B8'),
                'red': image.select('B4')}).rename('RVI')
        
        # Compute EVI
        evi = image.expression('2.5 * float(nir - red) / (nir + 6 * red - 7.5 * blue + 1)', {
                'nir': image.select('B8'),
                'red': image.select('B4'),
                'blue': image.select('B2')}).rename('EVI')
        
        newBands = ee.Image([evi, npcri,gci,rvi,sarvi]);       
        return image.addBands(newBands)    












