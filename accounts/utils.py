import requests
from django.conf import settings



class PremblyServices:

    def user_signup_verification_mail(email:str):
        url = f'{settings.PREMBLY_BASE_URL}/api/v2/biometrics/merchant/verification/emailage'
        headers = {
            { 
                'x-api-key':  settings.PREMBLY_X_API_KEY,
                'app-id' : settings.PREMBLY_APP_ID   
            } 
        }
        data = {'email': email }
        response = requests.post(url , headers=headers , data=data )

        if response.status_code == 200  :
            return True
        else:
            return False


    
    def channel_creation_verification(rc_number):
        url = f'{settings.PREMBLY_BASE_URL}/api/v2/biometrics/merchant/verification/cac?rc_number={rc_number}'
        headers = {
            { 
                'x-api-key':  settings.PREMBLY_X_API_KEY,
                'app-id' : settings.PREMBLY_APP_ID   
            } 
        }
        data = {'email': rc_number }
        response = requests.post(url , headers=headers , data=data )

        if response.status_code == 200  :
            return response.json()
        else:
            return None
       
        