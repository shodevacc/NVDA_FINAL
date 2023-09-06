from baseObject import ScriptableObject
from datetime import datetime
from scriptHandler import script
import ui
import api
import csv
import os
import pathlib

#: How to separate items in a speech sequence
SPEECH_ITEM_SEPARATOR = ";;"
#: How to separate speech sequences
SPEECH_SEQUENCE_SEPARATOR = "\n"
OUTPUT_DIRECTORY =  os.path.join(pathlib.Path.home(),"NVDA_DATA")
NOT_AVAILABLE = "N/A"
monitorActive = False
activities = []

class ActivityMonitor():
	def __init__(self, navObj):
		# print("LOGGER IS INITIALISED")
		self.obj = navObj
		self.attributes = self.getAllAttributes(keys=['tag', 'class'])

	def logGesture(self, gesture):
		self.attributes['gestures'].append(gesture)

	def logWord(self, word):
		self.attributes['words'].append(word)

	def logSpeechSequence(self, sequence):
			# to make the speech easier to read, we must separate the items.
		text = SPEECH_ITEM_SEPARATOR.join(
			speech for speech in sequence if isinstance(speech, str)
		)
		self.attributes['speech_sequence'].append(text)

	# Get the url of the current webpage
	def getUrl(self):
		try:
			url = self.obj.treeInterceptor.documentConstantIdentifier
			return url
		except:
			return NOT_AVAILABLE
		
	# Get the inner text content of the current element
	def getContent(self):
		content = ""
		# Get content of the object
		for text in self.obj.children:
			if isinstance(text.name, str):
				content += text.name
			else:
				break
		return content if len(content) else self.obj.name if isinstance(self.obj.name,str) else NOT_AVAILABLE
	
	# Get all the attributes we are interested in from NVDA
	def getAllAttributes(self, keys=[]):
		try:
			keys.append("url")
			keys.append("content")
			keys.append("start_time")
			# Set inital values of return dictonary to be all not available
			returnDictonary = dict.fromkeys(keys,NOT_AVAILABLE)
			# print("Initial ATTRIBUTES", returnDictonary)
			returnDictonary['content'] = self.getContent()
			returnDictonary['url'] = self.getUrl()
			returnDictonary['gestures'] = []
			returnDictonary['speech_sequence'] = []
			returnDictonary['words'] = []
			returnDictonary['start_time'] = datetime.now().timestamp()
			# print("UPDATED ATTRIBUTES", returnDictonary)
			# Check if this object has IA2Attributes
			if hasattr(self.obj, "IA2Attributes"):
				# Loop over all the keys we want
				for key in keys:
					# Check if this key exists in the IA2Attributes dictonary
					if key in self.obj.IA2Attributes.keys():
						# print("This ATTRIBUTES key is found", key)
						# Update the value of the key
						returnDictonary[key] = self.obj.IA2Attributes[key]
			# Finally return the attributes
			return returnDictonary
		except Exception as e:
			print("ATTRIBUTES ERROR", e)
			return None
        
class SessionTracker():
	def __init__(self):
		self.active = False
		# Store a list of all activities
		self.activities = []
		self.sequenceBuffer =None
		self.previous_activity = None
		# Store the current activity
		self.current_activity = None
		print("LOGGER IS INITIALISED")

	def addNewMonitor(self, activityMonitor):
		self.previous_activity = self.current_activity
		self.current_activity = activityMonitor
		self.activities.append(activityMonitor)

	def logGesture(self, gesture):
		if self.current_activity:
			self.current_activity.logGesture(gesture)

	def logSpeechSequence(self, sequence):
		if self.sequenceBuffer:
			if self.current_activity:
				self.current_activity.logSpeechSequence(self.sequenceBuffer)
				self.sequenceBuffer = sequence
		else:
			self.sequenceBuffer = sequence
		# if self.previous_activity:
		# 	self.previous_activity.logSpeechSequence(sequence)
		# if self.current_activity:
		# 	self.current_activity.logSpeechSequence(sequence)

	def logWord(self, word):
		if self.current_activity:
			self.current_activity.logGesture(word)

	def isSameObj(self, newNavObj):
		return self.current_activity.obj == newNavObj if self.current_activity is not None else False
	
	def getOnlyAttributes(self, obj):
		return obj.attributes
	
	def listAll(self):
		return list(map(self.getOnlyAttributes, self.activities))
	
	def create_output_dir(self):
		if not os.path.exists(OUTPUT_DIRECTORY):
			paths = OUTPUT_DIRECTORY.split(os.sep)
			createdPaths = ""
			for path in paths:
				createdPaths = os.path.join(createdPaths, path)
				if createdPaths.lower() == "c:":
					createdPaths = createdPaths + os.sep
				if not os.path.exists(createdPaths):
					os.mkdir(createdPaths)

	def toCsv(self):
		if len(self.activities) > 0:
			columnNames = list(self.activities[0].attributes.keys())
			rows = []
			self.create_output_dir()
			filename= os.path.join(OUTPUT_DIRECTORY,"{}.csv".format(datetime.now().timestamp()))
			for activity in self.activities:
				thisRow = [activity.attributes[column] for column in columnNames]
				rows.append(thisRow)
			with open(filename,'w') as csvFile:
				csvwriter = csv.writer(csvFile)
				csvwriter.writerow(columnNames)
				csvwriter.writerows(rows)
		else:
			ui.message("No data found in this session")

	def flush(self):
		# Store a list of all activities
		self.activities = []
		# Store the current activity
		self.current_activity = None
		self.sequenceBuffer = None
		
	def setActiveState(self, state):
		self.active = state
        
	
        

#: The singleton activity monitor instance.
monitor = None

def pumpAll():
	global monitor
	appName = api.getFocusObject().appModule.appName
	# Start the logger
	if appName.lower() == "chrome" and monitor and monitor.active:
		nav = api.getNavigatorObject()
		if monitor and not monitor.isSameObj(nav):
			monitor.addNewMonitor(ActivityMonitor(nav))
		print("The monitor state is", monitor.listAll())
	# Pause the logger
	# else:
	# 	print("PUMP IT UP elsewhere bitches", appName)

def isActive():
	global monitor
	return monitor.active

def logGesture(gesture):
	global monitor
	if monitor:
		monitor.logGesture(gesture)
	print("The gesture is", gesture)

def toCsv():
	global monitor
	if monitor:
		monitor.toCsv()

def startSession():
	ui.message("Starting a new session Please wait")
	global monitor
	monitor.flush()
	# Check if the monitor is already active
	if not monitor.active:
		monitor.setActiveState(True)
	ui.message("New Session Started.")

def endSession():
	ui.message("Ending a new session Please wait")
	global monitor
	if monitor:
		# Output the data to a csv
		monitor.toCsv()
		# Flush the data to start a new session
		monitor.flush()
		# Set state of monitor to inactive
		monitor.setActiveState(False)
	ui.message("Session Ended Successfully")
	
def logSpeechSequence(sequence):
	global monitor
	if monitor and monitor.active:
		monitor.logSpeechSequence(sequence)

def initialize():
	"""Initializes acitivty monitor, creating a global L{ActivityMonitor} singleton.
	"""
	global monitor
	monitor=SessionTracker()
        
def terminate():
	"""Terminates input core.
	"""
	print("Terminating the Activity Montitor source")
	global monitor
	monitor=None