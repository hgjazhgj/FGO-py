import json,time
from flask import Flask,redirect,render_template,request,url_for
import fgoKernel
from fgoLogging import getLogger
from fgoIniParser import IniParser
logger=getLogger('fgo.Web')

with open('fgoConfig.json')as f:
    config=json.load(f)
app=Flask(__name__,static_folder='fgoWebUI', template_folder='fgoWebUI')

@app.route('/')
def root():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html',device=fgoKernel.device.name)

@app.route('/api/connect',methods=['POST'])
def connect():
    fgoKernel.device=fgoKernel.Device(request.form['serial'])
    return fgoKernel.device.name

@app.route('/api/apply',methods=['POST'])
def apply():
    data=json.loads(request.form['data'])
    fgoKernel.Main.teamIndex=data['teamIndex']
    return ''

@app.route('/api/run/<action>',methods=['POST'])
def run(action):
    if not fgoKernel.device.available:
        return 'Device not available'
    getattr(fgoKernel,action)(**{i:int(j)for i,j in request.form})()
    return 'Done'

@app.route('/api/bench',methods=['POST'])
def bench():
    if not fgoKernel.device.available:
        return 'Device not available'
    return(lambda bench:f'{f"点击 {bench[0]:.2f}ms"if bench[0]else""}{", "if all(bench)else""}{f"截图 {bench[1]:.2f}ms"if bench[1]else""}')(fgoKernel.bench(15))

def main(args):
    app.run(host='0.0.0.0', port='15000')
