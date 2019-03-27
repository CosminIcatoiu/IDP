import json
import requests
import sys

def print_table(items, header=None, wrap=True, max_col_width=20, wrap_style="wrap", row_line=False, fix_col_width=False):
    if fix_col_width:
        c2maxw = dict([(i, max_col_width) for i in range(len(items[0]))])
        wrap = True
    elif not wrap:
        c2maxw = dict([(i, max([len(str(e[i])) for e in items])) for i in range(len(items[0]))])
    else:
        c2maxw = dict([(i, min(max_col_width, max([len(str(e[i])) for e in items])))
                        for i in range(len(items[0]))])
    if header:
        current_item = -1
        row = header
        if wrap and not fix_col_width:
            for col, maxw in c2maxw.iteritems():
                c2maxw[col] = max(maxw, len(header[col]))
                if wrap:
                    c2maxw[col] = min(c2maxw[col], max_col_width)
    else:
        current_item = 0
        row = items[current_item]
    while row:
        is_extra = False
        values = []
        extra_line = [""]*len(row)
        for col, val in enumerate(row):
            cwidth = c2maxw[col]
            wrap_width = cwidth
            val = str(val)
            try:
                newline_i = val.index("\n")
            except ValueError:
                pass
            else:
                wrap_width = min(newline_i+1, wrap_width)
                val = val.replace("\n", " ", 1)
            if wrap and len(val) > wrap_width:
                if wrap_style == "cut":
                    val = val[:wrap_width-1]+"+"
                elif wrap_style == "wrap":
                    extra_line[col] = val[wrap_width:]
                    val = val[:wrap_width]
            val = val.ljust(cwidth)
            values.append(val)
        print(' | '.join(values))
        if not set(extra_line) - set(['']):
            if header and current_item == -1:
                print(' | '.join(['='*c2maxw[col] for col in range(len(row)) ]))
            current_item += 1
            try:
                row = items[current_item]
            except IndexError:
                row = None
        else:
            row = extra_line
            is_extra = True
 
        if row_line and not is_extra and not (header and current_item == 0):
            if row:
                print(' | '.join(['-'*c2maxw[col] for col in range(len(row)) ]))
            else:
                print(' | '.join(['='*c2maxw[col] for col in range(len(extra_line)) ]))


if __name__ == "__main__":
    while True :

        operation = input("Hello dear better! May the odds be in your favour! " +\
            "Choose an operation between: place_bet, check_ticket, cancel_ticket and check_matches.\n")
        if operation == 'place_bet' :
            bets = {}
            while True :

                match = input("Please introduce the id of the match you want to bet on. If you have introduced " +\
                    "all the matches you wanted to bet on just hit enter.\n")
                if match == '' :
                    break

                if match in bets :
                    bet_type = input("You have already placed a bet on this match. You are not allowed to place more" +\
                        " than a bet on a match. If you want to change the bet type introduce the new one. Otherwise, " +\
                        " leave the field blank.\n")
                    if bet_type != '' :
                        bets[match] = bet_type
                else :
                    while True :
                        bet_type = input("Please specify the type of bet you want to make on this match.\n")
                        if bet_type != '':
                            bets[match] = bet_type
                            break
            money = input("Please specify the amount of money you want to bet. There is a minimum sum of 2$.\n")
            req = "http://" + sys.argv[1] + ":80/place_bet/?"
            index = 0
            for match in bets :
                if index == 0 :
                    req += "matches=" + match
                else :
                    req += "&matches=" + match

                req += "&bets=" + bets[match]
                index += 1
            req += "&money=" + str(money)

            r = requests.get(req)

            print("Thank you! Your ticket id that you can use for checking your ticket or for canceling it is: " +
                str(r.json()[0]) + " and the amount of money you can win is: " + str(r.json()[1]) + ".\n")
        elif operation == 'check_ticket' :
            tickets = []
            while True :
                ticket_id = input("Introduce the ticket id. If you finished all the ids hit enter.\n")
                if ticket_id == '' :
                    break
                else :
                    tickets.append(ticket_id)
            
            for i in range(len(tickets)) :
                req = "http://" + sys.argv[1] + ":80/check_ticket/?"
                req += "ticket_id=" + tickets[i]
                r = requests.get(req)
                print("Ticket " + tickets[i] + ": " + str(r.json()[0]))
        elif operation == "cancel_ticket" :
            tickets = []
            while True :
                ticket_id = input("Introduce the ticket id. If you finished all the ids hit enter.\n")
                if ticket_id == '' :
                    break
                else :
                    tickets.append(ticket_id)            
            for i in range(len(tickets)) :
                req = "http://" + sys.argv[1] + ":80/cancel_ticket/?"
                req += "ticket_id=" + tickets[i]
                r = requests.get(req)
                print("Ticket " + tickets[i] + ": " + str(r.json()[0]))
        elif operation == "check_matches" :
            req = "http://" + sys.argv[1] + ":80/print_matches/"
            r = requests.get(req)
            if r.json() == [] :
                print("There are no matches available for the moment.\n")
            else :
                print_table(r.json(),
                    header=[ "Match ID", "Home Team", "Away Team", "Home Victory", "Draw", "Away Victory", "Under 2 Goals", "2-3 Goals", "Over 3 Goals"],
                    wrap=True, max_col_width=15, wrap_style='wrap',
                    row_line=True, fix_col_width=True)
        else :
            print("The introduced operation is not valid!\n")
