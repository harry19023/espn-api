class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data, progress):
        self.data = data
        # progress is a dict of {nfl_team_id: pct_complete} for NFL games
        # that are happening today
        self.progress = progress
        self._fetch_matchup_info()

    def __repr__(self):
        return 'Matchup(%s, %s)' % (self.home_team, self.away_team, )

    def _fetch_matchup_info(self):
        '''Fetch info for matchup'''
        self.home_team = self.data['home']['teamId']
        self.away_team = self.data['away']['teamId']

        # if totalPoints has a non-zero value, the fantasy game is over
        if self.data['home']['totalPoints'] != 0:
            self.home_score = self.data['home']['totalPoints']
            self.away_score = self.data['away']['totalPoints']
            self.home_minutes_remaining = 0
            self.away_minutes_remaining = 0
            self.home_score_projected = self.data['home']['totalPoints']
            self.away_score_projected = self.data['away']['totalPoints']
        else:  # the fantasy game is not over yet
            for team in ['home', 'away']:
                # players in the current scoring period have 2 states:
                # not yet played, and game started.
                # for not yet played, add 60 minutes to minutes remaining and
                # add player projections to projected score.
                # for game started, check the pct_complete of the game, and use
                # to calculate the minutes remaining and the projected points
                # for the rest of the game games that have finished are treated
                # as games started with pct_complete of 100%
                score_not_yet_played = 0
                score_in_progress_projected = 0
                score_actual = 0
                minutes_remaining = 0
                entries = self.data[team]['rosterForCurrentScoringPeriod']
                entries = entries['entries']
                for player in entries:
                    # these are bench and IR, we want starters only
                    if player['lineupSlotId'] not in [20, 21]:
                        player = player['playerPoolEntry']['player']
                        # if there is projected & actual stats, game has started
                        if len(player['stats']) > 1:
                            # check if 1st is actual or projected stats
                            if player['stats'][0]['statSourceId'] == 1:
                                proj = player['stats'][0]
                                curr = player['stats'][1]
                            else:
                                proj = player['stats'][1]
                                curr = player['stats'][0]
                            proj_total = proj['appliedTotal']
                            current_total = curr['appliedTotal']
                            pro_team_id = str(curr['proTeamId'])
                            score_actual += current_total
                            # if the NFL game is today, check the pct_complete
                            # if the NFL game isn't today, it's 100% complete
                            # and no minutes or projections needed
                            if pro_team_id in self.progress:
                                minutes_remaining += int(
                                    round(60 * (1 - self.progress[pro_team_id]),
                                          0)
                                )
                                # Multiply percent of game remaining by
                                # projected score to get projected future score
                                score_in_progress_projected += (
                                        (1 - self.progress[pro_team_id]) *
                                        proj_total
                                )
                        # if no proj stats (bye, injured)
                        elif len(player['stats']) < 1:
                            pass
                        # only projected stats, so NFL game hasn't started
                        else:
                            score_not_yet_played += (
                                player['stats'][0]['appliedTotal']
                            )
                            minutes_remaining += 60
                if team == 'home':
                    self.home_score = round(score_actual, 2)
                    self.home_score_projected = (
                        round(score_actual +
                              score_not_yet_played +
                              score_in_progress_projected,
                              2)
                    )
                    self.home_minutes_remaining = minutes_remaining
                else:
                    self.away_score = round(score_actual, 2)
                    self.away_score_projected = (
                        round(score_actual +
                              score_not_yet_played +
                              score_in_progress_projected
                              , 2)
                    )
                    self.away_minutes_remaining = minutes_remaining
