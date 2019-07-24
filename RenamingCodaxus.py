# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 08:43:32 2019

@author: GelbJ
"""


from path import Path
import os
import numpy as np
import shutil


def FindFileName(File,i=0) : 
    if os.path.isfile(File) == False : 
        return File
    else : 
        i+=1
        Parts = File.split("COD")
        NewName = Parts[0]+str(i)+"_COD"+Parts[1]
        return FindFileName(NewName)


CodaxusFolder = Path("E:/Datas/_Montreal 2019/A)_FieldData/DonneesCodaxus/AllData")
DataFolder = Path("E:/Datas/_Montreal 2019/A)_FieldData")


### Step1 : recuperer tous les participants
Parts = np.unique([File.name.split("RP")[1][0] for File in CodaxusFolder.files("*.txt")])
DicoFolder = {}

for Part in Parts : 
    for Folder in DataFolder.dirs() : 
        if "ID"+Part == str(Folder.name).split("_")[0] : 
            DicoFolder[Part] = Folder
        
for File in CodaxusFolder.files("*.txt") : 
    Part = File.name.split("RP")[1][0]
    PartFolder = DicoFolder[Part]
    NewName = str(PartFolder.name)+"_"+File.name.split("_")[0]+"_COD.txt"
    Destination = FindFileName(PartFolder.joinpath(NewName))
    print("copying : "+str(File))
    print("to : "+str(Destination))
    shutil.copy2(File,Destination)


