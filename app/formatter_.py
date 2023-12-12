"""Functions to match appropriate formatting in the dashboard (frontend)"""

def formatlist(list_) -> str:
    if len(list_) == 0:
        return str(list_[0])
    return ', '.join(map(str, list_))

def formatint(int_, percentage:bool=False, round_=None) -> str:
    if percentage:
        return f"{round(int_, round_)}%"
    return f"{round(int_, round_)}"