/**
  ******************************************************************************
  * @file    GPIO_SNK_CONF.h
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
#ifndef GPIO_SNK_CONF_H
#define GPIO_SNK_CONF_H

#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32h5xx_ll_gpio.h"

/* Exported Defines ----------------------------------------------------------*/

/* GPIO ----------------------------------------------------------------------*/
//TCPP01 VCC OUT GPIO Configuration
#define TCPP01_PORT0_VCC_OUT_GPIO_PORT              GPIOB
#define TCPP01_PORT0_VCC_OUT_GPIO_PIN               GPIO_PIN_9
#define TCPP01_PORT0_VCC_OUT_GPIO_DEFVALUE()        HAL_GPIO_WritePin(TCPP01_PORT0_VCC_OUT_GPIO_PORT,TCPP01_PORT0_VCC_OUT_GPIO_PIN,GPIO_PIN_SET);
#define TCPP01_PORT0_VCC_OUT_GPIO_SET()             HAL_GPIO_WritePin(TCPP01_PORT0_VCC_OUT_GPIO_PORT,TCPP01_PORT0_VCC_OUT_GPIO_PIN,GPIO_PIN_SET);
#define TCPP01_PORT0_VCC_OUT_GPIO_RESET()           HAL_GPIO_WritePin(TCPP01_PORT0_VCC_OUT_GPIO_PORT,TCPP01_PORT0_VCC_OUT_GPIO_PIN,GPIO_PIN_RESET);

//TCPP01 DB OUT GPIO Configuration
#define TCPP01_PORT0_DB_OUT_GPIO_PORT               GPIOB
#define TCPP01_PORT0_DB_OUT_GPIO_PIN                GPIO_PIN_8
#define TCPP01_PORT0_DB_OUT_GPIO_DEFVALUE()         HAL_GPIO_WritePin(TCPP01_PORT0_DB_OUT_GPIO_PORT,TCPP01_PORT0_DB_OUT_GPIO_PIN,GPIO_PIN_SET);
#define TCPP01_PORT0_DB_OUT_GPIO_SET()              HAL_GPIO_WritePin(TCPP01_PORT0_DB_OUT_GPIO_PORT,TCPP01_PORT0_DB_OUT_GPIO_PIN,GPIO_PIN_SET);
#define TCPP01_PORT0_DB_OUT_GPIO_RESET()            HAL_GPIO_WritePin(TCPP01_PORT0_DB_OUT_GPIO_PORT,TCPP01_PORT0_DB_OUT_GPIO_PIN,GPIO_PIN_RESET);

#ifdef __cplusplus
}
#endif

#endif /* GPIO_SNK_CONF_H */
