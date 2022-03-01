from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import pprint
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from secondPage import SecondPage
from urllib.parse import unquote
import re

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path =="/favicon.ico"):
            pass
        if(self.path == "/metrics"):
            self.send_response(200)
            self.send_header('Content-type','text/json')
            self.end_headers()

            jsonFile = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\metrics.json", "r") # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
            data2 = json.dumps(data)
            jsonFile.close() # Close the JSON file
            self.wfile.write(bytes(data2, 'utf-8'))
            
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            file_to_open = open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\home.html").read()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        builder = SecondPage()

        self.wfile.write(bytes(builder.fullHTML(), "utf-8"))

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

            
        temp = unquote(post_body)
        email = temp[6:-11]
        print(email)

        CLIENT_SECRET_FILE = 'client_secret.json'
        API_NAME = 'gmail'
        API_VERSION = 'v1'
        SCOPES = ['https://mail.google.com/']
        service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

        emailMsg = builder.emailContent()
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] = email
        mimeMessage['subject'] = 'Activity and Music for you boredom.'
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

        message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        print(message)


    def metrics(self):
        # temp = SecondPage()
        # url = "https://www.boredapi.com/api/activity/"
        # response = requests.request("GET", url)
        # responseText = response.text

        # urlsearch = "https://shazam.p.rapidapi.com/search"
        # querystringsearch = {"term":"trending", "limit":"1"}

        # headers = {
        #     "x-rapidapi-host": "shazam.p.rapidapi.com",
        #     "x-rapidapi-key": temp.getApiKey(),
        # }

        # responseKey = requests.request("GET", urlsearch, headers=headers, params=querystringsearch)

        # res = responseKey.json()
        # key = res["tracks"]["hits"][0]["track"]["key"]


        # url = "https://shazam.p.rapidapi.com/songs/list-recommendations"
        # querystring = {"key": key}

        # response = requests.request("GET", url, headers=headers, params=querystring)

        # return responseText + "\n\n\n\n" + responseKey.text + "\n\n\n\n" + response.text


        # texttt = '''response time: 0.515844 secs
        # response time: 0.515844 secs'''

        # with open("C:\\Users\\Filip Martisca\\Desktop\\CC\\Tema1\\log.txt") as logFile:
        #     times = re.findall("^response.*secs$", texttt)
        # print(times)
        # return "Hola"
        pass
      

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")