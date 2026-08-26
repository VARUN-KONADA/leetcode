char * mergeAlternately(char * word1, char * word2)
{
    int len1 = strlen(word1);
    int len2 = strlen(word2);
    int i = 0;
    int j = 0;
    int k;
    static char op[500];
    int n = len1 + len2;
    for(k = 0; k < n; k++)
    {
        if(i == len1)
        {
            op[k] = word2[j++];
        }
        else if(j == len2)
        {
            op[k] = word1[i++];
        }
        else
        {
            op[k] = word1[i++];
            k++;
            op[k] = word2[j++];
        }
    }
    op[k] = '\0';
    return op;
}
