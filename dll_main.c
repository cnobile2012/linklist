/*
 * dll_main.c : An API for a double linked list.
 *
 * Copyright (c) 1996-2001 Carl J. Nobile
 * Created: December 22, 1996
 *
 * $Author$
 * $Date$
 * $Revision$
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define  _DLL_MAIN_C
#include "linklist.h"

/* Local Prototypes */
static DLL_Session *_createSession(List *list, size_t depth);
static List        *_getList(List *slist);
static DLL_Session *_getSession(List *slist);
static void         _deleteEntireList(List *list);
static DLL_Return   _addRecord(List *list, Info *info,
 int (*pFun)(Info *, Info *));


/**************************
 * Initialization Functions
 */

/*
 * Status   : Public
 *
 * DLL_CreateList() : Creates a structure of type List
 *
 * Arguments: list -- Pointer to a pointer to a name of a structure to create.
 * Returns  : Pointer to created structure
 *            NULL if unsuccessfull
 */
List *
DLL_CreateList(List **list)
   {
   if((*list = (List *) malloc(sizeof(List))) == NULL)
      return(NULL);

   return(*list);
   }


/*
 * Status   : Public
 *
 * DLL_InitializeList() : Initializes double link list
 *
 * Arguments: list          -- Pointer to type List
 *            infosize      -- Size of user Info
 * Returns  : DLL_NORMAL    -- Initialization was done successfully
 *            DLL_MEM_ERROR -- Memory allocation error during stack creation.
 *            DLL_ZERO_INFO -- sizeof(Info) is zero
 *            DLL_NULL_LIST -- Info is NULL
 *            DLL_THR_ERROR -- Thread lock initilization error
 */
