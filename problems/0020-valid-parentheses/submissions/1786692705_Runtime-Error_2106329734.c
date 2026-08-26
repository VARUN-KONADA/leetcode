
bool isValid(char* s)
{
    int len = strlen(s);
    char stack[len];
    int top = -1;
    for(int i = 0; i < len; i++)
    {
        if(s[i] == '(' || s[i] == '{' || s[i] == '[')
        {
            stack[++top] = s[i];
        }
        else
        {
            if(top != -1 && stack[top] == '(' && s[i] == ')' || stack[top] == '{' && s[i] == '}' || stack[top] == '[' && s[i] == ']')
            {
                top--;
            }
            else
            {
                return false;
            }
        }
    }
    if (top == -1)
    return true;
    else
    return false;
}
