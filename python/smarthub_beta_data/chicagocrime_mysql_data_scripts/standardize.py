csv_writer = open('data.csv', 'w+')
csv_writer.write('id_,latitude,longitude,neighborhood,crime,location,month,date,year,day,time,interval,season\n')
with open('data_revised.csv', 'rt') as f:
    for line in f:
        id_, latitude, longitude, neighborhood, crime, location, month, date, year, day, time, interval = line.split(
            ',')

        if id_ == 'id_':
            continue

        # neighborhood
        neighborhood = neighborhood.lower()
        neighborhood = neighborhood.replace(' ', '-')
        if neighborhood == 'near-west':
            neighborhood = 'near-west-side'
        neighborhood = neighborhood.replace(' ', '-')

        # crime (Knowledgebase has 31 values, but "ritualism, human-trafficking, and criminal-abortion are not in database"; hence 28 effective values)
        crime = crime.lower()
        crime = crime.strip()
        crime = crime.replace(' ', '-')
        if crime == 'crim-sexual-assault':
            crime = 'criminal-sexual-assault'

        if crime == 'deceptive-practice':
            crime = 'deceptive-practices'

        if crime == 'other-narcotic-violation':
            crime = 'narcotics'

        if crime == 'non---criminal':
            crime = 'non-criminal'

        # location (Knowledgebase has 58 values, but "aircraft, look-up facility, vehicle are not in database"; hence 55 effective values)
        location = location.lower()
        location = location.strip()
        location = location.replace(' ', '-')

        if location == 'airport-vending-establishment':
            location = 'airport'

        if location == 'cha-apartment':
            location = 'apartment'

        if location == 'church/synagogue/place-of-worship':
            location = 'church'

        if location == 'commercial-/-business-office':
            location = 'commercial'

        if location == 'cta-bus':
            location = 'c_t_a-bus'

        if location == 'cta-bus-stop':
            location = 'c_t_a-other-property'

        if location == 'cta-garage-/-other-property':
            location = 'c_t_a-garage'

        if location == 'cta-platform':
            location = 'c_t_a-other-property'

        if location == 'cta-station':
            location = 'c_t_a-other-property'

        if location == 'cta-tracks---right-of-way':
            location = 'c_t_a-other-property'

        if location == 'cta-train':
            location = 'c_t_a-train'

        if location == 'cha-hallway/stairwell/elevator':
            location = 'elevator'

        if location == 'hotel/motel':
            location = 'motel'

        if location == 'jail-/-lock-up-facility':
            location = 'jail'

        if location == 'lakefront/waterfront/riverbank':
            location = 'waterfront'

        if location == 'cha-parking-lot':
            location = 'parking-lot'

        if location == 'cha-parking-lot/grounds':
            location = 'parking-lot'

        if location == 'parking-lot/garage(non.resid.)':
            location = 'garage'

        if location == 'residence-porch/hallway':
            location = 'porch'

        if location == 'sports-arena/stadium':
            location = 'arena'

        if location == 'vacant-lot/land':
            location = 'vacant-land'

        if location == 'house':
            location = 'residence'

        if location == 'retail-store':
            location = 'small-retail-store'

        # time is on 24 hour clock but we need ex: 3-P_M insetad of 15 o'clock
        '''time_final = ''
        time_init = int(time)
        if time_init == 0:
            time_final = 'midnight'

        elif time_init == 12:
            time_final = 'noon'

        elif time_init < 12:
            time_final = ''.join( (time,'-A_M'))

        elif time_init > 12:
            time_final = ''.join( (time,'-P_M'))'''

        time_int = int(time)
        if time_int == 0:
            time = 'midnight'

        elif time_int == 12:
            time = 'noon'

        elif time_int < 12:
            time = str(time_int) + '-a_m'

        elif time_int > 12:
            time_int = time_int - 12
            time = str(time_int) + '-p_m'

        # interval defined as evening (6-P_M to midnight), afternoon (noon to 6-P_M), night (midnight to 6-A_M), morning (6-A_M to noon)
        interval = interval.lower()
        interval = interval.strip()

        if interval == 'evening':
            interval = '6-p_m-midnight'
        elif interval == 'afternoon':
            interval = 'noon-6-p_m'
        elif interval == 'night':
            interval = 'midnight-6-p_m'
        elif interval == 'morning':
            interval = '6-a_m-noon'

        # season
        month = month.lower()
        month = month.strip()
        season = ''
        if month == 'september' or month == 'october' or month == 'november':
            season = 'fall'
        if month == 'december' or month == 'january' or month == 'february':
            season = 'winter'
        if month == 'march' or month == 'april' or month == 'may':
            season = 'spring'
        if month == 'june' or month == 'july' or month == 'august':
            season = 'summer'

        # day
        day = day.lower()
        day = day.strip()

        data = id_ + ',' + latitude + ',' + longitude + ',' + neighborhood + ',' + crime + ',' + location + ',' + month + ',' + date + ',' + year + ',' + day + ',' + time + ',' + interval + ',' + season + '\n'
        csv_writer.write(data)

csv_writer.close()