DLL_Return
DLL_InitializeList(List *list, size_t infosize)
   {
   if(infosize == (size_t) 0)
      return(DLL_ZERO_INFO);

   if(list == NULL)
      return(DLL_NULL_LIST);

   list->head = NULL;
   list->tail = NULL;
   list->current = NULL;
   list->infosize = infosize;
   list->current_index = (unsigned long) 0;
   list->listsize = (unsigned long) 0;
   list->modified = DLL_FALSE;
   list->search_origin = DLL_HEAD;
   list->search_dir = DLL_DOWN;
   list->sessions = DLL_FALSE;

   if((list->mainSession = _createSession(list, DEFAULT_STACK_SIZE)) == NULL)
      return(DLL_MEM_ERROR);

   RWLOCK_INIT(&list->rwl_t, NULL);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_DestroyList() : Destroys Info, Node, and List structures
 *
 * Arguments: slist         -- Pointer to a pointer to a name of a
 *                             structure to destroy.
 * Returns  : DLL_NORMAL    -- Locks and list destroyed successfully.
 *            DLL_THR_ERROR -- Top level list was not destroyed or freed
 *                             because thread locks exited with an error.
 */
DLL_Return
DLL_DestroyList(List **slist)
   {
   List *list = _getList(*slist);
/*     DLL_Session *session = _getSession(*slist); */

   RWLOCK_WLOCK(&(list)->rwl_t);

   if(list == NULL)
      {
      RWLOCK_UNLOCK(&(list)->rwl_t);
      return(DLL_NORMAL);
      }

   if((list)->head != NULL)
      {
      _deleteEntireList(list);
      return(DLL_MEM_ERROR);
      }

   RWLOCK_UNLOCK(&(list)->rwl_t);
   RWLOCK_DESTROY(&(list)->rwl_t);
   free(list);
   list = NULL;
   return(DLL_NORMAL);
   }


/****************************
 * Session Specific Functions
 */

/*
 * Status   : Public
 *
 * DLL_CreateSession() : Creates a session and stack space.
 *
 * Arguments: list          -- Pointer to type List
 *            stackDepth    -- Depth of stack (number of saves before the stack
 *                             overflows)
 * Returns  : Pointer to session container or NULL if an error occurred.
 */
List *
DLL_CreateSession(List *list, size_t stackDepth)
   {
   DLL_Session *session = NULL;

/*     if(list->sessions == DLL_FALSE) */
/*        list->sessions = DLL_TRUE; */

   if((session = _createSession(list, stackDepth)) == NULL)
      return(NULL);

   return((List *) session);
   }


/*
 * Status   : Private
 *
 * _createSession() : Create a session and stack space.
 *
 * Arguments: slist -- Pointer to type List
 *            depth -- Depth of stack
 * Returns  : Pointer to session container or NULL if an error occurred.
 */
static DLL_Session *
_createSession(List *list, size_t depth)
   {
   DLL_Session *session = NULL;

   if((session = (DLL_Session *) malloc(sizeof(DLL_Session))) == NULL)
      return(NULL);

   if((session->stack = (Node **) malloc(sizeof(Node *) * depth)) == NULL)
      return(NULL);

   memset(session->stack, '\0', sizeof(Node *) * depth);
   session->sessions = DLL_TRUE;
   session->list = list;
   session->maxStackSize = depth;
   session->topOfStack = (size_t) 0;
   session->saveIndex = (unsigned long) 0;
   return(session);
   }


/*
 * Status   : Public
 *
 * DLL_SetStackSize() : Change the stack size after the original allocation.
 *
 * Arguments: slist         -- Pointer to type List
 *            stackDepth    -- Depth of stack (number of saves before the stack
 *                             overflows)
 * Returns  : DLL_NORMAL    -- Successful change of stack size.
 *            DLL_MEM_ERROR -- Memmory error while changing stack size.
 *            DLL_STK_ERROR -- New stack value is <= old stack value.
 */
DLL_Return
DLL_SetStackSize(List *slist, size_t stackDepth)
   {
   DLL_Session *session = _getSession(slist);

   if(stackDepth <= session->topOfStack)
      return(DLL_STK_ERROR);

   if((session->stack = (Node **) realloc(session->stack,
    sizeof(Node *) * stackDepth)) == NULL)
      return(DLL_MEM_ERROR);

   memset(session->stack + session->topOfStack, '\0',
    stackDepth - session->topOfStack);
   session->topOfStack = stackDepth;
   return(DLL_NORMAL);
   }


/*
 * Status  : Private
 *
 * _getList() : Get the actual list.
 *
 * Arguments: slist -- Could be the real list or a session container.
 *
 * Returns  : The real list
 */
static List *
_getList(List *slist)
   {
   if(slist->sessions == DLL_FALSE)
      return(slist);
   return(((DLL_Session *) slist)->list);
   }

/*
 * Status  : Private
 *
 * _getSession() : Get the actual session container.
 *
 * Arguments: slist -- Could be the real list or a session container.
 *
 * Returns  : The real list
 */
static DLL_Session *
_getSession(List *slist)
   {
   if(slist->sessions == DLL_FALSE)
      return(slist->mainSession);
   return((DLL_Session *) slist);
   }


/****************************
 * Status and State Functions
 */

/*
 * Status   : Public
 *
 * DLL_Version() : Returns a pointer to version information
 *
 * Arguments: NONE
 * Return   : char * -- Pointer to version info
 */
char *
DLL_Version(void)
   {
   memset(version, '\0', sizeof(version));
   strcpy(version, VERSION);
   strcat(version, "  ");
   strcat(version, VERDATE);
   strcat(version, "\n");
   strcat(version, CREDITS);
   strcat(version, "\n");
   return(version);
   }


/*
 * Status   : Public
 *
 * DLL_IsListEmpty() : Checks for an empty list
 *
 * Arguments: slist     -- Pointer to type List
 * Returns  : DLL_TRUE  -- List is empty
 *            DLL_FALSE -- List has items in it
 */
DLL_Boolean
DLL_IsListEmpty(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

    RWLOCK_RLOCK_NR(&list->rwl_t);

   if(list->head == NULL || list->tail == NULL)
      {
      RWLOCK_UNLOCK_NR(&list->rwl_t);
      return(DLL_TRUE);
      }

   RWLOCK_UNLOCK_NR(&list->rwl_t);
   return(DLL_FALSE);
   }


/*
 * Status   : Public
 *
 * DLL_IsListFull() : Checks for an empty list
 *
 * Arguments: slist     -- Pointer to type List
 * Returns  : DLL_TRUE  -- List is full (memory dependent)
 *            DLL_FALSE -- List is empty or partially full
 */
DLL_Boolean
DLL_IsListFull(List *slist)
   {
   Node *newN;
   Info *newI;
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_RLOCK_NR(&list->rwl_t);

   if((newN = (Node *) malloc(sizeof(Node))) == NULL)
      {
      RWLOCK_UNLOCK_NR(&list->rwl_t);
      return(DLL_TRUE);
      }

   if((newI = (Info *) malloc(list->infosize)) == NULL)
      {
      free(newN);
      RWLOCK_UNLOCK_NR(&list->rwl_t);
      return(DLL_TRUE);
      }

   free(newN);
   free(newI);
   RWLOCK_UNLOCK_NR(&list->rwl_t);
   return(DLL_FALSE);
   }


/*
 * Status   : Public
 *
 * DLL_GetNumberOfRecords() : Return number of records.
 *
 * Arguments: slist -- Pointer to type List
 * Returns  : Number of records
 */
unsigned long
DLL_GetNumberOfRecords(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   unsigned long size = (unsigned long) 0;

   RWLOCK_RLOCK_NR(&list->rwl_t);
   size = list->listsize;
   RWLOCK_UNLOCK_NR(&list->rwl_t);
   return size;
   }


/*
 * Status   : Public
 *
 * DLL_SetSearchModes() : Sets the pointer used to start a search origin
 *                        and the direction indicator.
 *
 * Arguments: slist            -- Pointer to type List
 *            origin           -- Indicates the start search pointer to use
 *            dir              -- Indicates the direction to search in
 * Returns  : DLL_NORMAL       -- Values assigned were accepted
 *            DLL_NOT_MODIFIED -- Values were not assigned--invalid type
 *                                (defaults are still in place)
 *            DLL_THR_ERROR    -- Thread lock/unlock error
 */
DLL_Return
DLL_SetSearchModes(List *slist, DLL_SrchOrigin origin, DLL_SrchDir dir)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   switch(origin)
      {
      case DLL_HEAD:
      case DLL_CURRENT:
      case DLL_TAIL:
      case DLL_ORIGIN_DEFAULT:
         break;
      default:
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NOT_MODIFIED);
      }

   switch(dir)
      {
      case DLL_DOWN:
      case DLL_UP:
      case DLL_DIRECTION_DEFAULT:
         break;
      default:
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NOT_MODIFIED);
      }

   if(origin != DLL_ORIGIN_DEFAULT)
      list->search_origin = origin;

   if(dir != DLL_DIRECTION_DEFAULT)
      list->search_dir = dir;

   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_GetSearchModes() : Returns the search modes
 *
 * Arguments: slist -- Pointer to type List
 *            ssp   -- Save structure pointer
 * Returns  : Pointer to type DLL_SearchModes
 */
