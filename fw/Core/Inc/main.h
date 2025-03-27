/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32h7xx_hal.h"
#include "stm32h7xx_nucleo.h"
#include <stdio.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define TxIQSCK_Pin GPIO_PIN_2
#define TxIQSCK_GPIO_Port GPIOE
#define TxIQNSS_Pin GPIO_PIN_4
#define TxIQNSS_GPIO_Port GPIOE
#define TxIQMISO_Pin GPIO_PIN_5
#define TxIQMISO_GPIO_Port GPIOE
#define TxIQMOSI_Pin GPIO_PIN_6
#define TxIQMOSI_GPIO_Port GPIOE
#define USBFault__Pin GPIO_PIN_0
#define USBFault__GPIO_Port GPIOF
#define TxEnable_Pin GPIO_PIN_2
#define TxEnable_GPIO_Port GPIOF
#define RxQ_Pin GPIO_PIN_6
#define RxQ_GPIO_Port GPIOA
#define RxMOSI_Pin GPIO_PIN_7
#define RxMOSI_GPIO_Port GPIOA
#define TxMOSI_Pin GPIO_PIN_2
#define TxMOSI_GPIO_Port GPIOB
#define RxI_Pin GPIO_PIN_11
#define RxI_GPIO_Port GPIOF
#define AntVSWR_Pin GPIO_PIN_13
#define AntVSWR_GPIO_Port GPIOF
#define RxTuneLDAC__Pin GPIO_PIN_0
#define RxTuneLDAC__GPIO_Port GPIOG
#define TxIQLDAC__Pin GPIO_PIN_1
#define TxIQLDAC__GPIO_Port GPIOG
#define RFGainHiLo_Pin GPIO_PIN_2
#define RFGainHiLo_GPIO_Port GPIOG
#define VFOSDA_Pin GPIO_PIN_9
#define VFOSDA_GPIO_Port GPIOC
#define VFOSCL_Pin GPIO_PIN_8
#define VFOSCL_GPIO_Port GPIOA
#define DbgUARTTX_Pin GPIO_PIN_9
#define DbgUARTTX_GPIO_Port GPIOA
#define DbgUARTRX_Pin GPIO_PIN_10
#define DbgUARTRX_GPIO_Port GPIOA
#define TxNSS_Pin GPIO_PIN_15
#define TxNSS_GPIO_Port GPIOA
#define TxSCK_Pin GPIO_PIN_10
#define TxSCK_GPIO_Port GPIOC
#define TxMISO_Pin GPIO_PIN_11
#define TxMISO_GPIO_Port GPIOC
#define TxTuneLDAC__Pin GPIO_PIN_0
#define TxTuneLDAC__GPIO_Port GPIOD
#define RxMISO_Pin GPIO_PIN_9
#define RxMISO_GPIO_Port GPIOG
#define RxNSS_Pin GPIO_PIN_10
#define RxNSS_GPIO_Port GPIOG
#define RxSCK_Pin GPIO_PIN_11
#define RxSCK_GPIO_Port GPIOG
#define LD2_Pin GPIO_PIN_1
#define LD2_GPIO_Port GPIOE

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
