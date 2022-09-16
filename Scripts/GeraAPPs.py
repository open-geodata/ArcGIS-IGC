# coding: utf8
'''
# -------------------------------------------------------------------------------------------------------
# CONVERTER GEODATABASE
# -------------------------------------------------------------------------------------------------------
# Michel Metran
# Setembro de 2017

# Python Script to ArcGIS
# Description: Geras APPs da rede hidrográfica vetorizada do IGC

'''

# -------------------------------------------------------------------------------------------------------
# Módulos e Codificação
import os
import sys
import arcpy
import arcpy.cartography as CA			    # Necessário para o Smooth

reload(sys)
sys.setdefaultencoding('utf8')

# -------------------------------------------------------------------------------------------------------
# Variável de Input
geodatabase = r'E:\SIG_MP_BasesCartograficas\SP_IGC\Geodata\Geo_IGC.mdb'
in_FeatureDataSet = 'Vetorizacao'
out_FeatureDataSet = 'Resultados'

# APPs em Metros
# Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_Nascentes = 50
# Alínea 'a', Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_CursoDagua = 30
# Alínea 'b', 'c', 'd', e 'e', Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_RioMaior10m = 0
# Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_Represa_NascentePerene = 50
# Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_Represa_NascenteIntermitente = 50
# Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_Represa_Menor20ha = 15
# Inciso I, Artigo 3º, Resolução Conama nº 302/02
APP_Represa_Maior20ha = 1
# Alínea 'b', Inciso I, Artigo 3º, Resolução Conama nº 303/02
APP_Lagoa_Menor20ha = 50
# Alínea 'b', Inciso I, Artigo 3º, Resolução Conama nº 303/02
APP_Lagoa_Maior20ha = 100
APP_Varzea = 30

# -------------------------------------------------------------------------------------------------------
# Print Variables
in_pathFeatureDataSet = os.path.join(geodatabase, in_FeatureDataSet)
out_pathFeatureDataSet = os.path.join(geodatabase, out_FeatureDataSet)
temp_pathFeatureDataSet = os.path.join(
    geodatabase, in_FeatureDataSet + "_temp")

arcpy.Delete_management(temp_pathFeatureDataSet, 'FeatureDataset')
arcpy.CreateFeatureDataset_management(
    geodatabase, in_FeatureDataSet + "_temp", in_pathFeatureDataSet)

print 'Geodatabase: ' + geodatabase
print 'Feature DataSet Input: ' + in_pathFeatureDataSet
print 'Feature DataSet Output: ' + out_pathFeatureDataSet
print 'Feature DataSet Temp: ' + temp_pathFeatureDataSet

# -------------------------------------------------------------------------------------------------------
# Variáveis de Ambiente do ArcGIS
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True
arcpy.env.workspace = temp_pathFeatureDataSet

# -------------------------------------------------------------------------------------------------------
# Input: Cursos d'água
print "## Etapa 1: APP dos Cursos d'Água"

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Linhas'),
                      'Hidro_Linhas_01_Select',
                      "[Tipo] = 'Perene'")
arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Linhas'),
                      'Hidro_Linhas_02_Select',
                      "[Tipo] = 'Intermitente' OR [Tipo] = 'Perene'")

CA.SmoothLine('Hidro_Linhas_01_Select',
              'Hidro_Linhas_03_Smooth',
              'PAEK', '30 Meters', 'NO_FIXED', 'FLAG_ERRORS')
CA.SmoothLine('Hidro_Linhas_02_Select',
              'Hidro_Linhas_04_Smooth',
              'PAEK', '30 Meters', 'NO_FIXED', 'FLAG_ERRORS')

arcpy.Buffer_analysis('Hidro_Linhas_03_Smooth',
                      'Hidro_Linhas_05_Buffer',
                      str(APP_CursoDagua) + ' Meters',
                      'FULL', 'ROUND', 'NONE')
arcpy.Buffer_analysis('Hidro_Linhas_04_Smooth',
                      'Hidro_Linhas_06_Buffer',
                      str(APP_CursoDagua) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

# -------------------------------------------------------------------------------------------------------
# Input: Nascentes
print '## Etapa 2: APP das Nascentes'

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Pontos'),
                      'Hidro_Pontos_01_Select',
                      "[Tipo] = 'Perene'")
arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Pontos'),
                      'Hidro_Pontos_02_Select',
                      "[Tipo] = 'Intermitente' OR [Tipo] = 'Perene'")

arcpy.Buffer_analysis('Hidro_Pontos_01_Select',
                      'Hidro_Pontos_03_Buffer',
                      str(APP_Nascentes) + ' Meters',
                      'FULL', 'ROUND', 'NONE')
