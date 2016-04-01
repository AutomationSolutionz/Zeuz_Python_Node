__author__ = 'shetu'
def compare_data(expected,actual):
    tuple_expected=list(set(filter( lambda x: not isinstance(x[1],list),expected)))
    group_expected=filter(lambda x:isinstance(x[1],list),expected)

    tuple_actual=list(set(filter( lambda x: not isinstance(x[1],list),actual)))
    group_actual=filter(lambda x: isinstance(x[1],list),actual)

    tuple_returned=match_tuple_data(tuple_expected,tuple_actual)
    group_returned=match_group_data(group_expected,group_actual)

    #print tuple_returned
    #print group_returned

    full_list=tuple_returned+group_returned

    print_compare_data(full_list)
    return full_list
def print_compare_data(data_list):
    print '  Field | Expected | Actual'
    print '----------------------------'
    for each in data_list:
        if not isinstance(each[1],list):
            if each[1]=='':
                d='--'
            else:
                d=each[1]
            if each[2]=='':
                t='--'
            else:
                t=each[2]
            print '{:^10}'.format(each[0])+'{:^10}'.format(d)+'{:^10}'.format(t)
        else:
            print 'Group Tag:',each[0]
            print "--------------"
            for i in each[1]:
                if i[1]=='':
                    d='--'
                else:
                    d=i[1]
                if i[2]=='':
                    t='--'
                else:
                    t=i[2]
                print '{:^10}'.format(i[0])+'{:^10}'.format(d)+'{:^10}'.format(t)


def match_group_data(expected_group,actual_group):
    full_list=[]
    expected_key=list([x[0] for x in expected_group])
    actual_key=list([x[0] for x in actual_group])
    matched_key=list(set(expected_key) & set(actual_key))
    print matched_key

    unmatched_expected=filter(lambda x:x[0] not in matched_key,expected_group)
    unmatched_actual=filter(lambda x:x[0] not in matched_key,actual_group)

    matched_expected=filter(lambda x:x[0] in matched_key,expected_group)
    matched_actual=filter(lambda x:x[0] in matched_key,actual_group)

    for each in unmatched_expected:
        t=match_tuple_data(each[1],[])
        full_list.append((each[0],t))
    for each in unmatched_actual:
        t=match_tuple_data(each[1],[])
        full_list.append((each[0],t))

    for each in matched_key:
        m_e=filter(lambda x:x[0]==each,matched_expected)
        m_a=filter(lambda x:x[0]==each,matched_actual)
        e=[]
        for i in m_e:
            e=list(set(e+i[1]))
        a=[]
        for i in m_a:
            a=list(set(a+i[1]))
        t=match_tuple_data(e,a)
        full_list.append((each,t))
    return full_list
def match_tuple_data(expected_tuple,actual_tuple):
    all_match=False
    expected_key=list(set([x[0] for x in expected_tuple]))
    actual_key=list(set([x[0] for x in actual_tuple]))

    matched_key=list(set(expected_key) & set(actual_key))

    unmatched_expected=filter(lambda x:x[0] not in matched_key,expected_tuple)
    unmatched_actual=filter(lambda x:x[0] not in matched_key,actual_tuple)

    matched_expected=list(set(expected_tuple)-set(unmatched_expected))
    matched_actual=list(set(actual_tuple)-set(unmatched_actual))

    m=[]
    for each in matched_key:
        m_e=filter(lambda x:x[0]==each,matched_expected)
        m_a=filter(lambda x:x[0]==each,matched_actual)
        temp=list(set(m_e) & set(m_a))
        for e in temp:
            m.append((e[0],e[1],e[1]))
        m_e=list(set(m_e)-set(temp))
        m_a=list(set(m_a)-set(temp))

        for i in zip(m_e,m_a):
            m.append((each,i[0][1],i[1][1]))
    u_e=[(x[0],x[1],'') for x in unmatched_expected]
    u_a=[(x[0],'',x[1]) for x in unmatched_actual]

    full_list=list(set(m+u_e+u_a))
    return full_list


def main():
    expected=[('name','shetu'),('password','shetu'),('','')]
    actual=[('password','shetu'),('name','shetu')]
    f=compare_data(expected,actual)
    print f

    n=filter(lambda x:x[1]!=x[2],f)
    if n:
        print "failed"

if __name__=="__main__":
    main()