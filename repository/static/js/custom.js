function vis()
{
    if (document.getElementById('searchform').style.visibility == 'visible')
    {
        document.getElementById('searchform').style.visibility= 'hidden';
    }
    else
    {
        document.getElementById('searchform').style.visibility= 'visible';
        document.getElementById('query').focus();
    }
}
