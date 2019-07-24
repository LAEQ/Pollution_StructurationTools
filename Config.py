# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 23:32:45 2018

@author: gelbj
"""

import sys
JBasicPath = "F:/Python/___JBasics"
DecalageHoraire = 0
sys.path.append(JBasicPath)

import JDate
import datetime

###############################################################################
## Champs utilises dans la structuration
###############################################################################

class FieldDef(object) :
    def __init__(self,RealName,Name,Type,Default) :
        self.Name = Name
        self.RealName = RealName
        self.Type = Type
        self.Default = Default
        

# SQLtypes = https://www.sqlite.org/datatype3.html

## Champs de N02
#NO2_1 = FieldDef("Date Time","Date","TEXT","NAN")
NO2_2 = FieldDef(" NO2(ppm)","NO2","REAL",-999)
NO2_3 = FieldDef(" RH(%)","RH2","REAL",-999)
NO2_4 = FieldDef(" TEMP(C)","TEMP_C2","REAL",-999)

##Champs O3
O3_2 = FieldDef(" O3(ppm)","O3","REAL",-999)
O3_3 = FieldDef(" RH(%)","RH","REAL",-999)
O3_4 = FieldDef(" TEMP(C)","TEMP_C","REAL",-999)

## Champs de PMS
PMS_1 = FieldDef("Date Time","Date","TEXT","NAN")
PMS_2 = FieldDef(" PM10(ppm)","PM10","REAL",-999)
PMS_3 = FieldDef(" PM2.5(ppm)","PM25","REAL",-999)

## Champs de DBA
DBA_1 = FieldDef("Start date","StDate","TEXT","NAN")
DBA_2 = FieldDef("Start time","StTime","TEXT","NAN")
DBA_3 = FieldDef("LAeq","LAEQ","REAL",-999)
DBA_4 = FieldDef("LCpeak","LCPEAK","REAL",-999)
DBA_5 = FieldDef("LavS","LAVS","REAL",-999)


## Champs XH
HX_1 = FieldDef("time [s/256]","Time256","REAL",-999)
HX_2 = FieldDef("breathing_rate [rpm](/api/datatype/33/)","BreathRt","REAL",-999)
HX_3 = FieldDef("heart_rate [bpm](/api/datatype/19/)","HeartRt","REAL",-999)
HX_4 = FieldDef("minute_ventilation [mL/min](/api/datatype/36/)","Ventil","REAL",-999)
HX_5 = FieldDef("cadence [spm](/api/datatype/53/)","Cadence","REAL",-999)
HX_6 = FieldDef("activity [g](/api/datatype/49/)","Activity","REAL",-999)

## champs fit (montre)
FIT_1 = FieldDef("altitude","Altitude","REAL",-999)
FIT_2 = FieldDef("position_lat","Lat","REAL",-999)
FIT_3 = FieldDef("position_long","Lon","REAL",-999)
FIT_4 = FieldDef("speed","Speed","REAL",-999)
FIT_5 = FieldDef("timestamp","TIME","REAL",-999)

## champ pour le codaxus
COD_1 = FieldDef("timestamp","TimeStamp","REAL",-999)
COD_2 = FieldDef("distance","DistCod","REAL",-999)

###############################################################################
## Fonctions de structuration initiales
###############################################################################


def StructureCod(InPut,Output,Params) : 
    """
    Fonction de structuration des fichiers codaxus
        -Besoin de rajouter les entetes
        -Besoinde creer un champ datetime propre
    """
    Sep = Params["Sep"]
    File = open(InPut,"r")
    OutFile = open(Output,"w")
    OutFile.write("timestamp"+Sep+"distance"+Sep+"TIME"+Sep+"DATETIME\n")
    Line = File.readline()
    while Line != "" : 
        Data = Line.replace("\n","").split(Sep)
        if len(Data)>1 :
            if len(Data)>2 : 
                Data = Data[0:2]
            #print(Line)
            try :
                if Data[1] ==""  : 
                    Data[1] = "-999"
                else : 
                    Data[1] = str(int(Data[1]))
            except ValueError : 
                Data[1] = "-999"
            
            T = int(float(Data[0]))
            Data.append(str(T))
            Data.append(datetime.datetime.fromtimestamp(T).strftime('%Y-%m-%d %H:%M:%S'))
            NewLine = Sep.join(Data)+"\n"
            NewLine=NewLine.replace(",,",",")
            OutFile.write(NewLine)
        Line = File.readline()
    File.close()
    OutFile.close()

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
        if "nan" not in Line :
            Data = Line.replace("\n","").split(Sep)
            T=int(float(Data[0])/256+(DecalageHoraire*60*60))
            Data.append(str(T))
            Data.append(datetime.datetime.fromtimestamp(T).strftime('%Y-%m-%d %H:%M:%S'))
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
        if Params["Mode"]=="AN" :
            Year,Month,Day = Data[0].split("-")
            Hour,Minute,Second = Data[1].split(":")
            #Moment = Data[1].split(" ")[1]
            LineTime = JDate.Jdatetime(Day=Day,Month=Month,Year=Year,Hour=Hour,Minute=Minute,Second=Second)
        elif Params["Mode"]=="FR" : 
            Day,Month,Year = Data[0].split("-")
            Hour,Minute,Second = Data[1].split(":")
            LineTime = JDate.Jdatetime(Day=Day,Month=Month,Year=Year,Hour=Hour,Minute=Minute,Second=Second,Moment="")
            for e in range(len(Data)) : 
                Data[e] = Data[e].replace(",",".")
            
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.DateTime.strftime('%Y-%m-%d %H:%M:%S'))
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
    if Params["Mode"] == "FR" : 
        Positions = [pos for pos, char in enumerate(Line) if char == ","]
        Line = Line[:Positions[3]]+"."+Line[Positions[3]+1:]
        Line = Line[:Positions[5]]+"."+Line[Positions[5]+1:]
        Line = Line[:Positions[7]]+"."+Line[Positions[7]+1:]
        
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        #ajout du TIME en tant que contraction de start date et start time
        LineTime = JDate.DateTimeFromText(Data[0])
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.DateTime.strftime('%Y-%m-%d %H:%M:%S'))
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
    if Params["Mode"] == "FR" : 
        Positions = [pos for pos, char in enumerate(Line) if char == ","]
        Line = Line[:Positions[3]]+"."+Line[Positions[3]+1:]
        Line = Line[:Positions[5]]+"."+Line[Positions[5]+1:]
        Line = Line[:Positions[7]]+"."+Line[Positions[7]+1:]
        Line = Line[:Positions[9]]+"."+Line[Positions[9]+1:]
            
    while Line != "" :
        Data = Line.replace("\n","").split(Sep)
        #ajout du TIME en tant que contraction de start date et start time
        LineTime = JDate.DateTimeFromText(Data[0])
        Data.append(str(LineTime.TimeStamp))
        Data.append(LineTime.DateTime.strftime('%Y-%m-%d %H:%M:%S'))
        NewLine = Sep.join(Data)+'\n'
        OutFile.write(NewLine)
        Line = File.readline()
    OutFile.close()
    File.close()


###############################################################################
## Objet de configuration
###############################################################################

Config = {"Tables" : [{"Name":"NO2",
                       "Fields":[NO2_2,NO2_3,NO2_4],
                       "Extension":"NO2.csv",
                       "Sep" : ",",
                       "Recording" : "MIN",
                       "Mode":"AN", #could be AN or FR
                       "StructFunc" : StructureNO2
                       },
                        {"Name":"O3",
                       "Fields":[O3_2,O3_3,O3_4],
                       "Extension":"O3.csv",
                       "Sep" : ",",
                       "Recording" : "MIN",
                       "Mode":"AN", #could be AN or FR
                       "StructFunc" : StructureNO2
                       },
                        {"Name":"PMS",
                       "Fields":[PMS_1,PMS_2,PMS_3],
                       "Extension":"PMS.csv",
                       "Sep" : ",",
                       "Recording" : "MIN",
                       "Mode":"AN", #could be AN or FR
                       "StructFunc" : StructurePMS
                       },
                        {"Name":"DBA",
                       "Fields":[DBA_1,DBA_2,DBA_3,DBA_4,DBA_5],
                       "Extension":"DBA.TXT",
                       "Sep" : "	",
                       "Recording" : "MIN",
					   "Mode":"AN", #could be AN or FR
                       "StructFunc" : StructureDba
                       },
                        {"Name":"HX",
                       "Fields":[HX_1,HX_2,HX_3,HX_4,HX_5,HX_6],
                       "Extension":"HX.csv",
                       "Sep" : ",",
                       "Recording" : "SEC",
                       "StructFunc" : StructureHx
                       },
                        {"Name":"COD",
                       "Fields":[COD_1,COD_2],
                       "Extension":"COD.txt",
                       "Sep" : ",",
                       "Recording" : "INFRASEC",
                       "StructFunc" : StructureCod
                       }
    ],
    "FitFile" : {"Fields":[FIT_1,FIT_2,FIT_3,FIT_4,FIT_5],
                 "Decalage":-4*60}, #a donner en minutes
    "JBasicsPath" :JBasicPath,
    }
