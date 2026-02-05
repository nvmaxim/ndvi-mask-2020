import numpy as np
import logging
from typing import Optional

# константы
MIN_NDVI = 0.5
MAX_NDVI = 0.65
START_DATE, MIN_DATE, MAX_DATE = 1, 4, 18

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ndvi_mask_logic(ndvi_stack: np.ndarray) -> np.ndarray:
    """
    Применяет векторизованную маску к стеку NDVI.
    Ожидаемая форма (shape): (bands, rows, cols)
    """
    try:
        # Валидация входных данных
        if ndvi_stack.ndim != 3:
            raise ValueError(f"Expected 3D array, got {ndvi_stack.ndim}D")
            
        logging.info("Calculating phases (Vectorized)...")
        
        # Векторизованные операции
        main_phase_max = np.max(ndvi_stack[MIN_DATE:MAX_DATE], axis=0)
        early_phase_max = np.max(ndvi_stack[START_DATE:MIN_DATE-1], axis=0)
        late_phase_max = np.max(ndvi_stack[MAX_DATE+1:], axis=0)

        # создаем булеву маску
        mask = (
            (main_phase_max > MAX_NDVI) & 
            (early_phase_max < MIN_NDVI) & 
            (late_phase_max < MIN_NDVI)
        )
        
        return mask.astype(np.float32)

    except Exception as e:
        logging.error(f"Failed to calculate mask: {e}")
        raise
