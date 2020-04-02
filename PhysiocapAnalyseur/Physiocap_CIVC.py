# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Physiocap_CIVC
								 A QGIS plugin
 Physiocap plugin helps analyse raw data from Physiocap in Qgis and 
 creates a synthesis of Physiocap measures' campaign
 Physiocap plugin permet l'analyse les données brutes de Physiocap dans Qgis et
 crée une synthese d'une campagne de mesures Physiocap
 
 Le module CIVC contient le filtre de données, de creation des csv 
 et shapfile, de creation des histogrammes
 
 Partie Calcul non modifié par rapport à physiocap_V8
 Les variables et fonctions sont nommées en Francais par compatibilité avec 
 la version physiocap_V8
							 -------------------
		begin                : 2015-07-31
		git sha              : $Format:%H$
		email                : jean@jhemmi.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 * Physiocap plugin créé par jhemmi.eu et CIVC est issu de :               *
 *- PSPY : PHYSIOCAP SCRIPT PYTHON VERSION 8.0 10/11/2014                  *
 *   CREE PAR LE POLE TECHNIQUE ET ENVIRONNEMENT DU CIVC                   *
 *   MODIFIE PAR LE CIVC ET L'EQUIPE VIGNOBLE DE MOËT & CHANDON            *
 *   AUTEUR : SEBASTIEN DEBUISSON, MODIFIE PAR ANNE BELOT ET MANON MORLET  *
 *   Physiocap plugin comme PSPY sont mis à disposition selon les termes   *
 *   de la licence Creative Commons                                        *
 *   CC-BY-NC-SA http://creativecommons.org/licenses/by-nc-sa/4.0/         *
 *- Plugin builder et Qgis API et à ce titre porte aussi la licence GNU    *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *   http://www.gnu.org/licenses/gpl-2.0.html                              *
 *                                                                         *