DLL_SearchModes *
DLL_GetSearchModes(List *slist, DLL_SearchModes *ssp)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_RLOCK_NR(&list->rwl_t);
   ssp->search_origin = list->search_origin;
   ssp->search_dir = list->search_dir;
   RWLOCK_UNLOCK_NR(&list->rwl_t);
   return(ssp);
   }


/*
 * Status   : Public
 *
 * DLL_GetCurrentIndex() : Return the index of the current record
 *                         NOTE: The index is always referenced from
 *                         the head of the list.
 *
 * Arguments: slist -- Pointer to type List
 * Returns  : Current record's index
 */
unsigned long
DLL_GetCurrentIndex(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   size_t index = (size_t) 0;

   RWLOCK_RLOCK_NR(&list->rwl_t);
   index = list->current_index;
   RWLOCK_UNLOCK_NR(&list->rwl_t);
   return index;
   }


/********************************
 * Pointer Manipulation Functions
 */

/*
 * Status   : Public
 *
 * DLL_CurrentPointerToHead() : Moves the current pointer to
 *                              the head of the list.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_CurrentPointerToHead(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->head == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   list->current = list->head;
   list->current_index = (unsigned long) 1;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_CurrentPointerToTail() : Moves the current pointer to
 *                              the tail of the list.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_CurrentPointerToTail(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->tail == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   list->current = list->tail;
   list->current_index = list->listsize;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_IncrementCurrentPointer() : Moves the current pointer to next position.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_NOT_FOUND -- Record not found
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_IncrementCurrentPointer(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(list->current->next == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   list->current = list->current->next;
   list->current_index++;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_DecrementCurrentPointer() : Moves the current pointer to last position.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_NOT_FOUND -- Record not found
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_DecrementCurrentPointer(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(list->current->prior == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   list->current = list->current->prior;
   list->current_index--;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_StoreCurrentPointer() : Saves the current pointer to either the list
 *                             struct.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NOT_FOUND -- Record not found
 *            DLL_THR_ERROR -- Thread lock/unlock error
 *            DLL_STK_ERROR -- The stack is full
 */
DLL_Return
DLL_StoreCurrentPointer(List *slist)
   {
   List *list = _getList(slist);
   DLL_Session *session = _getSession(slist);

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   if(session->topOfStack >= session->maxStackSize)
      {
      session->topOfStack = session->maxStackSize;
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_STK_ERROR);
      }

   session->stack[session->topOfStack] = list->current;
   session->saveIndex = list->current_index;
   session->topOfStack++;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_RestoreCurrentPointer() : Loads the previously saved current pointer
 *                               from the list struct.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NOT_FOUND -- Record not found
 *            DLL_THR_ERROR -- Thread lock/unlock error
 *            DLL_STK_ERROR -- Stack underflow
 */
