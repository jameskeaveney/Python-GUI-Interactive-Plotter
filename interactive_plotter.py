#!/usr/bin/env python
import matplotlib
matplotlib.use('WxAgg')
import pylab
pylab.ioff()

from matplotlib import rc
rc('text', usetex=False)
rc('font',**{'family':'serif'})

import wx, os, sys, csv
from numpy import arange,array,pi,zeros,append,std

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2WxAgg as Toolbar

#sys.path.append('/Users/xbnv46/Documents/Programming/IO')
#from smoothing import smoothTriangle as smooth
#from filters import *
#from databin import bin2 as bin

#filters
from scipy.fftpack import ifft, fft, fftfreq
from numpy import random
def Amp_dist(E,Ef):
	return ((1+(E/Ef)**2)**0.5)**(-1)
	
def lowpass(t,S,cutoff):
	tstep=t[1]-t[0]
	F = fft(S)
	freq = fftfreq(len(t),tstep)
	Foriginal = F
	
	print freq.max(),freq.min()

	for i in range(len(freq)):
		if freq[i]<-cutoff or freq[i]>cutoff: F[i]=0.	
	
	Sout = ifft(F)
	Sout = array(Sout)
	return Sout

def better_lowpass(t,S,cutoff):
	tstep=t[1]-t[0]
	F = fft(S)
	freq = fftfreq(len(t),tstep)
	Foriginal = F
	
	DD = Amp_dist(freq,cutoff)
	F = F * DD
	
	Sout = ifft(F)
	Sout = array(Sout)
	return Sout

def highpass(t,S,cutoff):
	tstep=t[1]-t[0]
	F = fft(S)
	freq = fftfreq(len(t),tstep)
	Foriginal = F
	
	print freq.max(),freq.min()

	for i in range(len(freq)):
		if freq[i]>-cutoff and freq[i]<cutoff: F[i]=0.	
	
	Sout = ifft(F)
	
	return Sout

def bandstop(t,S,lowcut,highcut):
	tstep=t[1]-t[0]
	F = fft(S)
	freq = fftfreq(len(t),tstep)
	Foriginal = F
	
	print freq.max(),freq.min()

	for i in range(len(freq)):
		if (freq[i]<-lowcut and freq[i]>-highcut) or (freq[i]>lowcut and freq[i]<highcut): F[i]=0.	
	
	Sout = ifft(F)
	
	return Sout

def bandpass(t,S,lowcut,highcut):
	tstep=t[1]-t[0]
	F = fft(S)
	freq = fftfreq(len(t),tstep)
	Foriginal = F
	
	print freq.max(),freq.min()

	for i in range(len(freq)):
		if (freq[i]>-lowcut and freq[i]<lowcut) or 		freq[i]>highcut or freq[i]<-highcut: F[i]=0.	
	
	Sout = ifft(F)
	
	return Sout#,freq,F,Foriginal

#Moving average smoothing
def smooth(data,degree,dropVals=False):
        """performs moving triangle smoothing with a variable degree."""
        """note that if dropVals is False, output length will be identical
        to input length, but with copies of data at the flanking regions"""
        triangle=array(range(degree)+[degree]+range(degree)[::-1])+1
        smoothed=[]
        for i in range(degree,len(data)-degree*2):
                point=data[i:i+len(triangle)]*triangle
                smoothed.append(sum(point)/sum(triangle))
        if dropVals: return smoothed
        smoothed=[smoothed[0]]*(degree+degree/2)+smoothed

        j = len(data)-len(smoothed)
        if j%2==1:
                for i in range(0,(j-1)/2):
                        smoothed.append(data[-1-(j-1)/2+i])
                        smoothed.insert(0,data[(j-1)/2-i])
                smoothed.append(data[-1])
        else:
                for i in range(0,j/2):
                        smoothed.append(data[-1-i])
                        smoothed.insert(0,data[i])
        #print j,len(data),len(smoothed)
        return array(smoothed)

#CSV reading
def read(filename,spacing=0,columns=2):
	f=open(filename,'U')
	fid=[]
	for line in f:
		fid.append(line)
	f.close()
	# -1: ignore last (blank) line in csv file (lecroy)
	fid = fid[spacing:-1]
	inData=csv.reader(fid,delimiter=',')
	# spacing : skips lines if needed (e.g., on oscilloscope files)
	
	data=[]
	for i in range(0,columns): data.append([])
	
	for row in inData:
		for i in range(0,columns):
			data[i].append(float(row[i]))
	
	for i in range(0,columns):
		data[i] = array(data[i])
		
	return data

