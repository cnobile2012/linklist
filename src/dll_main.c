/*
 * dll_main.c : An API for a double linked list.
 *
 * Copyright (c) 1996-2012 Carl J. Nobile
 * Created: December 22, 1996
 * Updated: 12/24/2011
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
 * Copyright (c) 2012 Carl J. Nobile.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Carl J. Nobile - initial API and implementation
 **************************************************************************
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define  _DLL_MAIN_C
#include "linklist.h"

/**************************
 * Initialization Functions
 */

/*
 * DLL_CreateList() : Creates a structure of type List
 *
 * Status   : Public
 *
 * Arguments: list -- Pointer to a pointer to a name of a structure to create.
 *
 * Returns  : Pointer to created structure
 *            NULL if unsuccessful
 */
List *DLL_CreateList(List **list)
    {
    if((*list = (List *) malloc(_getListSize())) == NULL)
        return(NULL);

    return(*list);
    }


/*
 * DLL_DestroyList() : Destroys Info, Node, and List structures
 *
 * Status   : Public
 *
 * Arguments: list -- Pointer to a pointer to a name of a structure to destroy.
 *
 * Returns  : void
 */
void DLL_DestroyList(List **list)
    {
    if(*list == NULL)
        return;

    DLL_DeleteEntireList(*list);
    free(*list);
    *list = NULL;
    }


/*
 * DLL_InitializeList() : Initializes double link list
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            infosize      -- Size of user Info
 *
 * Returns  : DLL_NORMAL    -- Initialization was done successfully
 *            DLL_ZERO_INFO -- sizeof(Info) is zero
 *            DLL_NULL_LIST -- Info is NULL
 */
DLL_Return DLL_InitializeList(List *list, size_t infosize)
    {
    if(infosize == (size_t) 0)
        return(DLL_ZERO_INFO);

    if(list == NULL)
        return(DLL_NULL_LIST);

    _initializeList(list, infosize);
    /*_printList(list);*/
    return(DLL_NORMAL);
    }


/****************************
 * Status and State Functions
 */

/*
 * DLL_Version() : Returns a pointer to version information
 *
 * Status   : Public
 *
 * Arguments: void
 *
 * Return   : char * -- Pointer to version info
 */
char *DLL_Version(void)
    {
    if(version == NULL)
        {
        int size = sizeof(VERSION) + sizeof(VERDATE) + sizeof(CREDITS) + 4;

        if((version = (char *) malloc(size)) != NULL)
            {
            strcpy(version, VERSION);
            strcat(version, "  ");
            strcat(version, VERDATE);
            strcat(version, "\n");
            strcat(version, CREDITS);
            strcat(version, "\n");
            }
        }

    return(version);
    }


/*
 * DLL_IsListEmpty() : Checks for an empty list
 *
 * Status   : Public
 *
 * Arguments: list      -- Pointer to type List
 *
 * Returns  : DLL_TRUE  -- List is empty
 *            DLL_FALSE -- List has items in it
 */
DLL_Boolean DLL_IsListEmpty(List *list)
    {
    if(list->head == NULL || list->tail == NULL)
        return(DLL_TRUE);

    return(DLL_FALSE);
    }


/*
 * DLL_IsListFull() : Checks for an empty list
 *
 * Status   : Public
 *
 * Arguments: list      -- Pointer to type List
 *
 * Returns  : DLL_TRUE  -- List is full (memory dependent)
 *            DLL_FALSE -- List is empty or partially full
 */
DLL_Boolean DLL_IsListFull(List *list)
    {
    Node *newN;
    Info *newI;

    if((newN = (Node *) malloc(sizeof(Node))) == NULL)
        return(DLL_TRUE);

    if((newI = (Info *) malloc(list->infosize)) == NULL)
        {
        free(newN);
        return(DLL_TRUE);
        }

    free(newN);
    free(newI);
    return(DLL_FALSE);
    }


/*
 * DLL_GetNumberOfRecords() : Return number of records.
 *
 * Status   : Public
 *
 * Arguments: list -- Pointer to type List
 *
 * Returns  : Number of records in list
 */
unsigned long DLL_GetNumberOfRecords(List *list)
    {
    return list->listsize;
    }


