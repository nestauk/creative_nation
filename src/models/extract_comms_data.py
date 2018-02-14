bc = pd.read_csv('/Users/jmateosgarcia/Desktop/projects_2016/creative_nation/data/roxana/19_1_2018_business_totals.csv')
emp = pd.read_csv('/Users/jmateosgarcia/Desktop/projects_2016/creative_nation/data/roxana/19_1_2018_employment_totals.csv')

def get_relevant_data(df,name):
    df = df.loc[df.year=='2015_2016',['All creative industries','not_creative','ttwa_name']].set_index('ttwa_name')
    
    df['share'] = 100*df['All creative industries']/df.sum(axis=1)
    df['total_rank'] = df['All creative industries'].rank(ascending=False)
    df['share_rank'] = df['share'].rank(ascending=False)
    df = df[['All creative industries','total_rank','share','share_rank']]
    df.columns = [x+'_'+name for x in df.columns]
    return(df)

all_out = pd.concat([get_relevant_data(x,y) for x,y in zip([bc,emp],['business','empl'])],axis=1)

all_out.sort_values('share_rank_empl').to_csv(
    '/Users/jmateosgarcia/Desktop/projects_2016/creative_nation/data/roxana/{date}_comms_totals.csv'.format(date=today_str))

locs = []

for x in ['All creative industries_business','share_business','All creative industries_empl','share_empl']:
    #print(x)
    locations = all_out.sort_values(x,ascending=False).index[:10]
    
    #print(", ".join(all_out.sort_values(x,ascending=False).index[:10]))
    
    locs.append(locations)
    
    #print("\n")
    

    locations = set([x for el in locs for x in el])

    other_data = pd.read_csv(
    '/Users/jmateosgarcia/Desktop/projects_2016/creative_nation/data/roxana/19_1_2018_profile_numbers_official_2.csv',
index_col=0)

comms_table = pd.concat([all_out,other_data[['contribution']]],axis=1).loc[locations]

#comms_table = comms_table.loc[:,['rank' not in x for x in comms_table.columns]]

#comms_table['share_business'],comms_table['share_empl'] = [np.round(comms_table.loc[:,x],2) for x in
#                                                          ['share_business','share_empl']]

comms_table.columns = ['creative businesses','creative businesses RANK',
                       'businesses (% total)','businesses (% total) RANK',
                       'creative employment','creative employment RANK',
                      'creative employment (% total)','creative employment (% total) RANK',
                       'contribution']


comms_table.to_excel('/Users/jmateosgarcia/Desktop/5_feb_2018_creative_nation_top_places.xls')