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


class AddLineRandomPoints(QgsProcessingAlgorithm):


    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    MAXDIST = 'MAXDIST'
    NPOINTS = 'NPOINTS'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AddLineRandomPoints()

    def name(self):

        return 'randlinepoints'

    def displayName(self):


        return self.tr('Random Points along line')

    def group(self):
        return self.tr('Teaching examples')

    def groupId(self):
        return 'rpltscripts'

    def shortHelpString(self):

        return self.tr("Returns point file randomly scattered along line")

    def initAlgorithm(self, config=None):

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine])
        )
        self.addParameter(QgsProcessingParameterNumber(
                self.MAXDIST, 
                self.tr('Maximimum distance from line in layer units'),
                defaultValue=100.)
        )
        self.addParameter(QgsProcessingParameterNumber(
                self.NPOINTS, 
                self.tr('Number of points'),
                defaultValue=100)
        )
        self.addParameter(QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'))
        )

    def processParameters(self,parameters,context,feedback):
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        nfeatures = source.featureCount()
        #feedback.pushInfo('NPOINTS is {}'.format(nfeatures))
        if nfeatures != 1:
            raise QgsProcessingException('Only one input line is currently allowed')    
        
        #create sink
        fields = QgsFields()
        fields.append(QgsField('ID',QVariant.Int))
        fields.append(QgsField('distance',QVariant.Double))
        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point,
            source.sourceCrs()
        )

        # Send some information to the user
        #feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        var_maxdist = self.parameterAsDouble(
            parameters,
            self.MAXDIST,
            context)
        
        var_npoints = self.parameterAsInt(
            parameters,
            self.NPOINTS,
            context)
        
        #make variable public
        self.source = source
        self.sink = sink
        self.dest_id = dest_id
        self.maxdist = var_maxdist
        self.npoints = var_npoints
        
    
    def processAlgorithm(self, parameters, context, feedback):
        #prepare parameters
        self.processParameters(parameters, context, feedback)
                
        extent = self.source.sourceExtent()
        #feedback.pushInfo('Extent is {}'.format(extent))
        xmin = extent.xMinimum() - self.maxdist #3
        xmax = extent.xMaximum() + self.maxdist
        ymin = extent.yMinimum() - self.maxdist
        ymax = extent.yMaximum() + self.maxdist
                
        features = self.source.getFeatures()
        line = next(features)
        line_geom = line.geometry()
        
        features = []
        id = 0
        while len(features) < self.npoints: 
            x = np.random.uniform(xmin,xmax) 
            y = np.random.uniform(ymin,ymax)
            point = QgsGeometry.fromPointXY(QgsPointXY(x,y))
            distance = line_geom.distance(point) 
            if distance < self.maxdist: 
                feature = QgsFeature()
                feature.setGeometry(point)
                feature.setAttributes([id,distance])
                features.append(feature)
                id+=1 #  
        self.sink.addFeatures(features)
        
        return {self.OUTPUT: self.dest_id}
