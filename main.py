import venues as v
from pandas import DataFrame
from datetime import datetime

combined_local_music = v.black_cat_maker() + v.anthem_maker() + v.nine_thirty_maker() + v.state_maker() + v.union_maker() + v.wolftrap_maker() + v.birchmere_maker()

#REFORMATS DATES
for conc in combined_local_music:
    un_month = int(conc["date"].split("-", 1)[0])
    if un_month < int(datetime.today().strftime('%m')):
        conc["date"] = conc["date"] + "-" + str(int(datetime.today().strftime('%Y')) + 1)
    else:
        conc["date"] = conc["date"] + "-" + datetime.today().strftime('%Y')
    conc["date"] = datetime.strptime(conc["date"], "%m-%d-%Y")

local_music = sorted(combined_local_music, key=lambda d: d['date'])

print(len(local_music))

df = DataFrame(local_music)

df.to_excel('band_spreadsheet.xlsx', sheet_name='sheet1', index=False)