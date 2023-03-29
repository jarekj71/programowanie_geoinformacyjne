from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *

import numpy as np
import os

from . import resources
from .rpForm import dialogForm

class randomPoints:

  def __init__(self, iface):
    self.iface = iface
    self.dialog=dialogForm()
    self.registry = QgsProject.instance()

  def initGui(self):
    self.action = QAction(QIcon(":/plugins/randomPoints/icon.png"), "Random points", self.iface.mainWindow())
    self.action.setStatusTip("Generates random points using existing extent")
    self.action.triggered.connect(self.run)  
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("&Home made", self.action)

  def unload(self):
    self.iface.removePluginMenu("&Home made", self.action)
    self.iface.removeToolBarIcon(self.action)

  def run(self):
    self.create_layer_list()
    self.dialog.show()
    result = self.dialog.exec_() 
    if result:
      self.parse_input()
      self.create_point_file()


# wlasne funkcje
  def create_layer_list(self):
    ''' Build list of layers'''
    self.dialog.chooseCombo.clear()
    self.layers = list(self.registry.mapLayers().values())
    
    #self.layers = self.iface.legendInterface().layers()
    layer_list = [""]+[layer.name() for layer in self.layers]
    self.dialog.chooseCombo.addItems(layer_list) # connetion to front end

  def __get_extent_form_file(self,filename):
    if not QFileInfo(filename).isFile():
      self.iface.messageBar().pushMessage("Error", "cannot find " + filename, 2)
      exit
    # continue processing, check if geospatial layer
    layer= processing.getObject(filename)

    if not layer.isValid():
      message = filename + " is not valid geospatial layer"
      self.iface.messageBar().pushMessage("Error", message, 2)
      exit

    self.extent = layer.extent()
    self.epsg = layer.crs().authid() or self.epsg # this will cause troubles

  def __get_extent_from_active_layers(self,index):
    self.extent = self.layers[index].extent()
    self.epsg = self.layers[index].crs().authid() or self.epsg

  def __get_extent_from_canvas(self):
    self.extent = self.iface.mapCanvas().extent()

  def parse_input(self):

    gbuffer = self.dialog.bufferField.text()
    try:
      buff = float(gbuffer)
    except:
      message = "buffer parameter " + gbuffer + " is not a valid number"
      self.iface.messageBar().pushMessage("Error", message, 2)
      exit
    self.buffer = buff

    self.npoints = self.dialog.npointsSpin.value() #is always integer

    index = self.dialog.chooseCombo.currentIndex()
    filename = self.dialog.chooseField.text()
    check = self.dialog.checkCanvas.checkState()  # no need to check, default option

    self.epsg = self.registry.crs().authid()
    self.extent = None
    if index > 0:
      self.__get_extent_from_active_layers(index-1)
    elif filename != "":
      self.__get_extent_form_file(filename)
    else:
      self.__get_extent_from_canvas()

  def create_point_file(self):
    ext = self.extent
    buff = self.buffer
    npoints = self.npoints

    if ext.xMinimum()-buff>=ext.xMaximum()+buff or ext.yMinimum()-buff>=ext.yMaximum()+buff:
      message = "layer extent is too small or buffer to large"
      self.iface.messageBar().pushMessage("Error", message, 2)
      exit

    x=list(np.random.uniform(ext.xMinimum()-buff,ext.xMaximum()+buff,npoints)) #wyznaczenie X i Y jako arrays
    y=list(np.random.uniform(ext.yMinimum()-buff,ext.yMaximum()+buff,npoints)) #zrealizowane przy pomocy numpy
    points = zip(x,y)

    layerSource ='Point?crs='+str(self.epsg)+'&field=id:integer'
    player = QgsVectorLayer(layerSource, 'random' ,'memory') # layer with points
    qPoints=[] #pusta lista

    for id,pt in enumerate(points):
        qPoint = QgsFeature() # feature objects
        qpt = QgsPointXY(*pt)
        qPoint.setGeometry(QgsGeometry.fromPointXY(qpt)) # geometry
        qPoint.setAttributes([id+1]) # attributes, id +1 to start from 1
        qPoints.append(qPoint) # add

    player.dataProvider().addFeatures(qPoints)
    player.updateExtents()
    self.registry.addMapLayer(player)
