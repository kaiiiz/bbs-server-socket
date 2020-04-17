from dotenv import load_dotenv
import sys, os

load_dotenv()

if len(sys.argv) == 2:
    BBS_PORT = int(sys.argv[1])
else:
    BBS_PORT = int(os.getenv("BBS_SERVER_DEFAULT_PORT"))

BBS_HOST = os.getenv("BBS_SERVER_IP")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_ROOT_USERNAME")
DB_PWD = os.getenv("DB_ROOT_PWD")