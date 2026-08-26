/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
bool* kidsWithCandies(int* candies, int candiesSize, int extraCandies, int* returnSize) 
{
    int t;
    bool high;
    static bool op[500];
    for(int i = 0; i < candiesSize; i++)
    {
        t = candies[i] + extraCandies;
        high = true;
        for(int j = 0; j < candiesSize; j++)
        {
            if( t < candies[j])
            {
                high = false;
            }
        }
        op[i] = high;
    }
    *returnSize = candiesSize;
    return op;
}
