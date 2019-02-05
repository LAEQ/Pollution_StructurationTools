9# -*- coding: utf-8 -*-
"""
Created on Mon Feb 05 16:43:35 2018

@author: GelbJ
"""

import sqlite3,os,sys,garmin
from Config import Config
from Config import FieldDef
from ReadingFitFiles import FitToDataTable
from osgeo import osr,ogr

sys.path.append(Config["JBasicsPath"])
from JQgis import JVectorLayer as VL
from JHtml import JsonToTable
import datetime
import json
import numpy as np

####################################
## Rajout du champ TIME dans toutes les tables
####################################
for Table in Config["Tables"] : 
    Table["Fields"].append(FieldDef("TIME","TIME","REAL",-999))
    Table["Fields"].append(FieldDef("DATETIME","DATETIME","TEXT","NAN"))
    
FieldConverter = {"REAL" : "float32","TEXT":"|S25","INTEGER":"int32"}
    


class PollutionBD(object) :
    
    def __init__(self,Folder,Config,Erase=False) :
        print("Initialising Database ...")
        self.Cleaned = False
        self.Root = Folder
        self.Config = Config
        #suppression de la BD si elle existe !
        if Erase : 
            if os.path.isfile(self.Root+"/Pollution.jdb") : 
                os.remove(self.Root+"/Pollution.jdb")
        #creation de la base de donnees si elle n'existe pas
        if os.path.isfile(self.Root+"/Pollution.jdb") :
            print("DataBase already exist")
            BD = sqlite3.connect(self.Root+"/Pollution.jdb")
        else :
            BD = sqlite3.connect(self.Root+"/Pollution.jdb")
            print("empty database created")
        # creation des tables si elle n'existent pas
        Cursor = BD.cursor()
        for Table in self.Config["Tables"] :
            Req = "create table if not exists "+Table["Name"]+" ("
            Fields = ""
            for Field in Table["Fields"] : 
                Fields+=Field.Name+" "+Field.Type+','
            Req+=Fields[:-1]+")"
            print(Req)
            Cursor.execute(Req)
        Cursor.close()
        BD.commit()
        
    def AllFields(self) :
        Fields = []
        #rajout des champs de la montre
        Fields.extend(self.Config["FitFile"]["Fields"])
        for Table in self.Config["Tables"] :
            for Field in Table["Fields"] : 
                if Field.Name!="TIME" and Field.Name!="DATETIME": 
                    Fields.append(Field)
        #Fields.append(FieldDef("TIME","TIME","REAL",-999))
        Fields.append(FieldDef("DATETIME","DATETIME","TEXT","NAN"))
        return Fields
        
    def Connect(self) :
        BD = sqlite3.connect(self.Root+"/Pollution.jdb")
        Cursor = BD.cursor()
        return BD,Cursor
    
    def CleanCSVs(self) : 
        print("Cleaning CSV Files ...")
        try :
            os.makedirs(self.Root+"/Structured")
        except :
            print("Structrured file seems to exists")
        Files = os.listdir(self.Root)
        for Table in self.Config["Tables"] : 
            for File in Files :
                #on garde le fichier si l'extension marche
                Ext = File[len(File)-len(Table["Extension"]):len(File)]
                if Ext == Table["Extension"] :
                    #on applique a ces fichiers la fonction de structuration
                    Table["StructFunc"](self.Root+'/'+File,self.Root+'/Structured/'+File,Table)
        self.Cleaned = True
        
    def Fill(self) : 
        print("Filling Database ...")
        if self.Cleaned == False : 
            if os.path.isdir(self.Root+"/Structured")==False :
                raise ValueError("Warning : the files seems not to have been cleaned")
        BD,Cursor = self.Connect()
        Files = os.listdir(self.Root+"/Structured")
        #iteration sur toutes les tables
        for Table in self.Config["Tables"] : 
            for File in Files :
                #on garde le fichier si l'extension marche
                Ext = File[len(File)-len(Table["Extension"]):len(File)]
                if Ext == Table["Extension"] :
                    print("    Adding Data from : "+File)
                    self.__AddData(File,Table,BD,Cursor)
        print("Filling Done !")
                    
    def __PrepData(self,Row,Table) :
        StrValues = []
        for element,Type in zip(Row,[Field.Type for Field in Table["Fields"]]) :
            if Type == "TEXT" : 
                StrValues.append("'"+str(element)+"'")
            else : 
                 StrValues.append(str(element))
        FinalRow = ",".join(StrValues)
        return FinalRow
                    
                    
    def __AddData(self,File,Table,BD,Cursor) :
        #Ajout de donnees dans une table
        Sep = Table["Sep"]
        CSV = open(self.Root+"/Structured/"+File)
        Header = CSV.readline().replace("\n","").split(Sep)
        #recuperation des indexs    
        Line = CSV.readline()
        if Line != "" :
            Indexes = [Header.index(Field.RealName) for Field in Table["Fields"]]
            Fields = [Field.Name for Field in Table["Fields"]]
            StrFields ="("+','.join(Fields)+")"
            while Line != "" : 
                Row = Line.replace("\n","").split(Sep)
                Data = [Row[ID] for ID in Indexes]
                StrData = "("+self.__PrepData(Data,Table)+")"
                Req = "INSERT INTO "+Table["Name"]+" "+StrFields+" VALUES "+StrData
                Cursor.execute(Req)
                Line = CSV.readline()
            BD.commit()
        else :
            print("        This file seems to be empty : "+File+" could you confirm ?")
        
    def Request(self,Time) : 
        #recuperation de toutes les valeurs entre deux periodes temporelles
        BD,Cursor = self.Connect()
        Values = {}
        for Table in self.Config["Tables"] : 
            Fields = [Field.Name for Field in Table["Fields"]]
            StrFields = ",".join(Fields)
            if Table["Recording"] == "MIN" : 
                Req = "SELECT "+StrFields+" FROM "+Table["Name"]+" WHERE TIME<"+str(Time+60)+" AND TIME>="+str(Time)
            elif Table["Recording"] == "SEC" : 
                Req = "SELECT "+StrFields+" FROM "+Table["Name"]+" WHERE TIME = "+str(Time)
            Rep = Cursor.execute(Req)
            Datas = Rep.fetchone()
            if Datas is None :
                for Field in Table["Fields"] :
                    Values[Field.Name] = Field.Default
            else :
                for Value,Field in zip(Datas,Fields) : 
                    Values[Field]=Value
        return Values
    
    def GenerateShps(self,Avoid = []) :
        print("Generating Shapefiles !")
        #creation du fichier de la sortie
        try :
            os.mkdir(self.Root+"/Shps")
        except WindowsError : 
            print("Folder Already existing")
        #preparation des descriptifs du shp
        SpatialRef = osr.SpatialReference()
        SpatialRef.ImportFromEPSG(4326)
        Fields = self.AllFields()
        
        #iteration sur les fichiers fit
        for File in os.listdir(self.Root) :
            if "." in File :
                if File.split(".")[1] == "fit" : 
                    print("    executing on this file : "+File)
                    Name = File.split(".")[0]
                    if Name in Avoid  : 
                        print("Avoiding this file as specified : "+Name)
                    else : 
                        if os.path.isfile(self.Root+"/Shps/"+Name+".shp") == False : 
                            FitTable = FitToDataTable(self.Root+'/'+File,Config["FitFile"]["Fields"])
                            Shp = VL.JFastLayer("")
                            Shp.MakeItEmpty({"SpatialRef":SpatialRef,"Fields":[F.Name for F in Fields],"FieldsTypes":[FieldConverter[F.Type] for F in Fields]})
                            #remplissage du shp
                            for Row in FitTable.Iterate(True) :
                                print("     Iterating on time : "+datetime.datetime.fromtimestamp(Row["TIME"]).strftime('%Y-%m-%d %H:%M:%S'))
                                Pt = ogr.Geometry(ogr.wkbPoint)
                                Pt.AddPoint(garmin.degrees(Row["Lon"]),garmin.degrees(Row["Lat"]))
                                Datas = self.Request(int(Row["TIME"]))
                                Datas.update(Row)
                                Datas["DATETIME"] = datetime.datetime.fromtimestamp(Row["TIME"]).strftime('%Y-%m-%d %H:%M:%S')
                                Datas["TIME"] = Row["TIME"]
            #                    print(Datas)
            #                    print([F.Name for F in Fields])
            #                    print([FieldConverter[F.Type] for F in Fields])
                                Shp.AppendFeat(Datas,Pt)
                            #enregistrement du shp
                            Shp.Save(self.Root+"/Shps/"+Name+".shp")
                            print("\a")
                        
    def EvaluateShps(self) : 
        """Methode pour verifier la qualite des donnees enregistrees dans les shapefiles
        """
        #### recuperation des Field a verifier
        Fields=[]
        for Table in self.Config["Tables"] :
            Fields += [(Field.Name,Field.Default) for Field in Table["Fields"]]
        
        Tables = {}
        #### Lecture des shapefiles
        ShapeFiles = os.listdir(self.Root+"/Shps")
        for File in ShapeFiles : 
            if File.split(".")[1] == "shp" : 
                Test = []
                print("Working on : "+File)
                Layer = VL.JFastLayer(self.Root+"/Shps/"+File)
                Layer.Initialize(ID = "OID",GeomIndex = False)
                ## test des Field
                for Field,Default in Fields : 
                    Column = list(Layer.AttrTable.GetVector(Field))
                    Missings = Column.count(Default)
                    Prt = round(Missings / float(len(Column)),2) *100
                    Test.append({"Missings" : Missings, "Field" : Field, "Prt" : Prt})
                Tables[File] = Test
        ### ecriture des resultats dans un fichier html
        Sortie = self.Root+"/EvaluateTables.html"
        Table = JsonToTable(Tables)
        Table.Write(Sortie)
        
    def PrepareTimeExcel(self) : 
        """
        Methode permettant de preparer les fichiers excel comprenant le debut 
        et la fin de chaque trajet
        """
        Sortie = open(self.Root+"/TimeTable.csv","w")
        Sortie.write("IDTrajet ; Debut Trajet (reel) ; Fin Trajet (reel) ; Debut Trajet (decoupe) ; Fin Trajet (Decoupe)\n")
        #### Lecture des shapefiles
        ShapeFiles = os.listdir(self.Root+"/Shps")
        for File in ShapeFiles : 
            if File.split(".")[1] == "shp" : 
                Layer = VL.JFastLayer(self.Root+"/Shps/"+File)
                Layer.Initialize(ID = "OID",GeomIndex = False)
                Start = Layer.NiceFeat(Layer[0])
                End = Layer.NiceFeat(Layer[Layer.FeatureCount-1])
                Sortie.write(File.split(".")[0]+";"+Start["DATETIME"]+";"+End["DATETIME"]+";--;--\n")
        Sortie.close()


#Process ==>
#chaque participant a un dossier avec tout ces fichiers dedans
#un fichier python de config indique 
#     le nom des fichiers que l'on s'attend a rencontrer
#     les champs a recuperer dans les CSV
#     
#Etape 1 : creation pour chaque participant d'une BD sqlite avec une table pour chaque type de donnees
#
#Etape 2 : remplissage des BD avec les differents fichiers enregistre, la colonne INDEX correspond a la date convertie en timestemp second
#
#Etape 3 : parser les fichier .fit des montres et requeter sur les BD pour les heures


