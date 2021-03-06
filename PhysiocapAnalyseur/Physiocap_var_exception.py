# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhysiocapException
                                 A QGIS plugin

 Le module Exception contient les définition d'exception
                             -------------------
        begin                : 2015-11-04
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
# ###########################
# Preparation Python 3 pour QGIS 3
# ###########################
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Suppression des u''
from __future__ import unicode_literals

##from builtins import open
##from builtins import str

import os 
import platform

# ###########################
# VARIABLES GLOBALES
# ###########################

# Ces variables sont nommées en Francais par compatibilité avec la version physiocap_V8
# dont les fonctions de calcul sont conservé à l'identique
# Répertoire de base et projet
PHYSIOCAP_TRACE = "YES"
# En prod CENTROIDES vaut NO
CENTROIDES = "NO"  # CENTROIDES YES est pour voir les centroides dans la synthese

REPERTOIRE_DONNEES_BRUTES = "Choisissez votre chemin"
PHYSIOCAP_NOM = "Physiocap"
PHYSIOCAP_UNI = u"\u03D5"
PHYSIOCAP_WARNING = u"\u26A0"

# Test de robustesse de la gestion des unicodes
PHYSIOCAP_TEST1 = "ȧƈƈḗƞŧḗḓ ŧḗẋŧ ƒǿř ŧḗşŧīƞɠ"
PHYSIOCAP_TEST2 = "ℛℯα∂α♭ℓℯ ♭ʊ☂ η☺т Ѧ$☾ℐℐ"
PHYSIOCAP_TEST3 = "¡ooʇ ןnɟǝsn sı uʍop-ǝpısdn"
PHYSIOCAP_TEST4 = "Moët"
POSTGRES_NOM = "postgres"


SEPARATEUR_ ="_"
NOM_PROJET = "PHY" + SEPARATEUR_ # + PHYSIOCAP_TEST4 + SEPARATEUR_

# Listes de valeurs
#CEPAGES = [ "INCONNU", "CHARDONNAY", "MERLOT", "NEGRETTE", "PINOT NOIR", "PINOT MEUNIER"]
CEPAGES = [ 'Inconnu', 'Airen', 'Alicante', 'Aligote', \
'Barbera', 'Blaufrankisch', 'Bobal', \
'Cabernet Franc', 'Cabernet Sauvignon', 'Castelao', 'Catarratto', 'Cayetana', 'Chardonnay', \
'Chasselas', 'Chenin', 'Cinsaut', 'Colombard', 'Concord', 'Cot', 'Criolla Grande', \
'Douce Noire', 'Doukkali', 'Fernao Pires', 'Feteasca', \
'Gamay', 'Garganega', 'Grasevina', 'Grenache', 'Gruner Veltliner', 'Isabella', \
'Listan Prieto', 'Macabeo', 'Mazuelo', 'Melon', 'Mencia', 'Merlot', 'Monastrell', \
'Montepulciano', 'Muscat', 'Muëller Thurgau', \
'Negroamaro', 'Niagara', 'Négrette', \
'Palomino Fino', 'Pamid', 'Pedro Gimenez', 'Pinot Blanc', 'Pinot Meunier', 'Pinot Noir', \
'Prokupac', 'Riesling', 'Rkatsiteli', \
'Sangiovese', 'Sauvignon', 'Semillon', 'Sultaniye', 'Syrah', \
'Tempranillo', 'Trebbiano', 'Trebbiano Romagnolo', 'Tribidrag', 'Zinfandel']

