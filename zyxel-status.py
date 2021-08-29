import requests
import argparse
import urllib3
import json
from flask import Flask

urllib3.disable_warnings()

def login(username,password,ip):
    headers = {'Accept-Language' : 'en',}
    url = "http://"+ip+"/login/login-page.cgi"
    data = {'AuthName':username, 'AuthPassword':password}
    try:
        r = requests.post(url,data=data,headers=headers,verify=False) 
    except ConnectionError as e:
        print("Connection Error:{}".format(e))
    
    cookie = r.cookies.get_dict()['SESSION']
    return cookie

def get_dsl_stats(cookie,ip):
    headers = {'Accept-Language' : 'en', 'Cookie':'SESSION='+cookie}
    url = "http://"+ip+"/pages/systemMonitoring/xdslStatistics/GetxdslStatistics.html"
    try:
        r = requests.get(url,headers=headers,verify=False)
    except ConnectionError as e:
        print("Connection Error: {}".format(e))
    d = {}
    for line in r.iter_lines():
        l = line.decode('UTF-8')
        if '=' not in l:
            k,v = '',''
            if ':' in l:
                k = l.split(':',1)[0].lstrip().replace(" ","")
                v = l.split(':',1)[1].lstrip().replace("\t", " ")
                d[k] = v
                if k == 'LOM':
                    break
    return d,r.text

def run_http(username,password,modemip,listen_host,listen_port):
    app = Flask(__name__)
    @app.route('/')
    def ret_data():
        cookie = login(username,password,modemip)
        data = get_dsl_stats(cookie,modemip)
        return json.dumps(data[0])
    
    app.run(threaded=True,host=listen_host,port=listen_port)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--username','-u',nargs="?",default='admin')
    parser.add_argument('--password','-p',nargs="?",default='admin')
    parser.add_argument('--http',action="store_true")
    parser.add_argument('--modem_ip',nargs="?", default='192.168.1.254')
    parser.add_argument('--listen_port',nargs="?", default='8080')
    parser.add_argument('--listen_ip',nargs="?",default='localhost')
    parser.add_argument('--text',action="store_true")
    args = parser.parse_args()

    if args.http:
        exit(run_http(args.username,args.password,args.modem_ip,args.listen_ip,args.listen_port))
    if args.text:
        cookie = login(args.username,args.password,args.modem_ip)    
        exit(print(get_dsl_stats(cookie,args.modem_ip)[1]))
    else:
        cookie = login(args.username,args.password,args.modem_ip)
        exit(print(json.dumps(get_dsl_stats(cookie,args.modem_ip)[0])))
