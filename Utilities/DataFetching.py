__author__='main'
import sys
import DataBaseUtilities as DBUtil
import inspect

unmask_characters={
    '{{1}}':'(',
    '{{2}}':')',
    '{{3}}':'[',
    '{{4}}':']',
    '{{5}}':',',
    '{{6}}':'#',
    '{{7}}':"'",
    '{{8}}':'%'
}
def unmask_string(givenText):
    for e in unmask_characters.keys():
        givenText=givenText.replace(e,unmask_characters[e])
    return givenText
def Get_Data_Like_Server(sHost,run_id,Data_Id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    total_data=[]
    query="select description,field,value,keyfield,ignorefield from result_master_data where run_id='%s' and id='%s' order by description"%(run_id,Data_Id)
    Conn=DBUtil.ConnectToDataBase(sHost=sHost)
    master_data_list=DBUtil.GetData(Conn,query,False)
    Conn.close()
    if master_data_list:
        for i in master_data_list:
            query="select description,field,value,keyfield,ignorefield from result_master_data where run_id='%s' and id='%s' order by description"%(run_id,i[2])
            Conn=DBUtil.ConnectToDataBase(sHost=sHost)
            group_data=DBUtil.GetData(Conn,query,False)
            Conn.close()
            if group_data:
                for g in group_data:
                    tmp=[]
                    tmp.append(unmask_string(i[1]))
                    for _index,h in enumerate(g[1:]):
                        if _index==0 or _index==1:
                            tmp.append(unmask_string(h))
                        else:
                            tmp.append(h)
                    total_data.append(tuple(tmp))
            else:
                tmp=[]
                for _index,h in enumerate(i[1:]):
                    if _index==0 or _index==1:
                        tmp.append(unmask_string(h))
                    else:
                        tmp.append(h)
                total_data.append(tuple(tmp))
    return total_data