#CRUs et régions dans le groupebox informations agronomiques ___Nadia___
CRUS=["","AILLEVILLE","ALLEMANT","AMBONNAY","ARCIS-LE-PONSART","ARCONVILLE","ARGANCON", \
"ARRENTIERES","ARSONVAL","AUBILLY","AVENAY-VAL-D'OR","AVIREY-LINGEY","AVIZE","AY","AZY-SUR-MARNE", \
"BAGNEUX-LA-FOSSE","BALNOT-SUR-LAIGNES","BAR-SUR-AUBE","BAR-SUR-SEINE","BARBONNE-FAYEL","BAROVILLE", \
"BARZY-SUR-MARNE","BASLIEUX-SOUS-CHATILLON","BASSU","BASSUET","BAULNE-EN-BRIE","BAYE","BEAUMONT-SUR-VESLE", \
"BEAUNAY","BELVAL-SOUS-CHATILLON","BERGERES","BERGERES-LES-VERTUS","BERGERES-SOUS-MONTMIRAIL","BERRU", \
"BERTIGNOLLES","BETHON","BEZANNES","BEZU-LE-GUERY","BILLY-LE-GRAND","BINSON-ET-ORQUIGNY","BISSEUIL", \
"BLESMES","BLIGNY","BLIGNY","BONNEIL","BOUILLY","BOULEUSE","BOURSAULT","BOUZY","BRAGELOGNE-BEAUVOIR", \
"BRANSCOURT","BRASLES","BRIMONT","BROUILLET","BROUSSY-LE-GRAND","BROYES","BRUGNY-VAUDANCOURT","BUXEUIL", \
"BUXIERES-SUR-ARCE","CAUROY-LES-HERMONVILLE","CELLES-LES-CONDE","CELLES-SUR-OURCE","CERNAY-LES-REIMS", \
"CHACENAY","CHALONS-SUR-VESLE","CHAMBRECY","CHAMERY","CHAMPIGNOL-LEZ-MONDEVILLE","CHAMPILLON", \
"CHAMPLAT-ET-BOUJACOURT","CHAMPVOISY","CHANGY","CHANNES","CHANTEMERLE","CHARLY-SUR-MARNE","CHARTEVES", \
"CHATEAU-THIERRY","CHATILLON-SUR-MARNE","CHAUMUZY","CHAVOT-COURCOURT","CHENAY","CHERVEY","CHEZY-SUR-MARNE", \
"CHIERRY","CHIGNY-LES-ROSES","CHOUILLY","CITRY","COIZARD-JOCHES","COLOMBE-LA-FOSSE","COLOMBE-LE-SEC", \
"COLOMBEY-LES-DEUX-EGLISES","CONGY","CONNIGIS","CORMICY","CORMONTREUIL","CORMOYEUX","COULOMMES-LA-MONTAGNE", \
"COURCELLES-SAPICOURT","COURJEONNET","COURMAS","COURTAGNON","COURTEMONT-VARENNES","COURTERON","COURTHIEZY", \
"COURVILLE","COUVIGNON","COUVROT","CRAMANT","CREZANCY","CROUTTES-SUR-MARNE","CRUGNY","CUCHERY","CUIS","CUISLES", \
"CUMIERES","CUNFIN","DAMERY","DIZY","DOLANCOURT","DOMPTIN","DORMANS","ECUEIL","EGUILLY-SOUS-BOIS","ENGENTE", \
"EPERNAY","ESSOMES-SUR-MARNE","ESSOYES","ETAMPES-SUR-MARNE","ETOGES","ETRECHY","FAVEROLLES-ET-COEMY", \
"FEREBRIANGES","FESTIGNY","FLEURY-LA-RIVIERE","FONTAINE","FONTAINE-DENIS-NUISY","FONTAINE-SUR-AY","FONTETTE", \
"FOSSOY","FRAVAUX","GERMAINE","GERMIGNY","GIVRY-LES-LOISY","GLAND","GLANNES","GRAUVES","GUEUX","GYE-SUR-SEINE", \
"HAUTVILLERS","HERMONVILLE","HOURGES","IGNY-COMBLIZY","JANVRY","JAUCOURT","JAULGONNE","JONCHERY-SUR-VESLE", \
"JONQUERY","JOUY-LES-REIMS","LA CELLE-SOUS-CHANTEMERLE","LA CHAPELLE-MONTHODON","LA NEUVILLE-AUX-LARRIS", \
"LA VILLE-SOUS-ORBAIS","LAGERY","LANDREVILLE","LE BREUIL","LE MESNIL-SUR-OGER","LES MESNEUX","LES RICEYS", \
"LEUVRIGNY","LHERY","LIGNOL-LE-CHATEAU","LISSE-EN-CHAMPAGNE","LOCHES-SUR-OURCE","LOISY-EN-BRIE","LOISY-SUR-MARNE", \
"LOUVOIS","LUDES","MAILLY-CHAMPAGNE","MANCY","MARDEUIL","MAREUIL-LE-PORT","MAREUIL-SUR-AY","MARFAUX","MERFY", \
"MERLAUT","MERREY-SUR-ARCE","MERY-PREMECY","MEURVILLE","MEZY-MOULINS","MONDEMENT-MONTGIVROUX","MONT-SAINT-PERE", \
"MONTBRE","MONTGENOST","MONTGUEUX","MONTHELON","MONTHUREL","MONTIER-EN-L'ISLE","MONTIGNY-SUR-VESLE", \
"MONTREUIL-AUX-LIONS","MORANGIS","MOSLINS","MOUSSY","MUSSY-SUR-SEINE","MUTIGNY","NANTEUIL-LA-FORET", \
"NANTEUIL-SUR-MARNE","NESLE-LE-REPONS","NESLES-LA-MONTAGNE","NEUVILLE-SUR-SEINE","NOE-LES-MALLETS", \
"NOGENT-L'ABBESSE","NOGENT-L'ARTAUD","NOGENTEL","OEUILLY","OGER","OIRY","OLIZY","ORBAIS-L'ABBAYE","ORMES", \
"OYES","PARGNY-LES-REIMS","PASSY-GRIGNY","PASSY-SUR-MARNE","PAVANT","PEVY","PIERRY","PLAINES-SAINT-LANGE", \
"POILLY","POLISOT","POLISY","PONTFAVERGER-MORONVILLIERS","POUILLON","POURCY","PROUILLY","PROVERVILLE","PUISIEULX", \
"REIMS","REUIL","REUILLY-SAUVIGNY","RILLY-LA-MONTAGNE","RIZAUCOURT-BUCHEY","ROMENY-SUR-MARNE","ROMERY","ROMIGNY", \
"ROSNAY","ROUVRES-LES-VIGNES","SAACY-SUR-MARNE","SACY","SAINT-AGNAN","SAINT-AMAND-SUR-FION", \
"SAINT-EUPHRAISE-ET-CLAIRIZET","SAINT-GILLES","SAINT-LUMIER-EN-CHAMPAGNE","SAINT-MARTIN-D'ABLOIS","SAINT-THIERRY", \
"SAINT-USAGE","SAINTE-GEMME","SARCY","SAUDOY","SAULCHERY","SAULCY","SAVIGNY-SUR-ARDRES","SELLES","SERMIERS", \
"SERZY-ET-PRIN","SEZANNE","SILLERY","SOULIERES","SPOY","TAISSY","TALUS-SAINT-PRIX","TAUXIERES-MUTRY","THIL", \
"TOURS-SUR-MARNE","TRAMERY","TRANNES","TRELOU-SUR-MARNE","TREPAIL","TRESLON","TRIGNY","TROIS-PUITS","TROISSY", \
"UNCHAIR","URVILLE","VAL-DE-VIERE","VAL-DES-MARAIS","VANAULT-LE-CHATEL","VANDEUIL","VANDIERES","VAUCIENNES", \
"VAUDEMANGE","VAVRAY-LE-GRAND","VAVRAY-LE-PETIT","VENTEUIL","VERNEUIL","VERPILLIERES-SUR-OURCE","VERT-TOULON", \
"VERTUS","VERZENAY","VERZY","VILLE-DOMMANGE","VILLE-EN-TARDENOIS","VILLE-SUR-ARCE","VILLENAUXE-LA-GRANDE", \
"VILLENEUVE-RENNEVILLE-CHEVIGNY","VILLERS-ALLERAND","VILLERS-AUX-NOEUDS","VILLERS-FRANQUEUX","VILLERS-MARMERY", \
"VILLERS-SOUS-CHATILLON","VILLEVENARD","VILLIERS-SAINT-DENIS","VINAY","VINCELLES","VINDEY","VITRY-EN-PERTHOIS", \
"VITRY-LE-CROISE","VIVIERS-SUR-ARTAUT","VOIGNY","VOIPREUX","VRIGNY"]

