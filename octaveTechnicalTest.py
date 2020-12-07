import json
import re
import sys
import urllib.request
from statistics import mean, median
from datetime import datetime, date, timedelta
import math

asteroidUrl = 'https://api.nasa.gov/neo/rest/v1/feed?start_date={}&end_date={}&' \
                  'api_key=3kgPFpxYiWKRc4wDNJFRbCLodLaobsI1kWzwcVVq'

def main():
    # Defaults provided for test
    infoStartDate = '2019-10-31'
    infoStopDate = '2019-11-02'
    statsStartDate = '2020-09-10'
    statsEndDate = '2020-09-17'
    numHazAsteroids = 3

    if len(sys.argv) == 6:
        infoDateDiff = datetime.strptime(sys.argv[2], '%Y-%m-%d') - datetime.strptime(sys.argv[1], '%Y-%m-%d')
        statsDateDiff = datetime.strptime(sys.argv[4], '%Y-%m-%d') - datetime.strptime(sys.argv[3], '%Y-%m-%d')
        if infoDateDiff.days > 7 or statsDateDiff.days > 7:
            print("Date limit is only 7 days, please reduce time range")
            return
        infoStartDate = sys.argv[1]
        infoStopDate = sys.argv[2]
        statsStartDate = sys.argv[3]
        statsEndDate = sys.argv[4]
        numHazAsteroids = abs(int(sys.argv[5]))
    elif len(sys.argv) != 1:
        print("Run this program with either 0 arguments for defaults, or 5 arguments. See README for proper format")
        return

    getAsteroidInformation(infoStartDate, infoStopDate)
    getVelocityStatistics(statsStartDate, statsEndDate)
    getMostRecentPotentHazardous(numHazAsteroids)
    return

def getAsteroidInformation(startDate, endDate):
    print('Part 1')
    urlResponse = urllib.request.urlopen(asteroidUrl.format(startDate, endDate))
    data = json.loads(urlResponse.read())
    print('asteroid name | id | close_approach_date_full')
    for asteroidData in data['near_earth_objects'].values():
        for asteroidDict in asteroidData:
            print(asteroidDict['name'] + '\t\t| ' + asteroidDict['id'] + '\t| '
                  + asteroidDict['close_approach_data'][0]['close_approach_date_full'])
    return

def getVelocityStatistics(startDate, endDate):
    print('\nPart 2')
    urlResponse = urllib.request.urlopen(asteroidUrl.format(startDate, endDate))
    data = json.loads(urlResponse.read())
    # Another option is to take the raw text, and strip out the content with kilometers_per_second, but testing
    # the runtime showed that the difference was negligible. If done the other way, it would look like:
    # asteroidString = urlResponse.read().decode('utf-8')
    # velocities = re.findall(r'"kilometers_per_second":"(.*?)"', asteroidString)
    velocities = []
    for asteroidData in data['near_earth_objects'].values():
        for asteroidDict in asteroidData:
            velocities.append(float(asteroidDict['close_approach_data'][0]['relative_velocity']['kilometers_per_second']))

    # Emailed Troy, it was unclear if built in functions included max/min/mean/median, which make this extremely easy,
    # so just to be safe, I will show both ways
    velocities.sort()
    print('Highest velocity:\tby hand: ' + str(velocities[-1]) + '\tby function: ' + str(max(velocities)))
    print('Lowest velocity:\tby hand: ' + str(velocities[0]) + '\tby function: ' + str(min(velocities)))
    print('Mean velocity:  \tby hand: ' + str(sum(velocities)/len(velocities)) + '\tby function: ' + str(mean(velocities)))
    print('Median velocity:\tby hand: ' + str(velocities[math.floor(len(velocities)/2)]) + '\tby function: ' + str(median(velocities)))
    return

def getMostRecentPotentHazardous(numAsteroids):
    print('\nPart 3')
    endDate = date.today()
    startDate = endDate - timedelta(7)
    urlResponse = urllib.request.urlopen(asteroidUrl.format(startDate, endDate))
    asteroidString = urlResponse.read().decode('utf-8')
    hazardous = re.findall(r'"is_potentially_hazardous_asteroid":true', asteroidString)
    if len(hazardous) < numAsteroids:
        print("Requested {} recent potential hazardous asteroids. In the last week there were only {}".format(numAsteroids, len(hazardous)))
        numAsteroids = len(hazardous)

    hazardousAsteroids = []
    data = json.loads(asteroidString)
    for asteroidData in data['near_earth_objects'].values():
        for asteroidDict in asteroidData:
            if asteroidDict['is_potentially_hazardous_asteroid'] == True:
                hazardousAsteroids.append([asteroidDict['id'],
                                           datetime.strptime(asteroidDict['close_approach_data'][0]['close_approach_date_full'], '%Y-%b-%d %H:%M')])

    hazardousAsteroids = sorted(hazardousAsteroids, key=lambda x: x[1], reverse=True)[:numAsteroids]
    print('Asteroid id | close_approach_date_full')
    for asteroid in hazardousAsteroids:
        print(asteroid[0], '|', str(asteroid[1]))
    return

if __name__ == '__main__':
    main()


