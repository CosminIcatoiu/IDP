from flask import Flask, request
import mysql.connector
import json
import heapq
import threading
from copy import deepcopy

app = Flask(__name__)
global related_bets

@app.route('/place_bet/')
def place_bet() :
    global related_bets
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': '1x2_betandwin'
    }

    matches = request.args.getlist('matches')
    bets = request.args.getlist('bets')
    money = request.args.get('money')

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    odd = 1.0

    for i in range(len(matches)) :
        query = "SELECT " + str(bets[i]) + " FROM matches WHERE match_id='" + str(matches[i]) + "'"
        cursor.execute(query)
        res = cursor.fetchone()
        odd *= float(res[0])

        query = "SELECT * FROM bets where match_id='" + str(matches[i]) + "' and bet_type='" + \
            str(bets[i]) + "'"

        cursor.execute(query)

        result = cursor.fetchone()
        if result is None :
            query = "INSERT INTO bets VALUES('" + matches[i] + "', '" + str(bets[i]) + "', 1)"
            cursor.execute(query)
        elif int(result[2]) < 9 :
            query = "UPDATE bets SET number_of_bets=" + str(int(result[2]) + 1) + " WHERE match_id='" + \
                str(matches[i]) + "' and bet_type ='" + str(bets[i]) + "'"
            cursor.execute(query)
        else :
            query = "UPDATE bets SET number_of_bets = 1 WHERE match_id='" + \
                str(matches[i]) + "' and bet_type ='" + str(bets[i]) + "'"
            cursor.execute(query)
            cursor.execute('COMMIT')

            query = "UPDATE matches SET " + str(bets[i]) + "=" + str(bets[i]) + "-0.1 ,"
            for j in range(len(related_bets[bets[i]])) :
                query += str(related_bets[bets[i]][j]) + "=" + str(related_bets[bets[i]][j]) + "+0.1"
                if j != len(related_bets[bets[i]]) - 1 :
                    query += ", "
            query += " WHERE match_id='" + str(matches[i]) + "'" 
            cursor.execute(query)
        cursor.execute('COMMIT')

    query = "SELECT * FROM tickets"
    cursor.execute(query)

    result = cursor.fetchall()
    if result is None or len(result) == 0 :
        new_id = 1
    else :
        new_id = int(result[len(result) -1][0]) + 1

    ticket = ""
    for i in range(len(matches)) :
        ticket += str(matches[i]) + "=" + str(bets[i])
        if i != len(matches) - 1 :
            ticket += ","

    query = "INSERT INTO tickets VALUES('" + str(new_id) + "', '" + ticket + "')"

    cursor.execute(query)
    cursor.execute('COMMIT')

    cursor.close()
    connection.close()
    return json.dumps([new_id, odd * float(money)])

@app.route('/check_ticket/')
def check_ticket() :
    global related_bets
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': '1x2_betandwin'
    }

    ticket_id = request.args.get('ticket_id')

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "SELECT * FROM tickets WHERE ticket_id='" + str(ticket_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result == None :
        cursor.close()
        connection.close()
        return json.dumps(["No ticket with this id in the system"])

    bets = result[1].split(',')
    end_result = 1

    for bet in bets :
        match = bet.split('=')[0]
        bet_type = bet.split('=')[1]

        query = "SELECT result, goals_result from results where match_id='" + str(match) + "'"
        cursor.execute(query)

        r = cursor.fetchone()
        if r is None or len(r) == 0 :
            end_result = 2
        else :
            if bet_type != r[0] and bet_type != r[1] :
                query = "DELETE from tickets WHERE ticket_id='" + str(ticket_id) + "'"
                cursor.execute(query)
                cursor.execute("COMMIT")
                cursor.close()
                connection.close()
                return json.dumps(["Ticket lost! Try again!"])

    if end_result == 2 :
        cursor.close()
        connection.close()
        return json.dumps(["You have matches on the ticket that haven't been played yet."])

    query = "DELETE from tickets WHERE ticket_id='" + str(ticket_id) + "'"
    cursor.execute(query)
    cursor.execute("COMMIT")
    cursor.close()
    connection.close()
    return json.dumps(['Winning ticket! Congratulations!'])

@app.route('/cancel_ticket/')
def cancel_ticket() :
    global related_bets
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': '1x2_betandwin'
    }

    ticket_id = request.args.get('ticket_id')

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "SELECT * FROM tickets WHERE ticket_id='" + str(ticket_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result is None :
        cursor.close()
        connection.close()
        return json.dumps(["No ticket with this id in the system"])

    bets = result[1].split(',')

    for bet in bets :
        match = bet.split('=')[0]
        bet_type = bet.split('=')[1]

        query = "SELECT result, goals_result from results where match_id='" + str(match) + "'"
        cursor.execute(query)

        r = cursor.fetchone()
        if r is None or len(r) == 0 :
            cursor.close()
            connection.close()
            return json.dumps(["Some of your matches have already started. You can't cancel the ticket anymore."])

    for bet in bets :
        match = bet.split('=')[0]
        bet_type = bet.split('=')[1]

        query = "UPDATE bets SET number_of_bets=number_of_bets-1 WHERE match_id='" + str(ticket_id) +\
             "' and bet_type='" + str(bet_type) + "'"
        cursor.execute(query)
        cursor.execute("COMMIT")

    query = "DELETE from tickets WHERE ticket_id='" + str(ticket_id) + "'"
    cursor.execute(query)
    cursor.execute("COMMIT")
    cursor.close()
    connection.close()
    return json.dumps(['Your ticket has been canceled'])

@app.route('/print_matches/')
def print_matches() :
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': '1x2_betandwin'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "SELECT * FROM matches"
    cursor.execute(query)

    result = []
    while True :
        r = cursor.fetchone()
        if r is None :
            break
        result.append(list(r))

    cursor.close()
    connection.close()
    return json.dumps(result)



if __name__ == '__main__':
    global related_bets
    related_bets = {}
    related_bets['home_victory'] = ['away_victory', 'draw']
    related_bets['away_victory'] = ['home_victory', 'draw']
    related_bets['draw'] = ['home_victory', 'away_victory']
    related_bets['under_2_goals'] = ['2_3_goals', 'over_3_goals']
    related_bets['2_3_goals'] = ['under_2_goals', 'over_3_goals']
    related_bets['over_3_goals'] = ['under_2_goals', '2_3_goals']

    app.run(host='0.0.0.0', port=80)
