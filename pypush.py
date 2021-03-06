# Simple Push Python Module

import znc
import re
import http.client, urllib
import traceback
import inspect

class pypush(znc.Module):
    module_types = [znc.CModInfo.UserModule]
    description = "Push python3 module for ZNC"

    def OnLoad(self, sArgs, sMessage):
        self.nick = ''
        self.debug = False
        return znc.CONTINUE

    def PutModuleDbg(self, s):
        if self.debug:
            self.PutModule(s)

    def PushMsg(self, title, msg):
        self.PutModuleDbg("{0} -- {1}".format(title, msg))
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": self.nv['token'],
                         "user": self.nv['user'],
                         "title": title,
                         "message": msg,
                     }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

    def Highlight(self, message):
        if self.nick != self.GetNetwork().GetCurNick():
            self.nick = self.GetNetwork().GetCurNick()
            words = [self.nick, ] + self.nv['highlight'].split()
            self.HighlightRE = re.compile(r'\b({0})\b'.format('|'.join(words)), flags=re.IGNORECASE).search
        return self.HighlightRE(message)

    def OnChanMsg(self, nick, channel, message):
        if self.Highlight(message.s):
            self.PushMsg("Highlight", "{0}: [{1}] {2}".format(channel.GetName(), nick.GetNick(), message.s))
        return znc.CONTINUE

    def OnPrivMsg(self, nick, message):
        self.PushMsg("Private", "[{0}] {1}".format(nick.GetNick(), message.s))
        return znc.CONTINUE

    def OnModCommand(self, commandstr):
        argv = commandstr.split()
        try:
            self.PutModule("Command!! {0}".format(argv))
            method = getattr(self, "DoCommand_" + argv[0].replace('-','_').lower(), self.DoCommandNotUnderstood)
            method(argv)
        except Exception:
            self.PutModule("Command Exception!! {0} -> {1}".format(argv, traceback.format_exc()))
        return znc.CONTINUE

    def DoCommandNotUnderstood(self, argv):
        self.PutModule("Command Not Understood: {0}".format(argv))

    def DoCommand_help(self, argv):
        '''Help'''
        self.PutModule("Help")
        for command in inspect.getmembers(self, lambda x: inspect.ismethod(x) and x.__name__.startswith('DoCommand_')):
            self.PutModule("{0} - {1}".format(command[0].split("_")[1], inspect.getdoc(command[1])))
        return znc.CONTINUE

    def DoCommand_setuser(self, argv):
        '''Sets the user string for Pushover'''
        try:
            self.nv['user'] = argv[1]
            self.PutModule("Pushover user set")
        except Exception:
            self.PutModule("SetUser requires a Pushover user string");

    def DoCommand_settoken(self, argv):
        '''Sets the token string for Pushover'''
        try:
            self.nv['token'] = argv[1]
            self.PutModule("Pushover token set")
        except Exception:
            self.PutModule("SetToken requires a Pushover token string");

    def DoCommand_sethighlight(self, argv):
        '''Sets additional words to highlight on'''
        self.nv['highlight'] = ' '.join(argv[1:])
        self.nick = '' # unset the nick to regenerate the re

    def DoCommand_debug(self, argv):
        '''Toggle Debugging'''
        self.debug = not self.debug
        self.PutModule("Debug {0}".format(self.debug));

    def DoCommand_test(self, argv):
        '''Send a test string to Pushover'''
        self.PushMsg("Test", "{0}".format(' '.join(argv[0:])))
        return znc.CONTINUE