DLL_Return
DLL_RestoreCurrentPointer(List *slist)
   {
   List *list = _getList(slist);
   DLL_Session *session = _getSession(slist);
   size_t tos = (size_t) 0;

   RWLOCK_WLOCK(&list->rwl_t);
   tos = session->topOfStack - 1;

   /*
    * This will error if DLL_RestoreCurrentPointer() is called
    * before DLL_StoreCurrentPointer() is called.
    */
   if(session->stack[tos] == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   if(tos < (size_t) 0)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_STK_ERROR);
      }

   list->current = session->stack[tos];
   list->current_index = session->saveIndex;
   session->topOfStack--;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/***********************
 * List Update Functions
 */

/*
 * Status   : Public
 *
 * DLL_AddRecord() : Creates a new node in list with or without sorting.
 *
 * Arguments: slist         -- Pointer to type List
 *            info          -- Record to add
 *            pFun          -- Pointer to search function
 * Returns  : DLL_NORMAL    -- Node was added successfully
 *            DLL_MEM_ERROR -- Memory allocation failed
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_AddRecord(List *slist, Info *info, int (*pFun)(Info *, Info *))
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   DLL_Return ret = DLL_NORMAL;

   RWLOCK_WLOCK(&list->rwl_t);
   ret = _addRecord(list, info, pFun);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(ret);
   }


/*
 * Status   : Private
 *
 * _addRecord() : Creates a new node in list with or without sorting.
 *
 * Arguments: list          -- Pointer to type List
 *            info          -- Record to add
 *            pFun          -- Pointer to search function
 * Returns  : DLL_NORMAL    -- Node was added successfully
 *            DLL_MEM_ERROR -- Memory allocation failed
 *            DLL_THR_ERROR -- Thread lock/unlock error
 *
 * NOTE: This function is not thread safe.
 */
static DLL_Return
_addRecord(List *list, Info *info, int (*pFun)(Info *, Info *))
   {
   Node *newN, *old, *step;
   Info *newI;

   /* Allocate space for new node */
   if((newN = (Node *) malloc(sizeof(Node))) == NULL)
      return(DLL_MEM_ERROR);

   /* Allocate space for new info */
   if((newI = (Info *) malloc(list->infosize)) == NULL)
      {
      free(newN);
      return(DLL_MEM_ERROR);
      }

   /* Put new info into allocated space */
   memcpy(newI, info, list->infosize);

   /*
    * If list->head is NULL, assume we had an empty list
    * and that this is the 1st record.
    */
   if(list->head == NULL)
      {
      newN->info = newI;
      newN->next = NULL;
      newN->prior = NULL;
      list->head = newN;
      list->tail = newN;
      list->current = newN;
      list->listsize = (unsigned long) 1;
      list->current_index = (unsigned long) 1;
      list->modified = DLL_TRUE;
      return(DLL_NORMAL);
      }

   if(pFun != NULL)           /* If NULL don't do sort */
      {
      step = list->head;
      old = list->tail;

      while(step != NULL)     /* Loop through records until a match is found */
         {
         if(((*pFun)(step->info, newI)) >= 0)
            break;

         list->current_index++;
         old = step;
         step = (Node *) step->next;
         }
      }
   else
      {
      step = NULL;
      old = list->tail;
      }

   /*
    * The order of the 'if' statements below is critical and
    * cannot be changed or a no sort (NULL) situation will fail.
    */
   if(step == NULL)           /* New last record */
      {
      newN->info = newI;
      old->next = newN;
      newN->next = NULL;
      newN->prior = old;
      list->tail = newN;
      list->current = newN;
      }
   else
      if(step->prior == NULL) /* New first record */
         {
         newN->info = newI;
         newN->prior = NULL;
         newN->next = step;
         step->prior = newN;
         list->head = newN;
         list->current = newN;
         }
      else                    /* New middle record */
         {
         newN->info = newI;
         step->prior->next = newN;
         newN->next = step;
         newN->prior = step->prior;
         step->prior = newN;
         list->current = newN;
         }

   list->listsize++;
   list->current_index++;
   list->modified = DLL_TRUE;
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_InsertRecord() : Creates a new node in list above or below current
 *                      record. The new record will be current after
 *                      completion.
 *
 * Arguments: slist            -- Pointer to type List
 *            info             -- Record to add
 *            dir              -- Direction to insert (DLL_ABOVE or DLL_BELOW)
 * Returns  : DLL_NORMAL       -- Node was added successfully
 *            DLL_MEM_ERROR    -- Memory allocation failed
 *            DLL_NOT_MODIFIED -- Insert direction is invalid (not DLL_ABOVE
 *                                or DLL_BELOW)
 *            DLL_THR_ERROR    -- Thread lock/unlock error
 */
DLL_Return
DLL_InsertRecord(List *slist, Info *info, DLL_InsertDir dir)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   Node *newN;
   Info *newI;

   RWLOCK_WLOCK(&list->rwl_t);

   /* Allocate space for new node */
   if((newN = (Node *) malloc(sizeof(Node))) == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_MEM_ERROR);
      }

   /* Allocate space for new info */
   if((newI = (Info *) malloc(list->infosize)) == NULL)
      {
      free(newN);
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_MEM_ERROR);
      }

   /* Put new info into allocated space */
   memcpy(newI, info, list->infosize);

   /* If list->head is NULL, assume empty list and this is the 1st record. */
   if(list->head == NULL)
      {
      newN->info = newI;
      newN->next = NULL;
      newN->prior = NULL;
      list->head = newN;
      list->tail = newN;
      list->current = newN;
      list->listsize = (unsigned long) 1;
      list->current_index = (unsigned long) 1;
      list->modified = DLL_TRUE;
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NORMAL);
      }

   /* Decide what to do according to dir */
   switch(dir)
      {
      case DLL_ABOVE:
         newN->info = newI;
         newN->next = list->current;
         newN->prior = list->current->prior;

         /* If current is not at head */
         if(list->current->prior)
            list->current->prior->next = newN;

         list->current->prior = newN;

         /* If none above new one, set head */
         if(newN->prior == NULL)
            list->head = newN;

         list->current = newN;
         break;
      case DLL_BELOW:
         newN->info = newI;
         newN->next = list->current->next;
         newN->prior = list->current;

         /* If current is not at tail */
         if(list->current->next)
            list->current->next->prior = newN;

         list->current->next = newN;

         /* If none below new one, set tail */
         if(newN->next == NULL)
            list->tail = newN;

         list->current = newN;
         list->current_index++;
         break;
      default:
         free(newI);
         free(newN);
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NOT_MODIFIED);
      }

   list->listsize++;
   list->modified = DLL_TRUE;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_SwapRecord() : Swaps current record up or down one place in the
 *                    list. The swaped record will still be current
 *                    after completion.
 *
 * Arguments: slist            -- Pointer to type List
 *            dir              -- Direction to swap (DLL_ABOVE or DLL_BELOW)
 * Returns  : DLL_NORMAL       -- Node was swaped successfully
 *            DLL_NULL_LIST    -- list->current is NULL
 *            DLL_NOT_MODIFIED -- Swap direction not DLL_ABOVE or DLL_BELOW
 *            DLL_NOT_FOUND    -- Current record is already at end of
 *                                list indicated by dir.
 *            DLL_THR_ERROR    -- Thread lock/unlock error
 */
