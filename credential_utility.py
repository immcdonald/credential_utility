import sys

from athenaeum.credential_manager import Credential_Manger

def modify_section(credmgr: object, sections: list, section_count: int, hide_password: bool) -> int:
    rc = 0
    if section_count > 0:
        print("Please choose which section below you want to modify [0-%s]:" % (section_count-1))
        for index in range(0, section_count):
            print("%d - %s" % (index, sections[index]))

        try:
            choice = int(input('\n> '))
        except:
            print("Error: Invalid Choice")
            return 1

        if choice >= 0 and choice < section_count:
            run = True
            while run:
                print("Please choose which key you wish to modif in section %s:" % sections[choice])
                result_dict = credmgr.get(sections[choice])
                if result_dict['rc'] == 0:
                    content = result_dict['contents']
                    keys = list(content.keys())
                    keys.append('Done')

                    key_count = len(keys)
                    for index in range(0, key_count):
                        print('%s %s' % (index, keys[index]))
                    try:
                        key_choice = int(input("> "))
                    except:
                        print("Error: Invalid Choice")
                        return 1


                    if key_choice >= 0 and key_choice < (key_count-1):
                        if key_choice != 'password' or hide_password is False:
                            new_value = input("Please enter a new value for %s >" % keys[key_choice])
                        else:
                            result_dict = credmgr.get_password("Please enter a new value for %s >" % keys[key_choice])

                            if result_dict['rc'] == 0:
                                new_value = result_dict['password']
                            else:
                                print(credmgr.error_list_to_str['errors'])
                                continue

                        content[keys[key_choice]] = new_value
                        result_dict = credmgr.modify(sections[choice],  content)

                        if result_dict['rc'] == 1:
                            print(credmgr.error_list_to_str['errors'])

                    elif key_choice == (key_count - 1):
                        run = False
                    else:
                        print("Error: Invalid key choice")
                else:
                    print(credmgr.error_list_to_str['errors'])    
        else:
            print("Error: Choice is out of range")

    else:
        print("Currently there are not sections available.")
    return rc


def main(argv: list) -> int:
    rc = 0

    credmgr = Credential_Manger()

    run = True
    hide_password = True

    while run:
        sections = credmgr.get_sections()
        section_count = len(sections)

        print("\nThere are currently %s sections.\n" % section_count)

        print('c - Create a new section')
        print('l - List sections')
        print('m - Modify section')
        print('q - Quit')
        
        if hide_password:
            print("t - Toggle hide visible passwords (Currently: On)")
        else:
            print("t - Toggle hide visible passwords (Currently: Off)")

        choice = input('Please make a selections >')

        if choice == 'c' or choice == 'C':
            pass

        elif choice == 'l' or choice == 'L':
            for section in sorted(sections):
                print("\n%s" % section)
                print("%s" % ('='*len(section)))

                result_dict = credmgr.get(section)
                if result_dict['rc'] == 0:
                    contents = result_dict['contents']

                    for key in contents.keys():
                        if key != 'password':
                            print("%s: %s" % (key, contents[key]))
                        else:
                            if hide_password is True:
                                print("%s: %s" % (key, 'X' * 10))
                            else:
                               print("%s: %s" % (key, contents[key])) 
                else:
                    print(credmgr.error_list_to_str['errors'])


        elif choice == 'm' or choice == 'M':
            modify_section(credmgr, sections, section_count, hide_password)
        elif choice == 'q' or choice == 'Q':
            run = False
        elif choice == 't' or choice == 'T':
            if hide_password:
                hide_password = False
            else:
                hide_password = True


    print("Exit Code: %s" % rc)
    return rc

if __name__ == "__main__":
    sys.exit(main(sys.argv))