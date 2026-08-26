bool isPalindrome(int x) 
{
    if(x < 0 || x % 10 == 0 && x != 0)
    {
        return false;
    }
    else
    {
        int rx = 0;
        while(x > rx)
        {
            rx = (x % 10) + rx * 10;
            x = x / 10;
        }

        if(x == rx || x == rx / 10)
            return true;

        else
            return false;
    }

}
