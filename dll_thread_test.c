/*
 * dll_thread_test.c : Unit test for testing threads in the DLL API.
 *
 * Copyright (c) 1996-2001 Carl J. Nobile
 * Created: October 07, 2000
 *
 * $Author$
 * $Date$
 * $Revision$
 */

#include <alloca.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "linklist.h"

#define Boolean      DLL_Boolean
#define FALSE        DLL_FALSE
#define TRUE         DLL_TRUE

#define NUM_TH       10
#define NUM_RECORDS  100
#define DISPLACEMENT 1000
#define WHERE        "Generated from main."


typedef struct my_stuff
   {
   int  number;
   char where;
   char when
   } MyStuff;


int main(void)
   {
   List *list = NULL;
   MyStuff *info = (MyStuff *) alloca(sizeof(MyStuff));
   pthread_t threadID[NUM_TH];
   int i;

   /* Create and initialize link list */
   if(DLL_CreateList(&list) == NULL)
      {
      (void) fprintf(stderr, "Error: DLL_CreateList failed.\n");
      exit(EXIT_FAILURE);
      }

   dllErrorHandler(DLL_InitializeList(list, sizeof(MyStuff)));

   /* Build beginning of list */
   memset(info, '\0', sizeof(MyStuff));

   for(i = 0; i < NUM_RECORDS; i++)
      {
      info->number = i + DISPLACEMENT;
      dllErrorHandler(DLL_AddRecord(list, info, NULL));
      }




   exit(EXIT_SUCCESS);
   }


void dllErrorHandler(DLL_Return status)
   {
   switch(status)
      {
      case DLL_NORMAL:           /* SUCCESS */
         return;
      case DLL_NOT_FOUND:        /* SUCCESS */
         (void) fprintf(stderr, "DLL Warning: Record not found.\n");
         return;
      case DLL_NOT_MODIFIED:     /* SUCCESS */
         (void) fprintf(stderr, "DLL Error: List has not been modified.\n");
         return;
      case DLL_MEM_ERROR:
         (void) fprintf(stderr, "DLL Error: Memory allocation error.\n");
         break;
      case DLL_ZERO_INFO:
         (void) fprintf(stderr, "DLL error: Size of record is zero.\n");
         break;
      case DLL_NULL_LIST:
         (void) fprintf(stderr, "DLL Error: List pointer is NULL.\n");
         break;
      case DLL_OPEN_ERROR:
         (void) fprintf(stderr, "DLL Error: File open error.\n");
         break;
      case DLL_WRITE_ERROR:
         (void) fprintf(stderr, "DLL Error: File write error.\n");
         break;
      case DLL_READ_ERROR:
         (void) fprintf(stderr, "DLL Error: File read error.\n");
         break;
      case DLL_NULL_FUNCTION:
         (void) fprintf(stderr, "DLL Error: Call back function "
          "is a NULL pointer.\n");
         break;
      case DLL_THR_ERROR:
         (void) fprintf(stderr, "DLL Error: Thread error.\n");
         break;
      case DLL_STK_ERROR:
         (void) fprintf(stderr, "DLL Error: Stack error.\n");
      default:
         (void) fprintf(stderr, "DLL Error: Unknown error %d\n", status);
      }
   exit(EXIT_FAILURE);
   }
