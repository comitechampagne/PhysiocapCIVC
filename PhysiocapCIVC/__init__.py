# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhysiocapAnalyseur
                                 A QGIS plugin
 Physiocap plugin helps analysing raw data from Physiocap in Qgis
                             -------------------
        begin                : 2015-07-31
        copyright            : (C) 2015 by jhemmi.eu
        email                : jean@jhemmi.eu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PhysiocapAnalyseur class from file PhysiocapAnalyseur.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Physiocap import PhysiocapAnalyseur
    return PhysiocapAnalyseur(iface)