/*
 * DLL_SetSearchModes() : Sets the pointer used to start a search origin
 *                        and the direction indicator.
 *
 * Status   : Public
 *
 * Arguments: list             -- Pointer to type List
 *            origin           -- Indicates the start search pointer to use
 *            dir              -- Indicates the direction to search in
 *
 * Returns  : DLL_NORMAL       -- Values assigned were accepted
 *            DLL_NOT_MODIFIED -- Values were not assigned--invalid type
 *                                (previous values are still in place)
 */
DLL_Return DLL_SetSearchModes(List *list, DLL_SrchOrigin origin,
  DLL_SrchDir dir)
    {
    switch(origin)
        {
        case DLL_HEAD:
        case DLL_CURRENT:
        case DLL_TAIL:
        case DLL_ORIGIN_DEFAULT:
            break;
        default:
            return(DLL_NOT_MODIFIED);
        }

    switch(dir)
        {
        case DLL_DOWN:
        case DLL_UP:
        case DLL_DIRECTION_DEFAULT:
            break;
        default:
            return(DLL_NOT_MODIFIED);
        }

    if(origin != DLL_ORIGIN_DEFAULT)
        list->search_origin = origin;

    if(dir != DLL_DIRECTION_DEFAULT)
        list->search_dir = dir;

    return(DLL_NORMAL);
    }


/*
 * DLL_GetSearchModes() : Returns the search modes
 *
 * Status   : Public
 *
 * Arguments: list -- Pointer to type List
 *            ssp  -- Save structure pointer
 *
 * Returns  : Pointer to type DLL_SearchModes
 */
DLL_SearchModes *DLL_GetSearchModes(List *list, DLL_SearchModes *ssp)
    {
    ssp->search_origin = list->search_origin;
    ssp->search_dir = list->search_dir;
    return(ssp);
    }


/*
 * DLL_GetCurrentIndex() : Return the index of the current record
 *
 * Note: The index is always referenced from the head of the list.
 *
 * Status : Public
 *
 * Arguments: list -- Pointer to type List
 *
 * Returns  : Current record's index
 */
unsigned long DLL_GetCurrentIndex(List *list)
    {
    return list->current_index;
    }


/********************************
 * Pointer Manipulation Functions
 */

/*
 * DLL_CurrentPointerToHead() : Moves the current pointer to
 *                              the head of the list.
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 */
DLL_Return DLL_CurrentPointerToHead(List *list)
    {
    if(list->head == NULL)
        return(DLL_NULL_LIST);

    list->current = list->head;
    list->current_index = 1L;
    return(DLL_NORMAL);
    }


/*
 * DLL_CurrentPointerToTail() : Moves the current pointer to
 *                              the tail of the list.
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 */
DLL_Return DLL_CurrentPointerToTail(List *list)
    {
    if(list->tail == NULL)
        return(DLL_NULL_LIST);

    list->current = list->tail;
    list->current_index = list->listsize;
    return(DLL_NORMAL);
    }


/*
 * DLL_IncrementCurrentPointer() : Moves the current pointer to next position.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_NOT_FOUND -- Record not found
 */
DLL_Return DLL_IncrementCurrentPointer(List *list)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    if(list->current->next == NULL)
        return(DLL_NOT_FOUND);

    list->current = list->current->next;
    list->current_index++;
    return(DLL_NORMAL);
    }


/*
 * DLL_DecrementCurrentPointer() : Moves the current pointer to last position.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NULL_LIST -- Empty list
 *            DLL_NOT_FOUND -- Record not found
 */
DLL_Return DLL_DecrementCurrentPointer(List *list)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    if(list->current->prior == NULL)
        return(DLL_NOT_FOUND);

    list->current = list->current->prior;
    list->current_index--;
    return(DLL_NORMAL);
    }


/*
 * DLL_StoreCurrentPointer() : Saves the current pointer.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NOT_FOUND -- Record not found
 */
DLL_Return DLL_StoreCurrentPointer(List *list)
    {
    if(list->current == NULL)
        return(DLL_NOT_FOUND);

    list->saved = list->current;
    list->save_index = list->current_index;
    return(DLL_NORMAL);
    }


/*
 * DLL_RestoreCurrentPointer() : Loads the previously saved current pointer.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record found
 *            DLL_NOT_FOUND -- Record not found
 */
DLL_Return DLL_RestoreCurrentPointer(List *list)
    {
    if(list->saved == NULL)
        return(DLL_NOT_FOUND);

    list->current = list->saved;
    list->saved = NULL;
    list->current_index = list->save_index;
    return(DLL_NORMAL);
    }


