#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, pango
import os
import datetime,time
import ConfigParser

class CalendarExample:
    DEF_PAD = 10
    DEF_PAD_SMALL = 5
    TM_YEAR_BASE = 1900

    si = None
    popup = None
    menu = None
    current_font_name = None
    calendar = None
    configuration_file = os.environ["HOME"] + '/.pycaltrayrc'
    signal_id = None
    popup_shown = False

    def calendar_date_to_string(self):
        year, month, day = self.window.get_date()
        mytime = time.mktime((year, month+1, day, 0, 0, 0, 0, 0, -1))
        return time.strftime("%x", time.localtime(mytime))

    def calendar_set_flags(self):
        options = 0
        for i in range(5):
            if self.settings[i]:
                options = options + (1<<i)
        if self.window:
            self.window.display_options(options)

    def calendar_toggle_flag(self, toggle):
        j = 0
        for i in range(5):
            if self.flag_checkboxes[i] == toggle:
                j = i

        self.settings[j] = not self.settings[j]
        self.calendar_set_flags()

    def save_default_font(self,font_name):
        config = ConfigParser.ConfigParser()
        config.add_section("font")
        config.set("font", "fontname",font_name)
        conffile = open(self.configuration_file,"w")
        config.write(conffile)
        self.current_font_name = font_name

    def calendar_font_selection_ok(self, button):
        self.font = self.font_dialog.get_font_name()
        if self.window:
            font_desc = pango.FontDescription(self.font)
            if font_desc: 
                self.window.modify_font(font_desc)
                self.save_default_font(self.font)

    def calendar_select_font(self, button):
        if not self.font_dialog:
            window = gtk.FontSelectionDialog("Font Selection Dialog")
            try:
                window.set_font_name(self.current_font_name)
            except:
                pass

            self.font_dialog = window
    
            #window.set_position(gtk.WIN_POS_MOUSE)
    
            window.connect("destroy", self.font_dialog_destroyed)
    
            window.ok_button.connect("clicked",
                                     self.calendar_font_selection_ok)
            window.cancel_button.connect_object("clicked",lambda wid: wid.destroy(),
                                                self.font_dialog)
        window = self.font_dialog
        if not (window.flags() & gtk.VISIBLE):
            window.show()
        else:
            window.destroy()
            self.font_dialog = None

    def font_dialog_destroyed(self, data=None):
        self.font_dialog = None

    def set_default_font(self,window):
        config = ConfigParser.ConfigParser()
     	config.read(self.configuration_file)
        font_name = None
        try:
            font_name = config.get("font","fontname")
        except:
            pass

        if font_name:
            self.current_font_name = font_name
            font_desc = pango.FontDescription(font_name)
            if font_desc:
                window.modify_font(font_desc)

    def position_popup(self,window,blah):
        a,rect,c = self.si.get_geometry();  #getting the X,Y into rect
        winx,winy = self.popup.get_size()
        self.popup.move(rect.x-int(winx/1.5)-20,abs(rect.y-winy))

    def toggle_popup(self,blah):
        if self.popup_shown == True:
            self.popup.hide()
            self.popup_shown = False
        else:
            today = time.localtime()
            self.calendar.select_month(today[1]-1,today[0])
            self.calendar.select_day(today[2])
            self.position_popup(self.popup,None) 
            self.popup.show_all()
            self.popup_shown = True

    def quit(self,si):
        gtk.main_quit()

    def calendar_window(self,blah):
        self.window = None
        self.font = None
        self.font_dialog = None
        self.flag_checkboxes = 5*[None]
        self.settings = 5*[0]
        self.marked_date = 31*[0]

        window = gtk.Window(gtk.WINDOW_POPUP)
        window.connect("configure-event",self.position_popup)
        window.set_title("PyCalTray")
        window.set_resizable(False)
        vbox = gtk.VBox(False, self.DEF_PAD)
        window.add(vbox)

        # The top part of the window, Calendar, flags and fontsel.

        # Calendar widget
        calendar = gtk.Calendar()
        self.calendar = calendar
        self.window = calendar
        self.calendar_set_flags()
        self.window.set_display_options(gtk.CALENDAR_SHOW_HEADING | gtk.CALENDAR_SHOW_DAY_NAMES | ~gtk.CALENDAR_SHOW_WEEK_NUMBERS)
        vbox.add(calendar)
        calendar.freeze()

        self.popup = window
        self.signal_id = self.si.connect("activate",self.toggle_popup)
        self.set_default_font(self.window)

    def on_popup_menu(self,status,button,time):
        self.menu.popup(None,None,None,button,time)

    def __init__(self):
        self.si = gtk.StatusIcon()
        #self.si.set_from_file("cal.png")
        self.si.set_from_icon_name("date")
        self.si.set_visible(True)
        self.si.connect("popup-menu",self.on_popup_menu)
        self.menu = gtk.Menu()
        font_item = gtk.MenuItem("Set Font")
        self.menu.append(font_item)
        font_item.connect("activate",self.calendar_select_font)
        font_item.show()
        quit_item = gtk.MenuItem("Quit PyCalTray")
        self.menu.append(quit_item)
        quit_item.connect("activate",self.quit)
        quit_item.show()
        self.calendar_window(self)

def main():
    CalendarExample()
    gtk.main()
    return 0

if __name__ == "__main__":
    main()