DLL_Return
DLL_SwapRecord(List *slist, DLL_InsertDir dir)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   Node *swap, *newPrior, *newNext;

   RWLOCK_WLOCK(&list->rwl_t);

   /* If current is NULL, can't swap it */
   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   /* Decide what to do according to dir */
   switch(dir)
      {
      case DLL_ABOVE:
         swap = list->current;

         /* current is at head */
         if(swap->prior == NULL)
            {
            RWLOCK_UNLOCK(&list->rwl_t);
            return(DLL_NOT_FOUND);
            }

         /* Save current new prior and new next */
         newPrior = swap->prior->prior;
         newNext = swap->prior;

         /* If prior node is not at head */
         if(newPrior != NULL)
            newPrior->next = swap;

         /* Set up old next record's prior node */
         if(swap->next != NULL)
            swap->next->prior = newNext;

         /* Set up new next record's next & prior nodes */
         newNext->next = swap->next;
         newNext->prior = swap;

         /* Set the current record's new next & prior node */
         swap->prior = newPrior;
         swap->next = newNext;

         /* If current is now at head, set list head */
         if(newPrior == NULL)
            list->head = swap;

         /* If current used to be at tail, set list tail */
         if(newNext->next == NULL)
            list->tail = newNext;

         list->current_index--;
         break;
      case DLL_BELOW:
         swap = list->current;

         /* current is at tail */
         if(swap->next == NULL)
            {
            RWLOCK_UNLOCK(&list->rwl_t);
            return(DLL_NOT_FOUND);
            }

         /* Save current new prior and new next */
         newPrior = swap->next;
         newNext = swap->next->next;

         /* If next node is not at tail */
         if(newNext != NULL)
            newNext->prior = swap;

         /* Set up old prior record's next node */
         if(swap->prior != NULL)
            swap->prior->next = newPrior;

         /* Set up new prior record's next & prior nodes */
         newPrior->next = swap;
         newPrior->prior = swap->prior;

         /* Set the current record's new next & prior node */
         swap->prior = newPrior;
         swap->next = newNext;

         /* If current is now at tail, set list tail */
         if(newNext == NULL)
            list->tail = swap;

         /* If current used to be at head, set list head */
         if(newPrior->prior == NULL)
            list->head = newPrior;

         list->current_index++;
         break;
      default:
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NOT_MODIFIED);
      }

   list->modified = DLL_TRUE;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_UpdateCurrentRecord() : Updates current record
 *
 * Arguments: slist         -- Pointer to type List
 *            record        -- Pointer to an Info structure in list
 * Returns  : DLL_NORMAL    -- Record updated
 *            DLL_NULL_LIST -- Empty list
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_UpdateCurrentRecord(List *slist, Info *record)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   memcpy(list->current->info, record, list->infosize);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_DeleteCurrentRecord() : Delete a record from the list.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- Record deleted
 *            DLL_NULL_LIST -- List is empty
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_DeleteCurrentRecord(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   Info *oldI;
   Node *oldN;

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   oldI = list->current->info;
   oldN = list->current;

   if(list->current == list->head)     /* current is first record */
      {
      /* A single record in a list can't do this ...next->prior */
      if(list->current->next != NULL)
         list->current->next->prior = NULL;

      list->head = list->current->next;
      list->current = list->head;
      }
   else
      if(list->current == list->tail)  /* current is last record */
         {
         list->current->prior->next = NULL;
         list->tail = list->current->prior;
         list->current = list->tail;
         list->current_index--;
         }
      else                             /* current is a middle record */
         {
         list->current->prior->next = list->current->next;
         list->current->next->prior = list->current->prior;
         list->current = list->current->next;
         }

   free(oldI);
   free(oldN);
   list->listsize--;
   list->modified = DLL_TRUE;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_DeleteRecord() : Delete a record from the list.
 *
 * Arguments: slist             -- Pointer to type List
 *            match             -- Pointer to an Info structure to match
 *                                 to list
 *            pFun              -- Pointer to search function
 * Returns  : DLL_NORMAL        -- Record found
 *            DLL_NULL_LIST     -- Empty list
 *            DLL_NOT_FOUND     -- Record not found
 *            DLL_NULL_FUNCTION -- pFun is NULL
 *            DLL_THR_ERROR     -- Thread error
 */

DLL_Return
DLL_DeleteRecord(List *slist, Info *match, int (*pFun)(Info *, Info *))
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   unsigned long save;
   Node *step;
   Node *oldN;
   Info *oldI;
   DLL_SrchDir dir;

   RWLOCK_WLOCK(&list->rwl_t);

   if(pFun == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_FUNCTION);
      }

   save = list->current_index;

   switch(list->search_origin)
      {
      case DLL_CURRENT:
         step = list->current;
         dir = list->search_dir;
         break;
      case DLL_TAIL:
         step = list->tail;
         list->search_dir = dir = DLL_UP;
         list->current_index = list->listsize;
         break;
      case DLL_HEAD:
      default:
         list->search_origin = DLL_HEAD;
         step = list->head;
         list->search_dir = dir = DLL_DOWN;
         list->current_index = (unsigned long) 1 ;
      }

   if(step == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   while(step != NULL)
      {
      if(((*pFun)(step->info, match)) == 0)
         {
         /* We have found the offending record, proceeding to delete it */
         oldI = step->info;
         oldN = step;

         if(step == list->head)     /* current is first record */
            {
            /* A single record in a list can't do this ...next->prior */
            if(step->next != NULL)
               step->next->prior = NULL;

            list->head = step->next;
            step = list->head;
            }
         else
            if(step == list->tail)  /* current is last record */
               {
               step->prior->next = NULL;
               list->tail = step->prior;
               step = list->tail;
               list->current_index--;
               }
            else                    /* current is a middle record */
               {
               step->prior->next = step->next;
               step->next->prior = step->prior;
               step = step->next;
               }

         free(oldI);
         free(oldN);
         list->listsize--;
         list->modified = DLL_TRUE;
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NORMAL);
         }

      step = (dir == DLL_DOWN) ? (Node *) step->next : (Node *) step->prior;
      list->current_index += (dir == DLL_DOWN)
         ? (unsigned long) 1
         : (unsigned long) -1;
      }

   list->current_index = save;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NOT_FOUND);
   }


