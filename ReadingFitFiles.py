# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 23:42:32 2018

@author: gelbj
"""

import fitparse.base as fitparse
from fitparse.base import FitFile
import sys, time

from Config import Config,DecalageHoraire
sys.path.append(Config["JBasicsPath"])

from JQgis import JVectorLayer as VL

###############################################################################
##Parametres Generaux
###############################################################################
Fields = {"altitude":"float32",
          "position_lat":"float32",
          "position_long":"float32",
          "speed":"float32",
          "timestamp":"|S25"}


#File = "G:/____Auckland/ID1_PA/ID1_PA_2018-02-20_TRAJET01.fit"

###############################################################################
##
###############################################################################

def ExtractRecords(Generator) : 
    Records = []
    Rejected = set(["hardware_version","sport","product","event_type","garmin_product"])
    for Record in Generator : 
        Keys = set(Record.keys())
        if len(Rejected.intersection(Keys))==0 :
            Records.append(Record)
    return Records

## Fonction pour obtenir une table de donnees a partir d'un fichier .fit
def FitToDataTable(MyFile,Fields) :
    File = FitFile(MyFile)
    File.parse()
    ##obtention des enregistrements
    Values = File.get_records_as_dicts()
    ##iteration sur les header inutiles jusqu'a l'annonce du fichier cycling
    Records = ExtractRecords(Values)
#    Continue = True
#    while Continue : 
#        Record = Values.next()
#        try : 
#            if Record["sport"] == "cycling" : 
#               Continue = False
#        except KeyError :
#            pass
    Datas=[]
    i=0
    #iteration sur les enregistrements
    Prec = None
    for Record in Records :
#        #print(Record)
#        if Record.has_key("product")==True : 
#            #rendu ici il n'y a plus d'enregistrements
#            try :
#                Record = Values.next()
#                if Record.has_key("event_type") == False : 
#                    print("Hey, we have to continue !")
#                else :
#                    break
#            except : 
#                break
#        if Record.has_key("event_type") == False : 
#            #sauter les evenements indiquant le 5km
#            #transformer le timestamp moche en un beau chiffre
        print(Record)
        TIME = time.mktime(Record["timestamp"].timetuple()) + (Config["FitFile"]["Decalage"]*60*60)
        Record["timestamp"] = int(TIME)
        #print(Fields)
        #try :
        Row = []
        NoMissing=True
        for Field in Fields : 
            if Record.has_key(Field.RealName)== False : 
                Row.append(Field.Default)
                print("          Missing this Field : "+Field.RealName)
                NoMissing=False
            else : 
                Row.append(Record[Field.RealName])
        #Row = list((Record[Field.RealName] for Field in Fields))
#            except : 
#                print("Error : ")
#                print(Record)
#                print(Row)
#                raise KeyError
        Row.insert(0,i)
        Datas.append(tuple(Row))
        i+=1
        if NoMissing :
            Prec = Record
    if Prec is None : 
        raise ValueError("Prec is none, so we have a problem with this file : "+MyFile)
    #obtention des types des enregistrements
    Types = [VL.GessNumpyType(str(Prec[Field.RealName])) for Field in Fields]
    FieldNames = [Field.Name for Field in Fields]
    FieldNames.insert(0,"OID")
    Types.insert(0,"int32")
    #print(Types)
    BD = VL.JDataTable(FieldNames,Types,"OID",Datas)
    return BD


#MyBd=FitToDataTable(File,Fields)
