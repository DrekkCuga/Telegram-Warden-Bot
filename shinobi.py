import requests

class Shinobi:
    def __init__(self, hostname, apikey, groupkey):
        self.hostname = hostname
        self.apikey = apikey
        self.groupkey = groupkey
        self.url = f"http://{hostname}/{apikey}/"
    
    def getMonitors(self):
        resp = requests.get(self.url + "monitor/" + self.groupkey)
        return resp.json()
        
    def getMonitorNames(self):
        names = []
        for m in self.getMonitors():
            names.append(m["name"])
        return names
    
    def getMonitorIdByName(self, name):
        monitors = self.getMonitors()
        for m in monitors:
            if m["name"] == name:
                return m["mid"]
        return ""
    
    def getSnapshot(self, monitorID):
        url = self.url + f"jpeg/{self.groupkey}/{monitorID}/s.jpg"
        resp = requests.get(url)
        return resp.content


def main():
    from PIL import Image
    from io import BytesIO
    
    API_KEY = "Zmy1NNlxUNHgt5BVwdCxC2FTHSx44E"
    GROUP_KEY = "2CGDqeZ6Bh"
    shi = Shinobi("nvr.local.nargacu.ga", API_KEY, GROUP_KEY)
    stream = BytesIO()
    stream.write(shi.getSnapshot("jwGdhvWIlk80"))
    stream.seek(0)
    
    img = Image.open(stream)
    img.show()

if __name__ == "__main__":
    main()