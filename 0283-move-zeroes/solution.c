void moveZeroes(int* nums, int numsSize) 
{
    int p = 0;
    for(int i = 0; i < numsSize ; i++)
    {
        if(nums[i] != 0)
            nums[p++] = nums[i];
    }
    for(;p < numsSize ; p++)
        nums[p] = 0;
}
