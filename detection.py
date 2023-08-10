import requests
import sys
import colorama
from colorama import Fore
from xml.etree import ElementTree as ET


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
    # Create the XML body
    body = f'''
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:aut="http://schemas.microsoft.com/exchange/2010/Autodiscover">
        <soap:Header>
            <a:Action xmlns:a="http://www.w3.org/2005/08/addressing"
                    soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
            <a:To xmlns:a="http://www.w3.org/2005/08/addressing"
                soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To>
            <a:ReplyTo xmlns:a="http://www.w3.org/2005/08/addressing">
                <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
            </a:ReplyTo>
        </soap:Header>
        <soap:Body>
            <aut:GetFederationInformationRequestMessage xmlns:aut="http://schemas.microsoft.com/exchange/2010/Autodiscover">
                <aut:Request>
                    <aut:Domain>{domain}</aut:Domain>
                </aut:Request>
            </aut:GetFederationInformationRequestMessage>
        </soap:Body>
    </soap:Envelope>
    '''

    # Create the headers
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": 'http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation',
        "User-Agent": "AutodiscoverClient"
    }

    # Make the request
    response = requests.post("https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc", data=body, headers=headers)

    # Parse the response
    xml_tree = ET.fromstring(response.text)
    namespaces = {'a': 'http://schemas.microsoft.com/exchange/2010/Autodiscover'}

    # Extract and sort the domains
    domains = xml_tree.find('.//a:Domains', namespaces)
    domain_list = [d.text for d in domains.findall('a:Domain', namespaces)]
    domain_list.sort()

    return domain_list

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
    for returned_domain in azure_ad:
        if 'onmicrosoft.com' in returned_domain:
            azure_ad_domain = returned_domain
    if azure_ad_domain:
        print(Fore.GREEN + f'Azure AD presence detected for {domain}' + Fore.RESET)
        print(f"Azure AD Domain Name: {azure_ad_domain}")
        print(f"Tenant Name: {azure_ad_domain.split('.')[0]}")
    else:
        print(Fore.RED + f'Azure AD presence not detected for {domain}' + Fore.RESET) 
    
if __name__ == '__main__':
    main()