/*
 * Status   : Public
 *
 * DLL_DeleteEntireList() : Delete the entire list.
 *
 * Arguments: slist         -- Pointer to type List
 * Returns  : DLL_NORMAL    -- List deleted
 *            DLL_NULL_LIST -- List is empty
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_DeleteEntireList(List *slist)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_WLOCK(&list->rwl_t);

   if(list->head == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   _deleteEntireList(list);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Private
 *
 * _deleteEntireList() : Delete the entire list.
 *
 * Arguments: list -- Pointer to type List
 *
 * Returns  : None
 *
 * NOTE: This function is not thread safe.
 */
static void
_deleteEntireList(List *list)
   {
   Info *oldI;
   Node *oldN;

   do
      {
      oldI = list->head->info;
      oldN = list->head;
      list->head = list->head->next;
      free(oldI);
      free(oldN);
      }
   while(list->head != NULL);

   list->head = NULL;
   list->tail = NULL;
   list->current = NULL;
   list->current_index = (unsigned long) 0;
   list->listsize = (unsigned long) 0;
   list->modified = DLL_TRUE;
   list->search_origin = DLL_HEAD;
   list->search_dir = DLL_DOWN;
   /* spin through all thread structures and initialize */
   }


/******************
 * Search Functions
 */

/*
 * Status   : Public
 *
 * DLL_FindRecord() : Find a record in list with search criteria
 *
 * Arguments: slist             -- Pointer to type List
 *            record            -- Pointer to an Info structure in list
 *            match             -- Pointer to an Info structure to match
 *                                 to list
 *            pFun              -- Pointer to search function
 * Returns  : DLL_NORMAL        -- Record found
 *            DLL_NULL_LIST     -- Empty list
 *            DLL_NOT_FOUND     -- Record not found
 *            DLL_NULL_FUNCTION -- pFun is NULL
 *            DLL_THR_ERROR     -- Thread lock/unlock error
 */
