#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File: Cipher_StreamlabsSystem.py
    Author: Ve
    Version: 0.3.94
    Date: 23/06/2018
    Modified: 25/06/2018
    License: MIT
    Python: 2.7.13
"""

import os, io, re, sys, json, ctypes
from time import time
from random import SystemRandom as prng

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from Store import Store #pylint: disable=E0401

'''
'''
ScriptName = 'Cipher'
Website = 'https://github.com/VeCious/Cipher'
Creator = 'Ve'
Version = '0.3.94'
Description = 'Generates random string from which viewers have to extract a number sequence'

'''
    Declare Constants
'''
ROOT_DIR = os.path.dirname(__file__)
CONF_DIR = os.path.join(ROOT_DIR, 'config')
CONF_FILE = os.path.join(CONF_DIR, '{}Config.json'.format(ScriptName))
STAT_FILE = os.path.join(CONF_DIR, '{}Leaderboard.json'.format(ScriptName))
AUTO_SAVE = time()
'''
    Declare global variables
'''
# message string variables
Parameters = Store({})
# define default settings
defaultSettings = {
    'command': '!cipher',
    'start': '!start',
    'help': 'help',
    'enable': 'enable',
    'disable': 'disable',
    'stats': 'stats',
    'ranks': 'top',
    'claim': 'N/A',
    'blacklist': 'HypeBot',
    'cost': 10,
    'costFail': 10,
    'cooldownRandom': 15.0,
    'cooldownUser': 5.0,
    'cooldownGlobal': 0.0,
    'codeLength': 6.0,
    'codeLengthHard': 9.0,
    'codeLengthScramble': 24.0,
    'timer': 10,
    'timerHard': 10,
    'timerStart': 1,
    'reward': 12,
    'rewardHard': 24,
    'random': 12.32,
    'hardMode': 18.68,
    'msgEncounter': '@$user you have generated a cipher, type [$start] to start decoding. Use [$help] to view instructions. [$time minute/s left]',
    'msgStart': '@$user your cipher is [$cipher], extract the code from it. [$time seconds left]!',
    'msgCurrency': 'You do not have enough $currency ($points), $cost needed!',
    'msgCooldown': 'The generator is cooling down, try again in [$cooldown]!',
    'msgTimeout': '/w cipher timed-out after $time, try again in [$cooldown].',
    'msgSolved': 'Congratulations @$user! You have earned $points $currency by solving the cipher in $time seconds.',
    'msgFailed': '@$user you have failed to input the correct code ($code) in time ($time), good luck next time!',
    'msgEnabled': '/w you have enabled random cipher encounters, to disable them use [$disable]',
    'msgDisabled': '/w you have disabled random cipher encounters, to enable them again use [$enable]',
    'msgStats': '/w Attempts: $attempts | Encounter: $encounter | Solved: $solved | Record: $record | Average: $average | Rate: $success',
    'msgRanks': 'Cipher Leaderboard: $users',
    'msgHelp': '/w $command generates a cipher, $start to start deciphering a cipher. $stats lists stats, $ranks lists top 3 crackers. $enable/$disable enables or disables random encounters. Extract the number sequence from the cipher to solve it.',
    'update': True
}
Settings = Store(defaultSettings)

Game = Store()

'''
    VSCode does not like the injected Parent variable, and I don't want to type it everytime,
    so let's make some simple wrappers.
'''
def Log(msg, title = ScriptName):
    ''' ChatBot Log function warpper, I don't want to type Parent everytime '''
    return Parent.Log(title, str(msg)) #pylint: disable=E0602
#enddef

def SendMessage(message, params = Parameters):
    """
    Sends a message to the chat or a whisper to a user.
    If the message string starts with "/w" and params dict contains the "username" property,
    the function will send a whisper to the user instead of a chat message.
    
    Parameters
    ----------
    message : str
        Message to send.
    params : dict, optional
        List of variables to replace with values from the dict
        in the message string. (the default is empty dict)
    """
    # if the message string starts with "/w" and params has "username" property, define the message as a whisper
    isWhisper = True if message[:2] == '/w' and 'uid' in params else False
    message = message if not isWhisper else message[3:] # remove "/w" if the message is whisper

    # if params is not empty replace the variables in the message string
    if params:
        regex = re.compile(r'\$(%s)' % '|'.join(map(re.escape, params.keys())))
        message = regex.sub(lambda m: str(params[m.group(1)]), message, count = 0)
        
    return Parent.SendStreamMessage(message) if not isWhisper else Parent.SendStreamWhisper(params.uid, message) #pylint: disable=E0602
#enddef

def IsOnCooldown(command, uid = 0):
    """
    Checks if the given command is on User or Global cooldown.
    Returns a formatted string "00:00" (Minutes:Seconds), or False if
    the command is not on cooldown.
    
    Parameters
    ----------
    command : str
        Command to check for.
    uid : int, optional
        User id to check for a cooldown (the default is 0)

    Returns
    -------
    ```
    str|False
    ```
        Returns the remaining cooldown duration as a formatted string 'Min:Sec'.
    
    """
    p = Parent #pylint: disable=E0602
    f = '{:0>2}:{:0>2}'
    if p.IsOnCooldown(ScriptName, command):
        return f.format(*divmod(p.GetCooldownDuration(ScriptName, command), 60))
    elif p.IsOnUserCooldown(ScriptName, command, uid):
        return f.format(*divmod(p.GetUserCooldownDuration(ScriptName, command, uid), 60))
    else:
        return False
#enddef

'''
    Script functions
'''
def OpenReleases():
    """
    Opens GitHub Releases
    
    """
    try:
        os.startfile('{}/releases'.format(Website))
    except Exception as error:
        Log(error, 'OpenReleases')
    return
#enddef

def ClearLeaderboard():
    """
    Clears the Leaderboard
    
    """
    Game.clear()
    Game.save(STAT_FILE)
    Log('Cleared Leaderboard: {}'.format(Game))
#enddef

def ResetSettings():
    """
    Revert Settings to defaults.
    
    """
    Settings = Store(defaultSettings)
    Settings.Save(CONF_FILE)
    try:
        with io.open(CONF_FILE.replace('json', 'js'), 'w+', encoding = 'utf-8') as fp:
            fp.write('var settings = {}'.format(str(Settings).encode('utf-8')))
        Settings.save(CONF_FILE)
        Log('Settings Reset')
    except Exception as error:
        Log(error, 'ResetSettings')
    return
#enddef

def Generate(length, scramble, hard = False):
    """
    Generates a random string with a shuffled number sequence.
    
    Parameters
    ----------
    length : int
        Length for ther number sequence
    scramble : int
        Length of the scramble string
    hard : bool, optional
        If True, additional characters will be used for the string (the default is False)
    
    """
    s = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$€₹₴₫฿₪₽¥£¢%&\'()*+,-./:;<=>?[\\]^_`{|}~'
    if hard:
        s += re.sub(r'\d+', '', 'œ©®µƱƷƻƼǾǽǼȢʬsdɮɜǮǯƽƕ÷™‰ƒ‡†ƆƋƔƜƟȡπξφψώϔϘϞϢЭЮѼѾ҂҉ҖҨӞӬӸܐܠ௫ᴟℨ∜ꖭꝝꝜ')
    code = ''.join(["%s" % prng().randint(0, 9) for num in range(0, length)]) #pylint: disable=W0612
    cipher = prng().sample(s, scramble) + list(code)
    prng().shuffle(cipher)
    return ''.join(cipher)
#enddef

def UpdateCheck():
    '''
        Checks if the script has the same version as the one on github
    '''
    try:
		MB_YESNO = 0x04
		ICON_INFO = 0x40
		MessageBox = ctypes.windll.user32.MessageBoxW

		res = json.loads(Parent.GetRequest('https://raw.githubusercontent.com/VeCious/Cipher/master/Cipher_StreamlabsSystem.py', {})) #pylint: disable=E0602

		if res['status'] != 200:
			Log('Update Check recieved unexpected ({}) code'.format(res['status']), 'Update Check')
		else:
			match = re.search(r'(Version = \'(.*?))\'', res['response'])
			if match and Settings.update:
				vrs = match.group(2)
				notify = '''
Update Available for {}, Version: {}.
Visit {} to download it.

(Pressing YES will open up Github, NO will close this window)
				'''.format(ScriptName, vrs, Website)
				if vrs <= Version:
					pass #Log('{} is up-to-date'.format(ScriptName), 'Update Check')
				else:
					Log('Update Available\nCurrent Version: {}\nNewest Version: {}'.format(Version, vrs))
					if MessageBox(0, notify, 'Update', MB_YESNO | ICON_INFO) == 6: # User pressed the button YES
						OpenReleases()
			else:
				Log('Failed to compare version.', 'Update Check')
    except Exception as err:
		Log(err, 'Update Check')
    return
#enddef

'''
    Required and Optional Chatbot callbacks
'''
def Init():
    ''' [REQUIRED] - ChatBot Constructor function '''
    # check if the settings directory exists and create it if it doesn't
    if not os.path.exists(CONF_DIR):
        os.makedirs(CONF_DIR)
    # check if the settings file already exists and save default configuration if it doesn't
    if not os.path.exists(CONF_FILE):
        Settings.save(CONF_FILE)
    else: # load settings if the file exists
        Settings.load(CONF_FILE)
    
    if os.path.exists(STAT_FILE): # load stats file if it exists
        Game.load(STAT_FILE)
        for uid in Game.keys():
            Game.update({uid: Store(Game[uid])})
    
    if Settings.update:
        UpdateCheck()
    return
#enddef

def Unload():
    Settings.save(CONF_FILE)
    for uid in Game:
        Game[uid].remove('timer', 'limit', 'isHard', 'cipher', 'code')
    Game.save(STAT_FILE)
    Game.clear()
    return
#enddef

def ScriptToggled(state):
    if not state:
        Unload()
    return
#enddef

def Tick():
    """
    [REQUIRED] Chatbot tick Callback
    Auto save player stats ever 12 minutes
    """
    global AUTO_SAVE
    if int((time() - AUTO_SAVE) / 60) > 12:
        Game.save(STAT_FILE)
        AUTO_SAVE = time()
    return
#enddef

def ReloadSettings(data):
    """
    [OPTIONAL] Chatbot callback for when the user save the settings in the Application.
    Saves *.json and *.js Settings file.
    
    Parameters
    ----------
    data : str
        JSON String
    """
    try:
        d = Store(json.loads(data, encoding = 'utf-8'))
        Settings.update(d)
        with io.open(CONF_FILE.replace('json', 'js'), 'w+', encoding = 'utf-8') as fp:
            fp.write('var settings = {}'.format(str(Settings).encode('utf-8')))
        Settings.save(CONF_FILE)
        Log('Settings Reloaded')
    except Exception as error:
        Log(error, 'ReloadSettings')
    return
#enddef

def Execute(data):
    """
    [REQUIRED] - Chatbot main Callback, executed when a message has been typed into the chat.
    
    Parameters
    ----------

    data : object
        Chatbot Data Object
    """
    #exit the function if we did not recieve a chat message or user is black-listed
    if not data.IsChatMessage() or data.IsWhisper() or data.UserName in Settings.blacklist.split('|'):
        return
    
    msg = data.GetParam(0).lower()
    uid = data.User
    name = data.UserName
    currency = Parent.GetPoints(uid) #pylint: disable=E0602

    # define mode values
    hardMode = prng().uniform(0.01, 100.0) < Settings.hardMode
    codeLength = int(Settings.codeLength if not hardMode else Settings.codeLengthHard)

    cooldown = IsOnCooldown(Settings.command, uid)
    encounterCooldown = IsOnCooldown('!cipherencounter', uid) # check for random encounter cooldown
    
    # Define player object
    Player = Game[uid] if uid in Game else Store()

    # define default response string variables
    Parameters.update(
        uid = uid,
        user = name,
        command = Settings.command,
        start = Settings.start,
        help = '{} {}'.format(Settings.command, Settings.help),
        enable = '{} {}'.format(Settings.command, Settings.enable),
        disable = '{} {}'.format(Settings.command, Settings.disable),
        cooldown = cooldown,
        currency = Parent.GetCurrencyName(), #pylint: disable=E0602
        time = Settings.timer if not hardMode else Settings.timerHard
    )

    # handle command
    if msg == Settings.command:
        opt = data.GetParam(1).lower() # get optional argument
        Parameters.update(time = Settings.timerStart)

        # process help option
        if opt == Settings.help:
            # Update paramaters for the response string
            Parameters.update(
                stats = '{} {}'.format(Settings.command, Settings.stats),
                ranks = '{} {}'.format(Settings.command, Settings.ranks)
            )
            SendMessage(Settings.msgHelp)

        # process enable option
        elif opt == Settings.enable:
            Player.enabled = True
            SendMessage(Settings.msgEnabled)

        # process disable option
        elif opt == Settings.disable:
            Player.enabled = False
            SendMessage(Settings.msgDisabled)

        # process stats option
        elif opt == Settings.stats:
            if Player:
                stats = Store(Player)
                stats.uid = uid
                stats.success = '{:.2f}%'.format(stats.success)
                SendMessage(Settings.msgStats, stats)

        # process leaderboard option
        elif opt == Settings.ranks:
            # format leaderboard
            if len(Game) > 0:
                users = ''
                sort = sorted(Game.items(), key = lambda k: k[1]['success'], reverse = True) # sort players by success key
                for i in range(len(sort)):
                    if i < 3:
                        users += '{}. {}: {} | '.format(i + 1, Parent.GetDisplayName(sort[i][0]), '{:.2f}%'.format(sort[i][1]['success'])) #pylint: disable=E0602
                Log(users)
                Log(users[:-2])
                Parameters.top = users[:-2] # remove the last whistespace and | separator
                SendMessage(Settings.msgRanks)

        # process cooldown or already generated cipher
        elif cooldown:
            # command is on cooldown
            SendMessage(Settings.msgCooldown)

        # process main command
        else:
            if currency < Settings.cost:
                # user has not enough currency to play
                Parameters.points = currency
                Parameters.cost = '{} {}'.format(Settings.cost, Parameters.currency)
                SendMessage(Settings.msgCurrency)
            else:
                # remove currency and set player playing
                Parent.RemovePoints(uid, name, Settings.cost) #pylint: disable=E0602
                Player.update(
                    enabled = True if not Player.enabled else Player.enabled,
                    encounter = 0 if not Player.encounter else Player.encounter,
                    solved = 0 if not Player.solved else Player.solved,
                    record = Settings.timerHard if not Player.record else Player.record,
                    success = float(Player.success),
                    isHard = hardMode,
                    timer = time(),
                    cipher = Generate(codeLength, int(Settings.codeLengthScramble), hardMode),
                    limit = Settings.timer if not hardMode else Settings.timerHard
                )

                SendMessage(Settings.msgEncounter)
                if Settings.cooldownGlobal > 0:
                    Parent.AddCooldown(ScriptName, Settings.command, Settings.cooldownGlobal * 60) #pylint: disable=E0602
                else:
                    Parent.AddUserCooldown(ScriptName, Settings.command, uid, Settings.cooldownUser * 60) #pylint: disable=E0602

    # process start command
    elif msg == Settings.start and Player.cipher:
        if divmod(time() - Player.timer, 60)[0] > float(Settings.timerStart):
            # remove unneeded value from the Player object
            Player.remove('timer', 'isHard', 'limit', 'cipher')
            SendMessage(Settings.msgTimeout)
        else:
            cipher = Player.pop('cipher')
            # extract the number sequence from the cipher
            code = ''.join(re.findall(r'\d+', cipher))
            Player.update(
                attempts = Player.attempts + 1,
                timer = time(),
                code = code,
                limit = Settings.timer if not Player.isHard else Settings.timerHard
            )
            Parameters.update(cipher = cipher, time = Player.limit)
            SendMessage(Settings.msgStart)

    # process code input
    elif data.GetParam(0).isdigit() and Player.code:
        elapsed = time() - Player.timer
        code = Player.pop('code')
        reward = Settings.reward if not Player.isHard else Settings.rewardHard
        reward = int((elapsed / Player.limit) * reward)
        Player.update(time = round(Player.time + (time() - Player.timer), 2))
        
        # check if player is over the time limit
        if (time() - Player.timer) > Player.limit or code != msg:
            Parent.RemovePoints(uid, name, Settings.costFail) #pylint: disable=E0602
            Parameters.code = code
            Parameters.time = round(time() - Player.timer, 2)
            SendMessage(Settings.msgFailed)
        else:
            Player.solved += 1
            Player.average = round(Player.time / Player.attempts, 2)
            Player.record = round(elapsed if elapsed < Player.record else Player.record, 2)
            Parameters.update(points = reward, time = '{:.2f}'.format(elapsed))
            SendMessage(Settings.msgSolved)
            Parent.AddPoints(uid, name, reward + Settings.cost) #pylint: disable=E0602
        Player.success = round((Player.solved * 100) / Player.attempts, 2)

        # delete unneeded player data
        Player.remove('limit', 'timer', 'isHard')

    #process random encounter
    elif not encounterCooldown and prng().uniform(0.01, 100) < Settings.random and (not Player.cipher and not Player.code) and Player.enabled:
        # set random encounter cooldown
        Parent.AddCooldown(ScriptName, '!cipherencounter', Settings.cooldownRandom * 60) #pylint: disable=E0602
        Player.update(
            enabled = True if not Player.enabled else Player.enabled,
            attempts = 0 if not Player.attempts else Player.attempts,
            solved = 0 if not Player.solved else Player.solved,
            record = Settings.timerHard if not Player.record else Player.record,
            success = float(Player.success),
            isHard = hardMode,
            timer = time(),
            cipher = Generate(codeLength, int(Settings.codeLengthScramble), hardMode),
            encounter = int(Player.encounter) + 1,
            limit = Settings.timer if not hardMode else Settings.timerHard
        )
        Parameters.update(time = Settings.timerStart)
        SendMessage(Settings.msgEncounter)

    elif Player.cipher and divmod(time() - Player.timer, 60)[0] > Player.limit:
        # cipher timed-out
        pass
    # clear the parameter list so we can start with a fresh one on the next execution
    Parameters.clear()
    if Player:
        # update players
        Game.update({uid: Player})
    return
#enddef