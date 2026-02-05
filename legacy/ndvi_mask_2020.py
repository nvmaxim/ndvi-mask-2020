#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
# Скрипт для создания маски по стеку NDVI.
# Запуск: python ndvi_mask.py NDVIStack_FILENAME.tif
# Выход: NDVIStack_FILENAME_Mask.tif

import sys
from osgeo import gdal
import numpy as np
import time

# ---- Параметры для анализа NDVI ----
MIN_NDVI = 0.5      # Минимальное значение NDVI для пика (фаза активной вегетации)
MAX_NDVI = 0.65     # Порог NDVI для счёта как пиковой вегетации
START_DATE = 1      # Слой начала контроля (ранняя фаза)
MIN_DATE = 4        # Слой начала окна для поиска пика NDVI
MAX_DATE = 18       # Слой конца окна для поиска пика NDVI

# ---- Чтение аргументов ----
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Missing parameter - NDVI stack required")
        print(sys.argv)
        sys.exit(1)
    else:
        NDVI_fname = sys.argv[1]
        _f_ndvi = gdal.Open(NDVI_fname)
        if _f_ndvi is None:
            print('NDVI stack does not exist')
            sys.exit(1)
        else:
            # Имя файла для маски
            MASK_fname = NDVI_fname[:NDVI_fname.rfind('.')] + '_Mask.tif'
            start_time = time.time()

    # ---- Подготовка массивов ----
    n_ndvi_bands = _f_ndvi.RasterCount                      # Количество слоёв (дат)
    ndvi_bands = [_f_ndvi.GetRasterBand(iband + 1) for iband in range(n_ndvi_bands)]
    ndvi_szx, ndvi_szy = ndvi_bands[0].XSize, ndvi_bands[0].YSize  # Размеры растра
    ndvi = np.empty((n_ndvi_bands, ndvi_szy, ndvi_szx), dtype=np.float32)
    mask = np.zeros((ndvi_szy, ndvi_szx), dtype=np.float32)        # Итоговая маска, изначально все 0

    # ---- Чтение стека NDVI в numpy-массив ----
    for iband in range(n_ndvi_bands):
        print('Reading band', iband)
        ndvi[iband, :, :] = ndvi_bands[iband].ReadAsArray()

    # ---- Формирование маски ----
    for x in range(ndvi_szx):
        if x % 100 == 0:
            print(f"Processing column {x} of {ndvi_szx}")
        for y in range(ndvi_szy):
            # Условия: пик в нужном окне, остальное время — низкая NDVI
            main_phase = np.max(ndvi[MIN_DATE:MAX_DATE, y, x]) > MAX_NDVI
            early_phase = np.max(ndvi[START_DATE:MIN_DATE-1, y, x]) < MIN_NDVI
            late_phase = np.max(ndvi[MAX_DATE+1:, y, x]) < MIN_NDVI
            if main_phase and early_phase and late_phase:
                mask[y, x] = 1

    # ---- Запись маски в GeoTIFF ----
    driver = gdal.GetDriverByName('GTiff')
    _f_mask = driver.Create(MASK_fname, ndvi_szx, ndvi_szy, 1, gdal.GDT_Float32)
    _f_mask.SetProjection(_f_ndvi.GetProjection())
    _f_mask.SetGeoTransform(_f_ndvi.GetGeoTransform())
    _f_mask.GetRasterBand(1).WriteArray(mask[:, :])

    # ---- Завершение ----
    _f_mask = None
    _f_ndvi = None
    total_time = time.time() - start_time
    print("\nScript finished in {0:0.2f} sec".format(total_time))
