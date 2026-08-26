int removeDuplicates(int* nums, int numsSize) 
{
    int i, j;
    for( i = 0; nums[i] != nums[numsSize-1]; i++)
    {
        for( j = i + 1; nums[i] >= nums[j]; j++);
        nums[i + 1] = nums[j];
    }

    return i + 1;
}
