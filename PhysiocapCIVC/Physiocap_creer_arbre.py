# -*- coding: utf-8 -*-
""" 
/***************************************************************************
 physiocap_creer_arbre
                                 A QGIS plugin
 Physiocap plugin helps analyse raw data from Physiocap in Qgis and 
 creates a synthesis of Physiocap measures' campaign
 Physiocap plugin permet l'analyse les données brutes de Physiocap dans Qgis et
 crée une synthese d'une campagne de mesures Physiocap
 
 Le module physiocap_creer_arbre gère le nommage et création 
 de l'arbre des résultats d'analyse (dans la même
 structure de données que celle créé par PHYSICAP_V8 du CIVC) 

 Les variables et fonctions sont nommées en Francais
 
                             -------------------
        begin                : 2015-12-05
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
from Physiocap_tools import physiocap_message_box, physiocap_question_box,\
        physiocap_log, physiocap_error, physiocap_write_in_synthese, \
        physiocap_rename_existing_file, physiocap_rename_create_dir, physiocap_open_file, \
        physiocap_look_for_MID, physiocap_list_MID
        
##        , physiocap_quel_uriname, \
##        physiocap_get_uri_by_layer, physiocap_tester_uri

from Physiocap_CIVC import physiocap_csv_vers_shapefile, physiocap_assert_csv, \
        physiocap_fichier_histo, physiocap_tracer_histo, physiocap_filtrer, physiocap_csv_sortie ,generer_contour_fin

from Physiocap_inter import physiocap_fill_combo_poly_or_point

from Physiocap_var_exception import *

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings, Qt 
from PyQt4.QtGui import QPixmap
from qgis.core import QgsProject, QgsVectorLayer , QgsMapLayerRegistry, QgsMapLayer

import glob
import shutil
import time  
   
# Creation des repertoires source puis resultats puis histo puis shape

class PhysiocapFiltrer( QtGui.QDialog):
    """QGIS Pour voir les messages traduits."""

    def __init__(self, parent=None):
        """Class constructor."""
        super( PhysiocapFiltrer, self).__init__()#___utiliser le constructeur de la classe parent 
    
    def physiocap_creer_donnees_resultats( self, dialogue, laProjection, EXT_CRS_SHP, EXT_CRS_PRJ,
        details = "NO", histogrammes = "NO", recursif = "NO"):
        """ Récupération des paramètres saisies et 
        creation de l'arbre "source" "texte" et du fichier "resultats"
        Ce sont les résultats de l'analyse filtration des données brutes"""
                    
        # Récupérer les paramètres saisies
        Repertoire_Donnees_Brutes = dialogue.lineEditDirectoryPhysiocap.text()#___recuperer le repertoire des donnes brutes 
        Repertoire_Donnees_Cibles = dialogue.lineEditDirectoryFiltre.text()#___recuperer le repertoire cible ou enregistrer les resultats 
        Nom_Projet = dialogue.lineEditProjet.text()#___recuperer le nom de projet 
        mindiam = float( dialogue.spinBoxMinDiametre.value())#___recuperer la valeur de diametre min
        maxdiam = float( dialogue.spinBoxMaxDiametre.value())#___recuperer le valeur de diametre max
        max_sarments_metre = float( dialogue.spinBoxMaxSarmentsParMetre.value())#___recuperer la valeur du nombre de sarments max par metre 

        if details == "YES":#___Execute si details sont demandes
            interrangs = float( dialogue.spinBoxInterrangs.value())#___recuperer la valeur d interrangs 
            interceps = float( dialogue.spinBoxInterceps.value())#___recuperer la valeur d interceps 
            hauteur = float( dialogue.spinBoxHauteur.value())#___recuperer la valeur d hauteur 
            densite = float( dialogue.doubleSpinBoxDensite.value())#___recuperer la valeur de densite 
            leCepage = dialogue.fieldComboCepage.currentText()#___recuperer la valeur de Cepage 
            laTaille = dialogue.fieldComboTaille.currentText()#___recuperer la valeur de Taille 
            
        # Vérification de l'existance ou création du répertoire projet
        chemin_projet = os.path.join(Repertoire_Donnees_Cibles, Nom_Projet)
        if not (os.path.exists( chemin_projet)):
            try:
                os.mkdir( chemin_projet)#___ si le repertoire projet n existe pas--> le creer
            except:
                raise physiocap_exception_rep( Nom_Projet)
        else:
            # Le répertoire existant est renommé en (+1)
            try: 
                chemin_projet = physiocap_rename_create_dir( chemin_projet)#___ si le repertoire projet existe deja--> le renommer en ajoutant des nums a la fin du nom de dossier 
            except:
                raise physiocap_exception_rep( chemin_projet)
        
        
        # Stocker dans la fenetre de synthese le nom du projet
        chemin_base_projet = os.path.basename( chemin_projet)
        dialogue.lineEditDernierProjet.setText( chemin_base_projet)#___ Ecrire dans l onglet Synthese le dernier nom de projet
        dialogue.settings= QSettings( PHYSIOCAP_NOM, PHYSIOCAP_NOM)
        dialogue.settings.setValue("Physiocap/dernier_repertoire", chemin_base_projet) #___definir les valeurs des variables : derneir_repertoire
        physiocap_log( self.trUtf8( "** {0} Début du traitement pour le projet Physiocap {1}").\
            format( PHYSIOCAP_UNI, chemin_base_projet))
        physiocap_log( self.trUtf8( "Paramètres pour filtrer les diamètres min : {0} max : {1}").\
            format( str( mindiam), str( maxdiam)))
                    
        # Progress BAR 2 %
        dialogue.progressBar.setValue( 2)
        
            
        # Verification de l'existance ou création du répertoire des sources MID et fichier csv
        chemin_sources = os.path.join(chemin_projet, REPERTOIRE_SOURCES)#___recuperer le chemin des Fichiers MID : fichiers sources
        if not (os.path.exists( chemin_sources)):
            try:
                os.mkdir( chemin_sources)#___si le dossier n existe pas , le creer???
            except:
                raise physiocap_exception_rep( REPERTOIRE_SOURCES)
                    
        # Fichier de concaténations CSV des résultats bruts        
        nom_court_csv_concat = Nom_Projet + SUFFIXE_BRUT_CSV#___construiree le nom de fichier de concatenation csv = nomProjet_RAW.csv
        try:
            nom_csv_concat, csv_concat = physiocap_open_file( nom_court_csv_concat, chemin_sources, "w")#___ creer/ouvrir le fichier en ecriture
        except physiocap_exception_fic as e:
            raise physiocap_exception_csv( nom_court_csv_concat)
            
        # Création du fichier concaténé
        nom_fichiers_recherches = os.path.join(Repertoire_Donnees_Brutes, EXTENSION_MID)#___construire le chemin d acces au fichiers MID
        
        # Assert le nombre de MID > 0
        # le Tri pour retomber dans l'ordre de Physiocap_V8
        if ( recursif == "YES"):
            # On appelle la fonction de recherche récursive
            listeTriee = physiocap_look_for_MID( Repertoire_Donnees_Brutes, "YES", REPERTOIRE_SOURCES) #___ lise = recuperer tous les fichiers dans le repertoire  de donnes brutes avec l extention .MID
        else:
            # Non recursif
            listeTriee = sorted(glob.glob( nom_fichiers_recherches))#___Trier les noms de fichiers 

        if len( listeTriee) == 0:#___ exception s il y a pas de fichiers MID dans le repertoire de donnes brutes 
            raise physiocap_exception_no_mid()
        
        # Verification si plus de 10 MIDs
        if len( listeTriee) >= 15:
            # Beaucoup de MIDs Poser une question si cancel, on stoppe
            uMsg =self.trUtf8( "Plus de 15 fichier MIDs sont à analyser. Temps de traitement > à 1 minute. Voulez-vous continuer ?")#___ afficher le message si le nombre des fichires depasse 15
            if ( physiocap_question_box( self, uMsg)):
                pass#___ si arret non demande --> rien faire
            else:
                # Arret demandé
                raise physiocap_exception_stop_user()#___ si l arret est demande  par l utilisateur
            
        for mid in listeTriee:
            try:
                shutil.copyfileobj(open(mid, "r"), csv_concat)#___ copier les fichiers MID dand le fichier de concatenation csv
                # et copie des MID
                nom_cible = os.path.join( chemin_sources, os.path.basename(mid))
                if os.path.exists( nom_cible):
                    nouveau_long = physiocap_rename_existing_file( nom_cible)
                    shutil.copyfile( mid, nouveau_long)#___si le fihciers MID existe deja creer un autre en renommant+1
                else:
                    shutil.copy( mid, chemin_sources)#___copier les fichiers MID dand le repertoire fichiers_source
            except:
                raise physiocap_exception_mid( mid)
        csv_concat.close()#___ close file handler

        #___verifier si le fichier de concaténation des données n'est pas vide
        if os.path.getsize( nom_csv_concat ) == 0 :
            uMsg = self.trUtf8( "Le fichier {0} a une taille nulle !").\
                format( nom_court_csv_concat)
            physiocap_message_box( self, uMsg)
            return physiocap_error( self, uMsg)
        
        # Création la première partie du fichier de synthèse
        fichier_resultat_analyse = chemin_base_projet + SEPARATEUR_ + FICHIER_RESULTAT
        nom_fichier_synthese, fichier_synthese = physiocap_open_file( fichier_resultat_analyse, chemin_projet , "w")
        fichier_synthese.write( "SYNTHESE PHYSIOCAP\n\n")
        fichier_synthese.write( "Générée le : ")
        a_time = time.strftime( "%d/%m/%y %H:%M\n",time.localtime())
        fichier_synthese.write( a_time)
        fichier_synthese.write( "Répertoire de base ")
        fichier_synthese.write( chemin_base_projet.encode("Utf-8") + "\n")
        fichier_synthese.write( "Nom des MID \t\t Date et heures\n=>Nb. Valeurs brutes\tVitesse km/h")
        if (CENTROIDES == "YES"):
            fichier_synthese.write("\nCentroïdes")
        fichier_synthese.write("\n")
        info_mid = physiocap_list_MID( Repertoire_Donnees_Brutes, listeTriee)
        for all_info in info_mid:
            info = all_info.split(";")
            fichier_synthese.write( str(info[0]) + "\t" + str(info[1]) + "->" + str(info[2])+ "\n")
            # une seule décimale pour vitesse
            fichier_synthese.write( "=>\t{0}\t{1:.1f}".format( info[3], float( info[4])))
            if (CENTROIDES == "YES"):
                # Centroides
                fichier_synthese.write( "\n" + str(info[5]) + "--" + str(info[6]))
            fichier_synthese.write("\n")
    ##        nom_mid = ""
    ##        for fichier_mid in listeTriee:
    ##            nom_mid = nom_mid + os.path.basename( fichier_mid) + " & "
    ##        fichier_synthese.write("Liste des fichiers MID : " + nom_mid[:-3] + "\n")
    ##        physiocap_log( "Liste des MID : " + nom_mid[:-3])
        
		
        #___Nadia___ Création du fichier de sortie csv
        fichier_resultat_CSV = chemin_base_projet + SEPARATEUR_ + FICHIER_RESULTAT_CSV
        nom_fichier_synthese_CSV, fichier_synthese_CSV = physiocap_open_file( fichier_resultat_CSV, chemin_projet , "w")
        dialogue.settings.setValue("Physiocap/chemin_fichier_synthese_CSV", nom_fichier_synthese_CSV)
        # Progress BAR 5 %
        dialogue.progressBar.setValue(5)
        physiocap_log ( self.trUtf8( "Fin de la création csv et début de synthèse"))#___ fin ecriture de la permiere partie du fichiers de synthese
       
        # Verification de l'existance ou création du répertoire textes
        chemin_textes = os.path.join(chemin_projet, REPERTOIRE_TEXTES)
        if not (os.path.exists( chemin_textes)):
            try :
                os.mkdir(chemin_textes)#___si le repertoire des fichers_texte(resultats) n existe pas --> le creer
            except :
                raise physiocap_exception_rep( REPERTOIRE_TEXTES)
                       
        # Ouverture du fichier des diamètres
        nom_court_fichier_diametre = "diam" + SUFFIXE_BRUT_CSV #___ fichier diam_RAW.csv
        nom_data_histo_diametre, data_histo_diametre = physiocap_open_file( nom_court_fichier_diametre,
            chemin_textes)#___ Creer ou detruit et re-cree un fichier diam_RAW.csv
        
        # Appel fonction de creation de fichier
        nom_court_fichier_sarment = "nbsarm" + SUFFIXE_BRUT_CSV #___fichier nbsarm_RAW.csv
        nom_data_histo_sarment, data_histo_sarment = physiocap_open_file( nom_court_fichier_sarment, 
            chemin_textes)#___ Creer ou detruit et re-cree un fichier nbsarm_RAW.csv

        # Todo: V3 ? Supprimer le fichier erreur
        nom_fichier_erreur, erreur = physiocap_open_file( "erreurs.csv" , chemin_textes)

        # ouverture du fichier source
        csv_concat = open(nom_csv_concat, "r")#___ Ouverture du fichier concatenation et verification s il ya des erreurs
        # Appeler la fonction de vérification du format du fichier csv
        # Si plus de 20 % d'erreur exception est monté
        try:
            pourcentage_erreurs = physiocap_assert_csv( self, csv_concat, erreur)
            if ( pourcentage_erreurs > TAUX_LIGNES_ERREUR):
                fichier_synthese.write("\nTrop d'erreurs dans les données brutes")
                # Todo : V3 question selon le taux de lignes en erreur autorisées
                #raise physiocap_exception_err_csv( pourcentage_erreurs)
        except:
            raise

        # Progress BAR 10 %
        dialogue.progressBar.setValue( 10)        
        fichier_synthese.write("\n\nPARAMETRES SAISIS ")#___ Deuxieme partie du fichier de synthese
        
        if os.path.getsize( nom_csv_concat ) == 0 :#___ si le fichier concatention est vide, raise error
            uMsg = self.trUtf8( "Le fichier {0} a une taille nulle !").\
                format( nom_court_csv_concat)            
            physiocap_message_box( self, uMsg)
            return physiocap_error( self, uMsg)

        # ouverture du fichier source
        csv_concat = open(nom_csv_concat, "r")

        # Appeler la fonction de traitement
        if histogrammes == "YES":#___ si les histogrammes sont demandes --> appeler la fonction qui fait le traitement 
            #################
            physiocap_fichier_histo( self, csv_concat, data_histo_diametre,    
                        data_histo_sarment, erreur)
            #################
            # Fermerture des fichiers
            data_histo_diametre.close()
            data_histo_sarment.close()
        csv_concat.close()
        erreur.close()
        
        # Progress BAR 12 %
        dialogue.progressBar.setValue( 12)
        
        # Verification de l'existance 
        chemin_histos = os.path.join(chemin_projet, REPERTOIRE_HISTOS)
        if not (os.path.exists( chemin_histos)):
            try:
                os.mkdir( chemin_histos)#___ si le dossier histogrammes n existe pas --> le creer
            except:
                raise physiocap_exception_rep( REPERTOIRE_HISTOS)

        if histogrammes == "YES":
            # creation d'un histo
            nom_data_histo_sarment, data_histo_sarment = physiocap_open_file( nom_court_fichier_sarment, chemin_textes, 'r')
            nom_histo_sarment, histo_sarment = physiocap_open_file( FICHIER_HISTO_SARMENT, chemin_histos)
            name = nom_histo_sarment
            physiocap_tracer_histo( data_histo_sarment, name, 0, 50, "SARMENT au m", "FREQUENCE en %", "HISTOGRAMME NBSARM AVANT TRAITEMENT")#___appel de la fonction qui trace l histogramme NBSARM AVANT TRAITEMENT
            histo_sarment.close()
            
            nom_data_histo_diametre, data_histo_diametre = physiocap_open_file( nom_court_fichier_diametre, chemin_textes, 'r')
            nom_histo_diametre, histo_diametre = physiocap_open_file( FICHIER_HISTO_DIAMETRE, chemin_histos)
            name = nom_histo_diametre
            physiocap_tracer_histo( data_histo_diametre, name, 0, 30, "DIAMETRE en mm", "FREQUENCE en %", "HISTOGRAMME DIAMETRE AVANT TRAITEMENT")#___appel de la fonction qui trace l histogramme DIAMETRE AVANT TRAITEMENT
            histo_diametre.close()        
            
            physiocap_log ( self.trUtf8( "Fin de la création des histogrammes bruts"))
        else:
            physiocap_log ( self.trUtf8( "Pas de création des histogrammes"))

        # Progress BAR 15 %
        dialogue.progressBar.setValue( 15) 
                  
        # Création des csv
        nom_court_csv_sans_0 = Nom_Projet + SEPARATEUR_ + "OUT.csv"#___creation du fichier NomProjet_OUT.csv --> fichier sans zeros
        nom_csv_sans_0, csv_sans_0 = physiocap_open_file(
            nom_court_csv_sans_0, chemin_textes)

        nom_court_csv_avec_0 = Nom_Projet + SEPARATEUR_ + "OUT0.csv"#___creation du fichier NomProjet_OUT0.csv --> fichier avec zeros
        nom_csv_avec_0, csv_avec_0 = physiocap_open_file( 
            nom_court_csv_avec_0, chemin_textes)
       
        nom_court_fichier_diametre_filtre = "diam_FILTERED.csv"#___diam_FILTERED.csv
        nom_fichier_diametre_filtre, diametre_filtre = physiocap_open_file( 
            nom_court_fichier_diametre_filtre, chemin_textes )

        # Ouverture du fichier source et re ouverture du ficheir erreur
        csv_concat = open(nom_csv_concat, "r")       
        erreur = open(nom_fichier_erreur,"a")

        # Filtrage des données Physiocap
        #################
        if details == "NO": #___ si les details ne sont pas demandes--> donner des valeurs par defaut pour les parametres details
            interrangs = 1
            interceps = 1 
            densite = 1
            hauteur = 1        
        retour_filtre = physiocap_filtrer( dialogue, csv_concat, csv_sans_0, csv_avec_0, \
                    diametre_filtre, nom_fichier_synthese, erreur, \
                    mindiam, maxdiam, max_sarments_metre, details,
                    interrangs, interceps, densite, hauteur)#___*********Appel de la fonction physiocap_filtrer de Physiocap_CIVC pour remplir le ficier csv qui va etre utilse pour le creation du shapefile**********
        #################
        # Fermeture du fichier destination
        csv_sans_0.close()
        csv_avec_0.close()
        diametre_filtre.close()
        erreur.close()
        # Fermerture du fichier source
        csv_concat.close()  

        # Todo : V3 ? Gerer cette erreur par exception
        if retour_filtre != 0:
            uMsg = self.trUtf8( "Erreur bloquante : problème lors du filtrage des données de {0}").\
                format( nom_court_csv_concat)
            return physiocap_error( self, uMsg)  

        # Progress BAR 60 %
        dialogue.progressBar.setValue( 41)

        if histogrammes == "YES":#___ si histogrammes sont demandes --> tracer le troisieme : DIAMETRE APRES TRAITEMENT
            # Histo apres filtration
            nom_fichier_diametre_filtre, diametre_filtre = physiocap_open_file( 
                nom_court_fichier_diametre_filtre, chemin_textes , "r")
            nom_histo_diametre_filtre, histo_diametre = physiocap_open_file( FICHIER_HISTO_DIAMETRE_FILTRE, chemin_histos)

            physiocap_tracer_histo( diametre_filtre, nom_histo_diametre_filtre, 0, 30, \
                "DIAMETRE en mm", "FREQUENCE en %", "HISTOGRAMME DIAMETRE APRES TRAITEMENT")
            diametre_filtre.close()        
            physiocap_log ( self.trUtf8( "Fin de la création de l'histogramme filtré"))
                                              
        # On écrit dans le fichiers résultats les paramètres du modéle #___ 3 eme partie du fichier de synthese
        fichier_synthese = open(nom_fichier_synthese, "a")
        if details == "NO":
            fichier_synthese.write("\nAucune information parcellaire saisie\n")
        else:
            fichier_synthese.write("\n")
            msg = "Cépage : %s \n" % leCepage.encode("Utf-8")
            fichier_synthese.write( msg)
            fichier_synthese.write("Type de taille : %s\n" %laTaille)        
            fichier_synthese.write("Hauteur de végétation : %s cm\n" %hauteur)
            fichier_synthese.write("Densité des bois de taille : %s \n" %densite)
            fichier_synthese.write("Ecartement entre rangs : %s cm\n" %interrangs)
            fichier_synthese.write("Ecartement entre ceps : %s cm\n" %interceps)        

        fichier_synthese.write("\n")
        fichier_synthese.write("Nombre de sarments max au mètre linéaire: %s \n" %max_sarments_metre)
        fichier_synthese.write("Diamètre minimal : %s mm\n" %mindiam)
        fichier_synthese.write("Diamètre maximal : %s mm\n" %maxdiam)
        fichier_synthese.close()

        # Progress BAR 42%
        dialogue.progressBar.setValue(42)
        
        # Verification de l'existance ou création du répertoire des sources MID et fichier csv
        chemin_shapes = os.path.join(chemin_projet, REPERTOIRE_SHAPEFILE)
        if not (os.path.exists( chemin_shapes)):
            try :
                os.mkdir( chemin_shapes)#____si le dossier shapefile n existe pas --> le creer
                dialogue.settings.setValue("Physiocap/chemin_shapes", chemin_shapes)
            except :
                raise physiocap_exception_rep( REPERTOIRE_SHAPEFILE)

        # Création des shapes sans 0
        nom_court_shape_sans_0 = Nom_Projet + NOM_POINTS + EXT_CRS_SHP#___ construire ele nom du fichier NomProjet_POINTS.shp
        nom_shape_sans_0 = os.path.join(chemin_shapes, nom_court_shape_sans_0)
        dialogue.settings.setValue("Physiocap/nom_shape_sans_0", nom_shape_sans_0)
        nom_court_prj_sans_0 = Nom_Projet + NOM_POINTS + EXT_CRS_PRJ
        nom_prj_sans_0 = os.path.join(chemin_shapes, nom_court_prj_sans_0)

            
        # Si le shape existe dejà il faut le détruire
        if os.path.isfile( nom_shape_sans_0):
            physiocap_log ( self.trUtf8( "Le shape file existant déjà, il est détruit."))
            os.remove( nom_shape_sans_0)            

        # cas sans 0, on demande la synthese en passant le nom du fichier
        retour = physiocap_csv_vers_shapefile(dialogue, 45, nom_csv_sans_0, nom_shape_sans_0, nom_prj_sans_0,
                laProjection,
                nom_fichier_synthese, details)
        if retour != 0:
            return physiocap_error( self, self.trUtf8(\
                "Erreur bloquante : problème lors de la création du shapefile {0}").\
                format(str ( nom_court_shape_sans_0)))

        # Progress BAR 65 %
        dialogue.progressBar.setValue( 65)
                
        # Création des shapes avec 0
        nom_court_shape_avec_0 = Nom_Projet + NOM_POINTS + EXTENSION_POUR_ZERO + EXT_CRS_SHP
        nom_shape_avec_0 = os.path.join(chemin_shapes, nom_court_shape_avec_0)
        nom_court_prj_avec_0 = Nom_Projet + NOM_POINTS + EXTENSION_POUR_ZERO + EXT_CRS_PRJ
        nom_prj_avec_0 = os.path.join(chemin_shapes, nom_court_prj_avec_0)
        # Si le shape existe dejà il faut le détruire
        if os.path.isfile( nom_shape_avec_0):
            physiocap_log ( self.trUtf8("Le shape file existant déjà, il est détruit."))
            os.remove( nom_shape_avec_0)
            
        # cas avec 0, pas de demande de synthese
        retour = physiocap_csv_vers_shapefile( dialogue, 65, nom_csv_avec_0, nom_shape_avec_0, nom_prj_avec_0, laProjection,
            "NO", details)
        if retour != 0:
            return physiocap_error( self, self.trUtf8( \
                "Erreur bloquante : problème lors de la création du shapefile {0}").\
                format( str ( nom_court_shape_avec_0))) 
        

				
				
        # Progress BAR 95%
        dialogue.progressBar.setValue(95)
        
        # Creer un groupe pour cette analyse
        # Attention il faut qgis > 2.4 metadata demande V2.4 mini
        root = QgsProject.instance().layerTreeRoot( )
        # Nommmer le groupe chemin_base_projet
        sous_groupe = root.addGroup( chemin_base_projet)
        
        # Récupérer des styles pour chaque shape
        dir_template = dialogue.fieldComboThematiques.currentText()
        # Affichage des différents shapes dans Qgis
        SHAPE_A_AFFICHER = []
        qml_is = ""
        if dialogue.checkBoxDiametre.isChecked():
            qml_is = dialogue.lineEditThematiqueDiametre.text().strip('"') + EXTENSION_QML
            # Pas de choix du shape, car il faut pour Inter un diam sans 0
            SHAPE_A_AFFICHER.append( (nom_shape_sans_0, 'DIAMETRE mm', qml_is))
        if dialogue.checkBoxSarment.isChecked():
            qml_is = dialogue.lineEditThematiqueSarment.text().strip('"') + EXTENSION_QML
            # Choix du shape à afficher
            if ( dialogue.fieldComboShapeSarment.currentIndex() == 0):
                SHAPE_A_AFFICHER.append( (nom_shape_sans_0, 'SARMENT par m', qml_is))
            else:
                SHAPE_A_AFFICHER.append( (nom_shape_avec_0, 'SARMENT par m', qml_is))
            
        if dialogue.checkBoxBiomasse.isChecked():
            qml_is = dialogue.lineEditThematiqueBiomasse.text().strip('"') + EXTENSION_QML
            # Choix du shape à afficher
            if ( dialogue.fieldComboShapeBiomasse.currentIndex() == 0):
                SHAPE_A_AFFICHER.append( (nom_shape_sans_0, 'BIOMASSE', qml_is))
            else:
                SHAPE_A_AFFICHER.append( (nom_shape_avec_0, 'BIOMASSE', qml_is))
        if dialogue.checkBoxVitesse.isChecked():
            qml_is = dialogue.lineEditThematiqueVitesse.text().strip('"') + EXTENSION_QML
            # Choix du shape à afficher
            if ( dialogue.fieldComboShapeVitesse.currentIndex() == 0):
                SHAPE_A_AFFICHER.append( (nom_shape_sans_0, 'VITESSE km/h', qml_is))
            else:
                SHAPE_A_AFFICHER.append( (nom_shape_avec_0, 'VITESSE km/h', qml_is))       

        for shapename, titre, un_template in SHAPE_A_AFFICHER:
