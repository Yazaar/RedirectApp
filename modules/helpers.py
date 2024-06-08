import os
from pathlib import Path
from . import entities

def getEnv():
    return entities.Env()

def createSession():
    return entities.Session()

def findSession(sessions: list[entities.Session], secret: str):
    for i in sessions:
        if i.secret == secret:
            return i

def cleanSessions(sessions: list[entities.Session]):
    count = len(sessions)
    for i in reversed(range(count)):
        if not sessions[i].is_valid():
            sessions.pop(i)

def validateSession(sessions: list[entities.Session], secret: str):
    if not secret: return None
    session = findSession(sessions, secret)
    if not session or not session.is_valid():
        return None
    session.reset_validity()
    return session

def flatPath(path: str):
    try: return Path(path).as_posix()
    except Exception: return None

def validateRedirect(rPath: str, rType: str, rTarget: str, rId: int):
    if not isinstance(rPath, str) or not isinstance(rType, str) or not isinstance(rTarget, str) or not (rId is None or isinstance(rId, int)):
        return False

    if rType != 'redirect'and rType != 'download': return False
    rTL = len(rTarget)
    if not (rTarget.startswith('http://') and rTL > 7) and not (rTarget.startswith('https://') and rTL > 8):
        return False
    if rPath[0] != '/' or len(rPath) < 2:
        return False
    return True