#Data Binning
def bin(x,y,blength):
	if blength % 2 == 0: 
		print '!!!!!!'
		print 'CAUTION: bin length not an odd number. errors likely to occur!'
		print '!!!!!!'
	nobins = len(x)/blength
	xmid = (blength-1)/2
	xbinmax = nobins*blength - xmid
	a=0
	binned=zeros((nobins,3))
	xout,yout,yerrout = array([]),array([]),array([])
	for i in range(int(xmid),int(xbinmax),int(blength)):
		xmin=i-int(xmid)
		xmax=i+int(xmid)
		xout=append(xout,sum(x[xmin:xmax+1])/blength)
		yout=append(yout,sum(y[xmin:xmax+1])/blength)
		yerrout=append(yerrout,std(y[xmin:xmax+1]))
	return xout,yout,yerrout
        
class MainWin(wx.Frame):
	def __init__(self,parent,title):
		wx.Frame.__init__(self,None,title=title,size=(1200,600))
		self.Bind(wx.EVT_CLOSE,self.OnExit)
				
###  Statusbar at the bottom of the window
		self.CreateStatusBar()

		panel = wx.Panel(self)
		
###  Text window (readonly) for outputting information (debug)
###  Command line for custom commands on the fly
		#cmdlbl = wx.StaticText(panel,label='Command-Line: ')
		#cmd = wx.TextCtrl(panel,style=wx.TE_PROCESS_ENTER)
		#self.Bind(wx.EVT_TEXT_ENTER,self.OnCommand,cmd)
		
		# H sizer:
		#cmline = wx.BoxSizer(wx.HORIZONTAL)
		#cmline.Add(cmdlbl,0,wx.EXPAND)
		#cmline.Add(cmd,1,wx.EXPAND)
		
		#indents for sizers
		Lindent = 60
		Rindent = 80

### Signal processing: smoothing
		SP_label = wx.StaticText(panel,label='Signal processing:',style=wx.ALIGN_CENTRE)
		font = wx.Font(14,wx.DEFAULT, wx.NORMAL,wx.NORMAL)
		SP_label.SetFont(font)
		
		# H sizer:
		SP_sizer = wx.BoxSizer(wx.HORIZONTAL)
		SP_sizer.Add((Lindent-15,-1),0,wx.EXPAND)
		SP_sizer.Add(SP_label,0,wx.EXPAND)	
		SP_sizer.Add((10,-1),1,wx.EXPAND)

#moving avg:
		smth_label = wx.StaticText(panel,label='Moving average smoothing')
		self.smooth_amount = 11
		smth_amount_label = wx.StaticText(panel,label='Factor:')
		smth_amount_box = wx.TextCtrl(panel,value='11',style=wx.TE_PROCESS_ENTER,size=(50,-1))
		self.Bind(wx.EVT_TEXT,self.OnSmoothCtrl,smth_amount_box)
		smth_button = wx.Button(panel,wx.ID_ANY,"Smooth data",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnSmoothBtn,smth_button)
		#H sizer:
		smth_sizer = wx.BoxSizer(wx.HORIZONTAL)
		smth_sizer.Add((Lindent,-1),0,wx.EXPAND)
		smth_sizer.Add(smth_label,0,wx.EXPAND)
		smth_sizer.Add((10,-1),1,wx.EXPAND)
		smth_sizer.Add(smth_amount_label,0,wx.EXPAND)
		smth_sizer.Add(smth_amount_box,0,wx.EXPAND)
		smth_sizer.Add((10,-1),0,wx.EXPAND)
		smth_sizer.Add(smth_button,0,wx.EXPAND)
		smth_sizer.Add((Rindent,-1),0,wx.EXPAND)

