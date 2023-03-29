# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes,
                       QgsGeometry,
                       QgsFeature,
                       QgsPointXY,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import processing
import numpy as np


class JoinHubsWithDestinations(QgsProcessingAlgorithm):


    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUTSOURCE = 'INPUTSOURCE'
    INPUTTARGET = 'INPUTTARGET'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return JoinHubsWithDestinations()

    def name(self):

        return 'joinhubswithdestinations'

    def displayName(self):


        return self.tr('Join source with targets')

    def group(self):
        return self.tr('Teaching examples')

    def groupId(self):
        return 'rpltscripts'

    def shortHelpString(self):

        return self.tr("Create lines to join targets (hubs) with nearest sources")

    def initAlgorithm(self, config=None):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(QgsProcessingParameterFeatureSource(
                self.INPUTSOURCE,
                self.tr('Input source layer'),
                [QgsProcessing.TypeVectorPoint])
        )
        self.addParameter(QgsProcessingParameterFeatureSource(
                self.INPUTTARGET,
                self.tr('Input target layer'),
                [QgsProcessing.TypeVectorPoint])
        )
        self.addParameter(QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'))
        )

    def processParameters(self,parameters,context,feedback):
        input_source = self.parameterAsSource(
            parameters,
            self.INPUTSOURCE,
            context
        )
        if input_source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUTSOURCE))

        input_target = self.parameterAsSource(
            parameters,
            self.INPUTTARGET,
            context
        )
        if input_target is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUTTARGET))

        if input_source.sourceCrs().authid() != input_target.sourceCrs().authid():
            raise QgsProcessingException('source and targets must have same crs!')
        
        # create sink
        fields = QgsFields()
        fields.append(QgsField('srcid',QVariant.Int))
        fields.append(QgsField('trgid',QVariant.Int))
        fields.append(QgsField('length',QVariant.Double)) #2

        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            input_source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
      
        #make variable public
        self.source = input_source
        self.target = input_target
        self.sink = sink
        self.dest_id = dest_id
        
    
    def processAlgorithm(self, parameters, context, feedback):
        #prepare parameters
        self.processParameters(parameters, context, feedback)
        
        sources=self.source.getFeatures() 
        for src in sources: 
            src_geom = src.geometry() 
            shortest_distance = 1e20  
            cur_trg = None 
            targets = self.target.getFeatures() 
            for trg in targets: 
                trg_geom = trg.geometry() 
                cur_distance = src_geom.distance(trg_geom) 
                if cur_distance < shortest_distance: 
                    shortest_distance = cur_distance  
                    cur_trg = trg 
            line = QgsGeometry.fromPolylineXY([QgsPointXY(src.geometry().asPoint()),
                                                QgsPointXY(cur_trg.geometry().asPoint())]) 
            feature = QgsFeature() 
            feature.setGeometry(line) 
            feature.setAttributes([src.id(),trg.id(),line.length()]) 
            self.sink.addFeature(feature) 

        
        return {self.OUTPUT: self.dest_id}
