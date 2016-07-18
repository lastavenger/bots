# -*- encoding: UTF-8 -*-
# Simple IRC log bot runs on <https://github.com/LastAvenger/labots>

import os
import json
import logging
from time import time, tzset, strftime
from bot import Bot, echo


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

time_zone = 'Asia/Shanghai'
json_output = './json'

def strip(msg):
    tmp = ''
    is_color = 0
    for c in msg:
        if c in '\x02\x0f\x16\x1d\x1f':
            continue
        if c == '\x03':
            is_color = 2
            continue
        if is_color and c in '0123456789':
            is_color -= 1
            continue
        tmp += c
    return tmp


# TODO: Inefficient
def log(func):
    def warpper(*args, **kw):
        res = func(*args, **kw)
        if not res:
            return
        t, log = res

        time1 = time()
        fname = os.path.join(json_output, t, strftime('%Y-%m-%d.json'))
        logger.debug('Try opening %s' % fname)
        if not os.path.exists(fname):
            with open(fname, 'w') as f:
                logger.info('New log file: %s' % fname)
                json.dump([{'TimeZone': time_zone}], f, ensure_ascii = False)

        logger.debug('Logging: %s' % log)
        with open(fname, 'r+') as f:
            j = json.load(f)
            j.append(log)
            f.seek(0)
            json.dump(j, f, ensure_ascii = False)

        logger.info('<%s> 1 message logged, time usage: %s'
                % (strftime('%H:%M:%S'), time() - time1))

    return warpper


class LogBot(Bot):
    targets = ['#archlinux-cn', '#linuxba']
    trig_cmds = ['JOIN', 'PART', 'QUIT', 'NICK', 'PRIVMSG']

    def init(self):
        os.environ['TZ'] = time_zone
        tzset()

        if not os.path.exists(json_output):
            logger.info('Creating JSON output directory "%s"' % json_output)
            os.makedirs(json_output)
        for t in self.targets:

            dirname = os.path.join(json_output, t)
            if not os.path.exists(dirname):
                logger.info('Creating directory "%s"' % dirname)
                os.makedirs(dirname)


    def finalize(self):
        pass

    @log
    def on_join(self, nick, chan):
        return (chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'JOIN',
                'channel': chan,
                'nick': nick,
                })

    @log
    def on_part(self, nick, chan, reason):
        return (chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'PART',
                'channel': chan,
                'nick': nick,
                'reason': reason,
                })

    @log
    def on_quit(self, nick, chan, reason):
        return (chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'QUIT',
                'nick': nick,
                'reason': reason,
                })

    @log
    def on_nick(self, nick, new_nick, chan):
        return (chan, {
                'time': strftime('%H:%M:%S'),
                'command': 'NICK',
                'nick': nick,
                'new_nick': new_nick,
                })

    @log
    def on_privmsg(self, nick, target, msg):
        return (target, {
                'time': strftime('%H:%M:%S'),
                'command': 'PRIVMSG',
                'channel': target,
                'nick': nick,
                'message': strip(msg),
                })


bot = LogBot()
