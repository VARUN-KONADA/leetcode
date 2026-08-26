int* twoSum(int* nums, int numsSize, int target, int* returnSize) 
{
    static int op[2];
    *returnSize = 2;
    for(int i = 0; i < numsSize - 1; i++)
    {
        for(int j = i+1; j < numsSize; j++)
        {
            if(nums[i] + nums[j] == target)
            {
                op[0] = i;
                op[1] = j;
                return op;
            }
        }
    }
    return op;
}
