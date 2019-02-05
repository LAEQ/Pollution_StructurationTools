# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 14:15:16 2018

@author: GelbJ
"""

Racine = "G:/___NewZeland/__Auckland/A)_FieldData"

######################################################
### Config Steph
######################################################
#Users = ["ID1_PA"]
#Users=["ID2_EL"]
Users=["ID3_JG"]


Avoid=[]

#####################################################
## Programme principal
#####################################################

from Config import Config
from JG_Structuring_BD import PollutionBD

import sys
sys.path.append(Config["JBasicsPath"])

for User in Users : 
    Path = Racine+"/"+User
    #generation de la BD (depuis le debut si necessaire)
    BD = PollutionBD(Path,Config,Erase=True)
    #nettoyage des CSV
    BD.CleanCSVs()
    #creation de la BD SQLITE
    BD.Fill()
    #Generation des fichiers SHP
    #Avoid = []
    BD.GenerateShps(Avoid = Avoid)
    BD.EvaluateShps()
    BD.PrepareTimeExcel()