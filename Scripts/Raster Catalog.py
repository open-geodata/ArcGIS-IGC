# coding: utf8
'''
# -------------------------------------------------------------------------------------------------------
# CONVERTER Geodatabase
# -------------------------------------------------------------------------------------------------------
# Michel Metran
# Maio de 2018

# Python Script to ArcGIS
# Description: Geras um Raster Catalog para melhor visualização das Cartas, em formato Raster, do IGC.
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
# Variável de Input do Grid das Cartas em vetores
PathGeodata = r'E:\SIG_MP_BasesCartograficas\SP_IGC'
Geodatabase = 'Geo_IGC.mdb'
FeatureDatasetIn = 'Grade_Cartas'

# -------------------------------------------------------------------------------------------------------
# Variável de Input do Grid Interno e Cartas em rasters
# Pasta onde estão os arquivos em raster.
PathRastersIn = os.path.join(PathGeodata, 'Rasters', 'Cartas_10k')
GridInterno = os.path.join(PathGeodata, 'Geodata',
                           Geodatabase, 'Grade_Interna', 'Grade_Linhas')
# Entorno no grid a ser excluído, em metros
EntornoGrid = 10

# -------------------------------------------------------------------------------------------------------
# Variável de Input da Máscara
Mascara = r'E:\SIG_MP_GAEMA\Geodata\Geo_PCJ.mdb\BR_IBGE\SP_2005_Municipios'
# Se for usar Query para Selecionarr alguma coisa, é 1, senão é 0
Selecionar = 1
# Consulta em SQL '[ID_GAEMA] = 9' ou '[Geo_Codigo] = 3538709' ou "[Nome] = 'Charqueada'"
Query = '[ID_GAEMA] = 9'
# Entorno da Área Selecionada em metros
EntornoSelect = 0

# -------------------------------------------------------------------------------------------------------
# Print Variables
PathFeatureDatasetIn = os.path.join(
    PathGeodata, 'Geodata', Geodatabase, FeatureDatasetIn)
PathFeatureDatasetTemp = os.path.join(
    PathGeodata, 'Geodata', Geodatabase, FeatureDatasetIn + '_temp')

arcpy.Delete_management(PathFeatureDatasetTemp, 'FeatureDataset')
arcpy.CreateFeatureDataset_management(os.path.join(
    PathGeodata, 'Geodata', Geodatabase), FeatureDatasetIn + '_temp', PathFeatureDatasetIn)

print 'Geodatabase: ' + Geodatabase
print 'Feature Dataset Input: ' + PathFeatureDatasetIn
print 'Feature Dataset Temp: ' + PathFeatureDatasetTemp

# -------------------------------------------------------------------------------------------------------
# Variáveis de Ambiente do ArcGIS
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True
arcpy.env.workspace = PathFeatureDatasetTemp

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
# Input: Seleciona Cartas Georreferenciadas e dá processamentos subsequentes
print '## Etapa 2: Seleciona Cartas Georreferenciadas'

arcpy.MakeFeatureLayer_management(os.path.join(PathFeatureDatasetIn, 'CartasTopograficas_10k'),
                                  'CartasTopograficas_10k_Geo_lyr',
                                  where_clause="[Georreferenciada] = 'Sim'")

arcpy.MakeFeatureLayer_management('AreaDeInteresse_Buffer_Dissolve',
                                  'AreaDeInteresse_Buffer_Dissolve_lyr')

arcpy.SelectLayerByLocation_management(in_layer='CartasTopograficas_10k_Geo_lyr',
                                       overlap_type='INTERSECT',
                                       select_features='AreaDeInteresse_Buffer_Dissolve_lyr',
                                       search_distance='',
                                       selection_type='NEW_SELECTION',
                                       invert_spatial_relationship='NOT_INVERT')

arcpy.CopyFeatures_management('CartasTopograficas_10k_Geo_lyr',
                              'CartasTopograficas_10k_Selecionadas')

# -------------------------------------------------------------------------------------------------------
# Processa Carta a Carta
print '## Etapa 3: Processa Carta a Carta'

arcpy.Delete_management(os.path.join(PathRastersIn, 'Mosaic_8bits'), 'Folder')
arcpy.CreateFolder_management(PathRastersIn, 'Mosaic_8bits')

arcpy.Delete_management(os.path.join(PathRastersIn, 'Mosaic'), 'Folder')
arcpy.CreateFolder_management(PathRastersIn, 'Mosaic')

arcpy.Delete_management(os.path.join(
    PathGeodata, 'Geodata', Geodatabase, 'Cartas_10k'), 'RasterCatalog')
arcpy.CreateRasterCatalog_management(os.path.join(PathGeodata, 'Geodata', Geodatabase),
                                     out_name='Cartas_10k',
                                     raster_spatial_reference="GEOGCS['GCS_Corrego_Alegre',DATUM['D_Corrego_Alegre',SPHEROID['International_1924',6378388.0,297.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8,98279933943848E-09;0,001;0,001;IsHighPrecision", spatial_reference="GEOGCS['GCS_Corrego_Alegre',DATUM['D_Corrego_Alegre',SPHEROID['International_1924',6378388.0,297.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8,98279933943848E-09;0,001;0,001;IsHighPrecision", config_keyword='', spatial_grid_1='0', spatial_grid_2='0', spatial_grid_3='0', raster_management_type='MANAGED', template_raster_catalog='')

rows = arcpy.SearchCursor('CartasTopograficas_10k_Selecionadas')

# Execute Copy, Clip, Buffer para cada carta
for row in rows:
    NomeCarta = row.getValue('Cod_Carta')
    feature = row.Shape
    print 'Processando a Carta ' + NomeCarta + '...'

    try:
        arcpy.CopyFeatures_management(feature, 'Carta_1Copy_' + NomeCarta)
        arcpy.Clip_analysis(GridInterno, feature, 'Carta_2Grid_' + NomeCarta)
        arcpy.Buffer_analysis('Carta_2Grid_' + NomeCarta,
                              'Carta_3Buffer_' + NomeCarta,
                              str(EntornoGrid) + ' Meters',
                              'FULL', 'ROUND', 'NONE')
        arcpy.Dissolve_management('Carta_3Buffer_' + NomeCarta,
                                  'Carta_4Dissolve_' + NomeCarta,
                                  '', '', 'MULTI_PART', 'DISSOLVE_LINES')
    except:
        error = arcpy.GetMessages()

    # Execute Raster Operations
    try:
        arcpy.ProjectRaster_management(os.path.join(PathRastersIn, NomeCarta + '.tif'),
                                       os.path.join(
                                           PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Project_' + NomeCarta + '.tif'),
                                       out_coor_system="GEOGCS['GCS_Corrego_Alegre',DATUM['D_Corrego_Alegre',SPHEROID['International_1924',6378388.0,297.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", resampling_type='NEAREST', cell_size='1,21758821105443E-05 1,22928257441342E-05', geographic_transform='', Registration_Point='',
                                       in_coor_system="PROJCS['Corrego_Alegre_UTM_Zone_23S',GEOGCS['GCS_Corrego_Alegre',DATUM['D_Corrego_Alegre',SPHEROID['International_1924',6378388.0,297.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',-45.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")

        arcpy.gp.ExtractByMask_sa(os.path.join(PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Project_' + NomeCarta + '.tif'),
                                  'Carta_1Copy_' + NomeCarta,
                                  os.path.join(PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Carta_' + NomeCarta + '.tif'))

        arcpy.gp.ExtractByMask_sa(os.path.join(PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Carta_' + NomeCarta + '.tif'),
                                  'Carta_4Dissolve_' + NomeCarta,
                                  os.path.join(PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Grid_' + NomeCarta + '.tif'))

        arcpy.CopyRaster_management(os.path.join(PathRastersIn, 'Mosaic_8bits', 'Carta_8bits_Grid_' + NomeCarta + '.tif'),
                                    os.path.join(
                                        PathRastersIn, 'Mosaic', 'Carta_' + NomeCarta + '.tif'),
                                    config_keyword='', background_value='', nodata_value="", onebit_to_eightbit='NONE',
                                    colormap_to_RGB='NONE', pixel_type='1_BIT',
                                    scale_pixel_value='NONE', RGB_to_Colormap='NONE',
                                    format='TIFF', transform='NONE')
    except:
        error = arcpy.GetMessages()

arcpy.WorkspaceToRasterCatalog_management(os.path.join(PathRastersIn, 'Mosaic'),
                                          os.path.join(
                                              PathGeodata, 'Geodata', Geodatabase, 'Cartas_10k'),
                                          include_subdirectories='NONE', project='PROJECT_ONFLY')

# -------------------------------------------------------------------------------------------------------
# Deletando Lixos
print '## Etapa 4: Deletando pasta de temporário'
arcpy.Delete_management(os.path.join(PathRastersIn, 'Mosaic_8bits'), 'Folder')
arcpy.Delete_management(PathFeatureDatasetTemp, 'FeatureDataset')

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'