/***********************
 * List Update Functions
 */

/*
 * DLL_AddRecord() : Creates a new node in list with or without sorting.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            info          -- Pointer to record to add
 *            pFun          -- Pointer to search function
 *
 * Returns  : DLL_NORMAL    -- Node was added successfully
 *            DLL_MEM_ERROR -- Memory allocation failed
 */
DLL_Return DLL_AddRecord(List *list, Info *info, int (*pFun)(Info *, Info *))
    {
    Node *newN = NULL, *old, *step;
    Info *newI = NULL;
    DLL_Return exitCode;

    if((exitCode = _createNewRecord(list, info, &newN, &newI)) != DLL_CONTINUE)
        return(exitCode);

    if(pFun != NULL) /* If NULL don't do sort */
        {
        step = list->head;
        old = list->tail;
        list->current_index = 1L;

        while(step != NULL) /* Loop through records until a match is found. */
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
        /* Will always be last record. */
        step = NULL;
        old = list->tail;
        list->current_index = list->listsize + 1;
        }

    /*
     * The order of the 'if' statements below is critical and
     * cannot be changed or a no sort (NULL) situation will fail.
     */
    if(step == NULL) /* New last record */
        {
        /*printf("New last record.\n");*/
        newN->info = newI;
        old->next = newN;
        newN->next = NULL;
        newN->prior = old;
        list->tail = newN;
        list->current = newN;
        }
    else if(step->prior == NULL) /* New first record */
        {
        /*printf("New first record.\n");*/
        newN->info = newI;
        newN->prior = NULL;
        newN->next = step;
        step->prior = newN;
        list->head = newN;
        list->current = newN;
        }
    else /* New middle record */
        {
        /*printf("New middle record.\n");*/
        newN->info = newI;
        step->prior->next = newN;
        newN->next = step;
        newN->prior = step->prior;
        step->prior = newN;
        list->current = newN;
        }

    list->listsize++;
    list->modified = DLL_TRUE;
    return(DLL_NORMAL);
    }


/*
 * DLL_InsertRecord() : Creates a new node in list above or below current
 *                      record. The new record will be current after completion.
 *
 * Status   : Public
 *
 * Arguments: list             -- Pointer to type List
 *            info             -- Record to add
 *            dir              -- Direction to insert, can be DLL_ABOVE
 *                                (toward head) or DLL_BELOW (toward tail)
 *
 * Returns  : DLL_NORMAL       -- Node was added successfully
 *            DLL_MEM_ERROR    -- Memory allocation failed
 *            DLL_NOT_MODIFIED -- Insert direction is invalid (not DLL_ABOVE
 *                                or DLL_BELOW)
 */
DLL_Return DLL_InsertRecord(List *list, Info *info, DLL_InsertDir dir)
    {
    Node *newN = NULL;
    Info *newI = NULL;
    DLL_Return retval;

    if((retval = _createNewRecord(list, info, &newN, &newI)) != DLL_CONTINUE)
        return retval;

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
            return(DLL_NOT_MODIFIED);
            break;
        }

    list->listsize++;
    list->modified = DLL_TRUE;
    return(DLL_NORMAL);
    }


/*
 * DLL_SwapRecord() : Swaps current record up or down one place in the
 *                    list. The swapped record will still be current
 *                    after completion.
 *
 * Status   : Public
 *
 * Arguments: list             -- Pointer to type List
 *            dir              --  Direction to swap, can be DLL_ABOVE
 *                                 (toward head) or DLL_BELOW (toward tail)
 *
 * Returns  : DLL_NORMAL       -- Node was swapped successfully
 *            DLL_NULL_LIST    -- list->current is NULL
 *            DLL_NOT_MODIFIED -- Swap direction not DLL_ABOVE or DLL_BELOW
 *            DLL_NOT_FOUND    -- Current record is already at end of
 *                                list indicated by dir.
 */
DLL_Return DLL_SwapRecord(List *list, DLL_InsertDir dir)
    {
    Node *swap, *newPrior, *newNext;

    /* If current is NULL, can't swap it */
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    /* Decide what to do according to dir */
    switch(dir)
        {
        case DLL_ABOVE:
            swap = list->current;

            /* current is at head */
            if(swap->prior == NULL)
                return(DLL_NOT_FOUND);

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
                return(DLL_NOT_FOUND);

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
            return(DLL_NOT_MODIFIED);
            break;
        }

    list->modified = DLL_TRUE;
    return(DLL_NORMAL);
    }


