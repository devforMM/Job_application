from Database import SessionMaker,Test_SessionMaker
def get_session():
    bd=SessionMaker()
    try:
        yield bd
    finally :
        bd.close()
        

def get_test_session():
    bd=SessionMaker()
    try:
        yield bd
    finally :
        bd.close()
        