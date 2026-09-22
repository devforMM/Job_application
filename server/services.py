from fastapi import APIRouter,Request,Depends
from datetime import datetime
import os
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import Form
from fastapi import UploadFile,File
from Database import User,Application
from utils_functions import *
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from Bridge import get_session
user_router=APIRouter()

templates=Jinja2Templates("../templates")


@user_router.get("/login")
def login_template(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="Login.html"
    )

@user_router.get("/register")
def register_template(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="Register.html"
    )




@user_router.get("/dashboard")
def dashboard_template(request:Request,user=Depends(get_current_user)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"user":user}

        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")



@user_router.get("/add_application")
def application_form(request:Request,user=Depends(get_current_user)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="add_application.html"
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")



@user_router.get("/get_applications")
def all_applications(request:Request,user=Depends(get_current_user)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="all_applications.html",
            context={
                "applications":user.applications
            }

        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")


@user_router.post("/update_status")
def update_status(id_application:int,db:Session=Depends(get_session),user=Depends(get_current_user),status=Form(...)):
    try:
        application=db.query(Application).filter(Application.id==id_application).first()
        application.status=status
        db.commit()
        db.refresh(application)

        return RedirectResponse(
            "/user/get_applications",
            status_code=303
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")






@user_router.post("/login")
def login(request:Request,db:Session=Depends(get_session),email=Form(...),password=Form(...)):
   try:
       user=db.query(User).filter(User.email==email).first()
       if user:
           if verify_password(password,user.password):
               token=create_token(
                   {"user_id":user.id,"email":user.email}
               )
               reponse=RedirectResponse(
                   "/user/dashboard",
                   status_code=303
               )
               reponse.set_cookie(
                    key="access_token",
                    value=token,
                    httponly=True,
                    secure=False
                )
               return reponse
           else:
               return templates.TemplateResponse(
                   request=request,
                   name="login.html",
                   context={"message":"invalid password"}
               )   
       else:
           return templates.TemplateResponse(
               request=request,
               name="login.html",
               context={"message":"invalid email"}
           )
        
   except Exception as e:
       raise HTTPException(status_code=400,detail=f"server error {e} ")


       
   


@user_router.post("/add_application")
async def add_application(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_session),

    job_position: str = Form(...),
    company: str = Form(...),
    job_type: str = Form(...),
    job_location: str = Form(...),
    website: str = Form(...),

    cv_file: UploadFile = File(...)
):
    try:
        cv_content = await cv_file.read()

        path = f"users_files/user-{user.id}/{job_position}"
        os.makedirs(path, exist_ok=True)

        file_path = f"{path}/{company}-cv.pdf"

        with open(file_path, "wb") as file:
            file.write(cv_content)

        new_application = Application(
            job_position=job_position,
            company=company,
            Job_type=job_type,
            job_location=job_location,
            status="Awaiting response",
            Website=website,
            Date=datetime.today().strftime("%Y-%m-%d"),
            user_id=user.id,
            Cv_path=file_path
        )

        db.add(new_application)
        db.commit()
        db.refresh(new_application)

        return templates.TemplateResponse(
            name="All_applications.html",
            request=request,
            context={
                "applications": user.applications
            }
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"server error: {e}"
        )





@user_router.post("/register")
def register_user(db:Session=Depends(get_session), first_name=Form(...),last_name=Form(...),email=Form(...),
        password=Form(...),phone_number=Form(...)):
    try:
        print("mama")
        new_user=User(
            first_name=first_name,last_name=last_name,email=email,password=hash_password(password),phone_number=phone_number   
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        reposnse=RedirectResponse(
            url="/user/login",
            status_code=303
        )
        return reposnse
    except Exception as e:
        raise HTTPException(detail=str(e),status_code=400)




@user_router.get("/application_details")
def application_details(request:Request,application_id:int,user=Depends(get_current_user),db:Session=Depends(get_session)):
    try:
        application=db.query(Application).filter(Application.id==application_id).first()
        return templates.TemplateResponse(
            request=request,
            name="application_details.html",
            context={
                "application":application
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")




@user_router.get("/download_cv")
def download_cv(application_id:int,db:Session=Depends(get_session)):
    try:
        application=db.query(Application).filter(Application.id==application_id).first()
        if application:
            return FileResponse(
                application.Cv_path,
                media_type="application/pdf",
                filename=f"{application.job_position}-{application.company}.cv",
                content_disposition_type="attachement"
            )



    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error: {e}")

@user_router.get("/logout")
def logout():
    reponse=RedirectResponse("user/login",status_code=303)
    reponse.delete_cookie("access_token")
    return reponse

@user_router.post("/users/delete_application")
def delete_application(request:Request,application_id:int,user=Depends(get_current_user),db:Session=Depends(get_current_user)):
    try:
        application=db.query(Application).filter(Application.id==application_id).first()
        db.delete(application)
        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="All_applications.html",
            context={
                "applications":user.applications
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400,)