/*
 * DLL_UpdateCurrentRecord() : Updates current record
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            record        -- Pointer to an Info structure in list
 *
 * Returns  : DLL_NORMAL    -- Record updated
 *            DLL_NULL_LIST -- Empty list
 */
DLL_Return DLL_UpdateCurrentRecord(List *list, Info *record)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    memcpy(list->current->info, record, list->infosize);
    return(DLL_NORMAL);
    }


/*
 * DLL_DeleteCurrentRecord() : Delete a record from the list. This removes the
 *                             Node and Info objects.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- Record deleted
 *            DLL_NULL_LIST -- List is empty
 */
DLL_Return DLL_DeleteCurrentRecord(List *list)
    {
    Info *oldI;
    Node *oldN;

    if(list->current == NULL)
        return(DLL_NULL_LIST);

    oldI = list->current->info;
    oldN = list->current;

    if(list->current == list->head) /* current is first record */
        {
        /* A single record in a list can't do this ...next->prior */
        if(list->current->next != NULL)
            list->current->next->prior = NULL;

        list->head = list->current->next;
        list->current = list->head;
        }
    else
        if(list->current == list->tail) /* current is last record */
            {
            list->current->prior->next = NULL;
            list->tail = list->current->prior;
            list->current = list->tail;
            list->current_index--;
            }
        else /* current is a middle record */
            {
            list->current->prior->next = list->current->next;
            list->current->next->prior = list->current->prior;
            list->current = list->current->next;
            }

    free(oldI);
    free(oldN);
    list->listsize--;
    list->modified = DLL_TRUE;
    return(DLL_NORMAL);
    }


/*
 * DLL_DeleteEntireList() : Deletes all the Node structures from the list then
 *                          reinitializes the control List structure for
 *                          continued use.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *
 * Returns  : DLL_NORMAL    -- List deleted
 *            DLL_NULL_LIST -- List is empty
 */
DLL_Return DLL_DeleteEntireList(List *list)
    {
    Info *oldI;
    Node *oldN;

    if(list->head == NULL)
        return(DLL_NULL_LIST);

    do
        {
        oldI = list->head->info;
        oldN = list->head;
        list->head = list->head->next;
        free(oldI);
        free(oldN);
        }
    while(list->head != NULL);

    _initializeList(list, 0L);
    return(DLL_NORMAL);
    }


/********************************
 * Search and Retrieval Functions
 */

/*
 * DLL_FindRecord() : Find a record in list with search criteria.
 *
 * Status   : Public
 *
 * Arguments: list              -- Pointer to type List
 *            record            -- Pointer to an Info structure in list
 *            match             -- Pointer to an Info structure to match to
 *                                 Node in list
 *            pFun              -- Pointer to search function
 *
 * Returns  : DLL_NORMAL        -- Record found
 *            DLL_NULL_LIST     -- Empty list
 *            DLL_NOT_FOUND     -- Record not found
 *            DLL_NULL_FUNCTION -- pFun is NULL
 */
DLL_Return DLL_FindRecord(List *list, Info *record, Info *match,
  int (*pFun)(Info *, Info *))
    {
    unsigned long save;
    Node *step;
    DLL_SrchDir dir;

    if(pFun == NULL)
        return(DLL_NULL_FUNCTION);

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
            list->current_index = 1L;
        }

    if(step == NULL)
        return(DLL_NULL_LIST);

    while(step != NULL)
        {
        if(((*pFun)(step->info, match)) == 0)
            {
            memcpy(record, step->info, list->infosize);
            list->current = step;
            return(DLL_NORMAL);
            }

        step = (dir == DLL_DOWN) ? (Node *) step->next : (Node *) step->prior;
        list->current_index += (dir == DLL_DOWN) ? 1 : -1;
        }

    list->current_index = save;
    return(DLL_NOT_FOUND);
    }


/*
 * DLL_FindNthRecord() : Returns the Nth record in the list based on the
 *                       setting of list->search_origin and list->search_dir.
 *
 * Note: The Nth record is found based on the ordinal numbering system, in
 *       other words if the current record is 1 then a skip value of 5 would
 *       return the 6th not the 5th record.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            record        -- Record to hold return data
 *            skip          -- Number of records to skip
 *                             (Always a positive number)
 *
 * Returns  : DLL_NORMAL    -- Node was found successfully
 *            DLL_NULL_LIST -- list->current is NULL
 *            DLL_NOT_FOUND -- Skip value is too large, too small or wrong dir
 *                             value (current index remains unchanged)
 */
