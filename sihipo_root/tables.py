import django_tables2 as tables
from sihipo_root.models import *

class PlantEvalIfTable(tables.Table):
	class Meta:
		model = PlantEvalIf
		
class PlantEvalThenTable(tables.Table):
	class Meta:
		model = PlantEvalThen
		
class PlantEvalTable(tables.Table):
	class Meta:
		model = PlantEval
		
class PlantEvalLogTable(tables.Table):
	class Meta:
		model = PlantEvalLog
		
class PlantPlantTable(tables.Table):
	class Meta:
		model = PlantPlant
		
class PlantOptTable(tables.Table):
	class Meta:
		model = PlantOpt
		
class PlantOptDetailTable(tables.Table):
	class Meta:
		model = PlantOptDetail
		
class PlantSensorTable(tables.Table):
	class Meta:
		model = PlantSensor
		
class PlantSensorDetailTable(tables.Table):
	class Meta:
		model = PlantSensorDetail
		
class PlantControlTable(tables.Table):
	class Meta:
		model = PlantControl
		
class PlantControlDetailTable(tables.Table):
	class Meta:
		model = PlantControlDetail
		
class PlantRackTable(tables.Table):
	class Meta:
		model = PlantRack
		
class PlantRackPointTable(tables.Table):
	class Meta:
		model = PlantRackPoint
		
class PlantControlLogTable(tables.Table):
	class Meta:
		model = PlantControlLog
		
class PlantControlLogDetailTable(tables.Table):
	class Meta:
		model = PlantControlLogDetail
		
class PlantSensorLogTable(tables.Table):
	class Meta:
		model = PlantSensorLog
		
class PlantSensorLogDetailTable(tables.Table):
	class Meta:
		model = PlantSensorLogDetail
		