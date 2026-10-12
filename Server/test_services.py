import pytest
from fastapi.testclient import TestClient
from Bridge import get_session,get_test_session,Test_SessionMaker
from utils_functions import get_current_user,create_token,hash_password
from server import app
from datetime import datetime
from Database import User,Application
import services
@pytest.fixture
def initialize_client():
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



@pytest.fixture
def get_user(initialize_client):
    db_session=Test_SessionMaker()
    try:
        new_user=User(first_name="lionel",last_name="messi",email="messi@gmail.com",password=hash_password("qwerty"),phone_number="10")
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        user_id=new_user.id
        try:
            token=create_token({"user_id":new_user.id,"email":new_user.email})
            initialize_client.cookies.set("access_token",token)
            yield new_user
            
        finally:
            db_session.rollback()
            db_session.query(Application).filter(Application.user_id==user_id).delete()
            db_session.query(User).filter(User.id==user_id).delete()
            db_session.commit()
            
    finally:
        db_session.rollback()
        db_session.close()

@pytest.fixture
def create_user():
    db_session=Test_SessionMaker()
    try:
        new_user=User(first_name="lamine",last_name="yamal",email="lamine@gmail.com",password=hash_password("qwerty"),phone_number="10")
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        user_id=new_user.id
        try:
            yield new_user
        finally:
            db_session.rollback()
            db_session.query(Application).filter(Application.user_id == user_id).delete()
            db_session.query(User).filter(User.id == user_id).delete()
            db_session.commit()
        
    finally:
        db_session.rollback()
        db_session.close()
    
@pytest.fixture
def create_application(get_user,tmp_path):
    db_session=Test_SessionMaker()
    cv_file=tmp_path/"cv.pdf"
    cv_file.write_bytes(b'%PDF-1.4 fake pdf content')
    try:
        new_application=Application(
            job_position="Ai Engineer",
                        company="Meta",
                        Job_type="Hybrid",
                        job_location="Uk",
                        status="Awaiting response",
                        Website="Meta.com",
                        Date=datetime.today().strftime("%Y-%m-%d"),
                        user_id=get_user.id,
                        Cv_path= str(tmp_path/"cv.pdf")
            
        )
        
        db_session.add(new_application)
        db_session.commit()
        db_session.refresh(new_application)
        application_id=new_application.id
        try:
            yield new_application
        finally:
            db_session.rollback()
            db_session.query(Application).filter(Application.id==application_id).delete()
            db_session.commit()     
    
    finally:
        db_session.close()
        
        
        

    
          

        

    

def test_login_template(initialize_client):
    
    reponse= initialize_client.get("/user/login")
    assert reponse.status_code==200
    assert 'name="email"' in reponse.text
    
    

def test_register_template(initialize_client):
    reponse= initialize_client.get("/user/register")
    assert reponse.status_code==200
    assert 'name="email"' in reponse.text
    print(reponse.text)
    
    
    

def test_dashboard_template(initialize_client, get_user):


    response = initialize_client.get("/user/dashboard")
    
    assert response.status_code == 200
    assert get_user.last_name in response.text.lower()
    assert get_user.first_name in response.text
    print(response.text)
    


    


def test_add_aplication_template(initialize_client,get_user):

    reponse=initialize_client.get("/user/add_application")
    
    assert reponse.status_code==200
    assert "Add New Job application" in reponse.text

def test_get_applications_template(initialize_client,get_user):

    reponse=initialize_client.get("/user/get_applications")
    print(reponse.text)
    assert reponse.status_code==200
    assert "All your jobs Applications" in reponse.text    
    
    
    

    

def test_register(initialize_client):
    reponse=initialize_client.post("/user/register",
                                   data={
                                       "first_name":"neymar",
                                       "last_name":"junior",
                                       "email":"neymar@gmail.com",
                                       "password":"qwerty",
                                       "phone_number":"11"
                                   },follow_redirects=False)
    assert reponse.status_code==303
    assert reponse.headers["location"]=="/user/login"



def test_login(initialize_client,create_user):
    reponse=initialize_client.post("/user/login",
                                   data={
                                       "email":create_user.email,
                                       "password":"qwerty"  
                                   },follow_redirects=False)
    assert reponse.status_code==303
    assert reponse.headers["location"]=="/user/dashboard"
    



    
    
def test_add_application(initialize_client,monkeypatch,tmp_path,get_user):
    
    monkeypatch.setattr(services,"users_dir",str(tmp_path/"users_files"))
    
    reponse=initialize_client.post("/user/add_application",
                                   data={
                                       "job_position":"Ingenieur",
                                       "company":"Amazon",
                                       "job_type":"Remote",
                                       "job_location":"USA",
                                       "website":"Amazon.com"
                                       
                                   },
                                   files={
                                       "cv_file":(
                                           "cv.pdf",
                                           b'%PDF-1.4 fake pdf content',
                                           "application/pdf"
                                       )
                                   })
    print(reponse.text)
    assert reponse.status_code==200
    file_path = (
        tmp_path / "users_files" / f"user-{get_user.id}"
        / "Ingenieur" / "Amazon-cv.pdf"
    )
    
    assert file_path.exists()
    assert file_path.read_bytes()==b"%PDF-1.4 fake pdf content"
    
    
    
    
    
 
    
    
    
def test_update_application(initialize_client,create_application,get_user):
    reponse=initialize_client.post("/user/update_status",
                                   params={"id_application": create_application.id},
                                   data={"status": "Accepted"},
                                   follow_redirects=False,)
    print(reponse.text)
    assert reponse.status_code==303
    
    assert reponse.headers["location"]=="/user/get_applications"
    
    


def test_download(initialize_client,create_application,get_user):
    reponse=initialize_client.get("/user/download_cv",
                                  params={
                                      "application_id":create_application.id
                                  })
    print(reponse.text)
    assert reponse.status_code==200
    assert reponse.headers["content-type"]=="application/pdf"
    assert reponse.content == b"%PDF-1.4 fake pdf content"
    assert "attachment" in reponse.headers["content-disposition"]
    


def test_delete_application(initialize_client,create_application,get_user):
    reponse=initialize_client.post("/user/delete_application",
                                  params={"application_id":create_application.id})
    
    print(reponse.text)
    assert reponse.status_code==200
    assert "All your jobs Applications" in reponse.text
    

    

def test_logout(initialize_client,get_user):
    reponse=initialize_client.get("/user/logout",follow_redirects=False)
    assert reponse.status_code==303
    assert reponse.headers["location"]=="/user/login"
    
  


  
  
def clean_test_db():
    db_session=Test_SessionMaker()
    try:
        db_session.query(Application).delete()
        db_session.query(User).delete()
        db_session.commit()
        
    finally:
        db_session.rollback()
        db_session.close()



        
    



@pytest.fixture(autouse=True)
def clean_db():
    
    yield clean_test_db()
    
        
      
    