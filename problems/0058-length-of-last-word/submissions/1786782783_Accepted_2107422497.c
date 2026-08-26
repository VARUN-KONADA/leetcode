int lengthOfLastWord(char* s) 
{
    int len = strlen(s);
    int start = 0;
    int count = 0;
    for(int i = 0; i < len; i++)
    {
        if(s[i] == ' ' && isalpha(s[i + 1]))
        {
            start = i + 1;
        }
    }
    for(int i = start; s[i] != ' ' && s[i] != '\0'; i++)
    {
        count ++;
    }
    return count;
}