#binning:
		self.bin_amount = 11
		bin_label = wx.StaticText(panel,label='Data binning')
		bin_label.SetToolTip(wx.ToolTip("Bin large arrays into smaller array, by the chosen factor"))
		bin_amount_label = wx.StaticText(panel,label='Factor (Odd!):')
		bin_amount_box = wx.TextCtrl(panel,value='11',style=wx.TE_PROCESS_ENTER,size=(50,-1))
		self.Bind(wx.EVT_TEXT,self.OnBinCtrl,bin_amount_box)
		bin_button = wx.Button(panel,wx.ID_ANY,"Bin data",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnBinBtn,bin_button)
		
		bin_sizer = wx.BoxSizer(wx.HORIZONTAL)
		bin_sizer.Add((Lindent,-1),0,wx.EXPAND)
		bin_sizer.Add(bin_label,0,wx.EXPAND)
		bin_sizer.Add((10,-1),1,wx.EXPAND)
		bin_sizer.Add(bin_amount_label,0,wx.EXPAND)
		bin_sizer.Add(bin_amount_box,0,wx.EXPAND)
		bin_sizer.Add((10,-1),0,wx.EXPAND)
		bin_sizer.Add(bin_button,0,wx.EXPAND)
		bin_sizer.Add((Rindent,-1),0,wx.EXPAND)
		
#filtering:
		Filter_label = wx.StaticText(panel,label='Frequency filters')
		
		freq_select = [1e0,1e3,1e6,1e9]
		freq_labels = ['Hz','kHz','MHz','GHz']
		self.dd = dict(Hz=1.,kHz=1e3,MHz=1e6,GHz=1e9)
		
		self.LPa = 1.
		LP_amount_label = wx.StaticText(panel,label='Low frequency cutoff:')
		LP_amount_box = wx.TextCtrl(panel,value='1', 
				style=wx.TE_PROCESS_ENTER)
		self.Bind(wx.EVT_TEXT,self.OnLPCtrl,LP_amount_box)

		self.LPm = 'kHz'
		self.LP_amount = self.LPa * self.dd[self.LPm]
		self.LPmult = wx.ComboBox(panel,value='kHz', 
			choices=freq_labels,style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX,self.OnLPmult,self.LPmult)

		self.HPa = 1.
		HP_amount_label = wx.StaticText(panel,label='High frequency cutoff:')
		
		HP_amount_box = wx.TextCtrl(panel,value='1',style=wx.TE_PROCESS_ENTER)
		self.Bind(wx.EVT_TEXT,self.OnHPCtrl,HP_amount_box)

		self.HPm = 'kHz'
		self.HP_amount = self.HPa * self.dd[self.HPm]
		self.HPmult = wx.ComboBox(panel,value='kHz', 
			choices=freq_labels,style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX,self.OnHPmult,self.HPmult)

		freq_tooltip = "Filter the y-axis (assuming x-axis is time) using hard-edge Fourier transform frequency filters"
		for item in [HP_amount_label,LP_amount_label,
					HP_amount_box,LP_amount_box,self.LPmult,
					self.HPmult,Filter_label]:
			item.SetToolTip(wx.ToolTip(freq_tooltip))
		
		LP_button = wx.Button(panel,wx.ID_ANY,"Low-Pass",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnLPBtn,LP_button)
		LP_button.SetToolTip(wx.ToolTip("Filter out high-frequency noise"))
		HP_button = wx.Button(panel,wx.ID_ANY,"High-Pass",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnHPBtn,HP_button)
		HP_button.SetToolTip(wx.ToolTip("Filter out low-frequency noise/offset"))
		BP_button = wx.Button(panel,wx.ID_ANY,"Band-Pass",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnBPBtn,BP_button)
		BP_button.SetToolTip(wx.ToolTip("Pass (retain) only the frequencies between low and high"))
		BS_button = wx.Button(panel,wx.ID_ANY,"Band-Stop",size=(150,-1))
		self.Bind(wx.EVT_BUTTON,self.OnBSBtn,BS_button)
		BS_button.SetToolTip(wx.ToolTip("Block only the frequencies between low and high. Also commonly called a 'notch' filter"))

	#filter sizer:
		filter_sizerV = wx.BoxSizer(wx.VERTICAL)
		
		t1_sizer = wx.BoxSizer(wx.HORIZONTAL)
		t1_sizer.Add((Lindent,-1),0,wx.EXPAND)
		t1_sizer.Add(Filter_label)
		t1_sizer.Add((30,-1),1,wx.EXPAND)
		t1_sizer.Add(LP_amount_label,0,wx.EXPAND)
		t1_sizer.Add(LP_amount_box,0,wx.EXPAND)
		t1_sizer.Add((10,-1),0,wx.EXPAND)
		t1_sizer.Add(self.LPmult,0,wx.EXPAND)
		t1_sizer.Add((Rindent,-1),0,wx.EXPAND)

		t2_sizer = wx.BoxSizer(wx.HORIZONTAL)
		t2_sizer.Add((Lindent,-1),0,wx.EXPAND)
		t2_sizer.Add((10,-1),1,wx.EXPAND)
		t2_sizer.Add((30,-1),1,wx.EXPAND)
		t2_sizer.Add(HP_amount_label,0,wx.EXPAND)
		t2_sizer.Add(HP_amount_box,0,wx.EXPAND)
		t2_sizer.Add((10,-1),0,wx.EXPAND)
		t2_sizer.Add(self.HPmult,0,wx.EXPAND)
		t2_sizer.Add((Rindent,-1),0,wx.EXPAND)
				
		t3_sizer = wx.BoxSizer(wx.HORIZONTAL)
		t3_sizer.Add((Lindent,-1),1,wx.EXPAND)
		t3_sizer.Add(LP_button,0,wx.EXPAND)
		t3_sizer.Add((20,-1),0,wx.EXPAND)
		t3_sizer.Add(HP_button,0,wx.EXPAND)
		t3_sizer.Add((Rindent,-1),0,wx.EXPAND)

		t4_sizer = wx.BoxSizer(wx.HORIZONTAL)
		t4_sizer.Add((Lindent,-1),1,wx.EXPAND)
		t4_sizer.Add(BP_button,0,wx.EXPAND)
		t4_sizer.Add((20,-1),0,wx.EXPAND)
		t4_sizer.Add(BS_button,0,wx.EXPAND)
		t4_sizer.Add((Rindent,-1),0,wx.EXPAND)

		filter_sizerV.Add(t1_sizer,0,wx.EXPAND)
		filter_sizerV.Add((-1,5),0,wx.EXPAND)
		filter_sizerV.Add(t2_sizer,0,wx.EXPAND)
		filter_sizerV.Add((-1,5),0,wx.EXPAND)
		filter_sizerV.Add(t3_sizer,0,wx.EXPAND)
		filter_sizerV.Add((-1,5),0,wx.EXPAND)
		filter_sizerV.Add(t4_sizer,0,wx.EXPAND)
		
		filter_sizerH = wx.BoxSizer(wx.HORIZONTAL)
		filter_sizerH.Add(filter_sizerV,1,wx.EXPAND)
		
