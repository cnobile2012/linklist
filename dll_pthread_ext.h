/*
 * dll_pthread_ext.h : Header file for the dll_pthread_ext.c source file.
 *
 * Copyright (c) 1996-1999 Carl J. Nobile
 * Created: May 11, 2000
 *
 * $Author$
 * $Date$
 * $Revision$
 */

#ifndef  _DLL_PTHREAD_EXT_H
#define  _DLL_PTHREAD_EXT_H

#include <pthread.h>

typedef enum
   {
   INIT_FAILED = 0,     /* initialization failed */
   INIT_SUCCEED         /* initialization succeeded */
   } InitStatus;


/* rdwr lock variable structure */
typedef struct rdwr_var
   {
   pthread_mutex_t   mutex;
   pthread_cond_t    read;          /* wait for read */
   pthread_cond_t    write;         /* wait for write */
   InitStatus        valid_init;    /* initialization validity */
   int               r_active;      /* read active */
   int               w_active;      /* write active */
   int               r_pending;     /* read pending */
   int               w_pending;     /* write pending */
   } pthread_rwl_t;

/* Attribute data type */
typedef void *pthread_rwlattr_t;

#define pthread_rwlattr_default NULL;

/* prototypes */
int pthread_rwl_init_np(pthread_rwl_t *rwlp, pthread_rwlattr_t *attrp);
int pthread_rwl_rlock_np(pthread_rwl_t *rwlp);
int pthread_rwl_wlock_np(pthread_rwl_t *rwlp);
int pthread_rwl_runlock_np(pthread_rwl_t *rwlp);
int pthread_rwl_wunlock_np(pthread_rwl_t *rwlp);


#endif   /* _DLL_PTHREAD_EXT_H */