***************************************************************************/
"""
from Physiocap_tools import physiocap_message_box, \
		physiocap_log, physiocap_error, physiocap_write_in_synthese,physiocap_quelle_projection_demandee

##        physiocap_quel_uriname, physiocap_tester_uri, \
##        physiocap_detruit_table_uri, physiocap_existe_table_uri, \
##        physiocap_get_uri_by_layer 
from Physiocap_var_exception import *

from PyQt4.QtCore import QSettings, Qt, QVariant
from qgis.core import QGis, QgsCoordinateReferenceSystem, QgsFields, QgsField,QgsProject, \
		QgsFeature, QgsGeometry, QgsPoint, QgsVectorFileWriter, QgsMessageLog, QgsVectorLayer, QgsMapLayerRegistry
from qgis.utils import iface
import processing
import sys, string,csv
from datetime import date


if platform.system() == 'Windows':
	import win32api

try :
	import csv
except ImportError:
	aText = "Erreur bloquante : module csv n'est pas accessible."
	QgsMessageLog.logMessage( aText, u"\u03D5 Erreurs", QgsMessageLog.WARNING)

try :
	from osgeo import osr
except ImportError:
	aText = "Erreur bloquante : module GDAL osr n'est pas accessible."
	QgsMessageLog.logMessage( aText, u"\u03D5 Erreurs", QgsMessageLog.WARNING)

try :
	##    from matplotlib.figure import Figure
	##    from matplotlib import axes
	import matplotlib.pyplot as plt
except ImportError:
	aText ="Erreur bloquante : module matplotlib.pyplot n'est pas accessible\n"
	aText = aText + "Sous Fedora : installez python-matplotlib-qt4"
	QgsMessageLog.logMessage( aText, u"\u03D5 Erreurs", QgsMessageLog.WARNING)

try :
	import numpy as np
except ImportError:
	aText ="Erreur bloquante : module numpy n'est pas accessible"
	QgsMessageLog.logMessage( aText, u"\u03D5 Erreurs", QgsMessageLog.WARNING)

def physiocap_csv_vers_shapefile( self, progress_barre, csv_name, shape_name, prj_name, laProjection, 
	nom_fichier_synthese = "NO", details = "NO"):
	""" Creation de shape file à partir des données des CSV
	Si nom_fichier_synthese n'est pas "NO", on produit les moyennes dans le fichier
	qui se nomme nom_fichier_synthese
	Selon la valeur de détails , on crée les 5 premiers ("NO") ou tous les attibuts ("YES")
	"""
	crs = None
	#Préparation de la liste d'arguments
	x,y,nbsarmshp,diamshp,biomshp,dateshp,vitesseshp= [],[],[],[],[],[],[]
	nbsarmm2,nbsarcep,biommm2,biomgm2,biomgcep=[],[],[],[],[]

	un_fic = open( csv_name, "r")
	lignes = un_fic.readlines()
	nombre_ligne = len( lignes)
	un_fic.close()
	progress_step = int( nombre_ligne / 19)
	barre = 1

	#Lecture des data dans le csv et stockage dans une liste
	with open(csv_name, "rt") as csvfile:
		try:
			r = csv.reader(csvfile, delimiter=";")
		except NameError:
			uText = u"Erreur bloquante : module csv n'est pas accessible."
			physiocap_error( self, uText)
			return -1

		for jj, row in enumerate( r):
			#skip header
			if jj > 0:
				# ON fait avancer la barre de progression de 19 points
				if ( jj > progress_step * barre):
					barre = barre + 1
					progress_barre = progress_barre + 1
					self.progressBar.setValue( progress_barre)

				crs = None
				if ( laProjection == "L93"):
					x.append(float(row[2]))
					y.append(float(row[3]))
					crs = QgsCoordinateReferenceSystem(EPSG_NUMBER_L93,
						QgsCoordinateReferenceSystem.PostgisCrsId)
				if ( laProjection == "GPS"):
					x.append(float(row[0]))
					y.append(float(row[1]))
					crs = QgsCoordinateReferenceSystem(EPSG_NUMBER_GPS,
						QgsCoordinateReferenceSystem.PostgisCrsId)
				nbsarmshp.append(float(row[4]))
				diamshp.append(float(row[5]))
				biomshp.append(float(row[6]))
				dateshp.append(str(row[7]))
				vitesseshp.append(float(row[8]))
				if details == "YES":
					# Niveau de detail demandé
					# assert sur len row
					if len(row) != 14:
						return physiocap_error( self, u"Le nombre de colonnes :" +
								str( len(row)) +
								u" du cvs ne permet pas le calcul détaillé")
					nbsarmm2.append(float(row[9]))
					nbsarcep.append(float(row[10]))
					biommm2.append(float(row[11]))
					biomgm2.append(float(row[12]))
					biomgcep.append(float(row[13]))

	# Prepare les attributs
	les_champs = QgsFields()
	# V1.0 Ajout du GID
	les_champs.append( QgsField("GID", QVariant.Int, "integer", 10))
	les_champs.append( QgsField("DATE", QVariant.String, "string", 25))
	les_champs.append( QgsField("VITESSE", QVariant.Double, "double", 10,2))
	les_champs.append(QgsField("NBSARM",  QVariant.Double, "double", 10,2))
	les_champs.append(QgsField("DIAM",  QVariant.Double, "double", 10,2))
	les_champs.append(QgsField("BIOM", QVariant.Double,"double", 10,2))
	if details == "YES":
		# Niveau de detail demandé
		les_champs.append(QgsField("NBSARMM2", QVariant.Double,"double", 10,2))
		les_champs.append(QgsField("NBSARCEP", QVariant.Double,"double", 10,2))
		les_champs.append(QgsField("BIOMM2", QVariant.Double,"double", 10,2))
		les_champs.append(QgsField("BIOMGM2", QVariant.Double,"double", 10,2))
		les_champs.append(QgsField("BIOMGCEP", QVariant.Double,"double", 10,2))

	# Creation du Shape
	writer = QgsVectorFileWriter( shape_name, "utf-8", les_champs,
			QGis.WKBPoint, crs , "ESRI Shapefile")

	#Ecriture du shp
	for j,k in enumerate(x):
		feat = QgsFeature()
		feat.setGeometry( QgsGeometry.fromPoint(QgsPoint(k,y[j]))) #écrit la géométrie
		if details == "YES":
			# Ecrit tous les attributs
		   feat.setAttributes( [ j, dateshp[j], vitesseshp[j], nbsarmshp[j],
								diamshp[j], biomshp[j],
								nbsarmm2[j], nbsarcep[j], biommm2[j],
								biomgm2[j], biomgcep[j]])
		else:
			# Ecrit les 5 premiers attributs
			feat.setAttributes( [ j, dateshp[j], vitesseshp[j], nbsarmshp[j],
								diamshp[j], biomshp[j]])
		# Ecrit le feature
		writer.addFeature( feat)

	# Flush vector
	del writer


	# Create the PRJ file
	prj = open(prj_name, "w")
	epsg = 'inconnu'
	if ( laProjection == PROJECTION_L93):
		# Todo: V3 ? Faire aussi un fichier de metadata
		epsg = EPSG_TEXT_L93
	if ( laProjection == PROJECTION_GPS):
		#  prj pour GPS 4326
		epsg = EPSG_TEXT_GPS

	prj.write(epsg)
	prj.close()

	# Création de la synthese   #___ Ecriture de la derniere partie du fichier synthese
	if nom_fichier_synthese != "NO":
		# ASSERT Le fichier de synthese existe
		if not os.path.isfile( nom_fichier_synthese):
			uMsg =u"Le fichier de synthese " + nom_fichier_synthese + "n'existe pas"
			physiocap_log( uMsg)
			return physiocap_error( self, uMsg)

		# Ecriture des resulats
		fichier_synthese = open(nom_fichier_synthese, "a")
		try:
			fichier_synthese.write("\n\nSTATISTIQUES\n")
			fichier_synthese.write("Vitesse moyenne d'avancement  \n	mean : %0.1f km/h\n" %np.mean(vitesseshp))
			fichier_synthese.write("Section moyenne \n	mean : %0.2f mm\t std : %0.1f\n" %(np.mean(diamshp), np.std(diamshp)))
			fichier_synthese.write("Nombre de sarments au m \n	mean : %0.2f  \t std : %0.1f\n" %(np.mean(nbsarmshp), np.std(nbsarmshp)))
			fichier_synthese.write("Biomasse en mm²/m linéaire \n	mean : %0.1f\t std : %0.1f\n" %(np.mean(biomshp), np.std(biomshp)))
			#enregistre les valeurs des variables pour les ecrire dans le fichier CSV de sortie  ___Nadia___
			self.settings.setValue("Physiocap/diamshp_moy", np.mean(diamshp)) #___definir les valeurs des variables : diametre moyen
			self.settings.setValue("Physiocap/nbsarmshp_moy", np.mean(nbsarmshp)) #___definir les valeurs des variables : nbsarmshp moyen
			self.settings.setValue("Physiocap/biomshp_moy", np.mean(biomshp)) #___definir les valeurs des variables : biomshp moyen
			self.settings.setValue("Physiocap/vitesseshp", np.mean(vitesseshp)) #___definir les valeurs des variables : biomshp moyen
			if details == "YES":
				fichier_synthese.write("Nombre de sarments au m² \n	 mean : %0.1f  \t std : %0.1f\n" %(np.mean(nbsarmm2), np.std(nbsarmm2)))
				fichier_synthese.write("Nombre de sarments par cep \n	mean : %0.1f \t\t std : %0.1f\n" %(np.mean(nbsarcep), np.std(nbsarcep)))
				fichier_synthese.write("Biomasse en mm²/m² \n	mean : %0.1f\t std : %0.1f\n" %(np.mean(biommm2), np.std(biommm2)))
				fichier_synthese.write("Biomasse en gramme/m² \n	mean : %0.1f\t std : %0.1f\n" %(np.mean(biomgm2), np.std(biomgm2)))
				fichier_synthese.write("Biomasse en gramme/cep \n	mean : %0.1f\t std : %0.1f\n" %(np.mean(biomgcep), np.std(biomgcep)))
		except:
			msg = "Erreur bloquante durant les calculs de moyennes\n"
			physiocap_error( self, msg )
			return -1

		fichier_synthese.close()

	return 0


def generer_contour_fin(self, nom_fichier_synthese_CSV="NO", nom_fichier_shape_sans_0="", ss_groupe=None):

	fichier_synthese_CSV = open(nom_fichier_synthese_CSV, "wb")

	infoAgro = self.settings.value("Physiocap/info_agro",
								   "")  # ___recuperer les valeurs des variables : InfoAgro : Renseign/Contour
	if infoAgro == "Renseign":
		# Ecriture de l'entête
		nom_parcelle = self.settings.value("Physiocap/nom_parcelle","xx")  # ___recuperer les valeurs des variables : nom de la parcelle
		annee_plant = self.settings.value("Physiocap/annee_plant","xx")  # ___recuperer les valeurs des variables : année de plantation
		comuune = self.settings.value("Physiocap/comuune", "xx")  # ___recuperer les valeurs des variables : commune
		region = self.settings.value("Physiocap/region", "xx")  # ___recuperer les valeurs des variables : region
		clone = self.settings.value("Physiocap/clone", "xx")  # ___définir les valeurs des variables : clone
		porte_greffe = self.settings.value("Physiocap/porte_greffe","xx")  # ___recuperer les valeurs des variables : porte-greffe
		sol_argile = self.settings.value("Physiocap/sol_argile", "xx")  # ___recuperer les valeurs des variables : sol pourcentage argile
		sol_mo = self.settings.value("Physiocap/sol_mo","xx")  # ___recuperer les valeurs des variables : sol pourcentage MO
		sol_caco3 = self.settings.value("Physiocap/sol_caco3","xx")  # ___recuperer les valeurs des variables : sol pourcentage CaCO3
		rendement = self.settings.value("Physiocap/rendement","xx")  # ___recuperer les valeurs des variables : rendement annee courante
		nb_grappes = self.settings.value("Physiocap/nb_grappes", "xx")  # ___recuperer les valeurs des variables : nombre de grappes annee courante
		poids_moy_grappes = self.settings.value("Physiocap/poids_moy_grappes","xx")  # ___recuperer les valeurs des variables : poids moyen de grappes annee courante
		rendement_1 = self.settings.value("Physiocap/rendement_1","xx")  # ___recuperer les valeurs des variables : rendement annee precedente
		nb_grappes_1 = self.settings.value("Physiocap/nb_grappes_1", "xx")  # ___recuperer les valeurs des variables : nombre de grappes annee precedente
		poids_moy_grappes_1 = self.settings.value("Physiocap/poids_moy_grappes_1","xx")  # ___recuperer les valeurs des variables : poids moyen de grappes annee precedente
		type_apports = self.settings.value("Physiocap/type_apports","xx")  # ___recuperer les valeurs des variables : type apports fertilisation
		produit = self.settings.value("Physiocap/produit", "xx")  # ___recuperer les valeurs des variables : produit
		dose = self.settings.value("Physiocap/dose", "xx")  # ___recuperer les valeurs des variables : dose(t/ha)
		strategie_entretien_sol = self.settings.value("Physiocap/strategie_entretien_sol", "xx")  # ___recuperer les valeurs des variables : strategie entretien de sol
		etat_sanitaire = self.settings.value("Physiocap/etat_sanitaire","xx")  # ___recuperer les valeurs des variables : etat sanitaire intensité*frequance
		cepage = self.settings.value("Physiocap/leCepage2","xx")  # ___recuperer les valeurs des variables : etat sanitaire intensité*frequance
		hauteur_rognage = self.settings.value("Physiocap/hauteur", "xx")  # ___recuperer les valeurs des variables : etat sanitaire intensité*frequance
		densite_plantation = self.settings.value("Physiocap/densite", "xx")  # ___recuperer les valeurs des variables : etat sanitaire intensité*frequance
		type_taille = self.settings.value("Physiocap/laTaille", "xx")  # ___recuperer les valeurs des variables : etat sanitaire intensité*frequance
		diamshp_moy = self.settings.value("Physiocap/diamshp_moy","xx")  # ___recuperer les valeurs des variables : diametre moyen
		nbsarmshp_moy = self.settings.value("Physiocap/nbsarmshp_moy","xx")  # ___recuperer les valeurs des variables : nbsarmshp moyen
		biomshp_moy = self.settings.value("Physiocap/biomshp_moy", "xx")  # ___recuperer les valeurs des variables : biomshp moyen
		vitesseshp_moy = self.settings.value("Physiocap/vitesseshp","xx")  # ___recuperer les valeurs des varoables : vitesse moyenne
		generer_contour = self.settings.value("Physiocap/generer_contour","xx")  # ___recuperer les valeurs des varoables : vitesse moyenne
		geom_wkt = ""
		(chemin_acces, file_name) = os.path.split(nom_fichier_shape_sans_0)
		chemin_fichier_convex = chemin_acces + "\contour_genere.shp"
		if self.checkBoxGenererContour.isChecked():
			# get shape file without 0 and run the function  qgis.convexhull
			processing.runalg("qgis:convexhull", nom_fichier_shape_sans_0, None, 0, chemin_fichier_convex)
			convexhull_layer = QgsVectorLayer(chemin_fichier_convex, 'contour_genere', 'ogr')
			self.settings.setValue("Physiocap/chemin_contour_genere", chemin_fichier_convex)
			# delete fields and leave just the geometry
			fields = convexhull_layer.dataProvider().fields()
			count = 0
			fieldsList = list()
			for field in convexhull_layer.pendingFields():
				fieldsList.append(count)
				count += 1
			convexhull_layer.dataProvider().deleteAttributes(fieldsList)
			convexhull_layer.updateFields()
			# add the layer to the legend
			convexhull_layer.setLayerTransparency(60)
			QgsMapLayerRegistry.instance().addMapLayer(convexhull_layer, False)
			ss_groupe.addLayer(convexhull_layer)
			# iface.addVectorLayer(chemin_fichier_convex, 'contour_genere', 'ogr')
			# get the geometry from the layer and paste it in the csv file
			for feature in convexhull_layer.getFeatures():
				buff = feature.geometry().buffer(0.5, 1)
				convexhull_layer.dataProvider().changeGeometryValues({feature.id(): buff})
				geom_wkt = str(feature.geometry().exportToWkt())
			# add attributes filled by the user
			convexhull_layer.startEditing()

			convexhull_layer.dataProvider().addAttributes([QgsField("Nom_Parcel", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Commune", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Region", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Cepage", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Clone", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Porte_gref", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Annee_plan", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Haut_rogn", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Dens_plan", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Type_tail", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Sol_argile", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Sol_MO", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Sol_CaCo3", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Rendement", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Poi_m_grap", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Nb_grap", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Rend_an-1", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Poi_m_gra1", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Nbgrap-1", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("type_appor", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Fert_prod", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Fert_dose", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("entr_sol", QVariant.String)])
			convexhull_layer.dataProvider().addAttributes([QgsField("Etat_sanit", QVariant.String)])

			convexhull_layer.updateFields()

			for feat in convexhull_layer.getFeatures():
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Nom_Parcel'),
													  nom_parcelle.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Commune'),
													  comuune.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Region'),
													  region.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Cepage'),
													  cepage.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Clone'),
													  clone.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Porte_gref'),
													  str(porte_greffe.encode("Utf-8")))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Annee_plan'),
													  str(annee_plant))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Haut_rogn'),
													  str(hauteur_rognage))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Dens_plan'),
													  str(densite_plantation))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Type_tail'),
													  type_taille.encode("Utf-8"))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Sol_argile'),
													  str(sol_argile))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Sol_MO'),
													  str(sol_mo))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Sol_CaCo3'),
													  str(sol_caco3))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Rendement'),
													  str(rendement))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Poi_m_grap'),
													  str(poids_moy_grappes))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Nb_grap'),
													  str(nb_grappes))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Rend_an-1'),
													  str(rendement_1))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Poi_m_gra1'),
													  str(poids_moy_grappes_1))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Nbgrap-1'),
													  str(nb_grappes_1))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('type_appor'),
													  str(type_apports.encode("Utf-8")))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Fert_prod'),
													  str(produit.encode("Utf-8")))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Fert_dose'),
													  str(dose))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('entr_sol'),
													  str(strategie_entretien_sol.encode("Utf-8")))
				convexhull_layer.changeAttributeValue(feat.id(), convexhull_layer.fieldNameIndex('Etat_sanit'),
													  str(etat_sanitaire.encode("Utf-8")))

			convexhull_layer.commitChanges()
		# get the feature geometry and copy the WKT
		# ecriture de l'entête
		# fichier_synthese_CSV.write("Nom_Parcelle; Commune ; Region ; Cepage; Clone; Porte_greffe; Annee_plantation; Hauteur_rognage; Densite_plantation; Type_taille; Sol_argile; Sol_MO; Sol_CaCo3; Rendement; Poids_moyen_grappes; Nombre_grappes; Rendemenr_annee-1; Poids_moyen_grappes-1; Nombre_grappes-1; Fert_type_apports; Fert_produit; Fert_dose; Strategie_entretien_sol; Etat_sanitaire; Nb_sarments_moy; Section_moy; Biomasse_moy "+"\n")
	return 0


# Fonction pour générer le fichier de sortie CSV ___Nadia___
def physiocap_csv_sortie(self, nom_fichier_synthese_CSV = "NO", nom_fichier_shape_sans_0=""):
	"""Fonction pour generere le ficher de synthese de sortie CSV avec les informations agronomiques"""

	#Ecriture des resultats dans un fichier csv ___Nadia___
	if nom_fichier_synthese_CSV != "NO":
		# ASSERT Le fichier de synthese existe
		if not os.path.isfile( nom_fichier_synthese_CSV):
			uMsg =u"Le fichier de synthese " + nom_fichier_synthese_CSV + "n'existe pas"
			physiocap_log( uMsg)
			return physiocap_error( self, uMsg)

		# Ecriture des resulats
		fichier_synthese_CSV = open(nom_fichier_synthese_CSV, "wb")
		#try:
		writer1 = csv.writer(fichier_synthese_CSV,delimiter=';')
		infoAgro=self.settings.value("Physiocap/info_agro","")#___recuperer les valeurs des variables : InfoAgro : Renseign/Contour
		today = date.today()
		annee = today.strftime("%Y")
		if infoAgro=="Renseign":
			# Ecriture de l'entête
			nom_parcelle=self.settings.value("Physiocap/nom_parcelle", "xx")#___recuperer les valeurs des variables : nom de la parcelle
			annee_plant=self.settings.value("Physiocap/annee_plant","xx")#___recuperer les valeurs des variables : année de plantation
			comuune=self.settings.value("Physiocap/comuune", "xx")#___recuperer les valeurs des variables : commune
			region=self.settings.value("Physiocap/region","xx")#___recuperer les valeurs des variables : region
			clone=self.settings.value("Physiocap/clone","xx")#___définir les valeurs des variables : clone
			porte_greffe=self.settings.value("Physiocap/porte_greffe", "xx")#___recuperer les valeurs des variables : porte-greffe
			sol_argile=self.settings.value("Physiocap/sol_argile","xx")#___recuperer les valeurs des variables : sol pourcentage argile
			sol_mo=self.settings.value("Physiocap/sol_mo","xx")#___recuperer les valeurs des variables : sol pourcentage MO
			sol_caco3=self.settings.value("Physiocap/sol_caco3","xx")#___recuperer les valeurs des variables : sol pourcentage CaCO3
			rendement=self.settings.value("Physiocap/rendement", "xx")#___recuperer les valeurs des variables : rendement annee courante
			nb_grappes=self.settings.value("Physiocap/nb_grappes", "xx")#___recuperer les valeurs des variables : nombre de grappes annee courante
			poids_moy_grappes=self.settings.value("Physiocap/poids_moy_grappes", "xx")#___recuperer les valeurs des variables : poids moyen de grappes annee courante
			rendement_1=self.settings.value("Physiocap/rendement_1","xx")#___recuperer les valeurs des variables : rendement annee precedente
			nb_grappes_1=self.settings.value("Physiocap/nb_grappes_1", "xx")#___recuperer les valeurs des variables : nombre de grappes annee precedente
			poids_moy_grappes_1=self.settings.value("Physiocap/poids_moy_grappes_1", "xx")#___recuperer les valeurs des variables : poids moyen de grappes annee precedente
			type_apports=self.settings.value("Physiocap/type_apports","xx")#___recuperer les valeurs des variables : type apports fertilisation
			produit=self.settings.value("Physiocap/produit", "xx")#___recuperer les valeurs des variables : produit
			dose=self.settings.value("Physiocap/dose", "xx")#___recuperer les valeurs des variables : dose(t/ha)
			strategie_entretien_sol=self.settings.value("Physiocap/strategie_entretien_sol", "xx")#___recuperer les valeurs des variables : strategie entretien de sol
			etat_sanitaire=self.settings.value("Physiocap/etat_sanitaire", "xx")#___recuperer les valeurs des variables : etat sanitaire intensité*frequance
			cepage=self.settings.value("Physiocap/leCepage2", "xx")#___recuperer les valeurs des variables : etat sanitaire intensité*frequance
			hauteur_rognage=self.settings.value("Physiocap/hauteur", "xx")#___recuperer les valeurs des variables : etat sanitaire intensité*frequance
			densite_plantation=self.settings.value("Physiocap/densite", "xx")#___recuperer les valeurs des variables : etat sanitaire intensité*frequance
			type_taille=self.settings.value("Physiocap/laTaille", "xx")#___recuperer les valeurs des variables : etat sanitaire intensité*frequance
			diamshp_moy=self.settings.value("Physiocap/diamshp_moy", "xx") #___recuperer les valeurs des variables : diametre moyen
			nbsarmshp_moy=self.settings.value("Physiocap/nbsarmshp_moy", "xx") #___recuperer les valeurs des variables : nbsarmshp moyen
			biomshp_moy=self.settings.value("Physiocap/biomshp_moy","xx") #___recuperer les valeurs des variables : biomshp moyen
			vitesseshp_moy=self.settings.value("Physiocap/vitesseshp","xx")#___recuperer les valeurs des varoables : vitesse moyenne
			generer_contour=self.settings.value("Physiocap/generer_contour","xx")#___recuperer les valeurs des varoables : vitesse moyenne
			geom_wkt=""
			(chemin_acces, file_name)=os.path.split(nom_fichier_shape_sans_0)
			chemin_fichier_convex=chemin_acces+"\contour_genere.shp"
			# get the feature geometry and copy the WKT
			# ecriture de l'entête
			#fichier_synthese_CSV.write("Nom_Parcelle; Commune ; Region ; Cepage; Clone; Porte_greffe; Annee_plantation; Hauteur_rognage; Densite_plantation; Type_taille; Sol_argile; Sol_MO; Sol_CaCo3; Rendement; Poids_moyen_grappes; Nombre_grappes; Rendemenr_annee-1; Poids_moyen_grappes-1; Nombre_grappes-1; Fert_type_apports; Fert_produit; Fert_dose; Strategie_entretien_sol; Etat_sanitaire; Nb_sarments_moy; Section_moy; Biomasse_moy "+"\n")
			if self.checkBoxGenererContour.isChecked():
				#recuperer le WKT du fichier genere
				chemin_contour_genere=self.settings.value("Physiocap/chemin_contour_genere","xx")
				contour_layer1 = QgsVectorLayer(chemin_contour_genere, 'contour_genere', 'ogr')
				for feature in contour_layer1.getFeatures():
					geom_wkt = str(feature.geometry().exportToWkt())
			else :
				#recuperer le WKT a partir du fichier selectionné dans la liste des contours
				chemin_contour_intra = self.settings.value("Physiocap/layer_intra", "xx")
				chemin_contour_intra2 = chemin_contour_intra.split('|')
				chemin_contour_intra3 = chemin_contour_intra2[0]
				contour_layer2 = QgsVectorLayer(chemin_contour_intra3, 'layer_intra', 'ogr')
				for feature in contour_layer2.getFeatures():
					geom_wkt = str(feature.geometry().exportToWkt())
			#if self.checkBoxGenererContour.isChecked():
			writer1.writerow( ("Nom_Parcelle","Commune ","Region ","Cepage","Clone","Porte_greffe","Annee_plantation",\
								  "Hauteur_rognage","Densite_plantation","Type_taille","Sol_argile","Sol_MO",\
								  "Sol_CaCo3","Rendement","Poids_moyen_grappes","Nombre_grappes","Rendemenr_annee-1",\
								  "Poids_moyen_grappes-1","Nombre_grappes-1","Fert_type_apports",\
								  "Fert_produit","Fert_dose","Strategie_entretien_sol","Etat_sanitaire","NbsarmMoy"+annee,"SectMoy"+annee,"BiomMoy"+annee,"vitMoy"+annee,"geomWKT"))
				# ecriture des veleurs de chaque colonne
				#fichier_synthese_CSV.write( ""+str(nom_parcelle) + ";"+str(comuune)+";"+str(region)+";"+str(cepage)+";"+str(clone)+";"+str(porte_greffe)+";"+str(annee_plant)+";"+ str(hauteur_rognage)+";"+str(densite_plantation)+";"+str(type_taille)+";"+str(sol_argile)+";"+str(sol_mo)+";"+str(sol_caco3)+";"+str(rendement)+";"+str(poids_moy_grappes)+";"+str(nb_grappes)+";"+str(rendement_1)+";"+str(poids_moy_grappes_1)+";"+str(nb_grappes_1)+";"+str(type_apports)+";"+str(produit)+";"+str(dose)+";"+str(strategie_entretien_sol)+";"+str(etat_sanitaire)+";"+str(nbsarmshp_moy)+";"+str(diamshp_moy)+";"+str(biomshp_moy)+"\n")
			writer1.writerow((str(nom_parcelle.encode("Utf-8")),str(comuune.encode("Utf-8")),str(region.encode("Utf-8")),str(cepage.encode("Utf-8")),str(clone.encode("Utf-8")),str(porte_greffe.encode("Utf-8")),str(annee_plant), str(hauteur_rognage),str(densite_plantation),str(type_taille.encode("Utf-8")),str(sol_argile),str(sol_mo),str(sol_caco3),str(rendement),str(poids_moy_grappes),str(nb_grappes),str(rendement_1),str(poids_moy_grappes_1),str(nb_grappes_1),str(type_apports.encode("Utf-8")),str(produit.encode("Utf-8")),str(dose),str(strategie_entretien_sol.encode("Utf-8")),str(etat_sanitaire.encode("Utf-8")),str(nbsarmshp_moy),str(diamshp_moy),str(biomshp_moy),str(vitesseshp_moy),geom_wkt))
				#if generer contour = yes then generer le contour avec la fnction qgis:convexhull
			#else :
				#writer1.writerow(("Nom_Parcelle", " Commune ", " Region ", " Cepage", " Clone", " Porte_greffe", " Annee_plantation", " Hauteur_rognage", " Densite_plantation", " Type_taille", " Sol_argile", " Sol_MO", " Sol_CaCo3", " Rendement", " Poids_moyen_grappes", " Nombre_grappes", " Rendemenr_annee-1", " Poids_moyen_grappes-1", " Nombre_grappes-1"," Fert_type_apports", " Fert_produit", " Fert_dose", " Strategie_entretien_sol", " Etat_sanitaire", " Nb_sarments_moy", " Section_moy", " Biomasse_moy ", "vitess_moy"))
				# ecriture des veleurs de chaque colonne
				# fichier_synthese_CSV.write( ""+str(nom_parcelle) + ";"+str(comuune)+";"+str(region)+";"+str(cepage)+";"+str(clone)+";"+str(porte_greffe)+";"+str(annee_plant)+";"+ str(hauteur_rognage)+";"+str(densite_plantation)+";"+str(type_taille)+";"+str(sol_argile)+";"+str(sol_mo)+";"+str(sol_caco3)+";"+str(rendement)+";"+str(poids_moy_grappes)+";"+str(nb_grappes)+";"+str(rendement_1)+";"+str(poids_moy_grappes_1)+";"+str(nb_grappes_1)+";"+str(type_apports)+";"+str(produit)+";"+str(dose)+";"+str(strategie_entretien_sol)+";"+str(etat_sanitaire)+";"+str(nbsarmshp_moy)+";"+str(diamshp_moy)+";"+str(biomshp_moy)+"\n")
				#writer1.writerow((str(nom_parcelle.encode("Utf-8")), str(comuune.encode("Utf-8")), str(region.encode("Utf-8")), str(cepage.encode("Utf-8")), str(clone.encode("Utf-8")), str(porte_greffe.encode("Utf-8")), str(annee_plant), str(hauteur_rognage),	 str(densite_plantation), str(type_taille.encode("Utf-8")), str(sol_argile), str(sol_mo), str(sol_caco3), str(rendement), str(poids_moy_grappes), str(nb_grappes), str(rendement_1), str(poids_moy_grappes_1), str(nb_grappes_1),	 str(type_apports.encode("Utf-8")), str(produit.encode("Utf-8")), str(dose), str(strategie_entretien_sol.encode("Utf-8")), str(etat_sanitaire.encode("Utf-8")), str(nbsarmshp_moy), str(diamshp_moy), str(biomshp_moy), str(vitesseshp_moy)))

		if infoAgro=="Contour":
			#get selected layer
			selected_layer=self.comboBoxContours.currentText()
			liste_fields_names=[]
			liste_fields_values=[]
			if selected_layer :
				#write rows from colomns

				nom_complet_poly = self.comboBoxContours.currentText().split( SEPARATEUR_NOEUD)
				inputLayer = nom_complet_poly[0]
				layer = self.lister_nom_couches( inputLayer)
				if layer is not None:
					k=0#indice pour parcourir les entites
					for feature in layer.getFeatures():
						k=k+1
					if k==0:
						print ("Le fichier est vide, aucune information ne peut etre extraite")
						physiocap_message_box( self, "Le fichier est vide, aucune information ne peut etre extraite", "information")
			else :
				print	("Il faut selectionner un fichier shp/si le projet ne contient aucun fichier shapefile , il faut l'ouvrir et ressayer")
				physiocap_message_box( self, "Il faut selectionner un fichier shp/si le projet ne contient aucun fichier shapefile , il faut l'ouvrir et ressayer", "information")
			#calcul points statistics for polygones pour avoir une moyenne de diam/biomass/nbsarments pour chaque parcelle
			last_project_path=self.settings.value("Physiocap/dernier_repertoire", "xx")
			chemin_donnees_cibles=self.lineEditDirectoryFiltre.text()
			chemin_entier_projet=chemin_donnees_cibles+'\\'+last_project_path
			chemin_shapeFiles = os.path.join(chemin_entier_projet, REPERTOIRE_SHAPEFILE)
			Nom_Projet=self.lineEditProjet.text()
			laProjection, EXT_CRS_SHP, EXT_CRS_PRJ, EXT_CRS_RASTER, EPSG_NUMBER = physiocap_quelle_projection_demandee( self)
			nom_complet_poly = self.comboBoxContours.currentText().split( SEPARATEUR_NOEUD)
			inputLayer = nom_complet_poly[0]
			layer = self.lister_nom_couches( inputLayer)
			nom_court_shape_sans_0 = Nom_Projet + "_POINTS" + EXT_CRS_SHP
			nom_shape_sans_0 = os.path.join(chemin_shapeFiles, nom_court_shape_sans_0)
			stat1="stat1.shp"
			stat2="stat2.shp"
			stat3="stat3.shp"
			stat4="stat4.shp"
			nom_stat1=os.path.join(chemin_shapeFiles,stat1)
			nom_stat2=os.path.join(chemin_shapeFiles, stat2)
			nom_stat3=os.path.join(chemin_shapeFiles, stat3)
			nom_stat4=os.path.join(chemin_shapeFiles, stat4)
			processing.runalg("saga:pointstatisticsforpolygons",nom_shape_sans_0 ,layer.source(),"DIAM",1,False,True,False,False,False,False,False,nom_stat1)
			processing.runalg("saga:pointstatisticsforpolygons",nom_shape_sans_0 ,nom_stat1,"BIOM",1,False,True,False,False,False,False,False,nom_stat2)
			processing.runalg("saga:pointstatisticsforpolygons",nom_shape_sans_0 ,nom_stat2,"NBSARM",1,False,True,False,False,False,False,False,nom_stat3)
			processing.runalg("saga:pointstatisticsforpolygons",nom_shape_sans_0 ,nom_stat3,"VITESSE",1,False,True,False,False,False,False,False,nom_stat4)

			#Ajouter les champs diametre,nbsarments et biomasse à la liste pour les ecriredans le fichier CSV
			#diamshp_moy=self.settings.value("Physiocap/diamshp_moy", "xx") #___recuperer les valeurs des variables : diametre moyen
			#nbsarmshp_moy=self.settings.value("Physiocap/nbsarmshp_moy", "xx") #___recuperer les valeurs des variables : nbsarmshp moyen
			#biomshp_moy=self.settings.value("Physiocap/biomshp_moy","xx") #___recuperer les valeurs des variables : biomshp moyen
			#liste_fields_names.append("Nb_sarments_moy")
			#liste_fields_names.append("Section_moy")
			#liste_fields_names.append("Biomasse_moy")
			#liste_fields_values.append(nbsarmshp_moy)
			#liste_fields_values.append(diamshp_moy)
			#liste_fields_values.append(biomshp_moy)

			chemin_stat_vector=nom_stat4.replace('\\','/')
			newVector = QgsVectorLayer( chemin_stat_vector, 'StatisticsCSV', 'ogr')
			#QgsMapLayerRegistry.instance().addMapLayer(newVector)
			for index, field in enumerate(newVector.dataProvider().fields()):
						mon_nom = field.name().encode("Utf-8")
						if "DIAM" in mon_nom or "BIOM" in mon_nom or  "NBSARM" in mon_nom or  "VITESSE" in mon_nom:
							liste_fields_names.append(mon_nom+annee)
						else:
							liste_fields_names.append(mon_nom)
			liste_fields_names.append("GeomWKT")
			writer1.writerow(liste_fields_names)

			for feature in newVector.getFeatures():
				for j in range(len(liste_fields_names)-1):
					liste_fields_values.append(str(feature[j]).encode("Utf-8"))
					#liste_fields_values.append((feature[j]))
				liste_fields_values.append(str(feature.geometry().exportToWkt()))
				writer1.writerow(liste_fields_values)
				del liste_fields_values [:]
				
		#except:
			#msg = "Erreur bloquante durant l ecriture du fichier CSV\n"
			#physiocap_error( self, msg )
			#return -1

		fichier_synthese_CSV.close()
		
		return 0


# Fonction pour vérifier le fichier csv
def physiocap_assert_csv(self, src, err):
	"""Fonction d'assert.
	Vérifie si le csv est au bon format:
	58 virgules
	une date en première colonne
	des float ensuite
	"""
	numero_ligne = 0
	nombre_erreurs = 0
	while True :
		ligne = src.readline() # lit les lignes 1 à 1
		if not ligne: break
		# Vérifier si ligne OK
		numero_ligne = numero_ligne + 1
		#physiocap_log( u"Assert CVS ligne lue %d" % (numero_ligne))

		result = ligne.split(",") # split en fonction des virgules
		# Vérifier si le champ date a bien deux - et 2 deux points
		tirets = result[ 0].count("-")
		deux_points = result[ 0].count(":")
		#physiocap_log( u"Champ date contient %d tirets et %d deux points" % (tirets, deux_points))
		if ((tirets != 2) or (deux_points != 2)):
			aMsg = "La ligne numéro %d ne commence pas par une date" % (numero_ligne)
			uMsg = unicode(aMsg, 'utf-8')
			nombre_erreurs = nombre_erreurs + 1
			if nombre_erreurs < 10:
				physiocap_error( self, uMsg )
			err.write( aMsg + '\n' ) # on écrit la ligne dans le fichier ERREUR.csv

			continue # on a tracé erreur et on saute la ligne

		# Vérifier si tous les champs sont des float
		i = 0
		for x in result[1:58]:
			i = i+1
			try:
				y = float( x)
				# physiocap_log( u"%d Champ  %s est de type %s" % (i, x, type( y)))
			except:
				aMsg = "La ligne numéro %d a des colonnes mal formatées (x.zzz attendu)" % (numero_ligne)
				uMsg = unicode(aMsg, 'utf-8')
				nombre_erreurs = nombre_erreurs + 1
				if nombre_erreurs < 10:
					physiocap_error( self, uMsg )
					err.write( aMsg + "\n") # on écrit la ligne dans le fichier ERREUR.csv
				break # on a tracé une erreur et on saute la ligne

		comptage = ligne.count(",") # compte le nombre de virgules
		if comptage > NB_VIRGULES:
			# Assert Trouver les lignes de données invalides ( sans 58 virgules ... etc)
			aMsg = "La ligne numéro %d n'a pas %s virgules" % (numero_ligne, NB_VIRGULES)
			uMsg = unicode(aMsg, 'utf-8')
			nombre_erreurs = nombre_erreurs + 1
			if nombre_erreurs < 10:
				physiocap_error( self, uMsg )
			err.write( aMsg + '\n') # on écrit la ligne dans le fichier ERREUR.csv
			continue # on a tracé erreur et on saute la ligne


	# Au bilan
	if (numero_ligne != 0):
		#physiocap_log( u"Assert CVS a lu %d lignes et trouvé %d erreurs" % (numero_ligne, nombre_erreurs ))
		pourcentage_erreurs = float( nombre_erreurs * 100 / numero_ligne)
		return pourcentage_erreurs
	else:
		return 0

##            try:
##                raise physiocap_exception_err_csv( pourcentage_erreurs)
##            except:
##                raise

# Fonction pour créer les fichiers histogrammes    
def physiocap_fichier_histo( self, src, histo_diametre, histo_nbsarment, err):
	"""Fonction de traitement. Creation des fichiers pour réaliser les histogrammes
	Lit et traite ligne par ligne le fichier source (src).
	Les résultats est écrit au fur et à mesure dans histo_diametre ou histo_nbsarment
	"""
   
	numero_ligne = 0
	while True :
		ligne = src.readline() # lit les lignes 1 à 1
		if not ligne: break
		# Vérifier si ligne OK
		numero_ligne = numero_ligne + 1
		comptage = ligne.count(",") # compte le nombre de virgules
		if comptage != NB_VIRGULES:
			# Assert ligne sans 58 virgules
			continue # on saute la ligne

		result = ligne.split(",") # split en fonction des virgules
		# Intergrer ici les autres cas d'erreurs

		try : # accompli cette fonction si pas d'erreur sinon except
			XY = [float(x) for x in result[1:9]]   # on extrait les XY et on les transforme en float  > Données GPS
			diams = [float(x) for x in result[9:NB_VIRGULES+1]] # on extrait les diams et on les transforme en float
			diamsF = [i for i in diams if i > 2 and i < 28 ] # on filtre les diams > diamsF correspond aux diams filtrés entre 2 et 28
			if comptage==NB_VIRGULES and len(diamsF)>0 : # si le nombre de diamètre après filtrage != 0 alors mesures
				if XY[7] != 0:
					nbsarm = len(diamsF)/(XY[7]*1000/3600) #8eme donnée du GPS est la vitesse. Dernier terme : distance entre les sarments
				else:
					nbsarm = 0
				histo_nbsarment.write("%f%s" %(nbsarm,";"))
				for n in range(len(diamsF)) :
					histo_diametre.write("%f%s" %(diamsF[n],";"))
		except : # accompli cette fonction si erreur
			msg = "%s%s\n" %("Erreur histo",ligne)
			physiocap_error( self, msg )
			err.write( str( msg) ) # on écrit la ligne dans le fichier ERREUR.csv
			pass # on mange l'exception



def physiocap_tracer_histo(src, name, min=0, max =28, labelx = "Lab X", labely = "Lab Y", titre = "Titre", bins = 100):
	#"""Fonction de traitement.
	#Lit et traite ligne par ligne le fichier source (src).
	#Le résultat est écrit au fur et à mesure dans le
	#fichier destination (dst).
	#"""
	ligne2 = src.readline()
	histo = ligne2.split(";") # split en fonction des virgules
	# Assert len(histo)
	XY = [float(x) for x in histo[0:-1]]   # on extrait les XY et on les transforme en float
	valeur = len(XY)
	#physiocap_log( u"Histo min %d et nombre de valeurs : %d " % (min, valeur))
	classes = np.linspace(min, max, max+1)
	plt.hist(XY,bins=classes,normed=1, facecolor='green', alpha=0.75)
	plt.xlabel(labelx)
	plt.ylabel(labely)
	plt.title(titre)
	plt.xlim((min, max))
	plt.grid(True)
	plt.savefig(name)
	plt.show( block = 'false')
	plt.close()


