/**
  ******************************************************************************
  * @file    ADC_SNK.h
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef ADC_SNK_H
#define ADC_SNK_H

#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32h5xx_ll_gpio.h"

/* Exported Defines ----------------------------------------------------------*/

#ifdef __cplusplus
extern "C" {
#endif

#define ADC_DIFF_CAPABLE

#define TCPP01_PORT0_VSENSE_ADC_INSTANCE            ADC2
#define TCPP01_PORT0_VSENSE_ADC_CHANNEL             ADC_CHANNEL_5

void ADC_Start(void);

#ifdef __cplusplus
}
#endif
#endif /* ADC_SNK_H */
