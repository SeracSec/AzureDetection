import requests
import sys
import colorama
from colorama import Fore

def check_params(inputs):
    if len(inputs) == 2:
        return inputs[1]
    else:
        print('Invalid Syntax. Proper Syntax: python3 detection.py <domain>')
        sys.exit()

def check_365_presence(domain):
    url = f'https://login.microsoftonline.com/getuserrealm.srf?login=username@{domain}&json=1'
    return requests.get(url).json()

def get_tenant_id(domain):
    url = f'https://login.microsoftonline.com/{domain}/v2.0/.well-known/openid-configuration'
    return requests.get(url).json()
    
def check_azure_ad(domain):
    cleaned = domain.split('.')[0]
    url = f'https://login.microsoftonline.com/getuserrealm.srf?login=username@{cleaned}.onmicrosoft.com&json=1'
    return requests.get(url).json()

def main():
    print('') #Spacing

    #Grab domain from command line arguments
    domain = check_params(sys.argv)

    #Call function to check Office 365 presence and parse output
    office_presence = check_365_presence(domain)
    if office_presence['NameSpaceType'] != 'Unknown':
        print(Fore.GREEN + f'Microsoft Office 365 presence detected for {domain}' + Fore.RESET)
        print(f"Name Space Type: {office_presence['NameSpaceType']}")
        print(f"Domain Name: {office_presence['DomainName']}")
        print(f"Federation Brand Name: {office_presence['FederationBrandName']}")
    else:
        print(Fore.RED + f'Microsoft Office 365 presence not detected for {domain}' + Fore.RESET)

    print('')

    #Call Function to get Azure tenant ID
    id = get_tenant_id(domain)
    if 'token_endpoint' in id.keys():
        endpoint = id['token_endpoint']
        tenant_id = endpoint.split("/")[3]
        print(Fore.GREEN + f'Microsoft Cloud Tenant ID: {tenant_id}' + Fore.RESET)
    else:
        print(Fore.RED + f'Microsoft Cloud Tenant ID not found for {domain}' + Fore.RESET)

    print('') # Spacing

    #Call function to check Azure AD presence and parse output
    azure_ad = check_azure_ad(domain)
    if azure_ad['NameSpaceType'] == 'Managed':
        print(Fore.GREEN + f'Azure AD presence detected for {domain}' + Fore.RESET)
        print(f"Name Space Type: {azure_ad['NameSpaceType']}")
        print(f"Domain Name: {azure_ad['DomainName']}")
        print(f"Federation Brand Name: {azure_ad['FederationBrandName']}")
    else:
        print(Fore.RED + f'Azure AD presence not detected for {domain}' + Fore.RESET) 
    
if __name__ == '__main__':
    main()