arcpy.Buffer_analysis('Hidro_Pontos_02_Select',
                      'Hidro_Pontos_04_Buffer',
                      str(APP_Nascentes) + ' Meters',
                      'FULL', 'ROUND', 'NONE')


# -------------------------------------------------------------------------------------------------------
# Input: Rios Maiores que 10 metros
print '## Etapa 3: APP dos rios maiores 10 metros'

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_01_Select', "[Tipo] = 'Rio'")

CA.SmoothPolygon('Hidro_Poligonos_01_Select',
                 'Hidro_Poligonos_02_Smooth',
                 'PAEK', '30 Meters', 'NO_FIXED', 'FLAG_ERRORS')

if APP_RioMaior10m == 0:
    try:
        arcpy.Buffer_analysis('Hidro_Poligonos_02_Smooth',
                              'Hidro_Poligonos_03_Buffer',
                              'APP', 'FULL', 'ROUND', 'NONE')

    except arcpy.ExecuteError:
        print arcpy.GetMessages()

elif APP_RioMaior10m > 0:
    try:
        arcpy.Buffer_analysis('Hidro_Poligonos_02_Smooth',
                              'Hidro_Poligonos_03_Buffer',
                              str(APP_RioMaior10m) + ' Meters',
                              'FULL', 'ROUND', 'NONE')

    except arcpy.ExecuteError:
        print arcpy.GetMessages()

else:
    pass


# -------------------------------------------------------------------------------------------------------
# Input: Polígonos
print '## Etapa 4: APP das represas'

arcpy.CalculateField_management(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                                'Area_ha', '!shape.area@hectares!', 'PYTHON_9.3')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_04_Select',
                      "[Tipo] = 'Nascente Perene'")
arcpy.Buffer_analysis('Hidro_Poligonos_04_Select',
                      'Hidro_Poligonos_05_Buffer',
                      str(APP_Represa_NascentePerene) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_06_Select',
                      "[Tipo] = 'Nascente Intermitente'")
arcpy.Buffer_analysis('Hidro_Poligonos_06_Select',
                      'Hidro_Poligonos_07_Buffer',
                      str(APP_Represa_NascenteIntermitente) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_08_Select',
                      "[Tipo] = 'Represa' AND [Area_ha] < 20")
arcpy.Buffer_analysis('Hidro_Poligonos_08_Select',
                      'Hidro_Poligonos_09_Buffer',
                      str(APP_Represa_Menor20ha) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_10_Select',
                      "[Tipo] = 'Represa' AND [Area_ha] >= 20")
arcpy.Buffer_analysis('Hidro_Poligonos_10_Select',
                      'Hidro_Poligonos_11_Buffer',
                      str(APP_Represa_Maior20ha) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_12_Select',
                      "[Tipo] = 'Lagoa' AND [Area_ha] < 20")
arcpy.Buffer_analysis('Hidro_Poligonos_12_Select',
                      'Hidro_Poligonos_13_Buffer',
                      str(APP_Lagoa_Menor20ha) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_14_Select',
                      "[Tipo] = 'Lagoa' AND [Area_ha] >= 20")
