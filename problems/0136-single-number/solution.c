int singleNumber(int* nums, int numsSize) 
{
    int has;
    for(int i = 0; i < numsSize; i++)
    {
        has = 1;
        for (int j = 0; j < numsSize; j++)
        {
            if (i != j && nums[i] == nums[j])
            {
                has =  0;
                break;
            }

        }
        if(has)
        {
            return nums[i];
        }
    }
    return 0;
}
