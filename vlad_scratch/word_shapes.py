from production import interfaces


for phrase in interfaces.POWER_PHRASES:
    print('---')
    print(phrase)
    h = 0
    for c in phrase:
        cmd = interfaces.COMMAND_BY_CHAR[c]
        if cmd in [interfaces.Action.se, interfaces.Action.sw]:
            h += 1
            print(' ', cmd, '**')
        else:
            print(' ', cmd)
    print('      ', len(phrase) / h)
