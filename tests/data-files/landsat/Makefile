.PHONY: get-mtl get-stac

get-stac:
	# Get a representative sample of STAC files to work with
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2020/081/119/LC08_L2SR_081119_20200101_20200823_02_T2/LC08_L2SR_081119_20200101_20200823_02_T2_SR_stac.json .
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2020/030/034/LC08_L2SP_030034_20201111_20201212_02_T1/LC08_L2SP_030034_20201111_20201212_02_T1_SR_stac.json .
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/etm/2007/167/064/LE07_L2SP_167064_20070321_20200913_02_T1/LE07_L2SP_167064_20070321_20200913_02_T1_SR_stac.json .
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/tm/1986/201/034/LT05_L2SP_201034_19860504_20200917_02_T1/LT05_L2SP_201034_19860504_20200917_02_T1_SR_stac.json .
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2019/232/122/LC08_L2SR_232122_20191218_20201023_02_T2/LC08_L2SR_232122_20191218_20201023_02_T2_SR_stac.json .

get-mtl:
	# Example to get an MTL
	aws s3 cp --request-payer requester \
		s3://usgs-landsat/collection02/level-2/standard/oli-tirs/2020/081/119/LC08_L2SR_081119_20200101_20200823_02_T2/LC08_L2SR_081119_20200101_20200823_02_T2_MTL.json .
