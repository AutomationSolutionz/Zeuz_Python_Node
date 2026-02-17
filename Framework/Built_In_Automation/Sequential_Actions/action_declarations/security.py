declarations = (
    { "name": "nmap",     "function": "port_scaning_nmap",      "screenshot": "none" },
    { "name": "nikto",     "function": "server_scaning_nikto",    "screenshot": "none" },
    { "name": "wapiti",     "function": "server_scaning_wapiti",    "screenshot": "none" },
    { "name": "arachni",     "function": "server_scaning_arachni",    "screenshot": "none" },

) 

module_name = "security"

for dec in declarations:
    dec["module"] = module_name