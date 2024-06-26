"Map Utils"
from math import pi, sin, cos, tan, asin, radians, sqrt, log, acos

def calc_tile(lat, lng, zoomlevel):
    tilecounts = [1,1,1,40,40,80,80,320,1E3,2E3,2E3,4E3,8E3,16E3,16E3,32E3]
    rlat = radians(lat)
    tilecount = tilecounts[zoomlevel]
    xTile = int((lng + 180.0) / 360.0 * tilecount)
    yTile = int((1.0 - log(tan(rlat) + 1 / cos(rlat)) / pi) / 2.0 * tilecount)
    return yTile, xTile

def calc_field_to_tiles(field):
    north = field['maxLatE6']
    east = field['maxLngE6']
    south = field['minLatE6']
    west = field['minLngE6']
    minxtile, minytile = calc_tile(north/1E6, west/1E6, 15)
    maxxtile, maxytile = calc_tile(south/1E6, east/1E6, 15)
    return minxtile, maxxtile, minytile, maxytile
    
    
def calc_dist(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    # km = 6378.137 * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1))
    dlat = lat1 - lat2
    dlng = lng1 - lng2
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2* asin(sqrt(a))
    m = 6378.137 * c * 1000
    # m = km * 1000
    return round(m)

def calc_dist_hires(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    km = 6378.137 * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lng2 - lng1))
    # dlat = lat1 - lat2
    # dlng = lng1 - lng2
    # a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    # c = 2* asin(sqrt(a))
    # m = 6367.0 * c * 1000
    m = km * 1000
    return round(m)

def trans_point_to_field(lat, lng, radius_km) :
#todo
    r = radius_km * 1000
    a = 180 * radius_km / (6378.137 * pi);
    minlat = lat - a
    maxlat = lat + a
    minlng = lng - a
    maxlng = lng + a
    field = {
        'minLngE6':round(minlng * 1E6),
        'minLatE6':round(minlat * 1E6),
        'maxLngE6':round(maxlng * 1E6),
        'maxLatE6':round(maxlat * 1E6),
    }
    return field
        
        
    
    
def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

def transform(wgLat, wgLon):
    """
    transform(latitude,longitude) , WGS84
    return (latitude,longitude) , GCJ02
    """
    a = 6378137.0
    ee = 0.00669342162296594323
    if (outOfChina(wgLat, wgLon)):
        mgLat = wgLat
        mgLon = wgLon
        return mgLat,mgLon
    dLat = transformLat(wgLon - 105.0, wgLat - 35.0)
    dLon = transformLon(wgLon - 105.0, wgLat - 35.0)
    radLat = wgLat / 180.0 * pi
    magic = sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi)
    dLon = (dLon * 180.0) / (a / sqrtMagic * cos(radLat) * pi)
    mgLat = wgLat + dLat
    mgLon = wgLon + dLon
    return mgLat,mgLon

def outOfChina(lat, lon):
    if (lon < 72.004 or lon > 137.8347):
        return True
    if (lat < 0.8293 or lat > 55.8271):
        return True
    return False

def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(abs(x))
    ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * sin(y * pi) + 40.0 * sin(y / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * sin(y / 12.0 * pi) + 320 * sin(y * pi / 30.0)) * 2.0 / 3.0
    return ret

def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x))
    ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
    ret += (20.0 * sin(x * pi) + 40.0 * sin(x / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * sin(x / 12.0 * pi) + 300.0 * sin(x / 30.0 * pi)) * 2.0 / 3.0
    return ret
    
def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    a = 6378245.0
    ee = 0.00669342162296594323
    dlat = transformLat(lng - 105.0, lat - 35.0)
    dlng = transformLon(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