#Plot panel - canvas and toolbar
		self.fig = pylab.figure(1,(4.5/2,3./2),80)
		self.ax = self.fig.add_subplot(111)
		self.fig.subplots_adjust(bottom=0.16)
		
		self.canvas = FigureCanvasWxAgg(panel, wx.ID_ANY, self.fig)
		self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
		
		# V sizer:
		plotpanel = wx.BoxSizer(wx.VERTICAL)
		plotpanel.Add(self.canvas, 1, wx.LEFT|wx.RIGHT|wx.GROW,border=0)
		plotpanel.Add(self.toolbar, 0, wx.LEFT|wx.RIGHT|wx.EXPAND,border=0)
				
#Buttons / button bar
		btnsize=30
		openrawfilebutton = wx.Button(panel,label="Open Raw File",size=(-1,btnsize))
		self.Bind(wx.EVT_BUTTON,self.OnOpenRawFile,openrawfilebutton)
		openrawfilebutton.SetToolTip(wx.ToolTip("Open a file from an oscilloscope, with some preamble at the start of the file (configured for LeCroy files)"))
		
		openprocfilebutton = wx.Button(panel,label="Open Processed File",size=(-1,btnsize))
		self.Bind(wx.EVT_BUTTON,self.OnOpenProcFile,openprocfilebutton)
		openprocfilebutton.SetToolTip(wx.ToolTip("Open a csv file with two columns and no additional formatting"))
		
		resetbutton = wx.Button(panel,wx.ID_ANY,'Revert',size=(-1,btnsize))
		self.Bind(wx.EVT_BUTTON,self.OnReset,resetbutton)
		resetbutton.SetToolTip(wx.ToolTip("Revert to originally loaded data set"))
		exitbutton = wx.Button(panel,wx.ID_ANY,"Exit",size=(-1,btnsize))
		self.Bind(wx.EVT_BUTTON,self.OnExit,exitbutton)
				
