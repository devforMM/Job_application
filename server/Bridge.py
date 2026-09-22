from Database import SessionMaker
def get_session():
    bd=SessionMaker()
    try:
        yield bd
    finally :
        bd.close()