REGIONS=["","BAR SUR AUBOIS","REGION DE SEZANNE","REGION DE BOUZY AMBONNAY","VALLEE DE L'ARDRE","BAR SUR AUBOIS", \
"BAR SUR AUBOIS","BAR SUR AUBOIS","BAR SUR AUBOIS","VALLEE DE L'ARDRE","GRANDE VALLEE DE LA MARNE","BAR SEQUANNAIS", \
"COTE DES BLANCS","GRANDE VALLEE DE LA MARNE","REGION DE L'AISNE","BAR SEQUANNAIS","BAR SEQUANNAIS","BAR SUR AUBOIS", \
"BAR SEQUANNAIS","REGION DE SEZANNE","BAR SUR AUBOIS","REGION DE L'AISNE","VALLEE DE LA MARNE RIVE DROITE", \
"REGION DE VITRY LE FRANCOIS","REGION DE VITRY LE FRANCOIS","REGION DE L'AISNE","LES COTEAUX DU PETIT MORIN", \
"REGION DE VERZY VERZENAY","LES COTEAUX DU PETIT MORIN","VALLEE DE LA MARNE RIVE DROITE","BAR SUR AUBOIS", \
"COTE DES BLANCS","LES COTEAUX DU PETIT MORIN","REGION DE VILLERS MARMERY TREPAIL","BAR SEQUANNAIS","REGION DE SEZANNE", \
"MONTAGNE OUEST","REGION DE L'AISNE","REGION DE VILLERS MARMERY TREPAIL","VALLEE DE LA MARNE RIVE DROITE", \
"GRANDE VALLEE DE LA MARNE","REGION DE L'AISNE","BAR SUR AUBOIS","VALLEE DE L'ARDRE","REGION DE L'AISNE", \
"MONTAGNE OUEST","VALLEE DE L'ARDRE","VALLEE DE LA MARNE RIVE GAUCHE","REGION DE BOUZY AMBONNAY","BAR SEQUANNAIS", \
"MONTAGNE OUEST","REGION DE L'AISNE","MASSIF DE SAINT THIERRY","VALLEE DE L'ARDRE","LES COTEAUX DU PETIT MORIN", \
"REGION DE SEZANNE","REGION D'EPERNAY","BAR SEQUANNAIS","BAR SEQUANNAIS","MASSIF DE SAINT THIERRY","REGION DE L'AISNE", \
"BAR SEQUANNAIS","REGION DE VILLERS MARMERY TREPAIL","BAR SEQUANNAIS","MASSIF DE SAINT THIERRY","VALLEE DE L'ARDRE", \
"MONTAGNE OUEST","BAR SUR AUBOIS","GRANDE VALLEE DE LA MARNE","VALLEE DE LA MARNE RIVE DROITE","REGION DE L'AISNE", \
"REGION DE VITRY LE FRANCOIS","BAR SEQUANNAIS","REGION DE SEZANNE","REGION DE L'AISNE","REGION DE L'AISNE", \
"REGION DE L'AISNE","VALLEE DE LA MARNE RIVE DROITE","VALLEE DE L'ARDRE","REGION D'EPERNAY","MASSIF DE SAINT THIERRY", \
"BAR SEQUANNAIS","REGION DE L'AISNE","REGION DE L'AISNE","REGION DE CHIGNY LES ROSES","COTE DES BLANCS","REGION DE L'AISNE", \
"LES COTEAUX DU PETIT MORIN","BAR SUR AUBOIS","BAR SUR AUBOIS","BAR SUR AUBOIS","LES COTEAUX DU PETIT MORIN", \
"REGION DE L'AISNE","MASSIF DE SAINT THIERRY","REGION DE CHIGNY LES ROSES","VALLEE DE LA MARNE RIVE GAUCHE", \
"MONTAGNE OUEST","MONTAGNE OUEST","LES COTEAUX DU PETIT MORIN","MONTAGNE OUEST","VALLEE DE L'ARDRE","REGION DE L'AISNE", \
"BAR SEQUANNAIS","REGION DE L'AISNE","VALLEE DE L'ARDRE","BAR SUR AUBOIS","REGION DE VITRY LE FRANCOIS","COTE DES BLANCS", \
"REGION DE L'AISNE","REGION DE L'AISNE","VALLEE DE L'ARDRE","VALLEE DE LA MARNE RIVE DROITE","COTE DES BLANCS", \
"VALLEE DE LA MARNE RIVE DROITE","GRANDE VALLEE DE LA MARNE","BAR SEQUANNAIS","VALLEE DE LA MARNE RIVE GAUCHE", \
"GRANDE VALLEE DE LA MARNE","BAR SUR AUBOIS","REGION DE L'AISNE","VALLEE DE LA MARNE RIVE DROITE","MONTAGNE OUEST", \
"BAR SEQUANNAIS","BAR SUR AUBOIS","REGION D'EPERNAY","REGION DE L'AISNE","BAR SEQUANNAIS","REGION DE L'AISNE", \
"LES COTEAUX DU PETIT MORIN","LES COTEAUX DU PETIT MORIN","VALLEE DE L'ARDRE","LES COTEAUX DU PETIT MORIN", \
"VALLEE DE LA MARNE RIVE GAUCHE","VALLEE DE LA MARNE RIVE GAUCHE","BAR SUR AUBOIS","REGION DE SEZANNE","REGION DE BOUZY AMBONNAY", \
"BAR SEQUANNAIS","REGION DE L'AISNE","BAR SUR AUBOIS","VALLEE DE L'ARDRE","MONTAGNE OUEST","LES COTEAUX DU PETIT MORIN", \
"REGION DE L'AISNE","REGION DE VITRY LE FRANCOIS","COTE DES BLANCS","MONTAGNE OUEST","BAR SEQUANNAIS","GRANDE VALLEE DE LA MARNE", \
"MASSIF DE SAINT THIERRY","VALLEE DE L'ARDRE","VALLEE DE LA MARNE RIVE GAUCHE","MONTAGNE OUEST","BAR SUR AUBOIS", \
"REGION DE L'AISNE","MONTAGNE OUEST","VALLEE DE LA MARNE RIVE DROITE","MONTAGNE OUEST","REGION DE SEZANNE","REGION DE L'AISNE", \
"VALLEE DE LA MARNE RIVE DROITE","REGION DE L'AISNE","VALLEE DE L'ARDRE","BAR SEQUANNAIS","REGION DE L'AISNE","COTE DES BLANCS", \
"MONTAGNE OUEST","BAR SEQUANNAIS","VALLEE DE LA MARNE RIVE GAUCHE","VALLEE DE L'ARDRE","BAR SUR AUBOIS", \
"REGION DE VITRY LE FRANCOIS","BAR SEQUANNAIS","LES COTEAUX DU PETIT MORIN","REGION DE VITRY LE FRANCOIS", \
"REGION DE BOUZY AMBONNAY","REGION DE CHIGNY LES ROSES","REGION DE VERZY VERZENAY","REGION D'EPERNAY", \
"VALLEE DE LA MARNE RIVE GAUCHE","VALLEE DE LA MARNE RIVE GAUCHE","GRANDE VALLEE DE LA MARNE","VALLEE DE L'ARDRE", \
"MASSIF DE SAINT THIERRY","REGION DE VITRY LE FRANCOIS","BAR SEQUANNAIS","VALLEE DE L'ARDRE","BAR SUR AUBOIS", \
"REGION DE L'AISNE","LES COTEAUX DU PETIT MORIN","REGION DE L'AISNE","REGION DE CHIGNY LES ROSES","REGION DE SEZANNE", \
"BAR SEQUANNAIS","REGION D'EPERNAY","REGION DE L'AISNE","BAR SUR AUBOIS","MASSIF DE SAINT THIERRY","REGION DE L'AISNE", \
"REGION D'EPERNAY","REGION D'EPERNAY","REGION D'EPERNAY","BAR SEQUANNAIS","GRANDE VALLEE DE LA MARNE","VALLEE DE L'ARDRE", \
"REGION DE L'AISNE","VALLEE DE LA MARNE RIVE GAUCHE","REGION DE L'AISNE","BAR SEQUANNAIS","BAR SEQUANNAIS", \
"REGION DE VILLERS MARMERY TREPAIL","REGION DE L'AISNE","REGION DE L'AISNE","VALLEE DE LA MARNE RIVE GAUCHE", \
"COTE DES BLANCS","COTE DES BLANCS","VALLEE DE LA MARNE RIVE DROITE","REGION DE L'AISNE","MONTAGNE OUEST", \
"LES COTEAUX DU PETIT MORIN","MONTAGNE OUEST","REGION DE L'AISNE","REGION DE L'AISNE","REGION DE L'AISNE", \
"MASSIF DE SAINT THIERRY","REGION D'EPERNAY","BAR SEQUANNAIS","VALLEE DE L'ARDRE","BAR SEQUANNAIS","BAR SEQUANNAIS", \
"REGION DE VILLERS MARMERY TREPAIL","MASSIF DE SAINT THIERRY","VALLEE DE L'ARDRE","MASSIF DE SAINT THIERRY", \
"BAR SUR AUBOIS","REGION DE VERZY VERZENAY","REGION DE CHIGNY LES ROSES","VALLEE DE LA MARNE RIVE DROITE", \
"REGION DE L'AISNE","REGION DE CHIGNY LES ROSES","BAR SUR AUBOIS","REGION DE L'AISNE","VALLEE DE LA MARNE RIVE GAUCHE", \
"VALLEE DE LA MARNE RIVE DROITE","MONTAGNE OUEST","BAR SUR AUBOIS","REGION DE L'AISNE","MONTAGNE OUEST","REGION DE L'AISNE", \
"REGION DE VITRY LE FRANCOIS","MONTAGNE OUEST","VALLEE DE L'ARDRE","REGION DE VITRY LE FRANCOIS","REGION D'EPERNAY", \
"MASSIF DE SAINT THIERRY","BAR SEQUANNAIS","REGION DE L'AISNE","VALLEE DE L'ARDRE","REGION DE SEZANNE", \
"REGION DE L'AISNE","BAR SUR AUBOIS","VALLEE DE L'ARDRE","REGION DE VILLERS MARMERY TREPAIL","MONTAGNE OUEST", \
"VALLEE DE L'ARDRE","REGION DE SEZANNE","REGION DE VERZY VERZENAY","LES COTEAUX DU PETIT MORIN","BAR SUR AUBOIS", \
"REGION DE CHIGNY LES ROSES","LES COTEAUX DU PETIT MORIN","REGION DE BOUZY AMBONNAY","MASSIF DE SAINT THIERRY", \
"REGION DE BOUZY AMBONNAY","VALLEE DE L'ARDRE","BAR SUR AUBOIS","REGION DE L'AISNE","REGION DE VILLERS MARMERY TREPAIL", \
"VALLEE DE L'ARDRE","MASSIF DE SAINT THIERRY","REGION DE CHIGNY LES ROSES","VALLEE DE LA MARNE RIVE GAUCHE", \
"VALLEE DE L'ARDRE","BAR SUR AUBOIS","REGION DE VITRY LE FRANCOIS","COTE DES BLANCS","REGION DE VITRY LE FRANCOIS", \
"VALLEE DE L'ARDRE","VALLEE DE LA MARNE RIVE DROITE","VALLEE DE LA MARNE RIVE GAUCHE","REGION DE VILLERS MARMERY TREPAIL", \
"REGION DE VITRY LE FRANCOIS","REGION DE VITRY LE FRANCOIS","VALLEE DE LA MARNE RIVE GAUCHE","REGION DE L'AISNE", \
"BAR SEQUANNAIS","LES COTEAUX DU PETIT MORIN","COTE DES BLANCS","REGION DE VERZY VERZENAY","REGION DE VERZY VERZENAY", \
"MONTAGNE OUEST","VALLEE DE LA MARNE RIVE DROITE","BAR SEQUANNAIS","REGION DE SEZANNE","COTE DES BLANCS", \
"REGION DE CHIGNY LES ROSES","MONTAGNE OUEST","MASSIF DE SAINT THIERRY","REGION DE VILLERS MARMERY TREPAIL", \
"VALLEE DE LA MARNE RIVE DROITE","LES COTEAUX DU PETIT MORIN","REGION DE L'AISNE","REGION D'EPERNAY","REGION DE L'AISNE", \
"REGION DE SEZANNE","REGION DE VITRY LE FRANCOIS","BAR SEQUANNAIS","BAR SEQUANNAIS","BAR SUR AUBOIS","COTE DES BLANCS","MONTAGNE OUEST"]
TYPE_APPORTS=["engrais organique","engrais mineral","engrais organo-mineral","amendements","pas d'apport","AUTRES"]
ENTRETIEN_SOL=[ "enherbement permanent tous les rangs","enherbement permanent un rang sur deux","couvert hivernal","travail du sol","sol nu","autres"]

