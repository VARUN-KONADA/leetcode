/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
 typedef struct ListNode node;
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) 
{
    node* op = NULL;
    node* temp = NULL;

    if(list1 == NULL && list2 == NULL)
        return op;

    else if(list2 == NULL)
    {
        op = list1;
        temp = list1;
        list1 = list1->next;
    }

    else if(list1 == NULL)
    {
        op = list2;
        temp = list2;
        list2 = list2->next;
    }

    else if( list1->val < list2->val )
        {
            op = list1;
            temp = list1;
            list1 = list1->next;
        }
    else 
        {
            op = list2;
            temp = list2;
            list2 = list2->next;
        }

    while( list1 != NULL && list2 != NULL )
    {
        if(list1->val < list2->val )
        {
            temp->next = list1;
            temp = list1;
            list1 = list1->next;
        }
        else
        {
            temp->next = list2;
            temp = list2;
            list2 = list2->next;
        }
    }
     if(list2 == NULL && list1 != NULL)
    {
        temp->next = list1;
    }
    else if(list1 == NULL && list2 != NULL)
    {
        temp->next = list2;
    }

    return op;
}
