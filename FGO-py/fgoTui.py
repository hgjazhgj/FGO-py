"""Textual frontend; press F1 for keyboard help."""
import cv2,locale,logging,os,sys,subprocess
from asyncio import Event,Queue as KeyQueue
from pathlib import Path
from queue import Queue,Empty
from threading import Thread
from xml.etree import ElementTree
from rich.color import Color
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal,Vertical,VerticalScroll
from textual.events import Key,Paste
from textual.screen import ModalScreen
from textual.strip import Strip
from textual.widgets import Button as TextualButton,Checkbox as TextualCheckbox,OptionList as TextualOptionList,Input,Select,RichLog,Static,TextArea,Footer
from fgoConst import VERSION
import fgoDevice,fgoKernel
from fgoMetadata import quest
logger=fgoKernel.getLogger("Tui")

class Translator:
    def __init__(self,language=None):
        self.messages={}
        if language is None:
            if os.name=="nt":
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Control Panel\International\User Profile")as key:
                        value,kind=winreg.QueryValueEx(key,"Languages")
                    if kind==winreg.REG_MULTI_SZ:language=":".join(value)
                except OSError:pass
                if not language:
                    import ctypes
                    language=locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage())
            else:
                language=next((os.environ[i]for i in("LC_ALL","LC_MESSAGES","LANG")if os.environ.get(i)),None)
                if not language or language.split(".")[0].upper()not in("C","POSIX"):language=os.getenv("LANGUAGE")or language
            language=language or locale.getlocale()[0]or"zh"
        self.language="zh"
        for name in language.split(":"):
            name=name.split(".")[0].split("@")[0].replace("-","_").split("_")[0].lower()
            if name in("c","posix"):break
            if Path(__file__).with_name(f"fgoI18n.{name}.ts").is_file():
                self.language=name
                break
        try:
            for context in ElementTree.parse(Path(__file__).with_name(f"fgoI18n.{self.language}.ts")).getroot().findall("context"):
                for item in context.findall("message"):
                    target=item.find("translation")
                    if target is not None and target.get("type")not in("unfinished","obsolete","vanished")and(target.text or"").strip():
                        self.messages[context.findtext("name"),item.findtext("source")]=target.text
        except(OSError,ElementTree.ParseError):pass
    def __call__(self,context,value):
        value="-".join(str(i)for i in value)if isinstance(value,tuple)else str(value)
        return self.messages.get((context,value),value)

def hotkey(widget,key):
    widget.hotkey=key
    return widget
def activate(widget):
    if widget.disabled:return
    if getattr(widget,"focusOnNavigation",True):widget.focus()
    match widget:
        case Button():widget.press()
        case Checkbox():widget.toggle()
        case Choice():widget.action_pick()

class Button(TextualButton):
    BINDINGS=[Binding("space","press",show=False)]
    def __init__(self,label,key,callback,focusOnNavigation=True,**kwargs):
        super().__init__(**kwargs)
        self.label=f"""{self.app.tr("fgoMainWindow",label)} ({key.upper()})"""
        self.hotkey,self.callback,self.focusOnNavigation=key,callback,focusOnNavigation

class Checkbox(TextualCheckbox):
    @property
    def BUTTON_INNER(self):return'X'if self.value else' '

class OptionList(TextualOptionList):
    def on_key(self,event):
        if self.has_focus and event.key in"1234567890":
            event.stop()
            event.prevent_default()
            index="1234567890".index(event.key)
            if index<self.option_count and not(option:=self.get_option_at_index(index)).disabled:
                if self.highlighted==index:self.post_message(self.OptionHighlighted(self,option,index))
                else:self.highlighted=index
                self.scroll_to_highlight()

class Number(Input):
    BINDINGS=[Binding("up","step(1)",show=False),Binding("down","step(-1)",show=False),Binding("space","edit",show=False,priority=True),Binding("escape","restore",show=False)]
    def __init__(self,label,key,value=0,minimum=0,maximum=114514,**kwargs):
        super().__init__(str(value),type="integer",max_length=12,select_on_focus=kwargs.pop("select_on_focus",True),**kwargs)
        self.border_title=f"""{self.app.tr("fgoMainWindow",label)} ({key.upper()})"""
        self.hotkey,self.minimum,self.maximum=key,minimum,maximum
        self.original=self.value
    @property
    def number(self):
        try:return max(self.minimum,min(self.maximum,int(self.value)))
        except ValueError:return self.minimum
    def on_focus(self):self.original=self.value
    def on_blur(self):self.value=str(self.number)
    def action_step(self,step):self.value=str(max(self.minimum,min(self.maximum,self.number+step)))
    def action_restore(self):self.value=self.original
    def action_edit(self):
        self.app.push_screen(InputDialog(str(self.border_title),self.number,self.minimum,self.maximum),lambda value:setattr(self,"value",str(value))if value is not None else None)

class Choice(Select):
    BINDINGS=[Binding(i,f"step({j})",show=False)for i,j in(("up",-1),("left",-1),("down",1),("right",1))]+[Binding(i,"pick",show=False)for i in("space","enter","alt+down")]
    def __init__(self,label,key,items=(),**kwargs):
        self.items=list(items)
        super().__init__([(text,i)for i,text in enumerate(self.items)],allow_blank=not self.items,**kwargs)
        self.border_title=f"""{self.app.tr("fgoMainWindow",label)} ({key.upper()})"""
        self.hotkey=key
    def on_mount(self):self.query_one("SelectCurrent").border_title=self.border_title
    def setItems(self,items):
        self.items=list(items)
        self.set_options([(text,i)for i,text in enumerate(self.items)])
        self.value=0 if self.items else Select.NULL
    def action_step(self,step):
        if self.items:self.value=max(0,min(len(self.items)-1,(self.value if isinstance(self.value,int)else 0)+step))
    def action_pick(self):
        if self.items:self.app.push_screen(ChoiceDialog(str(self.border_title),self.items,self.value),lambda value:setattr(self,"value",value)if value is not None else None)
    def on_select_current_toggle(self,event):
        event.stop()
        event.prevent_default()
        self.action_pick()

