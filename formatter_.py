"""Functions to match appropriate formatting in the dashboard (frontend)"""

def formatlist(list_) -> str:
    return ', '.join(map(str, list_))