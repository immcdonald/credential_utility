import sys
import os
import curses
import traceback

from athenaeum.credential_manager import Credential_Manger


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def section_page(stdscr: object, crdmgr: object, page_parameters: dict) -> int:
    rc = 0

    stdscr.addstr(0, 0, "Sections:")

    section_list = crdmgr.get_sections()

    section_count = len(section_list)
    display_rows = min(page_parameters['terminal_height'] - 4, section_count)

    page_parameters['list_hightlight_position'] += page_parameters['list_adjustment']

    if page_parameters['list_hightlight_position'] < 0:
        page_parameters['list_hightlight_position'] = section_count - 1

    if page_parameters['list_hightlight_position'] >= section_count:
        page_parameters['list_hightlight_position'] = 0
    
    if (page_parameters['list_hightlight_position']  + 1) > display_rows:
        local_offset = (page_parameters['list_hightlight_position']+1) - display_rows 
    else:
        local_offset = 0

    page_parameters['displayed_list_dict'] = {'highlighted': -1, 'option_dict': {}}

    for row_position in range(0, display_rows):
        
        if page_parameters['list_hightlight_position'] == row_position + local_offset:
            # Note this is stored by console line position not list position
            page_parameters['displayed_list_dict']['highlighted'] = row_position + 1
            stdscr.attron(curses.color_pair(4))
            
        stdscr.addstr(row_position + 1, 0, " - %s" % section_list[row_position + local_offset])

        page_parameters['displayed_list_dict']['option_dict'][row_position + 1] = section_list[row_position + local_offset]

        if page_parameters['list_hightlight_position'] == row_position + local_offset:
            stdscr.attroff(curses.color_pair(4))

    return rc


def draw_ui(stdscr: object) -> int:
    rc = 0
    
    crdmgr = Credential_Manger()

    curses.curs_set(0)  # Hide the cursor
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()


    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
    page = 'section'
    page_parameters = {'event': None, 
                       'page':'section',
                       'terminal_height': 0,
                       'terminal_width': 0, 
                       'mouse_x': -1,
                       'mouse_y': -1,
                       'mouse_button_state_list': [],
                       'modified': False,
                       'list_adjustment':0,
                       'list_hightlight_position': 0,
                       'displayed_list_dict': {'highlighted': '-1', 'option_dict': {}}}
    run = True

    fp_out = open('page_data.txt', 'w')

    while run:
        page_parameters['terminal_height'], page_parameters['terminal_width'] = stdscr.getmaxyx()

        if page_parameters['page'] == 'section':
           rc = section_page(stdscr, crdmgr, page_parameters)

        if page_parameters['modified']:
            statusbarstr = "Press (q)uit or (s)ave | STATUS BAR | Modified: True"
        else:
            statusbarstr = "Press (q)uit | STATUS BAR | Modified: False"       

        fp_out.write("%s\n" % page_parameters)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(page_parameters['terminal_height']-1, 0, statusbarstr)
        stdscr.addstr(page_parameters['terminal_height']-1, len(statusbarstr), " " * (page_parameters['terminal_width'] - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))
    
        stdscr.refresh()
        page_parameters['list_adjustment'] = 0
        page_parameters['event'] = stdscr.getch()

        # Exit if the event is q or 27 (esc)
        if page_parameters['event'] == ord('q') or page_parameters['event'] == 27:
            run = False
        # If the enter key is pressed
        elif page_parameters['event'] == 10:

            if page_parameters['displayed_list_dict']['highlighted'] != -1:
                highlighted = page_parameters['displayed_list_dict']['highlighted']
                selected = page_parameters['displayed_list_dict']['option_dict'][highlighted]
                fp_out.write("==> %s\n" % selected)
        elif page_parameters['event'] == curses.KEY_PPAGE: # Page Up
            page_parameters['list_adjustment'] = -1
        elif page_parameters['event'] == curses.KEY_NPAGE: # Page Down
            page_parameters['list_adjustment'] = 1
        elif page_parameters['event'] == curses.KEY_UP: # Page Up
            page_parameters['list_adjustment'] = -1
        elif page_parameters['event'] == curses.KEY_DOWN: # Page Down
            page_parameters['list_adjustment'] = 1
        elif page_parameters['event'] == ord('s'):
            if page_parameters['modified']:
                crdmgr.save()
                page_parameters['modified'] = False
        elif page_parameters['event'] == curses.KEY_MOUSE:
            try:
                mouse_list = curses.getmouse()
                mouse_id = mouse_list[0]
                page_parameters['mouse_y'] = mouse_list[1]
                page_parameters['mouse_x'] = mouse_list[2]
                page_parameters['mouse_button_state_list'] = []

                # Note, mouse_list[3] is an unused z value.
                if mouse_list[4] & curses.BUTTON1_PRESSED:
                    page_parameters['mouse_button_state_list'].append("BUTTON1_PRESSED")
                if mouse_list[4] & curses.BUTTON1_RELEASED:
                    page_parameters['mouse_button_state_list'].append("BUTTON1_RELEASED")
                if mouse_list[4] & curses.BUTTON1_CLICKED:
                    page_parameters['mouse_button_state_list'].append("BUTTON1_CLICKED")

                    if page_parameters['page'] == 'section':
                        if page_parameters['mouse_x'] in  page_parameters['displayed_list_dict']:
                            fp_out.write("==> %s\n" % page_parameters['displayed_list_dict']['option_dict'][page_parameters['mouse_x']])

                if mouse_list[4] & curses.BUTTON1_DOUBLE_CLICKED:
                    page_parameters['mouse_button_state_list'].append("BUTTON1_DOUBLE_CLICKED")
                if mouse_list[4] & curses.BUTTON1_TRIPLE_CLICKED:
                    page_parameters['mouse_button_state_list'].append("BUTTON1_TRIPLE_CLICKED")
                if mouse_list[4] & curses.BUTTON2_PRESSED:
                    page_parameters['mouse_button_state_list'].append("BUTTON2_PRESSED")
                if mouse_list[4] & curses.BUTTON3_PRESSED:
                    page_parameters['mouse_button_state_list'].append("BUTTON3_PRESSED")
                if mouse_list[4] & curses.BUTTON4_PRESSED: # Often scroll up
                    page_parameters['mouse_button_state_list'].append("BUTTON4_PRESSED (Scroll Up)")
                    page_parameters['list_adjustment'] = -1
                if mouse_list[4] & curses.BUTTON5_PRESSED: # Often scroll down
                    page_parameters['mouse_button_state_list'].append("BUTTON4_RELEASED (Scroll Down)")
                    page_parameters['list_adjustment'] = 1
                if mouse_list[4] & curses.BUTTON_SHIFT:
                    page_parameters['mouse_button_state_list'].append("SHIFT")
                if mouse_list[4] & curses.BUTTON_CTRL:
                    page_parameters['mouse_button_state_list'].append("CTRL")
                if mouse_list[4] & curses.BUTTON_ALT:
                    page_parameters['mouse_button_state_list'].append("ALT")
            except:
                print(traceback.format_exc())

    fp_out.close()
    return rc

def main(argv) -> int:
    exit_code = 0
    exit_code = curses.wrapper(draw_ui)

    print("Exit Code: %d" % exit_code)
    return exit_code

if __name__ == "__main__":
    sys.exit(main(sys.argv))