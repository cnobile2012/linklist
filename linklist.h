/*
 * linklist.h : Public header for applications
 *
 * Copyright (c) 1996-1998 Carl J. Nobile
 * Created: December 26, 1996
 * Updated: 11/04/98
 */

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
	DLL_NORMAL,					/* normal operation */
	DLL_MEM_ERROR,				/* malloc error */
	DLL_ZERO_INFO,				/* sizeof(Info) is zero */
	DLL_NULL_LIST,				/* List is NULL */
	DLL_NOT_FOUND,				/* Record not found */
	DLL_OPEN_ERROR,			/* Cannot open file */
	DLL_WRITE_ERROR,			/* File write error */
	DLL_READ_ERROR,			/* File read error */
	DLL_NOT_MODIFIED,			/* Unmodified list */
	DLL_NULL_FUNCTION			/* NULL function pointer */
	} DLL_Return;

typedef enum
	{
	DLL_ORIGIN_DEFAULT,		/* Use current origin setting */
	DLL_HEAD,					/* Set origin to head pointer */
	DLL_CURRENT,				/* Set origin to current pointer */
	DLL_TAIL						/* Set origin to tail pointer */
	} DLL_SrchOrigin;

typedef enum
	{
	DLL_DIRECTION_DEFAULT,	/* Use current direction setting */
	DLL_DOWN,					/* Set direction to down */
	DLL_UP						/* Set direction to up */
	} DLL_SrchDir;

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

typedef struct list List;
typedef void Info;
 
typedef struct search_modes
	{
	DLL_SrchOrigin search_origin;
	DLL_SrchDir    search_dir;
	} DLL_SearchModes;

/*
 * Prototypes
 */
List *DLL_CreateList(List **name);
void DLL_DestroyList(List **name);
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
DLL_Return DLL_FindRecord(List *list, Info *record, Info *match,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_GetCurrentRecord(List *list, Info *record);
DLL_Return DLL_GetNextRecord(List *list, Info *record);
DLL_Return DLL_GetPriorRecord(List *list, Info *record);
DLL_Return DLL_InitializeList(List *list, size_t infosize);
DLL_Return DLL_IncrementCurrentPointer(List *list);
DLL_Return DLL_LoadList(List *list, const char *path,
 int (*pFun)(Info *, Info *));
DLL_Return DLL_RestoreCurrentPointer(List *list);
DLL_Return DLL_SaveList(List *list, const char *path);
DLL_Return DLL_SetSearchModes(List *list, DLL_SrchOrigin origin, DLL_SrchDir dir);
DLL_Return DLL_StoreCurrentPointer(List *list);
DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record);
DLL_SearchModes *DLL_GetSearchModes(List *list);
unsigned long DLL_GetNumberOfRecords(List *list);