##            if ( dialogue.fieldComboFormats.currentText() == POSTGRES_NOM ):
##                uri_nom = physiocap_quel_uriname( dialogue)
##                #physiocap_log( u"URI nom : " + str( uri_nom))
##                uri_modele = physiocap_get_uri_by_layer( dialogue, uri_nom )
##                if uri_modele != None:
##                    uri_connect, uri_deb, uri_srid, uri_fin = physiocap_tester_uri( dialogue, uri_modele)            
##                    nom_court_shp = os.path.basename( shapename)
##                    #TABLES = "public." + nom_court_shp
##                    uri = uri_deb +  uri_srid + \
##                       " key='gid' type='POINTS' table=" + nom_court_shp[ :-4] + " (geom) sql="            
##    ##              "dbname='testpostgis' host='localhost' port='5432'" + \
##    ##              " user='postgres' password='postgres' SRID='2154'" + \
##    ##              " key='gid' type='POINTS' table=" + nom_court_shp[ :-4] + " (geom) sql="
##    ##                physiocap_log ( "Création dans POSTGRES : >>" + uri + "<<")
##    ##                vectorPG = QgsVectorLayer( uri, titre, POSTGRES_NOM)
##                else:
##                    aText = self.trUtf8( "Pas de connecteur vers Postgres : {0}. On continue avec des shapefiles").\
##                         format ((str( uri_nom)))
##                    physiocap_log( aText)
##                    # Remettre le choix vers ESRI shape file
##                    dialogue.fieldComboFormats.setCurrentIndex( 0)

            #physiocap_log( u"Physiocap : Afficher layer ")
            vector = QgsVectorLayer( shapename, titre, 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer( vector, False)
            # Ajouter le vecteur dans un groupe
            vector_node = sous_groupe.addLayer( vector)
            le_template = os.path.join( dir_template, un_template)
            if ( os.path.exists( le_template)):
                #physiocap_log( u"Physiocap le template : " + os.path.basename( le_template))
                vector.loadNamedStyle( le_template)

        # Créer un ficher de sortie CSV de synthese___Nadia___
        retour_gen_cont = generer_contour_fin(dialogue, nom_fichier_synthese_CSV, nom_shape_sans_0,sous_groupe)
        if retour_gen_cont != 0:
            return physiocap_error(self, self.trUtf8( \
                "Erreur bloquante : problème lors de la génération du contour "))



        # Fichier de synthese dans la fenetre resultats   
        fichier_synthese = open(nom_fichier_synthese, "r")
        while True :
            ligne = fichier_synthese.readline() # lit les lignes 1 à 1
            physiocap_write_in_synthese( dialogue, ligne)
            if not ligne: 
                fichier_synthese.close
                break

        # Progress BAR 95 %
        dialogue.progressBar.setValue( 95)
                    
        # Mettre à jour les histogrammes dans fenetre resultat
        if histogrammes == "YES":
            if ( dialogue.label_histo_sarment.setPixmap( QPixmap( nom_histo_sarment))):
                physiocap_log( self.trUtf8( "Physiocap histogramme sarment chargé"))
            if ( dialogue.label_histo_diametre_avant.setPixmap( QPixmap( nom_histo_diametre))):
                physiocap_log ( self.trUtf8( "Physiocap histogramme diamètre chargé"))                
            if ( dialogue.label_histo_diametre_apres.setPixmap( QPixmap( nom_histo_diametre_filtre))):
                physiocap_log ( self.trUtf8( "Physiocap histogramme diamètre filtré chargé"))    
        else:
            dialogue.label_histo_sarment.setPixmap( QPixmap( FICHIER_HISTO_NON_CALCULE))
            dialogue.label_histo_diametre_avant.setPixmap( QPixmap( FICHIER_HISTO_NON_CALCULE))
            dialogue.label_histo_diametre_apres.setPixmap( QPixmap( FICHIER_HISTO_NON_CALCULE))
            physiocap_log ( self.trUtf8( "Physiocap pas d'histogramme calculé"))    
                           
        # Progress BAR 100 %
        dialogue.progressBar.setValue( 100)
        # Fin 
        physiocap_log ( self.trUtf8( "** {0} a affiché des couches dans le groupe {1}").\
            format( PHYSIOCAP_UNI, chemin_base_projet))
        physiocap_fill_combo_poly_or_point( dialogue)
        #physiocap_log ( u"Mise à jour des poly et points")
        return 0 