class Popup(ModalScreen):
    BINDINGS=[Binding("escape","cancel",show=False,priority=True)]
    def __init__(self,title,widgets,focus=None):
        super().__init__()
        self.heading,self.widgets,self.initial=self.app.tr("fgoMainWindow",title),widgets,focus
    def compose(self):
        with VerticalScroll(classes="dialog")as dialog:
            dialog.border_title=self.heading
            yield from self.widgets
    def on_mount(self):
        for widget in self.query("*"):
            if not widget.border_title:continue
            width=Text(widget.border_title).cell_len+6
            minimum=widget.styles.min_width
            if minimum is None or minimum.is_cells and minimum.value<width:widget.styles.min_width=width
        (self.initial or self.widgets[0]).focus()
    def action_cancel(self):self.dismiss(None)
    def on_button_pressed(self,event):
        event.stop()
        if isinstance(event.button,Button):self.app.invoke(event.button.callback)

class Viewer(TextArea):
    def get_content_width(self,container,viewport):return self.document.get_size(self.indent_width)[0]+self.gutter_width+1
    def get_content_height(self,container,viewport,width):
        extra=sum(widget.get_content_height(container,viewport,width)+widget.styles.gutter.height+widget.styles.margin.height for widget in self.parent.children if widget is not self)
        maximum=self.parent.styles.max_height
        height=int(maximum.resolve(viewport,viewport))if maximum is not None else viewport.height
        height-=self.parent.styles.gutter.height+self.styles.gutter.height+self.styles.margin.height+extra
        return min(super().get_content_height(container,viewport,width),max(1,height))

class MessageDialog(Popup):
    def __init__(self,title,text,question=False):
        viewer=hotkey(Viewer(str(text),read_only=True,show_line_numbers=False,soft_wrap=True,classes="viewer"),'v')
        viewer.border_title="(V)"
        yes=Button("OK",'o',lambda:self.dismiss(True))
        cancel=Button("CANCEL",'c',lambda:self.dismiss(None))if question else None
        super().__init__(title,[viewer,Horizontal(cancel,yes,classes="row")if question else yes],cancel or yes)

class InputDialog(Popup):
    def __init__(self,title,value="",minimum=None,maximum=1919810):
        self.input=Number("",'i',value,minimum,maximum)if minimum is not None else hotkey(Input(str(value),select_on_focus=True),'i')
        self.input.border_title="(I)"
        super().__init__(self.app.tr("MainWindow",title),[self.input,Horizontal(Button("CANCEL",'c',lambda:self.dismiss(None)),Button("OK",'o',self.accept),classes="row")])
    def accept(self):self.dismiss(self.input.number if isinstance(self.input,Number)else self.input.value)
    def on_input_submitted(self,event):
        event.stop()
        self.accept()

class ExecuteDialog(Popup):
    def __init__(self):
        self.input=hotkey(Viewer(tab_behavior="focus",classes="viewer"),'i')
        self.input.border_title="(I)"
        super().__init__("Execute",[self.input,Horizontal(Button("CANCEL",'c',lambda:self.dismiss(None)),Button("OK",'o',lambda:self.dismiss(self.input.text)),classes="row")])

class ChoiceDialog(Popup):
    def __init__(self,title,items,index=0):
        self.list=hotkey(OptionList(*(Text(f"{i+1}. {text}")for i,text in enumerate(items)),classes="choices"),'a')
        self.list.border_title="(A)"
        self.list.highlighted=index if isinstance(index,int)else 0
        self.number=Number("#",'n',(self.list.highlighted or 0)+1,1,len(items))
        super().__init__(title,[self.list,self.number,Horizontal(Button("CANCEL",'c',lambda:self.dismiss(None)),Button("OK",'o',self.accept),classes="row")])
    def accept(self):self.dismiss(self.number.number-1)
    def on_option_list_option_highlighted(self,event):self.number.value=str(event.option_index+1)
    def on_option_list_option_selected(self,event):
        event.stop()
        self.dismiss(event.option_index)
    def on_input_submitted(self,event):
        event.stop()
        self.accept()
    def on_key(self,event):
        if self.focused is self.list and event.key=="space":
            event.stop()
            event.prevent_default()
            self.list.action_select()

class DeviceDialog(Popup):
    def __init__(self,devices,value):
        self.devices=list(devices)
        self.input=hotkey(Input(value),'i')
        self.input.border_title=f"""{self.app.tr("MainWindow","选择或填写一个设备")} (I)"""
        self.list=hotkey(OptionList(*(Text(i)for i in self.devices),classes="choices",disabled=not self.devices),'d')
        self.list.border_title=f"""{self.app.tr("fgoMainWindow","设备")} (D)"""
        self.list.highlighted=self.devices.index(value)if value in self.devices else 0 if self.devices else None
        super().__init__("FGO-py",[self.input,self.list,Horizontal(Button("CANCEL",'c',lambda:self.dismiss(None)),Button("OK",'o',self.accept),classes="row")])
    def on_option_list_option_highlighted(self,event):
        event.stop()
        if self.list.has_focus:self.input.value=self.devices[event.option_index]
    def on_option_list_option_selected(self,event):
        event.stop()
        self.input.value=self.devices[event.option_index]
        self.input.focus()
    def accept(self):
        if text:=self.input.value.replace(" ",""):self.dismiss(text)
        else:self.input.focus()
    def on_input_submitted(self,event):
        event.stop()
        self.accept()
    def on_key(self,event):
        if self.focused is self.list and event.key in("left","right","space"):
            event.stop()
            event.prevent_default()
            {"left":self.list.action_cursor_up,"right":self.list.action_cursor_down,"space":self.list.action_select}[event.key]()

class Mapping(Popup):
    def __init__(self):
        super().__init__("加载按键映射",[Button("BACK",'c',lambda:self.dismiss(None))])
    def on_key(self,event):
        if event.key in("tab","shift+tab","enter","space","escape")or event.key.startswith(("alt+","ctrl+")):return
        event.stop()
        event.prevent_default()
        self.app.invoke(lambda:self.app.mapKey(event.key,event.character))

