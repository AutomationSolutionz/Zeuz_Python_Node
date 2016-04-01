__author__ = 'Raju'
from AutomationFW.CoreFrameWork import FileUtilities
import ConfigParser
import os

def write_config_file(full_file_name,method,run_id,steps_data,default_configs,klass):
    config_file_name=full_file_name+os.sep+'ConfigFiles'+os.sep+klass+'.conf'
    result_file_path=full_file_name+os.sep+'Result'+os.sep+run_id.replace(':','-')+'.xml'#full_file_name+os.sep+'Result'+os.sep+run_id+'.xml'
    log_file_path=full_file_name+os.sep+'Log'+os.sep+run_id.replace(':','-')+'.log'#full_file_name+os.sep+'Log'+os.sep+run_id+'.log'
    config_parser=ConfigParser.ConfigParser()
    config_parser.read(config_file_name)
    if method not in config_parser.sections():
        config_parser.add_section(method)
        config_parser.set(method,'description','Default Description of this section.(can be overridden)')
    #give the data in the
    steps_data=steps_data[0]
    for each in steps_data:
        key=each[0]
        value=each[1]
        print method,key,value
        config_parser.set(method,key,value)
    for each in default_configs:
        if each not in config_parser.sections():
            config_parser.add_section(each)
        setting=default_configs[each]
        for eachtime in setting:
            config_parser.set(each,eachtime[0],eachtime[1])
    #override the log file
    config_parser.set('bench','result_path',result_file_path)
    config_parser.set('bench','log_path',log_file_path)
    FileUtilities.CreateFolder(full_file_name+os.sep+'ConfigFiles',False)
    with(open(config_file_name,'w')) as open_file:
        config_parser.write(open_file)
    open_file.close()

import os
# from funkload.ReportBuilder import FunkLoadXmlParser
def decode_result_performance(config_file_path):
    if os.path.isfile(config_file_path):
        config_parser=ConfigParser.ConfigParser()
        config_parser.read(config_file_path)
        xml_path=config_parser.get('bench','result_path')
        if os.path.isfile(xml_path):
            cycles=config_parser.get('bench','cycles').split(":")
            #print cycles
            xml_parser=FunkLoadXmlParser()
            xml_parser.parse(xml_path)
            #print xml_parser.stats
            response_list=[]
            test_list=[]
            for each in xml_parser.stats:
                phase=xml_parser.stats[each]
                #print "cycle for %s"%str(cycles[int(each)])
                for each_key in phase:
                    if each_key=='response':
                        response=phase[each_key]
                        #print 'Response:',response.max,response.min,response.total/float(response.count),response.total,response.count,response.success,response.error
                        response_list.append((response.max,response.min,response.total/float(response.count),response.total,response.count,response.success,response.error))
                    if each_key=='test':
                        test=phase[each_key]
                        #print 'Test: ',test.max,test.min,test.total/float(test.count),test.total,test.count,test.success,test.error
                        test_list.append((test.max,test.min,test.total/float(test.count),test.total,test.count,test.success,test.error))
                    """if each_key=='response_step':
                        response_list=phase[each_key]
                        count=0
                        total=0
                        success=0
                        error=0
                        all_time=[]
                        for k in response_list:
                            er = response_list[k]
                            all_time.append(er.total)
                            total+=er.total
                            count+=1
                            success+=er.success
                            error+=er.error
                        print "Response: ",max(all_time),min(all_time),total/float(count),success,error
                    """
                #print "======================================"
            #print cycles
            temp=[]
            for each in cycles:
                temp.append(int(each))
            cycles=sorted(temp,reverse=True)
            #print ":".join(str(x) for x in cycles)
            #print test_list
            #print response_list
            Dict={}
            column=['max_time','min_time','avg_time','total_time','count','success','error']
            temp=[{'cycles':":".join(str(x) for x in cycles)}]
            for i in range(0,7):
                #print ":".join(str(each[i]) for each in test_list)
                temp.append({column[i]:":".join(str(each[i]) for each in test_list)})
            temp.append({'result_type':'test'})
            Dict.update({'test':temp})
            temp=[{'cycles':":".join(str(x) for x in cycles)}]
            for i in range(0,7):
                #print ":".join(str(each[i]) for each in response_list)
                temp.append({column[i]:":".join(str(each[i]) for each in response_list)})
            temp.append({'result_type':'response'})
            Dict.update({'response':temp})
            return Dict
        else:
            return False
    else:
        return False

if __name__=="__main__":
    #decode_result_performance('E:\Workspace\Framework_0.1\Automationz\Framework_0.1\AutomationFW\Result\Sat-Jun-13-22-07-01-2015.xml')
    decode_result_performance('E:\Workspace\Framework_0.1\Automationz\Framework_0.1\AutomationFW\ConfigFiles\Sprout.conf')