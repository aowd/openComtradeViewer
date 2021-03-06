#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  GUI.py
#  
#  Copyright 2016 Leonardo M. N. de Mattos <l@mattos.eng.br>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 3 of the License.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import Tkinter as tkinter
import os
import tkFileDialog
import tkMessageBox
import sys
import pylab
import src.pyComtrade as pyComtrade
import src.GUI_Data
import src.GUI_Analyses

class mainWindow():
	
	def __init__(self,window,comtradeFile):
	
		# Class variables
		self.comtradeFile = comtradeFile
		self.comtradeObj = None
	
		# Adjust rows and columns weights		
		window.rowconfigure(0,weight=1)
		window.rowconfigure(1,weight=4)
		window.rowconfigure(2,weight=0)
		window.rowconfigure(3,weight=0)
		window.columnconfigure(0,weight=1)
		window.columnconfigure(1,weight=0)
		window.columnconfigure(2,weight=1)
		window.columnconfigure(3,weight=0)
		
		# Window title
		window.title("openComtradeViewer")
		
		# Window dimensions and position
		w = 434
		h = 300
		window.resizable(width='false', height='false')
		width = window.winfo_screenwidth()
		height = window.winfo_screenheight()
		posx = (width - w)/2.0
		posy = (height - h)/2.0
		window.geometry('%dx%d+%d+%d' % (w, h, posx, posy))
		
		# Set window icon
		if os.name == "nt":
			#~ window.wm_iconbitmap(default='.\icons\Statistics.ico')
			pass
		else:
			#~ Here will be placed the options for Linux/Mac OS X
			pass
		
		# Create Menubar
		self.setMenuBar(window)
		
		# listbox widget method
		self.lbl_analog = tkinter.Label(window, text="Analog Channels:")
		self.scroll_analog = tkinter.Scrollbar(window,orient='vertical')
		self.lbox_analog = tkinter.Listbox(window,\
		selectmode='extended',yscrollcommand=self.scroll_analog.set)
		self.scroll_analog.config(command=self.lbox_analog.yview)
		self.lbl_digital = tkinter.Label(window,text="Digital Channels:")
		self.scroll_digital = tkinter.Scrollbar(window,orient='vertical')
		self.lbox_digital = tkinter.Listbox(window,\
		selectmode='extended',yscrollcommand=self.scroll_digital.set)
		self.scroll_digital.config(command=self.lbox_digital.yview)
	
		# button to plot the selected graphics
		self.btn_runPlot = tkinter.Button(window, text="Plot!",command=lambda: self.runPlot())
		
		# status bar
		self.lbl_status = tkinter.Label(window, text="No COMTRADE (*.cfg) file selected", bd=1, relief='sunken')
		
		# Check if some file was given in the startup and update the widgets
		self.checkComtradeStartup()
		
		# Add the widgets to the window screen
		self.lbl_analog.grid(stick='w',row=0,column=0)
		self.lbox_analog.grid(stick='nsew',row=1,column=0)
		self.scroll_analog.grid(stick='nsw',row=1,column=1)
		self.lbl_digital.grid(stick='w',row=0,column=2)
		self.lbox_digital.grid(stick='nsew',row=1,column=2)
		self.scroll_digital.grid(stick='nsw',row=1,column=3)
		self.btn_runPlot.grid(sticky='nsew',row=2,column=0,columnspan=4)
		self.lbl_status.grid(sticky='nsew',row=3,column=0,columnspan=4)
		
	# Set and configure the menubar
	def setMenuBar(self,window):
		
		from GUI_About import aboutWin
		import webbrowser
		
		# Variables
		url = "http://github.com/ldemattos/openComtradeViewer"
		
		# Create menu bar
		self.menubar = tkinter.Menu(window)
		
		# File Menu
		self.filemenu = tkinter.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Select COMTRADE file...", command=self.fileSelection)
		self.filemenu.add_command(label="Exit", command=window.quit)
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		
		# Data menu
		self.datamenu = tkinter.Menu(self.menubar, tearoff=0)
		self.datamenu.add_command(label="COMTRADE Info", command=lambda: src.GUI_Data.OscilloInfo(self.comtradeObj))
		self.datamenu.add_command(label="Export selected data",\
		 command=lambda: src.GUI_Data.exportData(self.comtradeObj,self.lbox_analog.curselection(),self.lbox_digital.curselection()))
		self.menubar.add_cascade(label="Data", menu=self.datamenu)
		
		# Analyses menu
		self.analysesmenu = tkinter.Menu(self.menubar, tearoff=0)
		self.analysesmenu.add_command(label="Compute RMS...", command=lambda: src.GUI_Analyses.calcRMS(self.comtradeObj,\
		self.lbox_analog.curselection()))
		self.menubar.add_cascade(label="Analyses", menu=self.analysesmenu)

		# Help menu
		self.helpmenu = tkinter.Menu(self.menubar, tearoff=0)
		self.helpmenu.add_command(label="Project page", command=lambda: webbrowser.open(url,new=2))
		self.helpmenu.add_command(label="About", command=lambda: aboutWin())
		self.menubar.add_cascade(label="Help", menu=self.helpmenu)
			
		window.config(menu=self.menubar)
	
	# file selection method
	def fileSelection(self):
		
		# Options for file dialog
		options = {}
		options['defaultextension'] = '.cfg'
		options['filetypes'] = [('COMTRADE Files', '.cfg'),('All Files', '.*')]
		options['title'] = 'Select COMTRADE file:'
		self.comtradeFile = tkFileDialog.askopenfilename(**options)
		
		if len(self.comtradeFile) != 0:		
			
			# Update lbl_comtradeFile
			self.lbl_status.configure(text=os.path.basename(self.comtradeFile))
			
			# clean listboxes data
			self.lbox_analog.delete(0,'end')
			self.lbox_digital.delete(0,'end')
			
			# Update listboxes
			self.readChannels()		
			
		else: 
			
			# Update lis-file
			self.comtradeFile = None
			
			# clean listboxes data
			self.lbox_analog.delete(0,'end')
			self.lbox_digital.delete(0,'end')
			
			# Update lbl_LisFile
			self.lbl_status.configure(text="No COMTRADE (*.cfg) file selected")
			
	# method to setup the listbox with the given file
	def readChannels(self):
		
		self.comtradeObj = pyComtrade.ComtradeRecord(self.comtradeFile)
		checkCFG = self.comtradeObj.ReadCFG()

		if checkCFG != 2:
			# Read data file
			self.comtradeObj.ReadDataFile()
			
			# Update analog channels list
			for i in xrange(0,self.comtradeObj.A):
				self.lbox_analog.insert('end',"(#%i) "%(i+1)+self.comtradeObj.Ach_id[i])
			
			# Update digital channels list
			for i in xrange(0,self.comtradeObj.D):
				self.lbox_digital.insert('end',"(#%i) "%(i+1)+self.comtradeObj.Dch_id[i])
		
		else:
			tkMessageBox.showerror("COMTRADE Parsing - Error","Please select a valid COMTRADE cfg file.")
			# Update lis-file
			self.comtradeFile = None
			
			# clean listboxes data
			self.lbox_analog.delete(0,'end')
			self.lbox_digital.delete(0,'end')
			
			# Update lbl_LisFile
			self.lbl_status.configure(text="No COMTRADE (*.cfg) file selected")
	
	# Method for plotting data
	def runPlot(self):
		
		# plot analog selected data
		analog_curves = self.lbox_analog.curselection()
		if len(analog_curves) > 0:
			pylab.figure()		
			for i in analog_curves:
				i = int(i)
				label="%s (%s)"%(self.comtradeObj.Ach_id[i],self.comtradeObj.getAnalogUnit(i+1))
				pylab.plot(self.comtradeObj.getTime(),self.comtradeObj.getAnalogChannelData(i+1),label=label)
		
		# plot analog selected data
		digital_curves = self.lbox_digital.curselection()
		if len(digital_curves) > 0:
			pylab.figure()
			for i in digital_curves:			
				i = int(i)
				label="%s"%(self.comtradeObj.Dch_id[i])
				pylab.plot(self.comtradeObj.getTime(),self.comtradeObj.getDigitalChannelData(i+1),label=label)
		
		# show all plots
		if len(digital_curves) > 0 or len(analog_curves) > 0:
			pylab.legend()
			pylab.show()	
	
	# Check if some file was given in the startup
	def checkComtradeStartup(self):
		
		if self.comtradeFile != None:		
			# Update lbl_comtradeFile
			self.lbl_status.configure(text=os.path.basename(self.comtradeFile))
			
			# Update listboxes
			self.readChannels()		
	
