from flask import Flask, request, Response
import os
import requests
import logging
import cherrypy
import paste.translogger
import json
from sesamutils import Dotdictify

app = Flask(__name__)
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('SOLTEQ-Service')

with open("banner.txt", 'r', encoding='utf-8') as banner:
    logger.error(banner.read())
logger.error("")

Susername = os.getenv("username")
Spassword = os.getenv("password")
Spayload = {"logonId": Susername, "logonPassword": Spassword}
offset = 0
url = ""
# WCToken = ""
# WCTrustedToken = ""

env = os.getenv("env")
limit = os.getenv("batch_size")

def get_auth():
    loginurl = env +"wcs/resources/store/1/loginidentity"
    logger.info(loginurl)
    # logger.info(json.dumps(Spayload))
    getauth = requests.post(loginurl, json=Spayload)
    if getauth.status_code == 201:
        logger.info("Login successful (code: "+ str(getauth.status_code) + ")")
    else:
        logger.info("Unsuccessful login. (code: "+ str(getauth.status_code) + ")\n" + str(getauth.text))
    gettoken = json.loads(getauth.text)
    headers = {"WCToken": gettoken['WCToken'], "WCTrustedToken": gettoken['WCTrustedToken']}

    return headers

def stream_as_json(generator_function):
    first = True
    yield '['
    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(item)
    yield ']'

def get_all(offset=offset, url=url):
    try:
        headers = get_auth()
        
        # headers = get_auth(headers) #{"WCToken": WCToken, "WCTrustedToken": WCTrustedToken}
        nestedpath = "items" #request.args.get("nestedpath") having nested path hardcoded as this will probably not change.
        count = 0

        while True:
            param = f'?offset={offset}&limit={limit}'
            logger.info(f"Fetching data from url: {url + param}")
            req = requests.get(url + param, headers=headers)
            logger.info("Status get: "+ str(req.status_code))
            data = json.loads(req.text)
            # logger.info(data)

            for item in data[f'{nestedpath}']:
                i = dict(item)
                try:
                    i["_id"] = str(item['id'])
                    i["id"] = str(item['id'])
                    # i["memberId"] = str(item['memberId'])
                    i["_updated"] = offset
                except Exception as e:
                    logger.error(f"ERROR: {e}")
                yield i
                count +=1

            # if (data.get('next') is None):
            #     logger.info("no more pages, breaking")
            #     break
            if len(data[f'{nestedpath}']) == 0:
                logger.info("no more items, breaking")
                break
            else: 
                offset += int(limit)
            
        else:
            raise ValueError(f'value object expected in response to url: {url} got {req}')

        logger.info(f'Yielded: {count}. Since set to {offset}')
    except Exception as e:
        logger.error(f"def get_addresses issue: {e}")
       
@app.route("/<route>", methods=['GET'])
def entities(route):
    try:
        if (route == "addresses"):
            url = env+"rest/admin/v2/addresses"
        elif (route == "organizations"):
            url = env+"rest/admin/v2/organizations/manageable"
        else: 
            logger.error(f"Route ({route}) not found!")
            return (f"Route ({route}) not found!")
        if request.args.get('since') is     None:
            offset = 0
            # logger.info("since value is set to page " + str(page))
        else:
            offset = request.args.get('since')
            # offset = int(since) #-1
            # logger.info("since/page set to " + str(page))
        return Response(stream_as_json(get_all(offset, url)), mimetype='application/json')
    except Exception as e:
        logger.error(f"def entities issue: {e}")


@app.route("/<route>/new_version", methods=['POST'])
def entities(route):
    if (route == "addresses"):
        entities = request.get_json()
        logger.info("Receiving entities")
        if not isinstance(entities,list):
            entities = [entities]
        for entity in entities:
            url = f"rest/admin/v2/addresses/{entities['_id']}/new-version"
            logger.info(url)

        url = env+"rest/admin/v2/addresses"
    else:
        logger.error(f"Route ({route}) not found!")
        return (f"Route ({route}) not found!")



if __name__ == '__main__':
    format_string = '%(name)s - %(levelname)s - %(message)s'
    # Log to stdout, change to or add a (Rotating)FileHandler to log to a file
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    # Comment these two lines if you don't want access request logging
    app.wsgi_app = paste.translogger.TransLogger(app.wsgi_app, logger_name=logger.name,
                                                 setup_console_handler=False)
    app.logger.addHandler(stdout_handler)

    logger.propagate = False
    log_level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))  # default log level = INFO
    logger.setLevel(level=log_level)
    cherrypy.tree.graft(app, '/')
    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        'environment': 'production',
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()