DLL_Return DLL_FindNthRecord(List *list, Info *record, unsigned long skip)
    {
    unsigned long save;
    Node *step;
    DLL_SrchDir dir;
    register int nCnt;

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
            list->current_index = 1L;
        }

    if(step == NULL)
        return(DLL_NULL_LIST);

    if(skip <= 0 || ((dir == DLL_DOWN)
        ? (list->listsize < (list->current_index + skip))
        : (list->current_index <= skip)))
        {
        list->current_index = save;
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
            return(DLL_NOT_FOUND);
        }

    memcpy(record, step->info, list->infosize);
    list->current = step;
    list->current_index += (dir == DLL_DOWN) ? (1 * skip) : (-1 * skip);
    return(DLL_NORMAL);
    }


/*
 * DLL_GetCurrentRecord() : Get the current record.
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            record        -- Pointer to an Info structure
 *
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 */
DLL_Return DLL_GetCurrentRecord(List *list, Info *record)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    memcpy(record, list->current->info, list->infosize);
    return(DLL_NORMAL);
    }


/*
 * DLL_GetPriorRecord() : Get the record pointed to by current->prior
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            record        -- Pointer to an Info structure
 *
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 *            DLL_NOT_FOUND -- Beginning of list
 */
DLL_Return DLL_GetPriorRecord(List *list, Info *record)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    if(list->current->prior == NULL)
        return(DLL_NOT_FOUND);

    list->current = list->current->prior;
    memcpy(record, list->current->info, list->infosize);
    list->current_index--;
    return(DLL_NORMAL);
    }


/*
 * DLL_GetNextRecord() : Get the record pointed to by current->next
 *
 * Status   : Public
 *
 * Arguments: list          -- Pointer to type List
 *            record        -- Pointer to an Info structure
 *
 * Returns  : DLL_NORMAL    -- Record returned
 *            DLL_NULL_LIST -- List is empty
 *            DLL_NOT_FOUND -- End of list
 */
DLL_Return DLL_GetNextRecord(List *list, Info *record)
    {
    if(list->current == NULL)
        return(DLL_NULL_LIST);

    if(list->current->next == NULL)
        return(DLL_NOT_FOUND);

    list->current = list->current->next;
    memcpy(record, list->current->info, list->infosize);
    list->current_index++;
    return(DLL_NORMAL);
    }


/************************
 * Input/Output Functions
 */

/*
 * DLL_SaveList() : Save list to disk.
 *
 * Status   : Public
 *
 * Arguments: list             -- Pointer to type List
 *            path             -- Pointer to path and filename
 *
 * Return   : DLL_NORMAL       -- File written successfully
 *            DLL_NULL_LIST    -- List is empty
 *            DLL_OPEN_ERROR   -- File open error
 *            DLL_WRITE_ERROR  -- File write error
 *            DLL_NOT_MODIFIED -- Unmodified list no save was done
 */
DLL_Return DLL_SaveList(List *list, const char *path)
    {
    Node *step;
    FILE *fp;

    if(list->head == NULL)
        return(DLL_NULL_LIST);

    if(list->modified == DLL_FALSE)
        return(DLL_NOT_MODIFIED);

    if((fp = fopen(path, "wb")) == NULL)
        return(DLL_OPEN_ERROR);

    step = list->head;

    while(step != NULL)
        {
        if(fwrite(step->info, 1, list->infosize, fp) != list->infosize)
            {
            fclose(fp);
            return(DLL_WRITE_ERROR);
            }

        step = (Node *) step->next;
        }

    fclose(fp);
    list->modified = DLL_FALSE;
    return(DLL_NORMAL);
    }


/*
 * DLL_LoadList() : Load list to disk.
 *
 * Status   : Public
 *
 * Note: The list->current_index will have an arbitrary value it depending on
 *       the sort algorithm used.
 *
 * Arguments: list           -- Pointer to type List
 *            path           -- Pointer to path and filename
 *            pFun           -- Pointer to search function
 *
 * Return   : DLL_NORMAL     -- File written successfully
 *            DLL_MEM_ERROR  -- Memory allocation failed
 *            DLL_OPEN_ERROR -- File open error
 *            DLL_READ_ERROR -- File read error
 */
