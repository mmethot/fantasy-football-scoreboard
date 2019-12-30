from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
import time
import debug

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        # use this to check if week has changed
        self.week = data.week
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def render(self):
        while True:
            # todo: check for draft
            # self.__render_draft()
            # weeks 1-16, in season
            if self.data.week < 17:
                debug.info('In season state')
                self.__render_game()
            # weeks 17+, off season
            else:
                debug.info('Off season state')
                self.__render_off_season()

    def __render_game(self):
        # check if thursday and before 7pm est -> figure this out in utc
        time = self.data.get_current_date()
        if time.weekday() == 3 and time.hour >= 13:
            debug.info('Scheduled State')
            self._draw_pregame()
            time.sleep(1800)
        # thursday before 8pm est
        elif time.weekday() == 4 and 0 <= time.hour <= 1:
            debug.info('Pre-Game State')
            self._draw_pregame()
            time.sleep(60)
        # tuesday 1am until week change
        elif (time.weekday() == 1 and time.hour > 5) or (1 < time.weekday() < 4):
            debug.info('Final State')
            self._draw_post_game()
            # sleep 6 hours
            time.sleep(21600)
        # thursday after 8pm est until tuesday 1am (hopefully else should catch it)
        else:
            debug.info('Live State')
            # Draw the current game
            self._draw_game()
        debug.info('ping render_game')

    def __render_off_season(self):
        debug.info('ping_day_off')
        self._draw_off_season()
        time.sleep(86400) # sleep 24 hours

    # need to keep working on this
    def _draw_pregame(self):
        # get the matchup
        # get the matchup pics and resize them to 32x32
        if self.data.matchup:
            matchup = self.data.matchup
            # show a countdown?
            # game_time_pos = center_text(self.font_mini.getsize(game_time)[0], 32)
            opp_team_logo_pos = { "x": -15, "y": 0 }
            user_team_logo_pos = { "x": 45, "y": 0 }
            # Open the logo image file
            opp_team_logo = Image.open('logos/{}.png'.format(matchup['opp_av'])).resize((32, 32), 1)
            user_team_logo = Image.open('logos/{}.png'.format(matchup['user_av'])).resize((32, 32), 1)
            # Draw the text on the Data image.
            self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
            # self.draw.multiline_text((period_position, -1), period, fill=(255, 255, 255), font=self.font_mini, align="center")
            # self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(opp_team_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
            self.canvas.SetImage(user_team_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
    #
        # if self.data.get_schedule() != 0:

        #     overview = self.data.schedule

        #     # Save when the game start
        #     game_time = overview['game_time']

        #     # Center the game time on screen.
        #     game_time_pos = center_text(self.font_mini.getsize(game_time)[0], 32)

        #     # Set the position of each logo
        #     away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
        #     home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

        #     # Open the logo image file
        #     away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
        #     home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

        #     # Draw the text on the Data image.
        #     self.draw.text((22, -1), 'TODAY', font=self.font_mini)
        #     self.draw.multiline_text((game_time_pos, 5), game_time, fill=(255, 255, 255), font=self.font_mini, align="center")
        #     self.draw.text((25, 13), 'VS', font=self.font)

        #     # Put the data on the canvas
        #     self.canvas.SetImage(self.image, 0, 0)

        #     # Put the images on the canvas
        #     self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
        #     self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

        #     # Load the canvas on screen.
        #     self.canvas = self.matrix.SwapOnVSync(self.canvas)

        #     # Refresh the Data image.
        #     self.image = Image.new('RGB', (self.width, self.height))
        #     self.draw = ImageDraw.Draw(self.image)
        # else:
        #     #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
        #     self.draw.line((0, 0) + (self.width, 0), fill=128)
        #     self.canvas = self.matrix.SwapOnVSync(self.canvas)
        #     time.sleep(60)  # sleep for 1 min
        #     # Refresh canvas
        #     self.image = Image.new('RGB', (self.width, self.height))
        #     self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):
        self.data.refresh_matchup()
        matchup = self.data.matchup
        user_score = matchup['user_score']
        opp_score = matchup['opp_score']
        while True:
            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game matchup')
                self.data.refresh_matchup()
                self.data.needs_refresh = False
            if self.data.matchup:
                matchup = self.data.matchup
                # Use This code if you want the goal animation to run only for your fav team's goal
                # if self.data.fav_team_id == overview['home_team_id']:
                #     if overview['home_score'] > home_score:
                #         self._draw_big_play()
                # else:
                #     if overview['away_score'] > away_score:
                #         self._draw_big_play()
                # Use this code if you want the goal animation to run for both team's goal.
                # Run the goal animation if there is a goal.
                if matchup['user_score'] > user_score or matchup['opp_score'] > opp_score:
                   self._draw_big_play()
                # Prepare the data
                score = '{}-{}'.format(matchup['opp_score'], matchup['user_score'])
                # Set the projections on the screen?
                # time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 32)
                score_position = center_text(self.font.getsize(score)[0], 32)
                # period_position = center_text(self.font_mini.getsize(period)[0], 32)
                # Set the position of each logo on screen.
                opp_team_logo_pos = { "x": -15, "y": 0 }
                user_team_logo_pos = { "x": 45, "y": 0 }
                # Open the logo image file
                opp_team_logo = Image.open('logos/{}.png'.format(matchup['opp_av'])).resize((32, 32), 1)
                user_team_logo = Image.open('logos/{}.png'.format(matchup['user_av'])).resize((32, 32), 1)
                # Draw the text on the Data image.
                self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
                # self.draw.multiline_text((period_position, -1), period, fill=(255, 255, 255), font=self.font_mini, align="center")
                # self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")
                # Put the data on the canvas
                self.canvas.SetImage(self.image, 0, 0)
                # Put the images on the canvas
                self.canvas.SetImage(opp_team_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
                self.canvas.SetImage(user_team_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                # Save the scores.
                opp_score = matchup['opp_score']
                user_score = matchup['user_score']
                self.data.needs_refresh = True
                time.sleep(10)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(60)  # sleep for 1 min

    def _draw_post_game(self):
        self.data.refresh_matchup()
        if self.data.matchup != 0:
            matchup = self.data.matchup
            # Prepare the data
            game_date = 'WEEK {}'.format(self.data.week)
            score = '{}-{}'.format(matchup['opp_score'], matchup['user_score'])
            result = ''
            if matchup['opp_score'] > matchup['user_score']:
                result = 'LOSS'
            else:
                result = 'WIN'
            # Set the position of the information on screen.
            game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 32)
            result_pos = center_text(self.font_mini.getsize(result)[0], 32)
            score_position = center_text(self.font.getsize(score)[0], 32)
            # Draw the text on the Data image.
            self.draw.multiline_text((game_date_pos, -1), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
            self.draw.multiline_text((result_pos, 5), result, fill=(255, 255, 255), font=self.font_mini, align="center")
            # Open the logo image file
            opp_logo = Image.open('logos/{}.png'.format(matchup['opp_av']))
            user_logo = Image.open('logos/{}.png'.format(matchup['user_av']))
            # Set the position of each logo on screen.
            opp_team_logo_pos = { "x": -15, "y": 0 }
            user_team_logo_pos = { "x": 45, "y": 0 }
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(opp_logo.convert("RGB"), opp_team_logo_pos["x"], opp_team_logo_pos["y"])
            self.canvas.SetImage(user_logo.convert("RGB"), user_team_logo_pos["x"], user_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min

    def _draw_big_play(self):
        debug.info('poop')
        # Load the gif file
        im = Image.open("Assets/goal_light_animation.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        x = 0
        while x is not 5:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)
            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            time.sleep(0.1)

    def _draw_off_season(self):
        self.draw.text((0, -1), 'OFF SEASON\nshould\nprobably\nturn me off', font=self.font_mini)
        self.canvas.SetImage(self.image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)