class Screenshot(Static,can_focus=True):
    def __init__(self,im):
        super().__init__(classes="viewer")
        self.im,self.hotkey=im,'v'
        self.previewSize,self.preview=None,[]
        self.border_title=f"""{self.app.tr("MainWindow","截图")} (V)"""
    def render_line(self,y):
        width,height=self.content_size
        if not width or not height:return Strip.blank(width,self.rich_style)
        if self.previewSize!=self.content_size:
            rows,cols=self.im.shape[:2]
            scale=min(1,width/cols,2*height/rows)
            width,height=max(1,int(cols*scale)),max(1,int(rows*scale/2))
            im=cv2.resize(self.im,(width,min(rows,2*height)),interpolation=cv2.INTER_AREA)[...,:3][...,::-1].tolist()
            color=lambda row,x:Color.from_rgb(*im[min(row,len(im)-1)][x])
            lines=[Strip([Segment('▀',Style(color=color(2*row,x),bgcolor=color(2*row+1,x)))for x in range(width)],width)for row in range(height)]
            self.preview=list(Strip.align(lines,Style(),*self.content_size,"center","middle"))
            self.previewSize=self.content_size
        return self.preview[y].apply_style(self.rich_style)

class ScreenshotDialog(Popup):
    def compose(self):
        with Vertical(classes="dialog")as dialog:
            dialog.border_title=self.heading
            yield from self.widgets

