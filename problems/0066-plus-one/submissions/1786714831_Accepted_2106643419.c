/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* plusOne(int* digits, int digitsSize, int* returnSize) 
{
    int* op = malloc(digitsSize*sizeof(int));
    int update = digitsSize;
    for (int i = 0; i < digitsSize; i++)    //coping digits
    {
        op[i] = digits[i];
    }
    
    do
    {
        update--;
        if(update + 1 != digitsSize && op[update + 1] == 10)
            //  if 9+1 done in before step, makes it 0
        {
            op[update+1] = 0;
        }

        if(update == -1)    //if array exceeds length
        {
            op = realloc(op, (digitsSize + 1) * sizeof(int));
            memmove(&op[1], &op[0], (digitsSize) * sizeof(int));
            op[0] = 1;
            op[1] = 0;
            digitsSize++;
            break;
        }
        op[update] = op[update] + 1;
    }
    while(op[update] > 9 );
    
    *returnSize = digitsSize;
    return op;
}
