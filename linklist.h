/*
 * linklist.h : Public header for applications
 *
 * Copyright (c) 1996-2007 Carl J. Nobile
 * Created: December 26, 1996
 *
 * $Author$
 * $Date$
 * $Revision$
 *
 * Note on the copyright licenses.
 * -------------------------------
 * This Double Link List API is covered under either the Artistic or the
 * Eclipse license. The Eclipse license is more business friendly so I
 * have added it. Retaining the Artistic license prevents anybody that
 * preferred it from complaining.
 *
 **************************************************************************
 * Copyright (c) 2007 Carl J. Nobile.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Carl J. Nobile - initial API and implementation
 **************************************************************************
 */

#ifndef  _LINKLIST_H
#define  _LINKLIST_H

#ifdef __cplusplus
extern "C"
{
#endif

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
   DLL_NORMAL,              /* normal operation */
   DLL_MEM_ERROR,           /* malloc error */
   DLL_ZERO_INFO,           /* sizeof(Info) is zero */
   DLL_NULL_LIST,           /* List is NULL */
   DLL_NOT_FOUND,           /* Record not found */
   DLL_OPEN_ERROR,          /* Cannot open file */
   DLL_WRITE_ERROR,         /* File write error */
   DLL_READ_ERROR,          /* File read error */
   DLL_NOT_MODIFIED,        /* Unmodified list */
   DLL_NULL_FUNCTION        /* NULL function pointer */
   } DLL_Return;

typedef enum
   {
   DLL_ORIGIN_DEFAULT,      /* Use current origin setting */
   DLL_HEAD,                /* Set origin to head pointer */
   DLL_CURRENT,             /* Set origin to current pointer */
   DLL_TAIL                 /* Set origin to tail pointer */
   } DLL_SrchOrigin;

typedef enum
   {
   DLL_DIRECTION_DEFAULT,   /* Use current direction setting */
   DLL_DOWN,                /* Set direction to down */
   DLL_UP                   /* Set direction to up */
   } DLL_SrchDir;

typedef enum
   {
   DLL_INSERT_DEFAULT,      /* Use current insert setting */
   DLL_ABOVE,               /* Insert new record ABOVE current record */
   DLL_BELOW                /* Insert new record BELOW current record */
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
#define VERSION   "Ver: 1.2.0"
#define VERDATE   __DATE__
#define CREDITS   "-------------------------------\n" \
                  "Developed by:  Carl J. Nobile\n" \
                  "Contributions: Charlie Buckheit\n" \
                  "               Graham Inchley\n" \
                  "               Wai-Sun Chia\n" \
                  "               Mark M. Feenstra\n"

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
   Node           *head;
   Node           *tail;
   Node           *current;
   Node           *saved;
   size_t         infosize;
   unsigned long  listsize;
   unsigned long  current_index;
   unsigned long  save_index;
   DLL_Boolean    modified;
   DLL_SrchOrigin search_origin;
   DLL_SrchDir    search_dir;
   } List;
#else
typedef struct list List;
typedef struct node Node;
#endif   /* _DLL_MAIN_C || DEBUG */

typedef struct search_modes
   {
   DLL_SrchOrigin search_origin;
   DLL_SrchDir    search_dir;
   } DLL_SearchModes;

/*
 * Prototypes
 */
List *DLL_CreateList(List **list);
void DLL_DestroyList(List **list);
char *DLL_Version(void);
DLL_Boolean DLL_IsListEmpty(List *list);
DLL_Boolean DLL_IsListFull(List *list);
DLL_Return DLL_AddRecord(List *list, Info *info,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_CurrentPointerToHead(List *list);
DLL_Return DLL_CurrentPointerToTail(List *list);
DLL_Return DLL_DecrementCurrentPointer(List *list);
DLL_Return DLL_DeleteCurrentRecord(List *list);
DLL_Return DLL_DeleteEntireList(List *list);
DLL_Return DLL_FindNthRecord(List *list, Info *record, unsigned long nRec);
DLL_Return DLL_FindRecord(List *list, Info *record, Info *match,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_GetCurrentRecord(List *list, Info *record);
DLL_Return DLL_GetNextRecord(List *list, Info *record);
DLL_Return DLL_GetPriorRecord(List *list, Info *record);
DLL_Return DLL_InitializeList(List *list, size_t infosize);
DLL_Return DLL_IncrementCurrentPointer(List *list);
DLL_Return DLL_InsertRecord(List *list, Info *info, DLL_InsertDir dir);
DLL_Return DLL_LoadList(List *list, const char *path,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_RestoreCurrentPointer(List *list);
DLL_Return DLL_SaveList(List *list, const char *path);
DLL_Return DLL_SetSearchModes(List *list, DLL_SrchOrigin origin,
 DLL_SrchDir dir);
DLL_Return DLL_StoreCurrentPointer(List *list);
DLL_Return DLL_SwapRecord(List *list, DLL_InsertDir dir);
DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);
DLL_SearchModes *DLL_GetSearchModes(List *list, DLL_SearchModes *ssp);
unsigned long DLL_GetCurrentIndex(List *list);
unsigned long DLL_GetNumberOfRecords(List *list);

#ifdef __cplusplus
}
#endif

#endif   /* _LINKLIST_H */