TAILLES = [ "Inconnue", "Chablis", "Cordon de Royat", "Cordon libre", "Guyot simple", "Guyot double"]
FORMAT_VECTEUR = [ "ESRI Shapefile"] # POSTGRES_NOM] # "memory"]

# Répertoires des sources et de concaténation en fichiers texte
FICHIER_RESULTAT = "resultat.txt"
FICHIER_RESULTAT_CSV = "resultat_CSV.csv"
REPERTOIRE_SOURCES = "fichiers_sources"
SUFFIXE_BRUT_CSV = SEPARATEUR_ + "RAW.csv"
EXTENSION_MID = "*.MID"
NB_VIRGULES = 58

REPERTOIRE_TEXTES = "fichiers_texte"
REPERTOIRE_CARTES = "cartes"
# Pour histo
REPERTOIRE_HELP = os.path.join( os.path.dirname(__file__),"help")
FICHIER_HISTO_NON_CALCULE = os.path.join( REPERTOIRE_HELP, 
    "Histo_non_calcule.png")

REPERTOIRE_HISTOS = "histogrammes"
if platform.system() == 'Windows':
    # Matplotlib et png problematique sous Windows
    SUFFIXE_HISTO = ".tiff"
else:
    SUFFIXE_HISTO = ".png"
FICHIER_HISTO_SARMENT = "histogramme_SARMENT_RAW" + SUFFIXE_HISTO
FICHIER_HISTO_DIAMETRE = "histogramme_DIAMETRE_RAW"  + SUFFIXE_HISTO
FICHIER_HISTO_DIAMETRE_FILTRE = "histogramme_DIAM_FILTERED" +  SUFFIXE_HISTO

