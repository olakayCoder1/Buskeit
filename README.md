# Buskeit ( Backend-django)
Buskeit is an application for school bus fleet management. Currently, parents are asked to sign a 
book when their wards are picked up from the house. Buskeit intends to take out the manual process signing of
this book and digitize it. With buskeit, parents can acknowledge when their children have been picked up/ dropped off also.
Schools can also leverage this app for proper student administration/planning and better bus fleet tracking/management. 

## ENPOINTS
| METHOD | ROUTE | FUNCTIONALITY |ACCESS|
| ------- | ----- | ------------- | ------------- |
| *POST* | ```/api/v1/register/parents``` | _Register new user as parent_| _All users_|
| *POST* | ```/api/v1/password/forget``` | _Request password reset_|_All users_|
| *POST* | ```/api/v1/password/<token>/<uuidb64>/reset``` | _Reset password confirm_|_All users_|
| *POST* | ```/api/v1/password/reset``` | _Change user password_|_Authenticated user_|



## CONTRIBUTORS
| SN | USER | ROLE |PROFILE|
| ------- | ----- | ------------- | ------------- |
| 1 | Olanrewaju AbdulKabeer | _Backend_| _[olakayCoder1](https://github.com/olakayCoder1)_|
