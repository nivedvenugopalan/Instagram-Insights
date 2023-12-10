"""Functions to match appropriate formatting in the dashboard (frontend)"""

def formatlist(list_) -> str:
    if len(list_) == 0:
        return str(list_[0])
    return ', '.join(map(str, list_))

def formatint(int_, percentage:bool=False, round_:int=2) -> str:
    if percentage:
        return f'{int_*100:.{round_}f}%'
    return f'{int_:,}'