/*
 * dll_pthread_ext.c : Pthread extension calls for the dll.
 *
 * Copyright (c) 1996-1999 Carl J. Nobile
 * Created: May 11, 2000
 *
 * $Author$
 * $Date$
 * $Revision$
 */

#include <errno.h>
#include <pthread.h>
#include "dll_pthread_ext.h"

/* Local prototypes */
static void _pthread_rwlock_read_cleanup(void *rwlp);
static void _pthread_rwlock_write_cleanup(void *rwlp);


/*
 * pthread_rwlock_init_np() : Initialize read, write, and delete lock.
 *
 * Arguments: rwlp    -- Pointer to lock structure.
 *            attrp   -- Attribute value (non-functional at this time).
 *
 * Returns  : Zero    -- Success
 *            EINVAL  -- The mutex has not been properly initialized.
 *            EDEADLK -- The mutex is already locked by the calling thread.
 *
 * Note: The final and the draft POSIX versions of pthreads have different
 *       return values, consult your documentation for the correct values.
 */
int
pthread_rwlock_init_np(pthread_rwlock_t *rwlp, pthread_rwlockattr_t *attrp)
   {
   int status = 0;

   rwlp->r_active = 0;
   rwlp->w_active = 0;
   rwlp->r_pending = 0;
   rwlp->w_pending = 0;
   rwlp->valid_init = PTHREAD_INIT_FAILED;

   if((status = pthread_mutex_init(&rwlp->mutex, NULL)) != 0)
      return(status);

   if((status = pthread_cond_init(&rwlp->read, NULL)) != 0)
      {
      pthread_mutex_destroy(&rwlp->mutex);
      return(status);
      }

   if((status = pthread_cond_init(&(rwlp->write), NULL)) != 0)
      {
      pthread_cond_destroy(&rwlp->read);
      pthread_mutex_destroy(&rwlp->mutex);
      return(status);
      }

   rwlp->valid_init = PTHREAD_INIT_SUCCEED;
   return(0);
   }


/*
 * pthread_rwlock_destroy_np() : Destroy read, write, and delete lock.
 *
 * Arguments: rwlp    -- Pointer to lock structure.
 *
 * Returns  : EINVAL  -- The mutex has not been properly initialized.
 *            EDEADLK -- The mutex is already locked by the calling thread.
 *            EBUSY   -- The mutex is currently locked.
 *
 * Note: The final and the draft POSIX versions of pthreads have different
 *       return values, consult your documentation for the correct values.
 */
int
pthread_rwlock_destroy_np(pthread_rwlock_t *rwlp)
   {
   int status, status1, status2;

   if(rwlp->valid_init != PTHREAD_INIT_SUCCEED)
      return(EINVAL);

   if((status = pthread_mutex_lock(&rwlp->mutex)) != 0)
      return(status);

   /* Do any threads own the lock? */
   if(rwlp->r_active > 0 || rwlp->w_active)
      {
      pthread_mutex_unlock(&rwlp->mutex);
      return(EBUSY);
      }

   /* Are any threads in a pending state? */
   if(rwlp->r_pending != 0 || rwlp->w_pending != 0)
      {
      pthread_mutex_unlock(&rwlp->mutex);
      return(EBUSY);
      }

   rwlp->valid_init = PTHREAD_INIT_FAILED;

   if((status = pthread_mutex_unlock(&rwlp->mutex)) != 0)
      return(status);

   status = pthread_mutex_destroy(&rwlp->mutex);
   status1 = pthread_cond_destroy(&rwlp->read);
   status2 = pthread_cond_destroy(&rwlp->write);
   return(status2 != 0 ? status2 : (status1 != 0 ? status1 : status));
   }


/*
 * pthread_rwlock_rdlock_np() : Aquire read lock.
 *
 * Arguments: rwlp    -- Pointer to lock structure.
 *
 * Returns  : EINVAL  -- The mutex has not been properly initialized.
 *            EDEADLK -- The mutex is already locked by the calling thread.
 *            EBUSY   -- The mutex is currently locked.
 */
