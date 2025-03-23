/**
 ******************************************************************************
 * @file    STMicroelectronics.X-CUBE-TCPP.1.0.0
 * @brief   App Source application C file
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

/* Includes ------------------------------------------------------------------*/
#include "app_tcpp.h"

#if defined (_RTOS)
#include "cmsis_os.h"
#include "FreeRTOS.h"
#include "task.h"
#endif

#include "usbpd.h"

#ifdef _TRACE
#include "tracer_emb.h"
#endif /*_TRACE*/

#ifdef _GUI_INTERFACE
#include "gui_api.h"
#endif /*_GUI_INTERFACE*/

/* Private variables ---------------------------------------------------------*/

/* Private function prototypes -----------------------------------------------*/

void MX_TCPP_Init(void)
{

#ifndef tcpp01_PORT0_DB_OUT_TO_VCC
  HAL_GPIO_WritePin(TCPP01_PORT0_DB_OUT_GPIO_PORT, TCPP01_PORT0_DB_OUT_GPIO_PIN, GPIO_PIN_SET);
#endif
#ifndef TCPP01_PORT0_VCC_OUT_TO_VCC
  HAL_GPIO_WritePin(TCPP01_PORT0_VCC_OUT_GPIO_PORT, TCPP01_PORT0_VCC_OUT_GPIO_PIN, GPIO_PIN_SET);
#endif

  ADC_Start();
}

void MX_TCPP_Process(void)
{

}

/**
  * @brief This function is called to increment a global variable "uwTick"
  *        used as application time base.
  * @note In the default implementation, this variable is incremented each 1ms
  *       in Systick ISR.
  * @note This function overwrites the weak function.
  * @retval None
  */
void HAL_IncTick(void)
{
  uwTick += (uint32_t)uwTickFreq;
  USBPD_DPM_TimerCounter();
#if defined(_GUI_INTERFACE)
  GUI_TimerCounter();
#endif /* _GUI_INTERFACE */
}