REPERTOIRE_SHAPEFILE = "shapefile"
PROJECTION_L93 = "L93"
PROJECTION_GPS = "GPS"
EXTENSION_SHP = ".shp"
EXTENSION_PRJ = ".prj"
EXTENSION_RASTER = ".tif"
EXTENSION_RASTER_SAGA = ".sdat"

EXTENSION_QML = ".qml"

EXTENSION_POUR_ZERO = SEPARATEUR_ + "0"

EPSG_NUMBER_L93 = 2154
EPSG_NUMBER_GPS = 4326

EPSG_TEXT_L93 = 'PROJCS["RGF93_Lambert_93",GEOGCS["GCS_RGF93",DATUM["D_RGF_1993", \
SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0], \
UNIT["Degree",0.017453292519943295]],PROJECTION["Lambert_Conformal_Conic"], \
PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44], \
PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3], \
PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000], \
UNIT["Meter",1]]'
EPSG_TEXT_GPS = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984", \
SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0], \
UNIT["Degree",0.017453292519943295]]'

# Inter PARCELLAIRE
#SHAPE_CONTOURS = '/home/jhemmi/Documents/GIS/SCRIPT/QGIS/PhysiocapAnalyseur/data Cap/Contour.shp'
SEPARATEUR_NOEUD = "~~"
NOM_MOYENNE = SEPARATEUR_ + "MOYENNE" + SEPARATEUR_
VIGNETTES_INTER = "INTER_PARCELLAIRE"
NOM_POINTS = SEPARATEUR_ + "POINTS"
NOM_INTER = SEPARATEUR_ + "INTER"