int
pthread_rwlock_rdlock_np(pthread_rwlock_t *rwlp)
   {
   int status;

   if(rwlp->valid_init != PTHREAD_INIT_SUCCEED)
      return(EINVAL);

   if((status = pthread_mutex_lock(&rwlp->mutex)) != 0)
      return(status);

   if(rwlp->w_active)
      {
      rwlp->w_pending++;
      pthread_cleanup_push(_pthread_rwlock_read_cleanup, (void *) rwlp);

      while(rwlp->w_active)
         if((status = pthread_cond_wait(&rwlp->read, &rwlp->mutex)) != 0)
            break;

      pthread_cleanup_pop(0);
      rwlp->r_pending--;
      }

   if(status == 0)
      rwlp->r_active++;

   pthread_mutex_unlock(&(rwlp->mutex));
   return(status);
   }


/*
 * pthread_rwlock_wrlock_np() : Aquire write lock
 *
 * Arguments: rwlp    -- Pointer to lock structure.
 *
 * Returns  : EINVAL  -- The mutex has not been properly initialized.
 *            EDEADLK -- The mutex is already locked by the calling thread.
 *            EBUSY   -- The mutex is currently locked.
 */
int
pthread_rwlock_wrlock_np(pthread_rwlock_t *rwlp)
   {
   int status;

   if(rwlp->valid_init != PTHREAD_INIT_SUCCEED)
      return(EINVAL);

   if((status = pthread_mutex_lock(&rwlp->mutex)) != 0)
      return(status);

   if(rwlp->w_active || rwlp->r_active > 0)
      {
      rwlp->w_pending++;
      pthread_cleanup_push(_pthread_rwlock_write_cleanup, (void *) rwlp);

      while(rwlp->w_active || rwlp->r_active > 0)
         if((status = pthread_cond_wait(&rwlp->write, &rwlp->mutex)) != 0)
            break;

      pthread_cleanup_pop(0);
      rwlp->w_pending--;
      }

   if(status == 0)
      rwlp->w_active = 1;

   pthread_mutex_unlock(&(rwlp->mutex));
   return(status);
   }


/*
 * pthread_rwlock_unlock_np() : Unlock read or write mutex.
 *
 * Arguments: rwlp    -- Pointer to lock structure.
 *
 * Returns  : EINVAL  -- The mutex has not been properly initialized.
 *            EDEADLK -- The mutex is already locked by the calling thread.
 *            EBUSY   -- The mutex is currently locked.
 */
int
pthread_rwlock_unlock_np(pthread_rwlock_t *rwlp)
   {
   int status = 0, status1 = 0;

   if(rwlp->valid_init != PTHREAD_INIT_SUCCEED)
      return(EINVAL);

   if((status = pthread_mutex_lock(&rwlp->mutex)) != 0)
      return(status);

   if(rwlp->w_active)
      {
      /* Try to unlock the write mutex. */
       rwlp->w_active = 0;

       if(rwlp->r_pending > 0 &&
        (status = pthread_cond_broadcast(&rwlp->read)) != 0)
          {
          pthread_mutex_unlock(&rwlp->mutex);
          return(status);
          }

       if(rwlp->w_pending > 0 &&
        (status = pthread_cond_signal(&rwlp->write)) != 0)
          {
          pthread_mutex_unlock(&rwlp->mutex);
          return(status);
          }
      }
   else
      {
      /* Try to unlock a read mutex. */
      rwlp->r_active--;

      if(rwlp->r_active == 0 && rwlp->w_pending > 0)
         status = pthread_cond_signal(&rwlp->write);
      }

   status1 = pthread_mutex_unlock(&rwlp->mutex);
   return(status1 == 0 ? status : status1);
   }


/*
 * _pthread_rwlock_read_cleanup() : Clean up mutex lock if there is a an
 *                                  internal problem with the pthread API.
 *
 * Arguments: rwlp -- Pointer to lock structure
 *
 * Returns  : None
 */
static void
_pthread_rwlock_read_cleanup(void *rwlp)
   {
   pthread_rwlock_t *rwl_tmp = (pthread_rwlock_t *) rwlp;

   rwl_tmp->r_pending--;
   pthread_mutex_unlock(&rwl_tmp->mutex);
   }


/*
 * _pthread_rwlock_write_cleanup() : Clean up mutex lock if there is a an
 *                                   internal problem with the pthread API.
 *
 * Arguments: rwlp -- Pointer to lock structure
 *
 * Returns  : None
 */
static void
_pthread_rwlock_write_cleanup(void *rwlp)
   {
   pthread_rwlock_t *rwl_tmp = (pthread_rwlock_t *) rwlp;

   rwl_tmp->w_pending--;
   pthread_mutex_unlock(&rwl_tmp->mutex);
   }