class QRCode(RichLog):
    DATA={
        "支付宝":(29,"#00A0E8",b"\xfe\xc4\x9b\xf8\x82\x02\xe2\x08\xba\x9c\x8a\xe8\xba\xd7\xd2\xe8\xba\xf5\xfa\xe8\x82\x4c\x5a\x08\xfe\xaa\xab\xf8\x00\x50\xe0\x00\xf2\x82\x64\xe8\x64\xc2\xdf\x88\x1a\x84\xc6\x30\x9d\x1c\x8a\x08\xb3\x57\xf0\x60\x1c\x71\x72\x38\xeb\x8a\x18\xb8\x78\x4b\x31\x10\x3b\x94\x0d\xd0\x35\x2f\x2c\x70\x8e\xb9\xe4\x20\x21\xca\x51\x20\x5f\x12\x4f\xe0\x00\xc8\x08\xf8\xfe\x70\x1a\xd0\x82\x65\x18\xd8\xba\x47\x6f\xa8\xba\xa3\xbc\xc8\xba\x80\x99\x28\x82\xb0\x3d\xd0\xfe\x9e\x9d\x50"),
        "微信":(29,"#22AB38",b"\xfe\x2f\x93\xf8\x82\xa5\xa2\x08\xba\x09\x82\xe8\xba\xef\xda\xe8\xba\x44\xea\xe8\x82\xdd\xea\x08\xfe\xaa\xab\xf8\x00\x71\x00\x00\xfb\xd4\x85\x50\xa9\x2d\xaf\xa8\x9a\xa3\xe0\xb0\xd9\x8a\x22\x10\xcf\x6a\x08\xb0\xb0\x41\x9d\xe8\xd7\xbd\x09\xe0\x45\x53\x8b\x10\x36\x33\xc8\x38\xb5\x8a\x6d\xe8\x96\x85\x08\xe0\x9d\x8b\x2a\xc8\xaa\x4c\x8f\xa0\x00\xe2\x98\xc8\xfe\xbd\xda\xa0\x82\x70\x88\x98\xba\xd0\xef\xf8\xba\x8d\x81\x18\xba\xe7\xe4\xb0\x82\xad\x3e\x50\xfe\xcb\x47\xa0"),
        "Monero":(37,"#000000",b"\xfe\x4f\x42\x23\xf8\x82\x99\x45\xf2\x08\xba\xf9\x4b\x92\xe8\xba\x77\x62\x12\xe8\xba\x83\x91\x5a\xe8\x82\xd5\x52\x12\x08\xfe\xaa\xaa\xab\xf8\x00\xcb\xff\x98\x00\xd3\x2f\x0f\x73\xb0\xec\x75\xe6\x83\x38\x16\xc6\x92\x82\xf8\xe5\xa5\x15\xcc\xc8\xb7\xf4\x00\x7e\xc8\x79\x1c\x7c\xb7\x48\x43\x5e\x83\x2c\x88\x50\xbc\xff\xc7\xc0\x36\x8d\x5e\x9e\x78\xb9\xea\xb4\x8a\x88\x07\xc0\x6e\xa9\xb8\x40\xd2\x44\x31\x78\xc2\x5a\x10\x43\xc0\x59\xed\xc9\xa8\x58\x8e\x62\xfa\x6b\xb8\xb8\x5e\x9c\xce\x98\x7f\xbc\xc6\x83\xb0\x5c\x89\x6c\xa3\x78\xaf\x52\x23\x47\x48\x5d\x7d\xe7\x6f\x80\xce\x20\x82\x0f\xb0\x00\xd5\xb1\x38\xa8\xfe\xa2\x2c\xea\x98\x82\x6b\x7f\x28\xb8\xba\x16\x40\x2f\xc8\xba\x99\x8b\x88\xd8\xba\x42\x98\x65\xb8\x82\xef\x25\x7d\x00\xfe\xc9\x64\x5f\xf8"),
    }
    def __init__(self,name):
        size,ink,data=self.DATA[name]
        side,stride=size+8,(size+7)//8
        super().__init__(min_width=side,wrap=False,auto_scroll=False)
        self.hotkey='v'
        self.border_title="(V)"
        self.styles.height=(side+1)//2+2
        color=lambda y,x:ink if 4<=y<size+4 and 4<=x<size+4 and data[(y-4)*stride+(x-4)//8]&(0x80>>((x-4)%8))else"#FFFFFF"
        text=Text(no_wrap=True,overflow="crop")
        for y in range(0,side,2):
            if y:text.append("\n")
            for x in range(side):text.append('▀',Style(color=color(y,x),bgcolor=color(y+1,x)))
        self.write(text,width=side)
    def get_content_width(self,container,viewport):return self.min_width

class MainWindow(App):
    TITLE="FGO-py - hgjazhgj"
    ENABLE_COMMAND_PALETTE=False
    SUSPENDED_SCREEN_CLASS="-screen-suspended"
    # Bare Alt requires terminal support; F10 also works with legacy input.
    BINDINGS=[Binding(i,"navigation",show=False,priority=True)for i in("left_alt","right_alt")]+[
        Binding("f1","help","HELP",priority=True),Binding("f10","navigation","NAV ON",priority=True),
        Binding("ctrl+c","stop","终止战斗",priority=True),Binding("ctrl+q","quit","退出",priority=True)]
    CSS="""
Screen { layout: vertical; }
#TITLE { height: 1; text-align: center; text-style: bold; }
#MENU { height: auto; }
#MENU Button { min-width: 8; width: 1fr; }
#BODY { height: 1fr; }
#MAIN { height: auto; }
.panel { width: 1fr; height: auto; padding: 0 1; }
.row { height: auto; }
.row > * { width: 1fr; }
Button { width: 1fr; min-width: 8; height: 3; }
Input, Select { width: 1fr; height: 3; }
Input, Choice > SelectCurrent { border-title-color: $foreground 60%; }
Input:focus, Choice:focus > SelectCurrent { border-title-color: transparent; }
Checkbox { width: 1fr; height: 3; }
#LBL_DEVICE { height: 3; content-align: center middle; }
#LST_QUEST { height: 1fr; min-height: 6; border: round $primary; }
#LOG { height: 1fr; min-height: 6; border: round $secondary; }
.narrow #MAIN, .narrow .row { layout: vertical; }
.narrow .panel { width: 100%; }
.tiny #MENU { layout: vertical; }
ModalScreen { align: center middle; background: $background 60%; }
ModalScreen:ansi { background: transparent; }
.dialog { width: auto; max-width: 95%; height: auto; max-height: 95%; border: $accent; background: $surface; padding: 1; }
.dialog > *, .dialog .row > * { width: 1fr; max-width: 100%; expand: optimal; }
.dialog .row { min-width: 28; }
.dialog .row > * { min-width: 0; }
.viewer { height: auto; min-height: 3; border: round $primary; }
.choices { border: round $primary; }
ScreenshotDialog > .dialog { width: 95%; height: 95%; }
ScreenshotDialog .viewer { height: 1fr; }
Screenshot { border: round $primary; content-align: center middle; }
QRCode { border: round $primary; overflow: auto; }
"""
    def __init__(self,config):
        super().__init__(ansi_color=bool(os.getenv("NO_COLOR")))
        self.config=config
        self.operation=fgoKernel.Operation()
        self.chapter=sorted({i[:2]for i in quest})
        self.tr=Translator()
        self.events=Queue()
        self.worker=self.auxWorker=None
        self.running=self.quitting=self.paused=self.auxBusy=False
        self.finished=None
        self.result=None
        self.notifier=[]
        self.appointed=0
        self.snapshot=None
        self.handlers=[]
        self.navigation=True
        self.keys=KeyQueue()
        self.keyWorker=None
    def build(self):
        self.MENU=[Button(label,key,lambda name=name:self.menu(name))for name,label,key in(
            ("file","文件",'f'),("script","程序",'p'),("settings","设置",'s'),("control","控制",'c'),("about","关于",'h'))]
        self.CBB_CHAPTER=Choice("章节",'a',[self.tr("quest",i)for i in self.chapter],id="CBB_CHAPTER")
        self.CBB_QUEST=Choice("关卡",'q',id="CBB_QUEST")
        self.TXT_TIMES=Number("次数",'n',1,id="TXT_TIMES")
        self.BTN_QUESTADD=Button("+",'i',self.questAdd,focusOnNavigation=False)
        self.BTN_QUESTREMOVE=Button("-",'d',self.questRemove,focusOnNavigation=False)
        self.BTN_QUESTUP=Button("↑",'u',lambda:self.questMove(-1),focusOnNavigation=False)
        self.BTN_QUESTDOWN=Button("↓",'j',lambda:self.questMove(1),focusOnNavigation=False)
        self.BTN_QUESTCLEAR=Button("×",'e',self.questClear,focusOnNavigation=False)
        self.BTN_QUESTLOAD=Button("从每周任务载入",'w',lambda:self.runFunc(self.loadWeekly))
        self.TXT_TEAM=Number("编队",'t',self.config.teamIndex,maximum=15,id="TXT_TEAM")
        self.CKB_TEAM=hotkey(Checkbox(f"""{self.tr("fgoMainWindow","自动编队")} (O)""",id="CKB_TEAM"),'o')
        self.CBB_APPLE=Choice("苹果",'y',[self.tr("fgoMainWindow",i)for i in("金","银","青","铜","彩")],id="CBB_APPLE")
        self.TXT_APPLE=Number("要吃的苹果数量",'z',id="TXT_APPLE")
        self.LBL_DEVICE=Static(self.tr("MainWindow","未连接设备"),id="LBL_DEVICE")
        self.BTN_CONNECT=Button("更改",'v',self.connectDevice)
        self.BTN_MAIN=Button("肝!",'g',self.runMain)
        self.BTN_BATTLE=Button("完成战斗",'b',lambda:self.runFunc(fgoKernel.Battle()))
        self.BTN_CLASSIC=Button("陈年老肝",'r',self.runClassic)
        self.BTN_PAUSE=Button("挂起战斗",'k',self.pause,disabled=True)
        self.BTN_STOP=Button("终止战斗",'x',self.stop,disabled=True)
        self.BTN_STOPLATER=Button("预约终止",'l',self.stopLater,disabled=True)
        self.BTN_SCREENSHOT=Button("检查截图",'m',self.screenshot)
        self.LST_QUEST=hotkey(OptionList(id="LST_QUEST"),'[')
        self.LST_QUEST.border_title=f"""{self.tr("fgoMainWindow","关卡队列")} ([)"""
        self.LST_QUEST.tooltip="1-9/0: #1-10; Enter/Space: # → Enter"
        self.LOG=hotkey(RichLog(id="LOG",min_width=1,wrap=True,max_lines=500),']')
        self.LOG.border_title="Log (])"
        for widget,text in(
            (self.TXT_TIMES,"加入关卡队列后生效,0为不限制次数"),
            (self.TXT_TEAM,"所选编队在队伍编成界面的位置,从左到右1-10,0为不切换编队"),
            (self.CBB_APPLE,"要吃的苹果种类"),(self.TXT_APPLE,"要吃的苹果数量"),(self.BTN_CONNECT,"连接到设备"),
            (self.BTN_QUESTADD,"新增"),(self.BTN_QUESTREMOVE,"删除"),(self.BTN_QUESTUP,"上移"),(self.BTN_QUESTDOWN,"下移"),(self.BTN_QUESTCLEAR,"清空"),
            (self.BTN_MAIN,"在关卡列表界面将要刷的关卡置于第一个来清空体力,或是依次执行关卡队列中的关卡"),
            (self.BTN_BATTLE,"完成当前战斗"),(self.BTN_CLASSIC,"基于经典战斗的清空体力"),(self.BTN_PAUSE,"暂停/继续战斗"),
            (self.BTN_STOP,"立刻终止战斗"),(self.BTN_STOPLATER,"在完成若干场战斗后终止战斗"),(self.BTN_SCREENSHOT,"检查截图确定连接建立"),
        ):widget.tooltip=self.tr("fgoMainWindow",text)
        self.idle=[self.BTN_MAIN,self.BTN_BATTLE,self.BTN_CLASSIC,self.BTN_QUESTLOAD,self.MENU[1],self.BTN_CONNECT,self.BTN_QUESTADD,self.BTN_QUESTREMOVE,self.BTN_QUESTUP,self.BTN_QUESTDOWN,self.BTN_QUESTCLEAR,self.TXT_TEAM,self.CKB_TEAM,self.CBB_APPLE,self.TXT_APPLE]
    def compose(self):
        self.build()
        self.title=self.tr("fgoMainWindow",self.TITLE)
        yield Static(self.title,id="TITLE",markup=False)
        yield Horizontal(*self.MENU,id="MENU")
        with VerticalScroll(id="BODY"):
            with Horizontal(id="MAIN"):
                with Vertical(classes="panel"):
                    yield self.CBB_CHAPTER
                    yield self.CBB_QUEST
                    yield self.TXT_TIMES
                    yield Horizontal(self.BTN_QUESTADD,self.BTN_QUESTREMOVE,classes="row")
                    yield Horizontal(self.BTN_QUESTUP,self.BTN_QUESTDOWN,self.BTN_QUESTCLEAR,classes="row")
                    yield self.BTN_QUESTLOAD
                with Vertical(classes="panel"):
                    yield Horizontal(self.TXT_TEAM,self.CKB_TEAM,classes="row")
                    yield Horizontal(self.CBB_APPLE,self.TXT_APPLE,classes="row")
                    yield Horizontal(self.LBL_DEVICE,self.BTN_CONNECT,classes="row")
                    yield self.BTN_MAIN
                    yield Horizontal(self.BTN_BATTLE,self.BTN_PAUSE,self.BTN_SCREENSHOT,classes="row")
                    yield Horizontal(self.BTN_CLASSIC,self.BTN_STOP,self.BTN_STOPLATER,classes="row")
            yield self.LST_QUEST
            yield self.LOG
        yield Footer()
    def on_mount(self):
        self.screen_stack[0].screen_layout_refresh_signal.subscribe(self,self.refreshBackground)
        for key,action,text in(("f1","help","HELP"),("ctrl+c","stop","终止战斗"),("ctrl+q","quit","退出")):
            self._bindings.get_bindings_for_key(key)[:]=[Binding(key,action,self.tr("fgoMainWindow",text),priority=True)]
        if os.getenv("NO_COLOR"):self.theme="ansi-dark"
        self.begin_capture_print(self)
        for log in[logging.getLogger()]+[i for i in logging.Logger.manager.loggerDict.values()if isinstance(i,logging.Logger)]:
            for handler in log.handlers:
                if isinstance(handler,logging.StreamHandler)and not isinstance(handler,logging.FileHandler)and handler.stream in(sys.__stdout__,sys.__stderr__):
                    self.handlers.append((handler,handler.stream))
                    handler.setStream(sys.stderr)
        fgoKernel.Main.teamIndex=self.TXT_TEAM.number
        fgoKernel.Main.autoFormation=False
        fgoKernel.schedule.stopOnDefeated(self.config.stopOnDefeated)
        fgoKernel.schedule.stopOnKizunaReisou(self.config.stopOnKizunaReisou)
        self.questQuery(0)
        self.resizeLayout(self.size.width)
        self.set_interval(.1,self.flush)
        self.call_after_refresh(self.connectDevice)
    def on_unmount(self):
        for handler,stream in self.handlers:handler.setStream(stream)
        try:self.end_capture_print(self)
        except KeyError:pass
    def on_print(self,event):self.LOG.write(Text.from_ansi(event.text.rstrip()))
    def resizeLayout(self,width):
        self.screen_stack[0].set_class(width<96,"narrow")
        self.screen_stack[0].set_class(width<48,"tiny")
    def on_resize(self,event):self.resizeLayout(event.size.width)
    def refreshBackground(self,_):
        for screen in self.screen_stack[1:]:screen.refresh()
    def updateNavigation(self):
        label=f"""NAV {"ON"if self.navigation else"OFF"}"""
        bindings=self._bindings.get_bindings_for_key("f10")
        if bindings[0].description==label:return
        bindings[:]=[Binding("f10","navigation",label,priority=True)]
        self.screen_stack[0].refresh_bindings()
    def action_navigation(self):
        self.navigation=not self.navigation
        self.updateNavigation()
    async def on_event(self,event):
        if isinstance(event,(Key,Paste))and not event.is_forwarded:
            self.keys.put_nowait(event)
            if self.keyWorker is None:self.keyWorker=self.run_worker(self.dispatchKeys())
            return
        await super().on_event(event)
    async def dispatchKeys(self):
        while True:
            event=await self.keys.get()
            await self.dispatchKey(event)
            # Finish key bindings, then the change/submission messages they emit.
            target=self.focused or self.screen
            for _ in range(2):
                for widget in(target,*target.ancestors):
                    processed=Event()
                    if widget.call_later(processed.set):await processed.wait()
            self.keys.task_done()
    async def dispatchKey(self,event):
        # Intercept navigation before Input, TextArea or Mapping consumes a key.
        if isinstance(event,Key)and self.navigation and event.is_printable and event.key!="space"and event.character not in"0123456789":
            key=event.character.lower()
            for widget in self.screen.query("*"):
                if getattr(widget,"hotkey",None)==key and not widget.disabled and widget.display and widget.visible:
                    self.invoke(lambda:activate(widget))
                    break
            else:self.bell()
            return
        await super().on_event(event)
    def action_quit(self):self.askQuit()
    def action_stop(self):self.stop()if self.running else self.askQuit()
    def action_help(self):self.help()
    def invoke(self,func):
        try:return func()
        except Exception as e:
            logger.exception(e)
            self.message("FGO-py",repr(e))
    def on_button_pressed(self,event):
        if isinstance(event.button,Button):
            event.stop()
            self.invoke(event.button.callback)
    def on_key(self,event):
        if len(self.screen_stack)==1 and self.focused is self.LST_QUEST and event.key=="space":
            event.stop()
            event.prevent_default()
            self.selectQuest()
    def on_option_list_option_selected(self,event):
        if event.option_list is self.LST_QUEST:
            event.stop()
            self.selectQuest()
    def on_select_changed(self,event):
        if not isinstance(event.value,int):return
        if event.select is self.CBB_CHAPTER:self.questQuery(event.value)
        elif event.select is self.CBB_APPLE:self.operation.appleKind=event.value
    def on_input_changed(self,event):
        if self.running or not event.input.value:return
        if event.input is self.TXT_TEAM:self.config.teamIndex=fgoKernel.Main.teamIndex=self.TXT_TEAM.number
        elif event.input is self.TXT_APPLE:self.operation.appleTotal=self.TXT_APPLE.number
    def on_checkbox_changed(self,event):
        if event.checkbox is self.CKB_TEAM:fgoKernel.Main.autoFormation=event.value
        elif hasattr(event.checkbox,"callback"):self.invoke(lambda:event.checkbox.callback(event.value))
    def message(self,title,text):self.push_screen(MessageDialog(title,text))
    def prompt(self,title,value,callback,minimum=None,maximum=1919810):
        self.push_screen(InputDialog(title,value,minimum,maximum),lambda value: self.invoke(lambda:callback(value))if value is not None else None)
    def confirm(self,title,text,callback):self.push_screen(MessageDialog(title,text,True),lambda ok:self.invoke(callback)if ok else None)

    def questQuery(self,index):
        self.quest=[i for i in quest if self.chapter and i[:2]==self.chapter[index]]
        self.CBB_QUEST.setItems([self.tr("quest",i)for i in self.quest])
    def questAdd(self):
        if not self.running and isinstance(self.CBB_QUEST.value,int):
            self.operation.append((self.quest[self.CBB_QUEST.value],self.TXT_TIMES.number))
            self.flush()
            self.LST_QUEST.highlighted=len(self.operation)-1
    def questRemove(self):
        if not self.running and(cur:=self.LST_QUEST.highlighted)is not None and 0<=cur<len(self.operation):
            del self.operation[cur]
            self.flush()
    def questMove(self,step):
        if not self.running and(cur:=self.LST_QUEST.highlighted)is not None and 0<=cur<len(self.operation)and 0<=cur+step<len(self.operation):
            self.operation[cur],self.operation[cur+step]=self.operation[cur+step],self.operation[cur]
            self.flush()
            self.LST_QUEST.highlighted=cur+step
    def questClear(self):
        if not self.running:self.operation.clear()
    def questText(self,item):
        key,count=item
        return f"""{count:5}× {self.tr("quest",key[:2])}=={self.tr("quest",key)}"""
    def selectQuest(self):
        if self.operation:self.push_screen(ChoiceDialog("关卡队列",[self.questText(i)for i in list(self.operation)],self.LST_QUEST.highlighted or 0),lambda index:setattr(self.LST_QUEST,"highlighted",min(index,len(self.operation)-1))if index is not None and self.operation else None)
    def loadWeekly(self):self.operation.extend(fgoKernel.weeklyMission())
    def runMain(self):
        self.operation.battleClass=fgoKernel.Battle
        self.runFunc(self.operation)
    def runClassic(self):pass
    def isDeviceAvailable(self):
        if fgoDevice.device.available:return True
        self.message("FGO-py",self.tr("MainWindow","未连接设备"))
        return False
    def runFunc(self,func,device=True):
        if self.running or self.quitting or self.auxBusy:return
        if device and not self.isDeviceAvailable():return
        self.operation.appleTotal=self.TXT_APPLE.number
        self.operation.appleKind=self.CBB_APPLE.value
        self.config.teamIndex=fgoKernel.Main.teamIndex=self.TXT_TEAM.number
        fgoKernel.schedule.reset()
        self.funcBegin()
        def work():
            result,msg=None,"Done"
            try:result=func()
            except fgoKernel.ScriptStop as e:
                logger.critical(e)
                msg=str(e)
            except BaseException as e:
                logger.exception(e)
                msg=repr(e)
            finally:
                try:result=getattr(func,"result",result)
                except Exception:logger.debug("No complete result",exc_info=True)
                for reset in(fgoKernel.fuse.reset,fgoKernel.schedule.reset):
                    try:reset()
                    except Exception:logger.exception("Reset failed")
                if self.config.notifyEnable:
                    for notify in self.notifier:
                        try:
                            if not notify(msg):logger.error("Notify post failed")
                        except Exception:logger.exception("Notify post failed")
                self.events.put(("done",(msg,result)))
        self.worker=Thread(target=work,name="TuiWorker")
        try:self.worker.start()
        except BaseException:
            self.running=False
            self.updateControls()
            raise
    def funcBegin(self):
        self.running=True
        self.paused=False
        self.appointed=0
        self.updateControls()
    def updateControls(self):
        for widget in self.idle:widget.disabled=self.running or self.quitting
        for widget in(self.BTN_PAUSE,self.BTN_STOP,self.BTN_STOPLATER):widget.disabled=not self.running or self.quitting
        self.BTN_PAUSE.variant="success"if self.paused else"default"
        self.BTN_STOPLATER.variant="success"if self.appointed else"default"
    def funcEnd(self,msg,result):
        self.result=result
        self.TXT_APPLE.value=str(self.operation.appleTotal)
        self.running=self.paused=False
        self.appointed=0
        self.updateControls()
        if self.config.notifyEnable:self.bell()
        if not self.quitting:self.message(msg,self.resultText(result))
    def asyncCall(self,func,callback):
        if self.quitting or self.auxBusy:return
        self.auxBusy=True
        def work():
            try:self.events.put(("callback",(callback,func())))
            except Exception as e:
                logger.exception(e)
                self.events.put(("error",repr(e)))
        self.auxWorker=Thread(target=work,name="TuiDevice")
        try:self.auxWorker.start()
        except BaseException:
            self.auxBusy=False
            raise
    def flush(self):
        for _ in range(100):
            try:kind,value=self.events.get_nowait()
            except Empty:break
            match kind:
                case"done":self.finished=value
                case"callback":
                    if self.auxWorker:self.auxWorker.join()
                    self.auxBusy=False
                    if not self.quitting:self.invoke(lambda:value[0](value[1]))
                case"error":
                    if self.auxWorker:self.auxWorker.join()
                    self.auxBusy=False
                    if not self.quitting:self.message("FGO-py",value)
        if self.finished is not None and not self.worker.is_alive():
            self.worker.join()
            value,self.finished=self.finished,None
            self.funcEnd(*value)
        if self.running:self.TXT_APPLE.value=str(self.operation.appleTotal)
        if(snapshot:=list(self.operation))!=self.snapshot:
            self.snapshot=snapshot
            cur=self.LST_QUEST.highlighted or 0
            self.LST_QUEST.clear_options().add_options([Text(f"{i+1}. {self.questText(item)}")for i,item in enumerate(snapshot)])
            if snapshot:self.LST_QUEST.highlighted=min(cur,len(snapshot)-1)
        text=Text(getattr(fgoDevice.device,"name",None)or self.tr("MainWindow","未连接设备"))
        if self.LBL_DEVICE.content!=text:self.LBL_DEVICE.update(text)
        if self.quitting and not self.running and not(self.auxWorker and self.auxWorker.is_alive()):self.exit()
    def pause(self):
        if not self.running:return
        if self.paused and not self.isDeviceAvailable():return
        fgoKernel.schedule.pause()
        self.paused=not self.paused
        self.updateControls()
    def stop(self):
        if self.running:fgoKernel.schedule.stop("Stop Command Effected")
    def stopLater(self):
        if not self.running:return
        if self.appointed:
            fgoKernel.schedule.stopLater()
            self.appointed=0
            self.updateControls()
        else:
            def apply(value):
                if self.running:
                    self.appointed=value
                    fgoKernel.schedule.stopLater(value)
                    self.updateControls()
            self.prompt("剩余的战斗数量",1,apply,1)
    def askQuit(self):
        if self.quitting:return
        if self.running or self.auxWorker and self.auxWorker.is_alive():self.confirm("FGO-py",self.tr("MainWindow","战斗正在进行,确认关闭?"),self.quit)
        else:self.quit()
    def quit(self):
        self.quitting=True
        if self.running:fgoKernel.schedule.stop("Quit")
        self.updateControls()
        self.flush()
    def join(self):
        if self.worker and self.worker.is_alive():
            fgoKernel.schedule.stop("TUI closed")
            self.worker.join()
        if self.auxWorker and self.auxWorker.is_alive():self.auxWorker.join()
    def connectDevice(self):
        if self.running:return
        def show(devices):
            self.push_screen(DeviceDialog(devices,self.config.device),lambda name:self.invoke(lambda:connect(name))if name else None)
        def connect(name):
            def work():
                self.config.device=name
                fgoDevice.device=fgoDevice.Device(name)
            self.asyncCall(work,lambda _:self.isDeviceAvailable())
        self.asyncCall(fgoDevice.Device.enumDevices,show)
    def screenshot(self):
        if self.isDeviceAvailable():self.asyncCall(fgoKernel.XDetect,self.showScreenshot)
    def showScreenshot(self,chk):
        def save():
            if chk.save():self.pop_screen()
        self.push_screen(ScreenshotDialog("Screenshot",[Screenshot(chk.im),Horizontal(Button("BACK",'c',lambda:self.pop_screen()),Button("SAVE",'s',save),classes="row")]))
    def setting(self,key,value):
        self.config[key]=value
        if callable(func:=getattr(fgoKernel.schedule,key,None)):func(value)
    def menu(self,name):
        widgets=[]
        def button(label,key,func,disabled=False,tooltip=None):widgets.append(Button(label,key,func,disabled=disabled,tooltip=self.tr("fgoMainWindow",tooltip)if tooltip else None))
        def check(label,key,setting):
            widget=hotkey(Checkbox(f"""{self.tr("fgoMainWindow",label)} ({key.upper()})""",value=self.config[setting]),key)
            widget.callback=lambda value:self.setting(setting,value)
            widgets.append(widget)
        def run(func):
            self.pop_screen()
            self.runFunc(func)
        match name:
            case"file":
                button("资源管理器",'e',lambda:openPath(Path(__file__).parent))
                button("退出",'x',self.askQuit)
            case"script":
                for label,key,func,tooltip in(
                    ("抽友情",'f',"fpSummon","先抽一发友情十连,在结算界面运行本功能"),("抽奖池",'l',"lottery",None),("清理邮箱",'m',"mail",None),
                    ("强化",'s',"synthesis","在选择了强化对象未选择强化材料的界面运行本功能"),("召唤记录",'h',"summonHistory","统计导出召唤记录,在抽卡记录页面运行"),
                ):button(label,key,lambda func=func:run(getattr(fgoKernel,func)),self.running,tooltip)
                button("搓丸子",'e',self.expBall,tooltip="把若干张低星礼装合并成一个")
            case"settings":
                check("战败撤退时终止战斗",'d',"stopOnDefeated")
                check("获得羁绊礼装时终止战斗",'k',"stopOnKizunaReisou")
                button("若干特殊掉落后终止战斗",'s',lambda:self.prompt("剩余的特殊掉落数量",max(0,getattr(fgoKernel.schedule,"_Schedule__stopOnSpecialDropCount",0)),fgoKernel.schedule.stopOnSpecialDrop,0))
            case"control":
                button("加载按键映射",'k',self.openMapping)
                button("调整为16:9",'i',lambda:self.deviceAction("invoke169"),self.running)
                button("恢复原分辨率",'o',lambda:self.deviceAction("revoke169"),self.running)
                check("消息推送",'n',"notifyEnable")
                button("Bench",'b',lambda:run(fgoKernel.bench),self.running)
                button("Execute",'e',self.execute,self.running)
            case"about":
                button("关于FGO-py",'a',self.about)
                button("使用许可",'l',lambda:self.message("使用许可",(Path(__file__).resolve().parent.parent/"LICENSE").read_text(encoding="utf-8")))
        button("BACK",'c',lambda:self.pop_screen())
        self.push_screen(Popup(dict(file="文件",script="程序",settings="设置",control="控制",about="关于")[name],widgets))
    def deviceAction(self,name):
        if not self.running and self.isDeviceAvailable():self.asyncCall(lambda:getattr(fgoDevice.device,name)(),lambda _:None)
    def openMapping(self):
        if self.isDeviceAvailable():self.push_screen(Mapping())
    def mapKey(self,key,char):
        table={"left":'\x25',"up":'\x26',"right":'\x27',"down":'\x28',"backspace":'\x08','-':'\xbd','=':'\xbb','\\':'\xdc',';':'\xba','\'':'\xde',',':'\xbc','.':'\xbe','/':'\xbf'}
        value=chr(0x6f+int(key[1:]))if key.startswith("f")and key[1:].isdigit()else table.get(key,table.get(char,char.upper()if char else""))
        try:fgoDevice.device.press(value)
        except KeyError:pass
    def execute(self):
        def run(text):
            if not text.strip():return
            self.pop_screen()
            self.runFunc(lambda:exec(text,dict(fgoKernel=fgoKernel,fgoDevice=fgoDevice,self=self)),False)
        self.push_screen(ExecuteDialog(),lambda text:self.invoke(lambda:run(text))if text is not None else None)
    def resultText(self,result):
        tr=lambda text:self.tr("MainWindow",text)
        sentence=lambda *parts:(" "if self.tr.language=="en"else"").join(tr(i)for i in parts)
        lines=[]
        match result:
            case{"type":"Battle"}:lines.append(sentence(result["turn"],"回合完成战斗")+", "+sentence("用时",duration(result["time"])))
            case{"type":"Main"}:
                lines.append(sentence("在过去的",duration(result["time"]),"中完成了",result["battle"],"场战斗"))
                lines.append(sentence("平均每场战斗",f"""{result["turnPerBattle"]:.1f}""","回合")+", "+sentence("用时",f"""{result["timePerBattle"]//60:.0f}:{result["timePerBattle"]%60:04.1f}"""))
            case{"type":"SummonHistory"}:lines.extend((sentence("获取到",result["value"],"条抽卡记录")+", "+tr("图片保存至"),str(result["file"])))
            case{"type":"Bench"}:lines.append(", ".join(f"{tr(i)} {result[j]:.2f}ms"for i,j in(("点击","touch"),("截图","screenshot"))))
        if isinstance(result,dict)and"material"in result:lines+=[tr("获得了以下素材")+":"]+([f"""{self.tr("material",i)} × {j}"""for i,j in result["material"].items()]or[tr("无")])
        return"\n".join(lines)
    def expBall(self):
        self.message("FGO-py","\n".join(self.tr("MainWindow",i)for i in(
            "搓丸子是一个基于FGO-py的独立项目","https://github.com/hgjazhgj/FGO-ExpBall",
            "你看见了这个弹窗,说明你已经能够运行FGO-py了","那么,无需任何其他配置,你可以直接运行FGO-ExpBall",
        )))
    def about(self):
        tr=lambda text:self.tr("MainWindow",text)
        dialog=MessageDialog("FGO-py - About",f"""FGO-py
{tr("全自动免配置跨平台开箱即用的FGO助手")}
{tr("当前版本")}: {VERSION}
{tr("作者")}: hgjazhgj
{tr("项目主页")}: https://fgo-py.hgjazhgj.top/
{tr("QQ群")}: 932481680 ({tr("请按readme指引操作")})
https://github.com/sponsors/hgjazhgj/
https://patreon.com/hgjazhgj
https://paypal.me/hgjazhgjpp""")
        dialog.widgets.insert(1,Horizontal(*(Button(tr(name),key,lambda name=name:self.showQRCode(name))for name,key in(("支付宝",'a'),("微信",'w'),("Monero",'m'))),classes="row"))
        self.push_screen(dialog)
    def showQRCode(self,name):
        self.push_screen(Popup(self.tr("MainWindow",name),[QRCode(name),Button("BACK",'c',lambda:self.pop_screen())]))
    def help(self):
        self.message("HELP","\n".join(self.tr("MainWindow",text)for text in(
            "F10：进入/退出按键导航；终端能上报独立 Alt 时也可用 Alt 切换",
            "导航模式：按括号内按键操作按钮、复选框、展开下拉框或聚焦控件；打开和关闭弹窗后保持导航",
            "导航模式：数字可直接输入，输入其他内容前先退出导航",
            "Tab / Shift+Tab：切换焦点",
            "Enter / Space：操作按钮；Space：切换复选框、展开下拉框",
            "列表：获得焦点后，1–9 选中前九项，0 选中第十项；不存在的项目忽略",
            "下拉框：方向键切换；展开后可聚焦编号框 (N) 输入编号，Enter 确认",
            "数值框：直接输入；左右移动光标，上下加减；Space 弹窗编辑，Esc 恢复原值",
            "弹窗：Esc 取消；导航模式下 C 取消、O 确认",
            "Ctrl+Q：退出；Ctrl+C：停止任务",
        )))

def duration(seconds):return f"{int(seconds)//3600}:{int(seconds)//60%60:02}:{int(seconds)%60:02}"
def openPath(path):
    path=str(Path(path).resolve())
    if os.name=="nt":os.startfile(path)
    else:subprocess.Popen(["open"if sys.platform=="darwin"else"xdg-open",path],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main(config):
    assert sys.stdin.isatty()
    app=MainWindow(config)
    try:app.run()
    finally:app.join()