# Fonction de filtrage et traitement des données
def physiocap_filtrer(self, src, csv_sans_0, csv_avec_0, diametre_filtre, 
	nom_fichier_synthese, err,
	mindiam, maxdiam, max_sarments_metre, details,
	eer, eec, d, hv):
	"""Fonction de traitement.
	Filtre ligne par ligne les données de source (src) pour les valeurs
	comprises entre mindiam et maxdiam et verifie si on n'a pas atteint le max_sarments_metre.
	Le résultat est écrit au fur et à mesure dans les fichiers
	csv_sans_0 et csv_avec_0 mais aussi diametre_filtre
	La synthese est allongé
	"details" pilote l'ecriture de 5 parametres ou de la totalité des 10 parametres
	"""

	#S'il n'existe pas de données parcellaire, le script travaille avec les données brutes
	if details == "NO" :
		csv_sans_0.write("%s\n" % ("X ; Y ; XL93 ; YL93 ; NBSARM ; DIAM ; BIOM ; Date ; Vitesse")) # ecriture de l'entête
		csv_avec_0.write("%s\n" % ("X ; Y ; XL93 ; YL93 ; NBSARM ; DIAM ; BIOM ; Date ; Vitesse")) # ecriture de l'entête
	#S'il existe des données parcellaire, le script travaille avec les données brutes et les données calculées
	else:
		# Assert details == "YES"
		if details != "YES" :
			return physiocap_error( self, self.trUtf8("Problème majeur dans le choix du détail du parcellaire"))
		csv_sans_0.write("%s\n" % ("X ; Y ; XL93 ; YL93 ; NBSARM ; DIAM ; BIOM ; Date ; Vitesse ; \
			NBSARMM2 ; NBSARCEP ; BIOMMM2 ; BIOMGM2 ; BIOMGCEP ")) # ecriture de l'entête
		csv_avec_0.write("%s\n" % ("X ; Y ; XL93 ; YL93 ; NBSARM ; DIAM ; BIOM ; Date ; Vitesse ; \
			NBSARMM2 ; NBSARCEP ; BIOMMM2 ; BIOMGM2 ; BIOMGCEP ")) # ecriture de l'entête

	nombre_ligne = 0
	# Pour progress bar entre 15 et 40
	lignes = src.readlines()#___recuperer les lignes du fichier csv de concatenation
	max_lignes = len(lignes)#___recuperer le nombre de lignes dans le fichier csv de concatenation
	progress_step = int( max_lignes / 25)
	#physiocap_log("Bar step: " + str( progress_step))
	progress_bar = 15
	barre = 1
	for ligne in lignes :#___ Parcourir les lignes du fichier concatenation
		nombre_ligne = nombre_ligne + 1
		if not ligne: break

		# Progress BAR de 15 à 40 %
		if ( nombre_ligne > barre * progress_step):
			progress_bar = progress_bar + 1
			barre = barre + 1
			self.progressBar.setValue( progress_bar)

		comptage = ligne.count(",") # compte le nombre de virgules
		result = ligne.split(",") # split en fonction des virgules

		try : # accompli cette fonction si pas d'erreur sinon except
			XY = [float(x) for x in result[1:9]]   # on extrait les XY et on les transforme en float  #___result[0]=date
			# On transforme les WGS84 en L93
			WGS84 = osr.SpatialReference()
			WGS84.ImportFromEPSG( EPSG_NUMBER_GPS)
			LAMB93 = osr.SpatialReference()
			LAMB93.ImportFromEPSG( EPSG_NUMBER_L93)
			transformation1 = osr.CoordinateTransformation(WGS84,LAMB93)
			L93 = transformation1.TransformPoint(XY[0],XY[1])
			diams = [float(x) for x in result[9:NB_VIRGULES+1]] # on extrait les diams et on les transforme en float
			diamsF = [i for i in diams if i > mindiam and i < maxdiam ] # on filtre les diams avec les paramètres entrés ci-dessus
			if details == "NO" :
				if len(diamsF)==0: # si le nombre de diamètre après filtrage = 0 alors pas de mesures
					nbsarm = 0
					diam =0
					biom = 0
					csv_avec_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%i%s%i%s%i%s%s%s%0.2f\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam ,";",biom,";",result[0],";",XY[7]))  # on écrit la ligne dans le fichier OUT0.csv
				elif comptage==NB_VIRGULES and len(diamsF)>0 : # si le nombre de diamètre après filtrage != 0 alors mesures
					if XY[7] != 0:#___ la vitesse n est pas nulle donc il y a des mesures
						nbsarm = len(diamsF)/(XY[7]*1000/3600)#____************************* Calcul du nombre de sarments *************************************
					else:
						nbsarm = 0
					if nbsarm > 1 and nbsarm < max_sarments_metre :
						diam =sum(diamsF)/len(diamsF)#____************************* Calcul de diametre *************************************
						biom=3.1416*(diam/2)*(diam/2)*nbsarm#___calcul de biomasse
						csv_avec_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%0.2f%s%.2f%s%.2f%s%s%s%0.2f\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam,";",biom,";",result[0],";",XY[7])) # on écrit la ligne dans le fichier OUT0.csv
						csv_sans_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%0.2f%s%.2f%s%.2f%s%s%s%0.2f\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam,";",biom,";",result[0],";",XY[7])) # on écrit la ligne dans le fichier OUT.csv
						for n in range(len(diamsF)) :
							diametre_filtre.write("%f%s" %(diamsF[n],";"))
			elif details == "YES" :
				if len(diamsF)==0: # si le nombre de diamètre après filtrage = 0 alors pas de mesures
					nbsarm = 0
					diam =0
					biom = 0
					nbsarmm2 = 0
					nbsarcep = 0
					biommm2 = 0
					biomgm2 = 0
					biomgcep = 0
					csv_avec_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%i%s%i%s%i%s%s%s%0.2f%s%i%s%i%s%i%s%i%s%i\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam ,";",biom,";",result[0],";",XY[7],";",nbsarmm2,";",nbsarcep,";",biommm2,";",biomgm2,";",biomgcep))  # on écrit la ligne dans le fichier OUT0.csv
				elif comptage==NB_VIRGULES and len(diamsF)>0 : # si le nombre de diamètre après filtrage != 0 alors mesures
					if XY[7] != 0:
						nbsarm = len(diamsF)/(XY[7]*1000/3600)
					else:
						nbsarm = 0
					if nbsarm > 1 and nbsarm < max_sarments_metre :
						diam =sum(diamsF)/len(diamsF)
						biom=3.1416*(diam/2)*(diam/2)*nbsarm
						nbsarmm2 = nbsarm/eer*100
						nbsarcep = nbsarm*eec/100
						biommm2 = biom/eer*100
						biomgm2 = biom*d*hv/eer
						biomgcep = biom*d*hv*eec/100/100
						csv_avec_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%.2f%s%.2f%s%.2f%s%s%s%.2f%s%.2f%s%.2f%s%.2f%s%.2f%s%.2f\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam ,";",biom,";",result[0],";",XY[7],";",nbsarmm2,";",nbsarcep,";",biommm2,";",biomgm2,";",biomgcep)) # on écrit la ligne dans le fichier OUT0.csv
						csv_sans_0.write("%.7f%s%.7f%s%.7f%s%.7f%s%.2f%s%.2f%s%.2f%s%s%s%.2f%s%.2f%s%.2f%s%.2f%s%.2f%s%.2f\n" %(XY[0],";",XY[1],";",L93[0],";",L93[1],";",nbsarm,";",diam ,";",biom,";",result[0],";",XY[7],";",nbsarmm2,";",nbsarcep,";",biommm2,";",biomgm2,";",biomgcep)) # on écrit la ligne dans le fichier OUT.csv
						for n in range(len(diamsF)) :
							diametre_filtre.write("%f%s" %(diamsF[n],";"))
		except : # accompli cette fonction si erreur
			aMsg = "Erreur bloquante durant filtrage : pour la ligne numéro %d" %( nombre_ligne)
			uMsg = unicode(aMsg, 'utf-8')
			physiocap_error( self, uMsg )
			err.write( aMsg) # on écrit la ligne dans le fichier ERREUR.csv
			return -1
	#physiocap_log( u"Fin filtrage OK des "+ str(nombre_ligne - 1) + " lignes.")
	return 0


