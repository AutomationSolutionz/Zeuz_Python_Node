from selenium.webdriver.remote.webelement import WebElement
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


options = Options()
service = Service()
# options.add_argument("disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
# options.add_argument("profile.content_settings.exceptions.cookies.allowed_for_urls=www.hubspot.com")

selenium_driver = selenium.webdriver.Chrome(
    service=service,
    options=options,
)

# selenium_driver = selenium.webdriver.Edge(options=options)

d={'__pdst': '179f24cb92cc4b9fba62e6cac1ac195b', '__hs_cookie_cat_pref': '1:true_2:true_3:true', 'hubspotutk': '1a9e5de2eb8087cacdf0bb072717e2fe', 'trcksesh': 'a86fd7db-3f4b-4751-a21b-c159b45e4f49', 'hs_login_email': 'sweta.kumari@astegic.in', '_conv_r': 's%3Awww.google.com*m%3Aorganic*t%3A*c%3A', 'hubspotapi-prefs': '0', 'hubspotapi-csrf': 'AAccUfsBgQZiqnIRaBxrCzG9WJbisnCrwdyoVzM36tbsOTf7_NdzlsO14_oLW0NKlGOcZbTJ4xdZFqMCm7_cYDly9bLY0YM-ag', 'csrf.app': 'AAccUfsBgQZiqnIRaBxrCzG9WJbisnCrwdyoVzM36tbsOTf7_NdzlsO14_oLW0NKlGOcZbTJ4xdZFqMCm7_cYDly9bLY0YM-ag', '_gcl_au': '1.1.1170923742.1719316319', '__hssrc': '1', '_fbp': 'fb.1.1719316319317.513096624546995196', 'IR_gbd': 'hubspot.com', '_tt_enable_cookie': '1', '_ttp': 'ffGsb6Z01Bri0BUBEPWw85fCU1P', 'IR_PI': '3232476b-265b-11ef-8ded-8b65d6232029%7C1719316320172', '_gid': 'GA1.2.314381481.1719316321', 'saw_experiment': 'true', '_conv_v': 'vi%3A1*sc%3A5*cs%3A1719393996*fs%3A1719303070*pv%3A5*seg%3A%7B10031564.1-10034364.1-10034366.1%7D*exp%3A%7B100341862.%7Bv.1003162477-g.%7B100327900.1-100328009.1%7D%7D-100342007.%7Bv.1003162876-g.%7B100327900.1-100328009.1%7D%7D%7D*ps%3A1719387239', '_conv_s': 'si%3A5*sh%3A1719393996167-0.8504025071243075*pv%3A1', '__hstc': '20629287.1a9e5de2eb8087cacdf0bb072717e2fe.1719316319087.1719387239517.1719393997151.3', '__hssc': '20629287.1.1719393997151', '_rdt_uuid': '1719316319750.38ecc6ee-3653-4eba-8930-db70315c3c0e', '_uetsid': '7cdd73f032ca11efa5d22f6516591ab8', '_uetvid': 'b387ae002a2c11efbe2915d15a4d5b6f', 'IR_12893': '1719393998315%7C2643745%7C1719393998315%7C%7C', '_ga': 'GA1.1.1261872802.1719316321', '_ga_LXTM6CQ0XK': 'GS1.1.1719393998.3.1.1719393998.60.0.0'}
d2 = [{'domain': 'app.hubspot.com', 'expiry': 1727173657, 'httpOnly': False, 'name': 'NPS_e579c260_last_seen', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1719397657624'}, {'domain': '.hubspot.com', 'expiry': 1750933655, 'httpOnly': False, 'name': 'csrf.app', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'AAccUfs4fvUUifmMiPSYV5qkMAR03Hga6xUh-mgbTjt3e6ARJX-5Rb5zWFdKARR_E_IsUUqH3b24ro5z2Ry8BIeMNDoiP6079Q'}, {'domain': '.hubspot.com', 'expiry': 1750933655, 'httpOnly': False, 'name': 'hubspotapi-csrf', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'AAccUfs4fvUUifmMiPSYV5qkMAR03Hga6xUh-mgbTjt3e6ARJX-5Rb5zWFdKARR_E_IsUUqH3b24ro5z2Ry8BIeMNDoiP6079Q'}, {'domain': '.hubspot.com', 'expiry': 1734949538, 'httpOnly': False, 'name': '__hs_cookie_cat_pref', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1:true_2:true_3:true'}, {'domain': '.hubspot.com', 'expiry': 1750933655, 'httpOnly': False, 'name': 'hubspotapi-prefs', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '0'}, {'domain': '.hubspot.com', 'expiry': 1734949655, 'httpOnly': True, 'name': 'hs_c2l', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'GPvenE0iGQAQstEnSMKEJv1kiridxD-LIQWNV_DBXaw'}, {'domain': '.hubspot.com', 'httpOnly': True, 'name': 'hubspotapi', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'AAccUfv_C4SsS5AjhZIAT9Rxoc3Co2-9CwHyTpxaP1-7nNNCEJWoHEzCwMKAHMHFCgU8me4RJmA6yVwGoPrn8nrKU7oXU1irdXMcdtKnCUpk4PWfUvt008CkCf74TA18eiFRfX6N8joRV40mR5f8xDqTe3rMhyz33w5Hp_ZAY9uKStt0E4I9NAK4XrNy9ucrrPqLPGxajrtTmAVHS6pMneQxOSc7FLK4cr5tRbjvtCUgdAuxovG_KhIXFfq4GSgaGKyX71_C9SGvlQ8FX9wvOTxHdwZHPSGHZUEoGrcMaaR1cgRpdLXC1K1ZieHobl2PZ1BRAz6lMaMfpeCiAFN7-ZBpUvjs3d-4XfzHHDGOP61kQVLrSyZYZm87Si8Vhx2YuTd0LJcDVmoSbKiF5q5OB-9lT_8ADvUYsCaG8-TJh-h0P8xakafMsa1zHaYNhLbZ7SA2yzXwslTfQDov3zM4g1hWFFiDNmD1LbRaPfgaAGdTKGhFyfziz3sAqdMvXl8cBHFRkYHLUDenqLttg7ZymeH1BIgW45zmVCybLo5est7MTlKiQIe9NCa2ZVDQwqSBmf6HvdsYOVCeuEKwrVVsjf2tQx40GGuXIOhptvZ7FoEjCQZJgvaZl5p0OfkRYJW6CrbWy7r7BIOipzPBUcZJ0Y9jkBJe1TZTSPyqBMQzbNiyX-Q0hugQEwODw_EjO-zuyPR3ZCzhWws9YXs0A9WP8SE9aB3bMFPdU9fjXW8E0TLbgOq5SHYlPTB7AMeQH_RunFMC1hTjUGVvg-e2lEo3l_26IbTjSuw7xsSXAEoPpXwStKgTHtafe8ykwuKU3wG-P37YvgNU6Gj2CsRUVmmw9OqRUmQB7lGXcKhz0juY4jvU0qSTaFQRxFzeSlhNmEmiQ1j2P-A8mk8U9_Z8DTP5y9K6np3nqiMAvPEkMIGo39Evykzrtun9KjGC9f9AFXKL4fG6HWfAs_ESIv0NBRNOAsJCVIqKwRxFsQDRltR_chwlI8MX7gcrWehZQIR_4r2hnFkzKJu9LgmPMSWZ2Vi9kTcgm_PaWVXmgpVDOqBgjwiwN36JzHrjq8LI569QR72IVoeoG31mbngzhFOGv4SKYIQOGPBbLUw8UwjiOX9LXPgm4TIDMYfSdk8pnDmJjbkbBChjmohJilF3Us2RzDmE_NLzZYRvr6Sb4FdvdmR0Mq2N16RHRsDVEznVd4HFZp4WpO1zrH-qUS9kGh6Wu1flOygqrHdC3xCggA'}, {'domain': '.hubspot.com', 'httpOnly': True, 'name': '_cfuvid', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'VHVahDU40Dmu.1Qz980FJSPww1NhiLWl0Vccm1nqHeI-1719397525545-0.0.1.1-604800000'}, {'domain': '.hubspot.com', 'expiry': 1750933655, 'httpOnly': False, 'name': 'hs_login_email', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'sweta.kumari@astegic.in'}, {'domain': '.hubspot.com', 'expiry': 1719399324, 'httpOnly': True, 'name': '__cf_bm', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'DZACl4TpMi4DvonGPzq7smssgHwLiW0P6qv8_wG6sKY-1719397525-1.0.1.1-vpGOK0sWRMpGBwZQ_Sih0UFgwJ92YnBi_PDcXRqolS.uypW0iMyS7XTMchxyEFJQ758x1vLoIMmd6tZGxryH5Q'}]
d3 = [
    {
        'name': '_cfuvid',
        'value': '6q43VvZCGxj5SYyd6P0jD6IJ.uNBlgwO9dZAsTB0EBU-1719398293577-0.0.1.1-604800000',
        'domain': '.hubspot.com'
    }
]
selenium_driver.get('https://app.hubspot.com/user-guide/46427382?via=home')

print('Before:', selenium_driver.get_cookies())
for each in d2:
    try:
        selenium_driver.add_cookie(each)
    except Exception as e: print(e)
print('After:', selenium_driver.get_cookies())
selenium_driver.get('https://app.hubspot.com/user-guide/46427382?via=home')

print()
input('teardown?')
selenium_driver.quit()