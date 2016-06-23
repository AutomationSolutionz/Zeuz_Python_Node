

from Projects.DigiFlare import AndroidDemo_script as df


def testcase1():
    df.launch("ca.bellmedia.bnngo", "ca.bellmedia.bnngo.activities.SplashActivity")
    df.confirm_right()
    df.confirm_left()
    df.close()

def testcase2():
    df.launch("ca.bellmedia.bnngo", "ca.bellmedia.bnngo.activities.SplashActivity")
    df.go_left("News")
    df.confirm_submenu_items("All News")
    df.go_sub("All News")
    df.check_section("All News")
    df.close()
    
    
    
def testcase3():
    df.launch("ca.bellmedia.bnngo", "ca.bellmedia.bnngo.activities.SplashActivity")
    df.confirm_right()
    df.confirm_left()
    df.go_sub("News")
    df.confirm_submenu_items("All News")
    df.go_sub("All News")
    df.check_section("All News")
    df.close()
    
    
    
#testcase1()
#testcase2()
testcase3()