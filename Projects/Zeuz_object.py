shared_variables = {}
class zeuz:
    def __init__(
            self,
            const=False,
            session=False,
            masked=False,
            cleanup=True
    ):
        self.const = const
        self.session = session
        self.masked = masked
        self.cleanup = cleanup
def Set_Shared_Variables(key,val):
    global shared_variables
    class zeuzo(type(val)):
        num = 0
        def assign(self,zeuz_val):
            self.zeuz = zeuz_val

    value = zeuzo(val)
    value.assign(zeuz())
    shared_variables[key] = value

def Get_Shared_Variables(key):
    return shared_variables[key]

if __name__ == "__main__":
    Set_Shared_Variables("var",[1,2,"hello"])
    print(Get_Shared_Variables("var"))
    print()
    print()


import spacy
from spacy.lang.en import English

# Load the English language model in spaCy
nlp = spacy.load('en_core_web_md')