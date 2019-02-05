# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 07:31:27 2018

@author: gelbj
"""

###############################################################################
## Fichier de structuration des fichiers CSV du projet
###############################################################################
import datetime

###############################################################################
## Fonctions de structuration initiales
###############################################################################

def StructureHx(InPut,Output,Params) : 
    """
    Cette fonction de structuration des fichiers Hexoskin :
        -Besoin de diviser le champ time par 256
        -creation d'un champ datetime propre
    """
    ## ouveture du fichier HX
    print(Output)
    Sep = Params["Sep"]
    File = open(InPut,"r")
    OutFile = open(Output,"w")
    Header = File.readline().replace("\n","")+Sep+"TIME"+Sep+"DATETIME"+'\n'
    OutFile.write(Header)
    ## lecture des lignes et rajout du champ TIME
    Line = File.readline()
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        Data.append(str(int(Data[0])/256))
        Data.append(datetime.datetime.fromtimestamp(int(Data[0])/256).strftime('%Y-%m-%d %H:%M:%S'))
        NewLine = Sep.join(Data)+'\n'
        OutFile.write(NewLine)
        Line = File.readline()
    OutFile.close()
    File.close()
    

def StructureDba(Input,Output,Params) : 
    """
    Fonction de structuration des fichiers DBA
        -Besoin de supprimer l'entete trop longue des fichiers de DBA
        -Creation du champ TIME (Date et heure au format timestamp)
    """
    Sep = Params["Sep"]
    File = open(Input,"r")
    OutFile = open(Output,"w")
    ## passage des 12 lignes de trop
    for e in range(13) : 
        Line = File.readline()
    Header = File.readline().replace("\n","")+Sep+"TIME"+Sep+"DATETIME"+'\n'
    OutFile.write(Header)
    ## lecture des lignes
    Line = File.readline()
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        #ajout du TIME en tant que contraction de start date et start time
        LineTime = JDate.DateTimeFromText(Data[0]+" "+Data[1])
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.strftime('%Y-%m-%d %H:%M:%S'))
        NewLine = Sep.join(Data)+'\n'
        OutFile.write(NewLine)
        Line = File.readline()
    OutFile.close()
    File.close()
    
def StructureNO2(Input,Output,Params) : 
    """
    Fonction de structuration des fichiers NO2
        -Creation du champ TIME (Date et heure au format timestamp)
    """
    Sep = Params["Sep"]
    File = open(Input,"r")
    OutFile = open(Output,"w")
    Header = File.readline().replace("\n","")+Sep+"TIME"+Sep+"DATETIME"+'\n'
    OutFile.write(Header)
    ## lecture des lignes
    Line = File.readline()
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        #ajout du TIME en tant que contraction de start date et start time
        LineTime = JDate.DateTimeFromText(Data[0])
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.strftime('%Y-%m-%d %H:%M:%S'))
        NewLine = Sep.join(Data)+'\n'
        OutFile.write(NewLine)
        Line = File.readline()
    OutFile.close()
    File.close()
    
def StructurePMS(Input,Output,Params) : 
    """
    Fonction de structuration des fichiers PMS
        -Creation du champ TIME (Date et heure au format timestamp)
    """
    Sep = Params["Sep"]
    File = open(Input,"r")
    OutFile = open(Output,"w")
    Header = File.readline().replace("\n","")+Sep+"TIME"+Sep+"DATETIME"+'\n'
    OutFile.write(Header)
    ## lecture des lignes
    Line = File.readline()
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        #ajout du TIME en tant que contraction de start date et start time
        LineTime = JDate.DateTimeFromText(Data[0])
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.strftime('%Y-%m-%d %H:%M:%S'))
        NewLine = Sep.join(Data)+'\n'
        OutFile.write(NewLine)
        Line = File.readline()
    OutFile.close()
    File.close()