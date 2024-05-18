"Ingrex parser deal with message"
from datetime import datetime, timedelta
import json

''' Gedesic stuf '''
from geographiclib.geodesic import Geodesic
import math
geod = Geodesic.WGS84

class Message(object):
    "Message object"
    def __init__(self, raw_msg):
        self.raw = raw_msg
        self.guid = raw_msg[0]
        self.timestamp = raw_msg[1]
        seconds, millis = divmod(raw_msg[1], 1000)
        time = datetime.fromtimestamp(seconds) + timedelta(milliseconds=millis)
        #self.time = time.strftime('%Y/%m/%d %H:%M:%S:%f')
        self.timestamp_str = time.strftime('%Y/%m/%d %H:%M:%S:%f')[:-3]
        self.time_iso = time.isoformat()
        self.time = time.strftime('%H:%M')
        self.date = time.strftime('%Y/%m/%d')
        self.text = raw_msg[2]['plext']['text']
        self.type = raw_msg[2]['plext']['plextType']
        self.team = raw_msg[2]['plext']['team']
        self.is_link = raw_msg[2]['plext']['markup'][1][1]['plain'].count('linked') > 0
        self.is_controlfield = raw_msg[2]['plext']['markup'][1][1]['plain'].count('created a Control Field') > 0
        self.is_destroy = raw_msg[2]['plext']['markup'][1][1]['plain'].count('destroyed a Resonator') > 0
        self.is_deploy = raw_msg[2]['plext']['markup'][1][1]['plain'].count('deployed a Resonator') > 0
        self.is_virus = (self.is_destroy and 
                (raw_msg[2]['plext']['markup'][0][1]['team'] == raw_msg[2]['plext']['markup'][2][1]['team']))
        
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class ControlFieldMessage(Message):
    "ControlFieldMessage Object"
    def __init__(self, raw_msg):
        Message.__init__(self, raw_msg)
        self.portal = raw_msg[2]['plext']['markup'][2]
        self.latE6 = raw_msg[2]['plext']['markup'][2][1]['latE6']
        self.lngE6 = raw_msg[2]['plext']['markup'][2][1]['lngE6']
        self.portal_permalink = 'https://intel.ingress.com/intel?ll={0},{1}&z=15&pll={0},{1}'.format(self.latE6/1E6, self.lngE6/1E6)
        self.mu = int(raw_msg[2]['plext']['markup'][4][1]['plain'],10)
        if raw_msg[2]['plext']['markup'][3] == '-' :
          self.mu = self.mu * -1
        
class LinkMessage(Message):
    "LinkMessage Object"
    def __init__(self, raw_msg):
        Message.__init__(self, raw_msg)
        self.portal = raw_msg[2]['plext']['markup'][2]
        self.latE6 = raw_msg[2]['plext']['markup'][2][1]['latE6']
        self.lngE6 = raw_msg[2]['plext']['markup'][2][1]['lngE6']
        self.portal_permalink = 'https://intel.ingress.com/intel?ll={0},{1}&z=15&pll={0},{1}'.format(self.latE6/1E6, self.lngE6/1E6)
        self.target_portal = raw_msg[2]['plext']['markup'][4]
        self.target_latE6 = raw_msg[2]['plext']['markup'][4][1]['latE6']
        self.target_lngE6 = raw_msg[2]['plext']['markup'][4][1]['lngE6']
        self.target_permalink = 'https://intel.ingress.com/intel?ll={0},{1}&z=15&pll={0},{1}'.format(self.target_latE6/1E6, self.target_lngE6/1E6)
       
      
class Entity(object):
    "Entity object"
    def __init__(self, raw_entity):
        self.raw = raw_entity
        self.guid = raw_entity[0]
        self.is_controlfield = self.guid.endswith('.b')
        self.is_link = self.guid.endswith('.9')
        self.is_portal = self.guid.endswith('.16')
        self.timestamp = raw_entity[1]
        seconds, millis = divmod(raw_entity[1], 1000)
        time = datetime.fromtimestamp(seconds) + timedelta(milliseconds=millis)
        #self.time = time.strftime('%Y/%m/%d %H:%M:%S:%f')
        self.timestamp_str = time.strftime('%Y/%m/%d %H:%M:%S:%f')[:-3]
        self.time = time.strftime('%H:%M')
        self.date = time.strftime('%Y/%m/%d')
        #self.typecode = raw_entity[2][0]
        #self.type = self.__typecodeToType__(self.typecode)
        if self.is_controlfield :
            self.p1latE6, self.p1lngE6 = raw_entity[2][2][0][1], raw_entity[2][2][0][2]
            self.p2latE6, self.p2lngE6 = raw_entity[2][2][1][1], raw_entity[2][2][1][2]
            self.p3latE6, self.p3lngE6 = raw_entity[2][2][2][1], raw_entity[2][2][2][2]   
            self.polygonE6 = [[self.p1latE6, self.p1lngE6],[self.p2latE6, self.p2lngE6],[self.p3latE6, self.p3lngE6]]
            self.polygon = [[self.p1latE6/1E6, self.p1lngE6/1E6],[self.p2latE6/1E6, self.p2lngE6/1E6],[self.p3latE6/1E6, self.p3lngE6/1E6]]
            p = geod.Polygon()
            for pnt in self.polygon :
                p.AddPoint(pnt[0], pnt[1])
            self.num, self.perim, self.area = p.Compute()
            #self.mu_per_qm = self.mu / self.area
        self.faction = raw_entity[2][1]
        # self.object = raw_entity[2]
        
    # def __typecodeToType__(self, tc):
        # if tc == 'r': return 'Regtangle'
        # if tc == 'p': return 'Portal'
        # if tc == 'e': return 'Entity'
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
