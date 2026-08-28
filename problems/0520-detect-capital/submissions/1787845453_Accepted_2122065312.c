bool detectCapitalUse(char* word) 
{
    int count = 0;
    int size = strlen(word);
    for(int i = 0; i < size; i++)
    {
        if(isupper(word[i]))
            count++;
    }
    if(count == 0 || count == size || (count == 1 && isupper(word[0])))
        return true;
    return false;
}
