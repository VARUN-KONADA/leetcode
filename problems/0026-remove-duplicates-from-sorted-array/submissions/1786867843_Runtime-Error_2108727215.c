int removeDuplicates(int* nums, int numsSize) 
{
    int i, j;
    for( i = 0 ;true ; i++)
    {
        for( j = i + 1; nums[i] >= nums[j]; j++);
        nums[i + 1] = nums[j];
        if(nums[j] == nums[numsSize-1])
        {
            break;
        }

    }
    return i+2;
}
