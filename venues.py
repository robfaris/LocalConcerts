from bs4 import BeautifulSoup 
import requests
from pandas import DataFrame
from datetime import datetime


#TODO:
#SCRAPE USEFUL BAND CONCERT DATA FROM EACH VENUE SITE
#ASSEMBLE BAND CONCERT DATA IN DICT/CLASS OBJECT
#FORMAT AS SPREADSHEET/GOOGLE DOC ?
#REVIEW AND UPDATE SPREADSHEET WITH NEW BANDS

BLACK_CAT = ["The Black Cat","https://www.blackcatdc.com/schedule.html"]
THE_ANTHEM = ["The Anthem", "https://theanthemdc.com/calendar/"]
NINE_THIRTY= ["The 9:30 Club", "https://www.930.com/"]
STATE_THEATER = ["The State Theater", "http://www.thestatetheatre.com/events/upcoming_events.xml"]
#state theater next page looks like this, offset incremented by 8 each time -- http://www.thestatetheatre.com/events/upcoming_events.xml?_offset=8&_order=1
UNION_STAGE = ["Union Stage", "https://www.unionstagepresents.com/union-stage/"]
WOLFTRAP = ["Wolftrap", "https://www.wolftrap.org/calendar.aspx"]
BIRCHMERE = ["Birchmere", "https://www.birchmere.com/calendar/"]

local_music = []

def monthToNum(shortMonth):
    return {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9, 
            'oct': 10,
            'nov': 11,
            'dec': 12,
            'january': 1,
            'february': 2,
            'march': 3,
            'april': 4,
            'may': 5,
            'june': 6,
            'july': 7,
            'august': 8,
            'september': 9,
            'october': 10,
            'november': 11,
            'december': 12
    }[shortMonth]

def basescraper(venue):
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
    re = requests.get(venue[1], headers=headers)
    soup = BeautifulSoup(re.text, "html.parser")
    return soup

def black_cat_maker():
    bc_band_content = basescraper(BLACK_CAT).find_all('div', {'class': 'show-details'})

    bc_list = []

    for band in bc_band_content: 
        tickets = "Available"
        if band.find('h1').find('a'):
            band_name = band.find('h1').find('a').getText().title()
        if band.find('h2', {'class' : 'date'}):
            unformatted_date = band.find('h2', {'class' : 'date'}).getText().title().split(' ', 1)[1]
            month = monthToNum(unformatted_date.split(' ',1)[0].lower())
            day = unformatted_date.split(' ',1)[1]
            date = f"{month}-{day}"
        if band.find('p'):
            try: 
                cost = int(band.find('p').getText()[1:3])
            except:
                cost = None
        if '**SOLD OUT**' in band.text:
            tickets = "SOLD OUT"
        bc_list.append({
            'date' : date,
            'name' : band_name,
            'cost' : cost,
            'venue': BLACK_CAT[0],
            'tickets' : tickets,
            'link' : BLACK_CAT[1]
        })
    return bc_list

def anthem_maker():
    band_content = basescraper(THE_ANTHEM).find_all('div', {'class': 'event'})

    list = []
    for band in band_content: 
        tickets = "Available"
        if band.find('div').find('h3').find('a'):
            band_name = band.find('div').find('h3').find('a').getText().title()
            if " – " in band_name:
                band_name = band_name.split(" – ", 1)[0]
        if band.find('div', {'class' : 'event__date'}):
            date = band.find('div', {'class' : 'event__date'}).getText().title()
        if band.find('div' , {'class' : 'event__tickets'}).find('p'):
            try: 
                cost = int(band.find('div' , {'class' : 'event__tickets'}).find('p').getText().split('.', 1)[0][1:])
            except:
                cost = None
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"
        list.append({
            'date' : date.replace('/',"-"),
            'name' : band_name,
            'cost' : cost,
            'venue' : THE_ANTHEM[0],
            'tickets' : tickets,
            'link' : THE_ANTHEM[1]

        })
    return list

def nine_thirty_maker():
    band_content = basescraper(NINE_THIRTY).find('div' , {'id': 'upcoming-listview'}).find_all('article', {'class': 'event-status-live'})

    list = []
    cost = None
    for band in band_content: 
        tickets = "Available"
        if band.find('article' , {'class' : 'artist-info'}):
            band_name = band.find('article' , {'class' : 'artist-info'}).find('a').getText().title()
            if " - " in band_name:
                band_name = band_name.split(" - ", 1)[0]
            elif ":" in band_name:
                band_name = band_name.split(":", 1)[0]
        if band.find('span', {'class' : 'dates'}):
            date_full = band.find('span', {'class' : 'dates'}).getText().replace(" ","")
            day = int(date_full[4:7])
            mon = monthToNum(date_full[7:10].lower())
            date = f"{mon}-{day}"
        if band.find('span' , {'class' : 'price-range'}):
            try: 
                cost = band.find('span' , {'class' : 'price-range'}).getText().split(".", 1)[0][1:]
            except:
                cost = None
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"

        list.append({
            'date' : date.replace('\n','').strip(),
            'name' : band_name.replace('\n','').strip(),
            'cost' : cost,
            'venue' : NINE_THIRTY[0],
            'tickets': tickets,
            'link' : NINE_THIRTY[1]
        })
    return list    