DLL_Return
DLL_FindRecord(List *slist, Info *record, Info *match,
 int (*pFun)(Info *, Info *))
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   unsigned long save;
   Node *step;
   DLL_SrchDir dir;

   RWLOCK_RLOCK(&list->rwl_t);

   if(pFun == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_FUNCTION);
      }

   save = list->current_index;

   switch(list->search_origin)
      {
      case DLL_CURRENT:
         step = list->current;
         dir = list->search_dir;
         break;
      case DLL_TAIL:
         step = list->tail;
         list->search_dir = dir = DLL_UP;
         list->current_index = list->listsize;
         break;
      case DLL_HEAD:
      default:
         list->search_origin = DLL_HEAD;
         step = list->head;
         list->search_dir = dir = DLL_DOWN;
         list->current_index = (unsigned long) 1;
      }

   if(step == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   while(step != NULL)
      {
      if(((*pFun)(step->info, match)) == 0)
         {
         memcpy(record, step->info, list->infosize);
         list->current = step;
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NORMAL);
         }

      step = (dir == DLL_DOWN) ? (Node *) step->next : (Node *) step->prior;
      list->current_index += (dir == DLL_DOWN)
         ? (unsigned long) 1
         : (unsigned long) -1;
      }

   list->current_index = save;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NOT_FOUND);
   }


/*
 * Status   : Public
 *
 * DLL_FindNthRecord() : Returns the Nth record in the list based on the
 *                       setting of list->search_origin and list->search_dir.
 *
 * NOTE: The Nth record is found based on the ordinant numbering system, in
 *       other words the current record is 0 (zero) so a skip value of 5 would
 *       return the 6th not the 5th record.  Just think of C array indexing.
 *
 * Arguments: slist         -- Pointer to type List
 *            record        -- Record to hold return data
 *            skip          -- Number of records to skip
 * Returns  : DLL_NORMAL    -- Node was found successfully
 *            DLL_NULL_LIST -- list->current is NULL
 *            DLL_NOT_FOUND -- Index value is too large or wrong dir value
 *                             (current record index remains unchanged).
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_FindNthRecord(List *slist, Info *record, unsigned long skip)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   unsigned long save;
   Node *step;
   DLL_SrchDir dir;
   register int nCnt;

   RWLOCK_RLOCK(&list->rwl_t);
   save = list->current_index;

   switch(list->search_origin)
      {
      case DLL_CURRENT:
         step = list->current;
         dir = list->search_dir;
         break;
      case DLL_TAIL:
         step = list->tail;
         list->search_dir = dir = DLL_UP;
         list->current_index = list->listsize;
         break;
      case DLL_HEAD:
      default:
         list->search_origin = DLL_HEAD;
         step = list->head;
         list->search_dir = dir = DLL_DOWN;
         list->current_index = (unsigned long) 1;
      }

   if(step == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(skip <= 0 || ((dir == DLL_DOWN)
    ? (list->listsize < (list->current_index + skip))
    : (list->current_index <= skip)))
      {
      list->current_index = save;
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   switch(dir)
      {
      case DLL_DOWN:
         for(nCnt = 0; nCnt < skip && step->next != NULL; nCnt++)
            step = step->next;

         break;
      case DLL_UP:
         for(nCnt = 0; nCnt < skip && step->prior != NULL; nCnt++)
            step = step->prior;

         break;
      default:
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_NOT_FOUND);
      }

   memcpy(record, step->info, list->infosize);
   list->current = step;
   list->current_index += (dir == DLL_DOWN)
      ? ((unsigned long) 1 * skip)
      : ((unsigned long) -1 * skip);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_GetCurrentRecord() : Gets the record pointed to by current
 *
 * Arguments: slist         -- Pointer to type List
 *            record        -- Pointer to a pointer to an Info structure
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_GetCurrentRecord(List *slist, Info *record)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_RLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   memcpy(record, list->current->info, list->infosize);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_GetPriorRecord() : Gets the record pointed to by current->prior
 *
 * Arguments: slist         -- Pointer to type List
 *            record        -- Pointer to a pointer to an Info structure
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 *            DLL_NOT_FOUND -- Beginning of list
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_GetPriorRecord(List *slist, Info *record)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_RLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(list->current->prior == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   list->current = list->current->prior;
   memcpy(record, list->current->info, list->infosize);
   list->current_index--;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_GetNextRecord() : Gets the record pointed to by current->next
 *
 * Arguments: slist         -- Pointer to type List
 *            record        -- Pointer to a pointer to an Info structure
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 *            DLL_NOT_FOUND -- End of list
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_GetNextRecord(List *slist, Info *record)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */

   RWLOCK_RLOCK(&list->rwl_t);

   if(list->current == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(list->current->next == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_FOUND);
      }

   list->current = list->current->next;
   memcpy(record, list->current->info, list->infosize);
   list->current_index++;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/************************
 * Input/Output Functions
 */

