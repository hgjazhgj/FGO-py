import base64,cv2,json,time
from flask import Flask,redirect,render_template,request,url_for
import fgoDevice
import fgoKernel
from fgoLogging import getLogger
from fgoTeamupParser import IniParser
logger=getLogger('Web')

teamup=IniParser('fgoTeamup.ini')
app=Flask(__name__,static_folder='fgoWebUI',template_folder='fgoWebUI')

@app.route('/')
def root():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html',teamups=teamup.sections(),config=config,device=fgoDevice.device.name)

@app.route('/api/connect',methods=['POST'])
def connect():
    fgoDevice.device=fgoDevice.Device(request.form['serial'],config['package'])
    return fgoDevice.device.name

@app.route('/api/teamup/load',methods=['POST'])
def teamupLoad():
    return {i:eval(j)for i,j in teamup[request.form['teamName']].items()}

@app.route('/api/teamup/save',methods=['POST'])
def teamupSave():
    teamup[request.form['teamName']]=json.loads(request.form['data'])
    with open('fgoTeamup.ini','w')as f:
        teamup.write(f)
    return ''

@app.route('/api/apply',methods=['POST'])
def apply():
    data=json.loads(request.form['data'])
    fgoKernel.Main.teamIndex=data['teamIndex']
    fgoKernel.ClassicTurn.skillInfo=data['skillInfo']
    fgoKernel.ClassicTurn.houguInfo=data['houguInfo']
    fgoKernel.ClassicTurn.masterSkill=data['masterSkill']
    return ''

@app.route('/api/run/main',methods=['POST'])
def runMain():
    if not fgoDevice.device.available:
        return 'Device not available'
    fgoKernel.Main(**{i:int(j)for i,j in request.form.items()})()
    return 'Done'

@app.route('/api/run/battle',methods=['POST'])
def runBattle():
    if not fgoDevice.device.available:
        return 'Device not available'
    fgoKernel.Battle()()
    return 'Done'

@app.route('/api/run/classic',methods=['POST'])
def runClassic():
    if not fgoDevice.device.available:
        return 'Device not available'
    fgoKernel.Main(**{i:int(j)for i,j in request.form.items()},battleClass=lambda:fgoKernel.Battle(fgoKernel.ClassicTurn))()
    return 'Done'

@app.route('/api/pause',methods=['POST'])
def pause():
    fgoKernel.schedule.pause()

@app.route('/api/stop',methods=['POST'])
def stop():
    fgoKernel.schedule.stop()

@app.route('/api/stopLater',methods=['POST'])
def stopLater():
    fgoKernel.schedule.stopLater(int(request.form['value']))

@app.route('/api/screenshot',methods=['POST'])
def screenshot():
    if not fgoDevice.device.available:
        return 'Device not available'
    return base64.b64encode(cv2.imencode('.png',fgoKernel.Detect().im)[1].tobytes())

@app.route('/api/bench',methods=['POST'])
def bench():
    if not fgoDevice.device.available:
        return 'Device not available'
    return(lambda bench:f'{f"点击 {bench[0]:.2f}ms"if bench[0]else""}{", "if all(bench)else""}{f"截图 {bench[1]:.2f}ms"if bench[1]else""}')(fgoKernel.bench(15))

def main(config):
    globals()['config']=config
    app.run(host='0.0.0.0', port='15000')