def state_maker():
    page_1 = basescraper(STATE_THEATER).find_all('div' , {'class' : 'box'})
    x = "8"
    state_theater_page = [STATE_THEATER[0] , STATE_THEATER[1] + "?_offset=" + x + "&_order=1"]
    page_2 = basescraper(state_theater_page).find_all('div' , {'class' : 'box'})
    x = "16"
    page_3 = basescraper(state_theater_page).find_all('div' , {'class' : 'box'})
    band_content = page_1 + page_2 + page_3

    list = []
    cost = None
    for band in band_content: 
        tickets = "Available"
        if band.find('h4'):
            band_name = band.find('h4').getText().title()
            if " - " in band_name:
                band_name = band_name.split(" - ", 1)[0]
            elif ":" in band_name:
                band_name = band_name.split(":", 1)[0]
        if band.find('div', {'class' : 'date'}):
            date_full = band.find('div', {'class' : 'date'}).getText().replace("/","-")
            date = date_full[4:]
        cost = None
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"

        list.append({
            'date' : date.strip(),
            'name' : band_name,
            'cost' : cost,
            'venue' : STATE_THEATER[0],
            'tickets': tickets,
            'link' : STATE_THEATER[1]
        })
    return list    

def union_maker():
    band_content = basescraper(UNION_STAGE).find_all('div' , {'class': 'card'})

    list = []
    cost = None
    for band in band_content: 
        tickets = "Available"
        if band.find('h4'):
            band_name = band.find('h4').getText().title()
            if " - " in band_name:
                band_name = band_name.split(" - ", 1)[0]
            elif ":" in band_name:
                band_name = band_name.split(":", 1)[0]
        if band.find('span', {'class' : 'date'}):
            date_full = band.find('span', {'class' : 'date'}).getText()
            day = int(date_full[3:])
            mon = monthToNum(date_full[0:3].lower())
            date = f"{mon}-{day}"
        cost = None
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"
        if "canceled" in band_name.lower() or "private event" in band_name.lower():
            pass
        else:
            list.append({
                'date' : date.strip(),
                'name' : band_name,
                'cost' : cost,
                'venue' : UNION_STAGE[0],
                'tickets': tickets,
                'link' : UNION_STAGE[1]
            })
    return list   

def wolftrap_maker():
    band_content = basescraper(WOLFTRAP).find_all('article' , {'class': 'event-card'})

    list = []
    cost = None
    for band in band_content: 
        tickets = "Available"
        if band.find('h3'):
            band_name = band.find('h3').getText().title().strip()
            if " - " in band_name:
                band_name = band_name.split(" - ", 1)[0]
            elif ":" in band_name:
                band_name = band_name.split(":", 1)[0]
        if band.find('span', {'class' : 'event-card__date'}):
            full_date = band.find('span', {'class' : 'event-card__date'}).getText().strip()
            un_full_date = full_date.split("|", 1)[0].rstrip().replace("/", "-")[-5:]
            if "y" in un_full_date:
                date = un_full_date.replace("y", "").strip()
            else:
                date = un_full_date.strip()
        cost = None
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"
            print("something was sold out at least")

        list.append({
            'date' : date,
            'name' : band_name,
            'cost' : cost,
            'venue' : WOLFTRAP[0],
            'tickets': tickets,
            'link' : WOLFTRAP[1]
        })
    return list   

def birchmere_maker():
    band_content = basescraper(BIRCHMERE).find_all('div' , {'class': 'tribe-events-calendar-list__event-details tribe-common-g-col'})

    list = []
    cost = None
    for band in band_content: 
        tickets = "Available"
        if band.find('h3'):
            band_name = band.find('h3').getText().title().strip()
            if " - " in band_name:
                band_name = band_name.split(" - ", 1)[0]
            elif ":" in band_name:
                band_name = band_name.split(":", 1)[0]
        if band.find('time'):
            date = band.find('time').get('datetime')[5:]
        if band.find('span' , {'class' : 'tribe-events-c-small-cta__price'}):
            try: 
                cost = band.find('span' , {'class' : 'tribe-events-c-small-cta__price'}).getText().split(".", 1)[0][1:]
            except:
                cost = None        
        if 'sold out' in band.text.lower():
            tickets = "SOLD OUT"

        list.append({
            'date' : date,
            'name' : band_name,
            'cost' : cost,
            'venue' : BIRCHMERE[0],
            'tickets': tickets,
            'link' : BIRCHMERE[1]
        })
    return list 

combined_local_music = black_cat_maker() + anthem_maker() + nine_thirty_maker() + state_maker() + union_maker() + wolftrap_maker() + birchmere_maker()

#REFORMATS DATES
for conc in combined_local_music:
    un_month = int(conc["date"].split("-", 1)[0])
    if un_month < int(datetime.today().strftime('%m')):
        conc["date"] = conc["date"] + "-" + str(int(datetime.today().strftime('%Y')) + 1)
    else:
        conc["date"] = conc["date"] + "-" + datetime.today().strftime('%Y')
    conc["date"] = datetime.strptime(conc["date"], "%m-%d-%Y")

local_music = sorted(combined_local_music, key=lambda d: d['date'])

#CHECKS FOR NEWLY SOLD OUT CONCERTS
sheety_get_url = "https://api.sheety.co/7acba122ea77e5543ad47b19ef940e3e/thingsToDo/bands"

sheety_response = requests.get(url=sheety_get_url).json()

old_available = []
for row in sheety_response["bands"]:
    if row["tickets"] == "Available":
        line = f"{row['name']} on {row['date']}"
        old_available.append(line)

new_sold_out = []
for new in local_music:
    if new["tickets"] == "SOLD OUT":
        liner = f"{new['name']} on {new['date'].date()}"
        new_sold_out.append(liner)

print("New bands sold out: " +  str(set(new_sold_out) - set(old_available)))


print(len(local_music))


df = DataFrame(local_music)


df.to_excel('band_spreadsheet.xlsx', sheet_name='sheet1', index=False)