arcpy.Buffer_analysis('Hidro_Poligonos_14_Select',
                      'Hidro_Poligonos_15_Buffer',
                      str(APP_Lagoa_Maior20ha) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

arcpy.Select_analysis(os.path.join(in_pathFeatureDataSet, 'Hidro_Poligonos'),
                      'Hidro_Poligonos_16_Select',
                      "[Tipo] = 'Várzea'")
arcpy.Buffer_analysis('Hidro_Poligonos_16_Select',
                      'Hidro_Poligonos_17_Buffer',
                      str(APP_Varzea) + ' Meters',
                      'FULL', 'ROUND', 'NONE')

# -------------------------------------------------------------------------------------------------------
# Análises: Unindo os Polígonos que geram APPs
print '## Etapa 5: Unindo os Polígonos que geram APPs'

arcpy.Merge_management(['Hidro_Poligonos_03_Buffer',
                        'Hidro_Poligonos_05_Buffer',
                        'Hidro_Poligonos_09_Buffer',
                        'Hidro_Poligonos_11_Buffer',
                        'Hidro_Poligonos_13_Buffer',
                        'Hidro_Poligonos_15_Buffer',
                        'Hidro_Poligonos_17_Buffer'],
                       'Hidro_Poligonos_18_Merge')

arcpy.Merge_management(['Hidro_Poligonos_03_Buffer',
                        'Hidro_Poligonos_05_Buffer',
                        'Hidro_Poligonos_07_Buffer',
                        'Hidro_Poligonos_09_Buffer',
                        'Hidro_Poligonos_11_Buffer',
                        'Hidro_Poligonos_13_Buffer',
                        'Hidro_Poligonos_15_Buffer',
                        'Hidro_Poligonos_17_Buffer'],
                       'Hidro_Poligonos_19_Merge')


# -------------------------------------------------------------------------------------------------------
# Análises: Unindo APPs
print '## Etapa 6: Unindo APPs'

arcpy.Merge_management(['Hidro_Linhas_05_Buffer',
                        'Hidro_Pontos_03_Buffer',
                        'Hidro_Poligonos_03_Buffer',
                        'Hidro_Poligonos_18_Merge'],
                       'APP_01_Merge')

arcpy.Merge_management(['Hidro_Linhas_06_Buffer',
                        'Hidro_Pontos_04_Buffer',
                        'Hidro_Poligonos_03_Buffer',
                        'Hidro_Poligonos_19_Merge'],
                       'APP_02_Merge')

arcpy.Dissolve_management('APP_01_Merge',
                          'APP_03_Dissolve',
                          '', '', 'MULTI_PART',
                          'DISSOLVE_LINES')
arcpy.Dissolve_management('APP_02_Merge',
                          'APP_04_Dissolve',
                          '', '', 'MULTI_PART',
                          'DISSOLVE_LINES')

# -------------------------------------------------------------------------------------------------------
# Análises: Removendo polígonos
print '## Etapa 7: Removendo polígonos'

arcpy.Merge_management(['Hidro_Poligonos_01_Select',
                        'Hidro_Poligonos_04_Select',
                        'Hidro_Poligonos_08_Select',
                        'Hidro_Poligonos_10_Select',
                        'Hidro_Poligonos_12_Select',
                        'Hidro_Poligonos_14_Select',
                        'Hidro_Poligonos_16_Select'],
                       'Hidro_Poligonos_20_Merge')

arcpy.Merge_management(['Hidro_Poligonos_01_Select',
                        'Hidro_Poligonos_06_Select',
                        'Hidro_Poligonos_08_Select',
                        'Hidro_Poligonos_10_Select',
                        'Hidro_Poligonos_12_Select',
                        'Hidro_Poligonos_14_Select',
                        'Hidro_Poligonos_16_Select'],
                       'Hidro_Poligonos_21_Merge')

arcpy.Erase_analysis('APP_03_Dissolve',
                     'Hidro_Poligonos_20_Merge',
                     'APP_05_Erase', '#')
arcpy.Erase_analysis('APP_04_Dissolve',
                     'Hidro_Poligonos_21_Merge',
                     'APP_06_Erase', '#')


# -------------------------------------------------------------------------------------------------------
# Análises: Ajustando tabela de atributos
print '## Etapa 8: Ajustando tabela de atributos'

arcpy.AddField_management('APP_05_Erase', 'APP', 'TEXT',
                          '', '', 20, '', 'NULLABLE', 'NON_REQUIRED')
arcpy.AddField_management('APP_06_Erase', 'APP', 'TEXT',
                          '', '', 20, '', 'NULLABLE', 'NON_REQUIRED')

arcpy.CalculateField_management(
    'APP_05_Erase', 'APP', repr('Sim'), 'PYTHON_9.3')
arcpy.CalculateField_management(
    'APP_06_Erase', 'APP', repr('Sim'), 'PYTHON_9.3')

arcpy.AddField_management('APP_05_Erase', 'Area_ha', 'FLOAT')
arcpy.AddField_management('APP_06_Erase', 'Area_ha', 'FLOAT')

arcpy.CalculateField_management(
    'APP_05_Erase', 'Area_ha', '!shape.area@hectares!', 'PYTHON_9.3')
arcpy.CalculateField_management(
    'APP_06_Erase', 'Area_ha', '!shape.area@hectares!', 'PYTHON_9.3')


# -------------------------------------------------------------------------------------------------------
# Produtos Finais
print '## Etapa 9: Produtos Finais'

arcpy.MultipartToSinglepart_management('APP_05_Erase', 'APP_07_Multipart')
arcpy.MultipartToSinglepart_management('APP_06_Erase', 'APP_08_Multipart')
arcpy.DeleteField_management('APP_07_Multipart', 'ORIG_FID')
arcpy.DeleteField_management('APP_08_Multipart', 'ORIG_FID')

arcpy.Copy_management('APP_07_Multipart',
                      os.path.join(out_pathFeatureDataSet, 'APP_HidroPerene'))
arcpy.Copy_management('APP_08_Multipart',
                      os.path.join(out_pathFeatureDataSet, 'APP_HidroIntermitente'))


# -------------------------------------------------------------------------------------------------------
# Deletando Lixos
print '## Etapa 10: Deletando pasta de temporário'

arcpy.Delete_management(temp_pathFeatureDataSet, 'FeatureDataset')

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'