/*
 * Status   : Public
 *
 * DLL_SaveList() : Save list to disk
 *
 * Arguments: slist            -- Pointer to type List
 *            path             -- Pointer to path and filename
 * Return   : DLL_NORMAL       -- File written successfully
 *            DLL_NULL_LIST    -- List is empty
 *            DLL_OPEN_ERROR   -- File open error
 *            DLL_WRITE_ERROR  -- File write error
 *            DLL_NOT_MODIFIED -- Unmodified list no save was done
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_SaveList(List *slist, const char *path)
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   Node *step;
   FILE *fp;

   RWLOCK_RLOCK(&list->rwl_t);

   if(list->head == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NULL_LIST);
      }

   if(list->modified == DLL_FALSE)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_NOT_MODIFIED);
      }

   if((fp = fopen(path, "wb")) == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_OPEN_ERROR);
      }

   step = list->head;

   while(step != NULL)
      {
      if(fwrite(step->info, 1, list->infosize, fp) != list->infosize)
         {
         fclose(fp);
         RWLOCK_UNLOCK(&list->rwl_t);
         return(DLL_WRITE_ERROR);
         }

      step = (Node *) step->next;
      }

   fclose(fp);
   list->modified = DLL_FALSE;
   RWLOCK_UNLOCK(&list->rwl_t);
   return(DLL_NORMAL);
   }


/*
 * Status   : Public
 *
 * DLL_LoadList() : Load list to disk
 *
 * Arguments: slist          -- Pointer to type List
 *            path           -- Pointer to path and filename
 *            pFun           -- Pointer to search function
 * Return   : DLL_NORMAL     -- File written successfully
 *            DLL_MEM_ERROR  -- Memory allocation failed
 *            DLL_OPEN_ERROR -- File open error
 *            DLL_READ_ERROR -- File read error
 *            DLL_THR_ERROR -- Thread lock/unlock error
 */
DLL_Return
DLL_LoadList(List *slist, const char *path, int (*pFun)(Info *, Info *))
   {
   List *list = _getList(slist);
/*     DLL_Session *session = _getSession(slist); */
   Info *set;
   FILE *fp;
   DLL_Return ExitCode;

   RWLOCK_WLOCK(&list->rwl_t);

   if((fp = fopen(path, "rb")) == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_OPEN_ERROR);
      }

   if(list->head != NULL)
      {
      _deleteEntireList(list);
      return(DLL_MEM_ERROR);
      }

   list->head = list->tail = NULL;

   if((set = (Info *) malloc(list->infosize)) == NULL)
      {
      RWLOCK_UNLOCK(&list->rwl_t);
      return(DLL_MEM_ERROR);
      }

   for(;;)
      {
      if(fread(set, 1, list->infosize, fp) != list->infosize)
         {
         if(feof(fp))
            ExitCode = DLL_NORMAL;
         else
            ExitCode = DLL_READ_ERROR;

         break;
         }

      if((ExitCode = _addRecord(list, set, pFun)) == DLL_MEM_ERROR)
         break;
      }

   if(!pFun)
      list->modified = DLL_FALSE;

   free(set);
   fclose(fp);
   RWLOCK_UNLOCK(&list->rwl_t);
   return(ExitCode);
   }
