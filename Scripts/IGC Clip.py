# coding: utf8
'''
# -------------------------------------------------------------------------------------------------------
# CONVERTER Geodatabase
# -------------------------------------------------------------------------------------------------------
# Michel Metran
# Agosto de 2018

# Python Script to ArcGIS
# Description: Recorta uma área de interesse, com um buffer, dos shapes vetorizados do IGC.
'''

# -------------------------------------------------------------------------------------------------------
# Módulos e Codificação
import os
import sys
import arcpy
from arcpy.sa import *

reload(sys)
sys.setdefaultencoding('utf8')

# -------------------------------------------------------------------------------------------------------
# Variável de Input da Máscara
Mascara = r'E:\SIG_MP_BasesCartograficas\SP_IGC\Geodata\Geo_IGC.mdb\Vetorizacao\Limite_BaciasHidrograficas'
# Se for usar Query para Selecionar alguma coisa, é 1, senão é 0
Selecionar = 1
# Consulta em SQL '[ID_GAEMA] = 9' ou '[Geo_Codigo] = 3538709' ou "[Nome] = 'Charqueada'"
Query = "[Nome] = 'BH da Represa do Lobo'"
# Entorno da Área Selecionada em metros
EntornoSelect = 5

# -------------------------------------------------------------------------------------------------------
# Variável de Input do Grid das Cartas em vetores
PathGeodata = r'E:\SIG_MP_BasesCartograficas\SP_IGC'
Geodatabase_In = 'Geo_IGC.mdb'
Geodatabase_Out = 'Geo_IGC_Clip.mdb'

shapes = ['Vetorizacao//Hidro_Linhas',
          'Vetorizacao//Hidro_Poligonos',
          'Vetorizacao//Hidro_Pontos',
          'Vetorizacao//Limite_BaciasHidrograficas',
          'Vetorizacao//Limite_Municipios',
          'Resultados//APP_HidroIntermitente',
          'Resultados//APP_HidroPerene']

# -------------------------------------------------------------------------------------------------------
# Print Variables
geo_In = os.path.join(PathGeodata, 'Geodata', Geodatabase_In)
geo_Out = os.path.join(PathGeodata, 'Geodata', Geodatabase_Out)
PathFeatureDataset1 = os.path.join(geo_In, 'Vetorizacao')
PathFeatureDataset2 = os.path.join(geo_In, 'Resultados')

arcpy.Delete_management(geo_Out, 'Workspace')
arcpy.CreatePersonalGDB_management(
    os.path.join(PathGeodata, 'Geodata'), Geodatabase_Out)
arcpy.CreateFeatureDataset_management(
    geo_Out, 'Vetorizacao', PathFeatureDataset1)
arcpy.CreateFeatureDataset_management(
    geo_Out, 'Resultados', PathFeatureDataset2)

# -------------------------------------------------------------------------------------------------------
# Variáveis de Ambiente do ArcGIS
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True
arcpy.env.workspace = geo_Out

# -------------------------------------------------------------------------------------------------------
# Seleciona a Máscara da Área de Interesse
print '## Etapa 1: Seleciona a Máscara da Área de Interesse'

# Seleciona
if Selecionar == 1:
    try:
        arcpy.Select_analysis(Mascara,
                              'AreaDeInteresse',
                              Query)
    except arcpy.ExecuteError:
        print arcpy.GetMessages()

elif Selecionar == 0:
    try:
        arcpy.Copy_management(Mascara,
                              'AreaDeInteresse')
    except arcpy.ExecuteError:
        print arcpy.GetMessages()

else:
    pass

# Buffer
if EntornoSelect > 0:
    try:
        arcpy.Buffer_analysis('AreaDeInteresse',
                              'AreaDeInteresse_Buffer',
                              str(EntornoSelect) + ' Meters',
                              'FULL', 'ROUND', 'NONE')
    except arcpy.ExecuteError:
        print arcpy.GetMessages()

elif EntornoSelect == 0:
    try:
        arcpy.Copy_management('AreaDeInteresse',
                              'AreaDeInteresse_Buffer')
    except arcpy.ExecuteError:
        print arcpy.GetMessages()

else:
    pass

arcpy.Dissolve_management('AreaDeInteresse_Buffer',
                          'AreaDeInteresse_Buffer_Dissolve',
                          '', '', 'MULTI_PART', 'DISSOLVE_LINES')

# -------------------------------------------------------------------------------------------------------
# Variável de Input do Grid Interno e Cartas em rasters

for shape in shapes:
    fc_In = ''
    fc_Out = ''
    fc_In = os.path.join(geo_In, shape)
    fc_Out = os.path.join(geo_Out, shape)

    print 'Input:' + fc_In
    print 'Input:' + fc_Out

    try:
        arcpy.Clip_analysis(fc_In, 'AreaDeInteresse_Buffer_Dissolve', fc_Out)
    except:
        print 'Erro qualquer no geodatabase'

# -------------------------------------------------------------------------------------------------------
# Deletando Lixos
print '## Etapa 4: Deletando pasta de temporário'
arcpy.Delete_management(os.path.join(
    geo_Out, 'AreaDeInteresse'), 'FeatureClass')
arcpy.Delete_management(os.path.join(
    geo_Out, 'AreaDeInteresse_Buffer'), 'FeatureClass')
arcpy.Delete_management(os.path.join(
    geo_Out, 'AreaDeInteresse_Buffer_Dissolve'), 'FeatureClass')

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'
