# Sentinel-1 RTC test data

from `aws s3 sync s3://sentinel-s1-rtc-indigo/tiles/RTC/1/IW/12/S/YJ/2016/S1B_20161121_12SYJ_ASC .`

but instead of storing geotiffs for testing, just store VRT to save space:
gdal_translate -of VRT /vsis3/sentinel-s1-rtc-indigo/tiles/RTC/1/IW/12/S/YJ/2016/S1B_20161121_12SYJ_ASC/Gamma0_VV.tif Gamma0_VV.tif
