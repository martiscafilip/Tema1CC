import json
import requests


class SecondPage:
    def __init__(self):
        self.firstPart = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity</title>
    <style>
        .title{
            margin-top: 2vh;
            text-align: center;
            color: green;
            font: bold;
            font-size: 70px;
        }

        .activity{
            margin-top: 4vh;
            text-align: center;
            font-size: 4vw;
            margin-bottom: 4vh;
        }

        .playlist-intro{
            text-align: center;
            font-size: 30px;
            font:bold;
        }

        .email-text{
            text-align: center;
        }

        .link{
            margin: 0;
            padding: 13px;
            padding-left: 5vw;
            border: solid 1px;
            border-color: black;
            font-size: 20px;
        }
        .links{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

    </style>
</head>
<body>
    <h1 class="title">ENJOY!</h1>
    <p class="activity">"""
        self.midPart = """.</p><p class="playlist-intro">Here's a playlist of songs to listen to while doing your activity.</p>
    <hr><div class="links">"""
        self.finalPart ="""</div><br>
    <p class="email-text">We've sent an email with the activity and the music playlist to you.</p>
    </body>
    </html>"""
        self.urlList = ""
        self.urlListForEmails = []

        self.succes = "0"
        self.fail = "0"
        self.minlatency1 = "0"
        self.maxlatency1 = "0"
        self.minlatency2 = "0"
        self.maxlatency2 = "0"
        self.totalRequests = "0"
        

    def fullHTML(self):
        self.getOldMetrics()
        self.getActivity()
        self.getSongs()
        self.updateJsonFile()
        return self.firstPart + self.activity + self.midPart + self.urlList + self.finalPart

    def getActivity(self):
        url = "https://www.boredapi.com/api/activity/"
        response = requests.request("GET", url)
        responseJson = response.json()
        self.activity = responseJson["activity"]
        self.category = responseJson["type"]
        
        if(response.status_code!=200):
            self.fail = str(int(self.fail)+1)
            self.totalRequests = str(int(self.totalRequests)+1)
        else:
            self.succes = str(int(self.succes)+1)
            self.totalRequests = str(int(self.totalRequests)+1)
        if(response.elapsed.total_seconds()<float(self.minlatency1)):
            self.minlatency1 = str(response.elapsed.total_seconds())
        elif(response.elapsed.total_seconds()>float(self.maxlatency1)):
            self.maxlatency1 = str(response.elapsed.total_seconds())

        f = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\log.txt", "a")
        f.write(url + "\n")
        f.write(response.text + "\n")
        f.write("response time: " + str(response.elapsed.total_seconds()) + " secs" + "\n\n")
        f.close()

    def getSongs(self):

        urlsearch = "https://shazam.p.rapidapi.com/search"
        querystringsearch = {"term":self.category, "limit":"1"}

        headers = {
            "x-rapidapi-host": "shazam.p.rapidapi.com",
            "x-rapidapi-key": self.getApiKey(),
        }

        response = requests.request("GET", urlsearch, headers=headers, params=querystringsearch)

        if(response.status_code!=200):
            self.fail = str(int(self.fail)+1)
            self.totalRequests = str(int(self.totalRequests)+1)
        else:
            self.succes = str(int(self.succes)+1)
            self.totalRequests = str(int(self.totalRequests)+1)
        if(response.elapsed.total_seconds()<float(self.minlatency2)):
            self.minlatency2 = str(response.elapsed.total_seconds())
        elif(response.elapsed.total_seconds()>float(self.maxlatency2)):
            self.maxlatency2 = str(response.elapsed.total_seconds())

        res = response.json()
        key = res["tracks"]["hits"][0]["track"]["key"]

        f = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\log.txt", "a")
        f.write(urlsearch + json.dumps(querystringsearch) + "\n")
        f.write(response.text + "\n")
        f.write("response time: " + str(response.elapsed.total_seconds()) + " secs" + "\n\n")
        

        url = "https://shazam.p.rapidapi.com/songs/list-recommendations"
        querystring = {"key": key}

        response = requests.request("GET", url, headers=headers, params=querystring)

        urls = response.json()

        f.write(url + json.dumps(querystring) + "\n")
        f.write(response.text + "\n")
        f.write("response time: " + str(response.elapsed.total_seconds()) + " secs" + "\n\n")
        f.close()
        
        for index in range(8):
            self.urlList = self.urlList + "<a class=\"link\" href=" + urls["tracks"][index]["share"]["href"] + "\">" + urls["tracks"][index]["share"]["href"] + "</a>"
            self.urlListForEmails.append(urls["tracks"][index]["share"]["href"])
    
    def emailContent(self):
        content  = self.activity + "\n\n"
        for index in range(8):
            content = content + self.urlListForEmails[index] + "\n"
        return content 

    def getApiKey(self):
        with open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\private.json") as json_file:
            data = json.load(json_file)
        return data["api-key"]

    def getOldMetrics(self):
        with open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\metrics.json") as json_file:
            data = json.load(json_file)
            self.succes = data["succes"]
            self.fail = data["fail"]
            self.minlatency1 = data["minlatency1"]
            self.maxlatency1 = data["maxlatency1"]
            self.minlatency2 = data["minlatency2"]
            self.minlatency2 = data["maxlatency2"]
            self.totalRequests = data["totalRequests"]

    def updateJsonFile(self):
        jsonFile = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\metrics.json", "r") # Open the JSON file for reading
        data = json.load(jsonFile) # Read the JSON into the buffer
        jsonFile.close() # Close the JSON file

        ## Working with buffered content
        data["succes"]=self.succes
        data["fail"]=self.fail
        data["minlatency1"]=self.minlatency1
        data["maxlatency1"]=self.maxlatency1
        data["minlatency2"]=self.minlatency2
        data["maxlatency2"]=self.maxlatency2
        data["totalRequests"]=self.totalRequests

        ## Save our changes to JSON file
        jsonFile = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\metrics.json", "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close() 