DLL_Return DLL_LoadList(List *list, const char *path,
  int (*pFun)(Info *, Info *))
    {
    Info *set;
    FILE *fp;
    DLL_Return exitCode;

    if((fp = fopen(path, "rb")) == NULL)
        return(DLL_OPEN_ERROR);

    DLL_DeleteEntireList(list);

    list->head = list->tail = NULL;

    if((set = (Info *) malloc(list->infosize)) == NULL)
        return(DLL_MEM_ERROR);

    for(;;)
        {
        if(fread(set, 1, list->infosize, fp) != list->infosize)
            {
            if(feof(fp))
                exitCode = DLL_NORMAL;
            else
                exitCode = DLL_READ_ERROR;

            break;
            }

        if((exitCode = DLL_AddRecord(list, set, pFun)) == DLL_MEM_ERROR)
            break;
        }

    if(!pFun)
        list->modified = DLL_FALSE;

    free(set);
    fclose(fp);
    return(exitCode);
    }


/******************
 * Helper Functions
 */

/*
 * _getListSize : Get the list size--sizeof(List)
 *
 * Status   : Private
 *
 * Arguments: Void
 *
 * Return   : Size of the List
 */
size_t _getListSize(void)
    {
    return sizeof(List);
    }


/*
 * _initializeList(): Initialize the list
 *
 * Status   : Private
 *
 * Arguments: list     -- Pointer to type List
 *            infosize -- Size of user Info
 *
 * Returns  : void
 */
void _initializeList(List *list, size_t infosize)
    {
    list->head = NULL;
    list->tail = NULL;
    list->current = NULL;
    list->saved = NULL;
    if(infosize) list->infosize = infosize;
    list->listsize = 0L;
    list->modified = DLL_FALSE;
    list->search_origin = DLL_HEAD;
    list->search_dir = DLL_DOWN;
    list->save_index = 0L;
    list->current_index = 0L;
    }


/*
 * _createNewRecord : Allocates space for a new node and info structure and
 *                    possibly adds the new node to the list if the list is
 *                    empty.
 *
 * Status   : Private
 *
 * Arguments: list          -- Pointer to type List
 *            info          -- Record to add
 *            newN          -- Pointer to new node
 *            newI          -- Pointer to new info
 *
 * Return   : DLL_NORMAL    -- File written successfully
 *            DLL_MEM_ERROR -- Memory allocation failed
 *            DLL_CONTINUE  -- Continue (internal use only)
 */
DLL_Return _createNewRecord(List *list, Info *info, Node **newN, Info **newI)
    {
    /* Allocate space for new node */
    if((*newN = (Node *) malloc(sizeof(Node))) == NULL)
        return(DLL_MEM_ERROR);

    /* Allocate space for new info */
    if((*newI = (Info *) malloc(list->infosize)) == NULL)
        {
        free(*newN);
        return(DLL_MEM_ERROR);
        }

    /* Put new info into allocated space */
    memcpy(*newI, info, list->infosize);

    /* If list->head is NULL, assume empty list and this is the 1st record. */
    if(list->head == NULL)
        {
        (*newN)->info = *newI;
        (*newN)->next = NULL;
        (*newN)->prior = NULL;
        list->head = *newN;
        list->tail = *newN;
        list->current = *newN;
        list->listsize = 1L;
        list->current_index = 1L;
        list->modified = DLL_TRUE;
        return(DLL_NORMAL);
        }

    return(DLL_CONTINUE);
    }


void _printList(List *list)
    {
    printf("list->head: %lx\n", (long unsigned int) list->head);
    printf("list->tail: %lx\n", (long unsigned int) list->tail);
    printf("list->current: %lx\n", (long unsigned int) list->current);
    printf("list->saved: %lx\n", (long unsigned int) list->saved);
    printf("list->infosize: %ld\n", (long int) list->infosize);
    printf("list->listsize: %ld\n", (long int) list->listsize);
    printf("list->modified: %ld\n", (long int) list->modified);
    printf("list->search_origin: %ld\n", (long int) list->search_origin);
    printf("list->search_dir: %ld\n", (long int) list->search_dir);
    printf("list->save_index: %ld\n", (long int) list->save_index);
    printf("list->current_index: %ld\n", (long int) list->current_index);
    }
