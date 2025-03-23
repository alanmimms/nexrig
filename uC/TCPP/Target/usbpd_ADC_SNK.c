/**
  ******************************************************************************
  * @file    ADC_SNK.c
  * @author  DFD Application Team
  * @brief   Header file for TCPP_Conf.c
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */

#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "usbpd_ADC_SNK.h"

#ifdef __cplusplus
extern "C" {
#endif

extern ADC_HandleTypeDef            hadc2;

void ADC_Start()
{
  HAL_ADC_Start(&hadc2);
}

#ifdef __cplusplus
}
#endif
