import sys

from athenaeum.credential_manager import Credential_Manger

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

        print('q - Quit')
        
        if hide_password:
            print("t - Toggle visible passwords (Currently: On)")
        else:
            print("t - Toggle visible passwords (Currently: Off)")

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
                            print("-%s: %s" % (key, contents[key]))
                        else:
                            if hide_password is True:
                                print("%s: %s" % (key, 'X' * 10))
                            else:
                               print("%s: %s" % (key, contents[key])) 
                else:
                    print(credmgr.error_list_to_str['errors'])

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