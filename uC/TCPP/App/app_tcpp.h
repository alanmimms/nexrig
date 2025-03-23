/**
 ******************************************************************************
 * @file    STMicroelectronics.X-CUBE-TCPP.1.0.0
 * @brief   APP SOURCE H file
 ******************************************************************************
 * @attention
 *
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
 *
 ******************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef APP_SOURCE_APPLICATION_H
#define APP_SOURCE_APPLICATION_H

/* Includes ------------------------------------------------------------------*/
#include "usbpd_ADC_SNK.h"
#include "usbpd_GPIO_SNK.h"
#include "STMicroelectronics.X-CUBE-TCPP_conf.h"

#define STM32H5XX
#define ADC_FULL_SCALE       (0x0FFFU)

/* Exported functions --------------------------------------------------------*/
void MX_TCPP_Init(void);
void MX_TCPP_Process(void);

void HAL_IncTick(void);

/* Exported types ------------------------------------------------------------*/

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */
/* USER CODE END EC */

#endif /* APP_SOURCE_APPLICATION_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