CONSOLIDATION = "CONSOLIDATION"

# Intra PARCELLAIRE
VIGNETTES_INTRA = "INTRA_PARCELLAIRE"
NOM_INTRA = SEPARATEUR_ + "INTRA"
REPERTOIRE_RASTERS = "INTRA_PARCELLAIRE"
ATTRIBUTS_INTRA = [ "DIAM", "NBSARM", "BIOM"] 
ATTRIBUTS_INTRA_DETAILS = [ "NBSARMM2", "NBSARCEP","BIOMM2", "BIOMGM2", "BIOMGCEP" ] 
CHEMIN_TEMPLATES = [ "modeleQgis", "project_templates"]
UNE_SEULE_FOIS = "NO"

# Exceptions Physiocap 
TAUX_LIGNES_ERREUR= 30

# ###########################
# Exceptions Physiocap
# ###########################
class physiocap_exception( Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class physiocap_exception_rep( physiocap_exception):
    pass
class physiocap_exception_fic( physiocap_exception):
    pass
class physiocap_exception_csv( physiocap_exception):
    pass
class physiocap_exception_err_csv( physiocap_exception):
    pass
class physiocap_exception_mid( physiocap_exception):
    pass
class physiocap_exception_no_mid( ):
    pass
class physiocap_exception_stop_user( ):
    pass  
class physiocap_exception_params( physiocap_exception):
    pass

# INTRA
class physiocap_exception_interpolation( physiocap_exception):
    pass
class physiocap_exception_vignette_exists( physiocap_exception):
    pass
class physiocap_exception_points_invalid( physiocap_exception):
    pass
class physiocap_exception_no_processing( ):
    pass
class physiocap_exception_no_saga( ):
    pass
class physiocap_exception_project_contour_incoherence( physiocap_exception):
    pass
class physiocap_exception_project_point_incoherence( physiocap_exception):
    pass
class physiocap_exception_windows_saga_ascii( physiocap_exception):
    pass
class physiocap_exception_windows_value_ascii( physiocap_exception):
    pass
class physiocap_exception_pg( physiocap_exception):
    pass

