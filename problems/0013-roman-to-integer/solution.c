int val(char c);
int romanToInt(char* s) 
{
    int len = strlen(s);
    int value = 0;
    int p, q;
    for(int i = 0; i < len; i++)
    {
        p = val(s[i]);
        q = val(s[i+1]);
        if(p >= q)
        {
            value += p;
        }
        else
        {
            value += q - p;
            i++;
        }
    }
    return value;
}
int val(char c)
{
        if(c == 'I')
            return 1;

        else if (c == 'V')
            return 5;

        else if (c == 'X')
            return 10;  

        else if (c == 'L')
            return 50;  

        else if (c == 'C')
            return 100;

        else if (c == 'D')
            return 500;

        else if (c == 'M')
            return 1000;
    return 0;
}
