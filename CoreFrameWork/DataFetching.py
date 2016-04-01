'''

'''
import sys
sys.path.append("..")
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
def Get_PIM_Data_By_Id(Data_Id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    Data_List = []
    SQLQuery = ("select "
    " pmd.id,"
    " pmd.field,"
    " pmd.value,"
    " pmd.keyfield,"
    " pmd.ignorefield"
    " from master_data pmd"
    " where"
    " pmd.id = '%s' order by description;" % (Data_Id))
    conn=DBUtil.ConnectToDataBase()
    Data_List = DBUtil.GetData(conn, SQLQuery, False)
    Data_List = [tuple(x[1:])for x in Data_List]
    conn.close()
    AddressList = []
    for i in range(len(Data_List) - 1, -1, -1):
        eachTuple = Data_List[i]
        if eachTuple[1].startswith(Data_Id):  # or eachTuple[0] == 'Home Address' or eachTuple[0] == 'Other Address':
            if eachTuple[1] != "":
                address_find_SQLQuery = ("select "
                " pmd.field,"
                " pmd.value,"
                " pmd.keyfield,"
                " pmd.ignorefield"
                " from master_data pmd"
                " where"
                " pmd.id = '%s' order by description"
                " ;" % (eachTuple[1]))
                conn=DBUtil.ConnectToDataBase()
                AddressData = DBUtil.GetData(conn, address_find_SQLQuery, False)
                conn.close()
            else:
                AddressData = ''
            Data_List.pop(i)
            AddressList.append((eachTuple[0], AddressData))
    for eachAddrData in AddressList:
        Data_List.append(eachAddrData)

    return Data_List


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