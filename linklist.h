/*
 * linklist.h : Header file for the linklist API
 *
 * Copyright (c) 1996-2001 Carl J. Nobile
 * Created: December 22, 1996
 *
 * $Author$
 * $Date$
 * $Revision$
 */

#ifndef  _LINKLIST_H
#define  _LINKLIST_H

#ifdef __cplusplus
extern "C"
{
#endif

#if defined (_DLL_THREADS)
#  if defined (_DLL_MAIN_C)
#  include "dll_lock_wrappers.h"
#  else /* defined (_DLL_MAIN_C) */
#    if defined (LINUX) || defined (OSF1)
#    include <pthread.h>
#    define RWLOCK_T      pthread_rwlock_t
#    elif defined (SOLARIS)
#    include "dll_pthread_ext.h"
#    define RWLOCK_T      pthread_rwlock_t
#    endif /* platform dependencies */
#  endif /* defined (_DLL_MAIN_C) */
#else
/* Dummy macros if _DLL_THREADS is not defined */
#define RWLOCK_INIT(a,b)
#define RWLOCK_DESTROY(a)
#define RWLOCK_RLOCK(a)
#define RWLOCK_WLOCK(a)
#define RWLOCK_UNLOCK(a)
#define RWLOCK_RLOCK_NR(a)
#define RWLOCK_UNLOCK_NR(a)
#endif /* defined (_DLL_THREADS) */

typedef enum
   {
   DLL_NORMAL,             /* normal operation */
   DLL_MEM_ERROR,          /* malloc error */
   DLL_ZERO_INFO,          /* sizeof(Info) is zero */
   DLL_NULL_LIST,          /* List is NULL */
   DLL_NOT_FOUND,          /* Record not found */
   DLL_OPEN_ERROR,         /* Cannot open file */
   DLL_WRITE_ERROR,        /* File write error */
   DLL_READ_ERROR,         /* File read error */
   DLL_NOT_MODIFIED,       /* Unmodified list */
   DLL_NULL_FUNCTION,      /* NULL function pointer */
#if defined (_DLL_THREADS)
   DLL_THR_ERROR,          /* Thread error */
#endif
   DLL_STK_ERROR           /* Stack error */
   } DLL_Return;

/*
 * type defines
 */
typedef enum
   {
   DLL_FALSE,
   DLL_TRUE
   } DLL_Boolean;

typedef enum
   {
   DLL_ORIGIN_DEFAULT,     /* Use current origin setting */
   DLL_HEAD,               /* Set origin to head pointer */
   DLL_CURRENT,            /* Set origin to current pointer */
   DLL_TAIL                /* Set origin to tail pointer */
   } DLL_SrchOrigin;

typedef enum
   {
   DLL_DIRECTION_DEFAULT,  /* Use current direction setting */
   DLL_DOWN,               /* Set direction to down */
   DLL_UP                  /* Set direction to up */
   } DLL_SrchDir;

typedef enum
   {
   DLL_INSERT_DEFAULT,     /* Use current insert setting */
   DLL_ABOVE,              /* Insert new record ABOVE current record */
   DLL_BELOW               /* Insert new record BELOW current record */
   } DLL_InsertDir;

/*
 * Structures
 *
 * The structure holding your data should look something like this:
 *
 * typedef struct your_info
 *    {
 *    type your_data;
 *    } YourInfo;
 *
 * YourInfo any_info_name;
 *
 * The following structure pointer also needs to be defined:
 *
 * List *any_list_name;
 */

typedef void Info;

#if defined (_DLL_MAIN_C)
#define VERSION   "Ver: 2.0.0"
#define VERDATE   __DATE__
#define CREDITS   "-------------------------------\n" \
                  "Developed by:  Carl J. Nobile\n" \
                  "Contributions: Charlie Buckheit\n" \
                  "               Graham Inchley\n" \
                  "               Wai-Sun Chia\n"

static char version[sizeof(VERSION) + sizeof(VERDATE) + sizeof(CREDITS) + 1];
#endif   /* _DLL_MAIN_C */

#if defined (_DLL_MAIN_C) || defined (DEBUG)
typedef struct node
   {
   Info *info;
   struct node *next;
   struct node *prior;
   } Node;

typedef struct list
   {
   DLL_Boolean    sessions;
   void           *mainSession;
   Node           *head;
   Node           *tail;
   Node           *current;
   size_t         infosize;
   unsigned long  listsize;
   unsigned long  current_index;
   DLL_Boolean    modified;
   DLL_SrchOrigin search_origin;
   DLL_SrchDir    search_dir;
#if defined (_DLL_THREADS)
   RWLOCK_T       rwl_t;
#endif
   } List;
#else
typedef struct list List;
typedef struct node Node;
#endif   /* _DLL_MAIN_C || DEBUG */

#define DEFAULT_STACK_SIZE    10

typedef struct session
   {
   DLL_Boolean   sessions;
   List          *list;
   Node          **stack;
   size_t        maxStackSize;
   size_t        topOfStack;
   unsigned long saveIndex;
   } DLL_Session;

typedef struct search_modes
   {
   DLL_SrchOrigin search_origin;
   DLL_SrchDir    search_dir;
   } DLL_SearchModes;


/*
 * Prototypes
 */
List *DLL_CreateList(List **list);
List *DLL_CreateSession(List *list, size_t stackDepth);
char *DLL_Version(void);
DLL_Boolean DLL_IsListEmpty(List *slist);
DLL_Boolean DLL_IsListFull(List *slist);
DLL_Return DLL_AddRecord(List *slist, Info *info,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_CurrentPointerToHead(List *slist);
DLL_Return DLL_CurrentPointerToTail(List *slist);
DLL_Return DLL_DecrementCurrentPointer(List *slist);
DLL_Return DLL_DeleteCurrentRecord(List *slist);
DLL_Return DLL_DeleteEntireList(List *slist);
DLL_Return DLL_DeleteRecord(List *slist, Info *match,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_DestroyList(List **slist);
DLL_Return DLL_FindNthRecord(List *slist, Info *record, unsigned long nRec);
DLL_Return DLL_FindRecord(List *slist, Info *record, Info *match,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_GetCurrentRecord(List *slist, Info *record);
DLL_Return DLL_GetError(List *list);
DLL_Return DLL_GetNextRecord(List *slist, Info *record);
DLL_Return DLL_GetPriorRecord(List *slist, Info *record);
DLL_Return DLL_InitializeList(List *list, size_t infosize);
DLL_Return DLL_IncrementCurrentPointer(List *slist);
DLL_Return DLL_InsertRecord(List *slist, Info *info, DLL_InsertDir dir);
DLL_Return DLL_LoadList(List *slist, const char *path,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_RestoreCurrentPointer(List *slist);
DLL_Return DLL_SaveList(List *slist, const char *path);
DLL_Return DLL_SetSearchModes(List *slist, DLL_SrchOrigin origin,
 DLL_SrchDir dir);
DLL_Return DLL_SetStackSize(List *slist, size_t stackDepth);
DLL_Return DLL_StoreCurrentPointer(List *slist);
DLL_Return DLL_SwapRecord(List *slist, DLL_InsertDir dir);
DLL_Return DLL_UpdateCurrentRecord(List *slist, Info *record);
DLL_SearchModes *DLL_GetSearchModes(List *slist, DLL_SearchModes *ssp);
unsigned long DLL_GetCurrentIndex(List *slist);
unsigned long DLL_GetNumberOfRecords(List *slist);

#ifdef __cplusplus
}
#endif

#endif   /* _LINKLIST_H */