#Clear Figure, Axis Labels, Axis Text Size

		PP_label = wx.StaticText(panel,label='Plot parameters:',style=wx.ALIGN_CENTRE)
		font = wx.Font(14,wx.DEFAULT, wx.NORMAL,wx.NORMAL)
		PP_label.SetFont(font)
		# H sizer:
		PP_sizer = wx.BoxSizer(wx.HORIZONTAL)
		PP_sizer.Add((Lindent-15,-1),0,wx.EXPAND)
		PP_sizer.Add(PP_label,0,wx.EXPAND)	
		PP_sizer.Add((10,-1),1,wx.EXPAND)


		#initialise plot param values
		self.xsize=18; self.ysize=18
		self.xlabel=''; self.ylabel=''
		self.holdgraph=False
		self.ticklabelsize=13
		
		#create list of strings to use as sizelist
		sizelist = arange(8,33).tolist()
		for i in range(0,len(sizelist)): sizelist[i]=str(sizelist[i])		

		
		#xlabels and sizes
		xl = wx.StaticText(panel, label="X-Axis Label: ")
		self.xlab = wx.TextCtrl(panel, value="")
		xfsl = wx.StaticText(panel,label="Size: ")
		self.xfs = wx.ComboBox(panel,value='18', choices=sizelist,style=wx.CB_READONLY)
		self.Bind(wx.EVT_TEXT,self.xtext,self.xlab)
		self.Bind(wx.EVT_CHAR,self.xchange,self.xlab)		
		self.Bind(wx.EVT_COMBOBOX,self.OnXfs,self.xfs)
		
		#ylabels and sizes
		yl = wx.StaticText(panel, label="Y-Axis Label: ")
		self.ylab = wx.TextCtrl(panel, value="")
		yfsl = wx.StaticText(panel,label="Size: ")
		self.yfs = wx.ComboBox(panel,value='18', choices=sizelist,style=wx.CB_READONLY)
		self.Bind(wx.EVT_TEXT,self.ytext,self.ylab)
		self.Bind(wx.EVT_CHAR,self.ychange,self.ylab)
		self.Bind(wx.EVT_COMBOBOX,self.OnYfs,self.yfs)
		
		#put labels/sizes together in sizer
		Labels = wx.BoxSizer(wx.VERTICAL)
		L1 = wx.BoxSizer(wx.HORIZONTAL)
		L1.Add((10,-1),1,wx.EXPAND)
		L1.Add(xl,0,wx.EXPAND)
		L1.Add(self.xlab,1,wx.EXPAND)
		L1.Add((10,-1),0,wx.EXPAND)
		L1.Add(xfsl,0,wx.EXPAND)
		L1.Add(self.xfs,0,wx.EXPAND)
		L1.Add((10,-1),1,wx.EXPAND)
		
		L2 = wx.BoxSizer(wx.HORIZONTAL)
		L2.Add((10,-1),1,wx.EXPAND)
		L2.Add(yl,0,wx.EXPAND)
		L2.Add(self.ylab,1,wx.EXPAND)
		L2.Add((10,-1),0,wx.EXPAND)
		L2.Add(yfsl,0,wx.EXPAND)
		L2.Add(self.yfs,0,wx.EXPAND)
		L2.Add((10,-1),1,wx.EXPAND)
		
		Labels.Add(L1,0,wx.EXPAND)
		Labels.Add((-1,5),0,wx.EXPAND)
		Labels.Add(L2,0,wx.EXPAND)

