from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix= "/users",
                   tags= ["users"],
                   responses= {404: {"message": "No ha jalado esto pa"}})
 
class User(BaseModel):
    id: int 
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id = 1, name = "Jesús", surname = "Quiñones", url = "https://google.com", age = 22),
              User(id = 2, name = "Eduardo", surname = "Mata", url = "https://youtube.com", age = 22)]

@router.get("/usersjson")
async def users_json():
    return [{"name ": "Jesús", "surname": "Quiñones", "url": "https://google.com", "age": "22"},
            {"name ": "Eduardo", "surname": "Mata", "url": "https://youtube.com", "age": "22"}]

# Function to get all the users
@router.get("/")
async def users():
    return users_list

# Function to get a user by id Path
@router.get("/{id}")
async def user(id: int):
    return search_user(id)

# Functoin to get a user by id Query
@router.get("/user/")
async def user(id: int):
    return search_user(id)

# Other http functions

@router.post("/user/", response_model= User, status_code = 201)
async def user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code= 404, detail= "El usuario ya existe")

    users_list.append(user)
    return user

# Create a function to update a user with fastapi
@router.put("/user/")
async def user(user: User):
    
    found = False
    
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True

    if not found:
        return {"error": "No se ha actualizado el usuario"}

    return user

@router.delete("/user/{id}")
async def user(id:int):

    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            found = True
        
    if not found:
        return {"error": "No se ha encontrado el usuario"}

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return {"error": "No se ha encontrado el user"}
