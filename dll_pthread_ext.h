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
   PTHREAD_INIT_FAILED = 0,         /* initialization failed */
   PTHREAD_INIT_SUCCEED             /* initialization succeeded */
   } PthreadInitStatus;


/* rdwr lock variable structure */
typedef struct rdwr_var
   {
   pthread_mutex_t   mutex;
   pthread_cond_t    read;          /* wait for read */
   pthread_cond_t    write;         /* wait for write */
   PthreadInitStatus valid_init;    /* initialization validity */
   int               r_active;      /* read active */
   int               w_active;      /* write active */
   int               r_pending;     /* read pending */
   int               w_pending;     /* write pending */
   } pthread_rwlock_t;

/* Attribute data type */
typedef void *pthread_rwlockattr_t;

#define pthread_rwlockattr_default NULL;

/* prototypes */
int pthread_rwlock_init_np(pthread_rwlock_t *rwlp,
 pthread_rwlockattr_t *attrp);
int pthread_rwlock_destroy_np(pthread_rwlock_t *rwlp);
int pthread_rwlock_rdlock_np(pthread_rwlock_t *rwlp);
int pthread_rwlock_wrlock_np(pthread_rwlock_t *rwlp);
int pthread_rwlock_unlock_np(pthread_rwlock_t *rwlp);

#endif   /* _DLL_PTHREAD_EXT_H */