# scales and normalise
		XFactor_lbl = wx.StaticText(panel,label='X-axis scaling factor:')
		YFactor_lbl = wx.StaticText(panel,label='Y-axis scaling factor:')
		
		self.XScale = 1
		XScC = wx.TextCtrl(panel, value='1',size=(50,-1))
		self.Bind(wx.EVT_TEXT,self.XScaleCtrl,XScC)
		
		self.YScale = 1
		YScC = wx.TextCtrl(panel, value='1',size=(50,-1))
		self.Bind(wx.EVT_TEXT,self.YScaleCtrl,YScC)
		
		XSc = wx.Button(panel,label="Scale x-axis",size=(100,-1))
		self.Bind(wx.EVT_BUTTON,self.OnXscale,XSc)

		YSc = wx.Button(panel,label="Scale y-axis",size=(100,-1))
		self.Bind(wx.EVT_BUTTON,self.OnYscale,YSc)
		
		scale_sizer = wx.BoxSizer(wx.VERTICAL)
		s1 = wx.BoxSizer(wx.HORIZONTAL)
		s1.Add((10,-1),1,wx.EXPAND)
		s1.Add(XFactor_lbl,0,wx.EXPAND)
		s1.Add(XScC,0,wx.EXPAND)
		s1.Add((10,-1),0,wx.EXPAND)
		s1.Add(XSc,0,wx.EXPAND)
		s1.Add((10,-1),1,wx.EXPAND)
		s2 = wx.BoxSizer(wx.HORIZONTAL)
		s2.Add((10,-1),1,wx.EXPAND)
		s2.Add(YFactor_lbl,0,wx.EXPAND)
		s2.Add(YScC,0,wx.EXPAND)
		s2.Add((10,-1),0,wx.EXPAND)
		s2.Add(YSc,0,wx.EXPAND)
		s2.Add((10,-1),1,wx.EXPAND)
		
		scale_sizer.Add(s1,0,wx.EXPAND)
		scale_sizer.Add((-1,5),0,wx.EXPAND)
		scale_sizer.Add(s2,0,wx.EXPAND)
		
	#normalise
		Norm_lbl = wx.StaticText(panel,label='Normalise by:')
		normlist = ['Peak','Area']
		self.NormType = wx.ComboBox(panel,value=normlist[0], 
				choices=normlist,style=wx.CB_READONLY)
		NormBtn = wx.Button(panel,label='Normalise Y-data',size=(170,-1))
		self.Bind(wx.EVT_BUTTON,self.OnNorm,NormBtn)
		normTT = "Peak: normalise so that the peak value of the data is 1.\
		 Area: normalise so that the integrated area of the data is 1."
		for item in [Norm_lbl,self.NormType,NormBtn]:
			item.SetToolTip(wx.ToolTip(normTT))
		
		norm_sizer = wx.BoxSizer(wx.HORIZONTAL)
		norm_sizer.Add((10,-1),1,wx.EXPAND)
		norm_sizer.Add(Norm_lbl,0,wx.EXPAND)
		norm_sizer.Add((10,-1),0,wx.EXPAND)
		norm_sizer.Add(self.NormType,0,wx.EXPAND)
		norm_sizer.Add((10,-1),0,wx.EXPAND)
		norm_sizer.Add(NormBtn,0,wx.EXPAND)
		norm_sizer.Add((10,-1),1,wx.EXPAND)
		
#clear figure tickbox
		OptionClear=wx.CheckBox(panel,label='Clear Figure on Update?')
		self.Bind(wx.EVT_CHECKBOX,self.OnClear,OptionClear)
		OptionClear.SetValue(True)
		OptionClear.SetToolTip(wx.ToolTip("Like the holdoff command in MATLAB"))

#Log scale tickboxes
		self.logX = False
		self.logY = False
		LogXTickBox = wx.CheckBox(panel,label='Logarithmic X-axis')
		LogYTickBox = wx.CheckBox(panel,label='Logarithmic Y-axis')
		self.Bind(wx.EVT_CHECKBOX,self.OnLogX,LogXTickBox)
		self.Bind(wx.EVT_CHECKBOX,self.OnLogY,LogYTickBox)
		
		log_sizer = wx.BoxSizer(wx.HORIZONTAL)
		log_sizer.Add((10,-1),1,wx.EXPAND)
		log_sizer.Add(LogXTickBox,0,wx.EXPAND)
		log_sizer.Add((40,-1),0,wx.EXPAND)
		log_sizer.Add(LogYTickBox,0,wx.EXPAND)
		log_sizer.Add((10,-1),1,wx.EXPAND)
		
		
				
