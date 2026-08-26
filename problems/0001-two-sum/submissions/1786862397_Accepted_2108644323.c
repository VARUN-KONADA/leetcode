int* twoSum(int* nums, int numsSize, int target, int* returnSize) 
{
    static int op[2];
    *returnSize = 2;
    for(int i = 0; i < numsSize; i++)
    {
        for(int j = 0; j < numsSize; j++)
        {
            if(i != j && nums[i] + nums[j] == target)
            {
                op[0] = i;
                op[1] = j;
                return op;
            }
        }
    }
    return op;
}
