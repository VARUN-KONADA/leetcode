int* smallerNumbersThanCurrent(int* nums, int numsSize, int* returnSize) 
{
    static int op[500];
    int val;
    for(int i = 0; i < numsSize; i++)
    {
        val = 0;
        for(int j = 0; j < numsSize; j++)
        {
            if(i != j && nums[j] < nums[i])
            {
                val++;
            }
        }
        op[i] = val;
    }
    *returnSize = numsSize;
    return op;
}