# open file / exit buttons
		buttonbar = wx.BoxSizer(wx.HORIZONTAL)
		buttonbar.Add((20,-1),0,wx.EXPAND)
		buttonbar.Add(openprocfilebutton,0,
			 wx.RIGHT,border=15)
		buttonbar.Add(openrawfilebutton,0,wx.RIGHT,border=20)
		buttonbar.Add((10,-1),1,wx.EXPAND)
		buttonbar.Add(resetbutton,0,wx.RIGHT,border=15)
		buttonbar.Add(exitbutton,0,wx.RIGHT,border=20)

		optionbar = wx.BoxSizer(wx.HORIZONTAL)
		optionbar.Add((10,-1),1,wx.EXPAND)		
		optionbar.Add(OptionClear,0,wx.EXPAND|wx.LEFT|wx.RIGHT,border=20)
		optionbar.Add((10,-1),1,wx.EXPAND)						
		
		#cmdline = wx.BoxSizer(wx.HORIZONTAL)
		#cmdline.Add((10,-1),1,wx.EXPAND)
		#cmdline.Add(cmline,1,wx.EXPAND|wx.LEFT|wx.RIGHT,border=20)
		#cmdline.Add((10,-1),1,wx.EXPAND)
		
				
#### Main sizer::

		left = wx.BoxSizer(wx.VERTICAL)
		left.Add(plotpanel,1,wx.EXPAND,border=0)
		
		right = wx.BoxSizer(wx.VERTICAL)
		right.Add((-1,10),0,wx.EXPAND)
		right.Add(PP_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(Labels,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(optionbar,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(scale_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(norm_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(log_sizer,0,wx.EXPAND)
		right.Add((-1,25))
		right.Add(SP_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(bin_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(smth_sizer,0,wx.EXPAND)
		right.Add((-1,10))
		right.Add(filter_sizerH,0,wx.EXPAND)
		right.Add((-1,40),1,wx.EXPAND)
		right.Add(buttonbar,0,wx.EXPAND)		
		
		finalsizer = wx.BoxSizer(wx.HORIZONTAL)
		finalsizer.Add(left,1,wx.EXPAND)
		finalsizer.Add(right,0,wx.EXPAND)

		panel.SetSizer(finalsizer)
		panel.Layout()

#
##
######################  Actions for events...	 #############################
##
#		
	def OnAbout(self,event):
		dlg = wx.MessageDialog(self,'Plotting Program','What is this?',wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnReset(self,event):
		self.x = self.xo
		self.y = self.yo
		self.ax.set_autoscale_on(True)		
		self.graph_update(self.x,self.y)
		self.ax.set_autoscale_on(False)
	
	def OnCommand(self,event):
		try:
			exec(event.GetString())
		except:
			print 'Not a valid command... \n'
		self.canvas.draw()	

	def OnOpenRawFile(self,event):
		self.dirname= ''
		dlg = wx.FileDialog(self,"Choose Raw Scope CSV File...",self.dirname,"","*.csv",wx.OPEN)
		
		#if ok button clicked, open and read file
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			#call read
			spacing = 5
			self.x,self.y = read(os.path.join(self.dirname,self.filename),spacing=spacing)
			#record original
			self.xo = self.x
			self.yo = self.y
			#plot
			self.graph(self.x,self.y)
			#self.layout()
			
		dlg.Destroy()

	def OnOpenProcFile(self,event):
		self.dirname= ''
		dlg = wx.FileDialog(self,"Choose 2-column csv file",self.dirname,"","*.csv",wx.OPEN)
		
		#if ok button clicked, open and read file
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			#call read
			self.x,self.y = read(os.path.join(self.dirname,self.filename),spacing=0)
			#record original (for reset button)
			self.xo = self.x
			self.yo = self.y
			#plot
			self.graph(self.x,self.y)
			#self.layout()
			
		dlg.Destroy()
		
#tick boxes
	def OnClear(self,event):
		self.holdgraph= not(bool(event.Checked()))
		print self.holdgraph
		
#plot graph, labels, sizes
	def graph(self,x,y):
		if not self.holdgraph:
			pylab.cla()
		self.ax.set_autoscale_on(True)
		self.plotline, = self.ax.plot(array(x),y,lw=2.0)
		self.canvas.draw()

	def graph_update(self,x,y):
		self.plotline.set_data(x,y)
		self.canvas.draw()
	
	def xtext(self,event):
		self.xlabel=event.GetString()
		self.ax.set_xlabel(self.xlabel,size=self.xsize)
		self.canvas.draw()

	def ytext(self,event):
		self.ylabel=event.GetString()
		self.ax.set_ylabel(self.ylabel,size=self.ysize)
		self.canvas.draw()
	
	def xchange(self,event):
		self.xlabel=event.GetString()
		self.ax.set_xlabel(self.xlabel,size=self.xsize)
		self.canvas.draw()

	def ychange(self,event):
		self.ylabel=event.GetString()
		self.ax.set_ylabel(self.ylabel,size=self.ysize)
		self.canvas.draw()

	def OnXfs(self,event):
		self.xsize=int(event.GetString())
		self.ax.set_xlabel(self.xlabel,size=self.xsize)
		self.canvas.draw()
		
	def OnYfs(self,event):
		self.ysize=int(event.GetString())
		self.ax.set_ylabel(self.ylabel,size=self.ysize)
		self.canvas.draw()

#scales
	def XScaleCtrl(self,event):
		self.Xscale = float(event.GetString())
	def OnXscale(self,event):
		self.x = self.x * self.Xscale
		self.graph_update(self.x,self.y)
		self.ax.set_xlim(self.ax.get_xlim()[0]*self.Xscale, 
					self.ax.get_xlim()[1]*self.Xscale)
		self.canvas.draw()

	def YScaleCtrl(self,event):
		self.Yscale = float(event.GetString())
	def OnYscale(self,event):
		self.y = self.y * self.Yscale
		self.graph_update(self.x,self.y)
		self.ax.set_ylim(self.ax.get_ylim()[0]*self.Yscale, 
					self.ax.get_ylim()[1]*self.Yscale)
		self.canvas.draw()

#normalise
	def OnNorm(self,event):
		if self.NormType.GetValue()=='Area':
			print 'area'
			self.Yscale = 1./sum(self.y)
		elif self.NormType.GetValue()=='Peak':
			print 'peak'
			self.Yscale = 1./self.y.max()
		self.y = self.y * self.Yscale
		self.graph_update(self.x,self.y)
		self.ax.set_ylim(self.ax.get_ylim()[0]*self.Yscale, 
					self.ax.get_ylim()[1]*self.Yscale)
		self.canvas.draw()
		
			
#log x/y axes
	def OnLogX(self,event):
		if bool(event.Checked()):
			self.ax.set_xscale('log')
		else:
			self.ax.set_xscale('linear')
		self.canvas.draw()
		
	def OnLogY(self,event):
		if bool(event.Checked()):
			self.ax.set_yscale('log')
		else:
			self.ax.set_yscale('linear')
		self.canvas.draw()
		
#exit button/menu item	
	def OnExit(self,event):
		self.Destroy()
		app.ExitMainLoop()
		
# Signal processing
	def OnSmoothCtrl(self,event):
		self.smooth_amount = int(event.GetString())
	def OnSmoothBtn(self,event):
		self.y = smooth(self.y,self.smooth_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)

	def OnBinCtrl(self,event):
		self.bin_amount = int(event.GetString())	
	def OnBinBtn(self,event):
		self.x,self.y,ye = bin(self.x,self.y,self.bin_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)

	def OnLPCtrl(self,event):
		self.LPa = float(event.GetString())
		self.LP_amount = self.LPa * self.dd[self.LPm]
		print self.LP_amount

	def OnHPCtrl(self,event):
		self.HPa = float(event.GetString()) 
		self.HP_amount = self.HPa * self.dd[self.HPm]

	def OnLPmult(self,event):
		self.LPm = self.LPmult.GetValue()
		self.LP_amount = self.LPa * self.dd[self.LPm]

	def OnHPmult(self,event):
		self.HPm = self.HPmult.GetValue()
		self.HP_amount = self.HPa * self.dd[self.HPm]

	def OnLPBtn(self,event):
		print 'Filter freq:',self.LP_amount
		self.y = lowpass(self.x,self.y,self.LP_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)

	def OnHPBtn(self,event):
		self.y = highpass(self.x,self.y,self.HP_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)

	def OnBPBtn(self,event):
		self.y = bandpass(self.x,self.y,self.LP_amount,self.HP_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)

	def OnBSBtn(self,event):
		self.y = bandstop(self.x,self.y,self.LP_amount,self.HP_amount)
		self.ax.set_autoscale_on(False)
		self.graph_update(self.x,self.y)
		
###################

#redirect: error messages go to a pop-up box
app = wx.App(redirect=True)
frame = MainWin(None,"Interactive Plotter")
frame.Show()
app.MainLoop()
