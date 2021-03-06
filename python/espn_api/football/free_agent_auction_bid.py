from datetime import datetime


class FreeAgentAuctionBid(object):
    def __init__(self, data, player_map, get_team_data):
        # print(data)
        status = data['status']
        if status == 'CANCELED' or status == 'PENDING':
            self.result = 'Canceled'
        else:
            if status == 'EXECUTED':
                self.result = 'Processed'
            elif status == 'FAILED_AUCTIONBUDGETEXCEEDED':
                self.result = 'Not enough FAAB remaining'
            elif status == 'FAILED_INVALIDPLAYERSOURCE':
                self.result = 'Outbid'
            elif status == 'FAILED_PLAYERALREADYDROPPED' or status == 'FAILED_ROSTERLIMIT':
                self.result = 'Player already dropped'

            else:  # Useful to store the new ESPN status for debug purposes
                self.result = status

            self.amount = data['bidAmount']
            self.time = datetime.fromtimestamp(int(data['processDate'] / 1000))  # convert from milliseconds to seconds
            self.teamId = data['teamId']
            self.dropped_player = None
            for item in data['items']:
                if item['type'] == 'ADD':
                    self.player = item['playerId']
                elif item['type'] == 'DROP' and self.result == 'Processed':
                    self.dropped_player = item['playerId']

    def __lt__(self, other):
        # sort by status, then bid amount
        result_ranking = {'Processed': 4,
                          'Not enough FAAB remaining': 3,
                          'Outbid': 2,
                          'Player already dropped': 1,
                          'CANCELLED': 0}
        if result_ranking[self.result] != result_ranking[other.result]:
            return result_ranking[self.result] < result_ranking[other.result]
        else:
            # sort by bid amount
            return self.amount < other.amount

    def __repr__(self):
        if self.result == 'Canceled':
            return 'Canceled bid'
        else:
            ret_string = 'FreeAgentAuctionBid(Player:{0}, Team:{1}, Result:{2}, Bid:{3}'.format(self.player, self.teamId,
                                                                                self.result, self.amount)
            if self.dropped_player:
                ret_string += ', Dropped:{0})'.format(self.dropped_player)
            else:
                ret_string += ')'
            return ret_string
