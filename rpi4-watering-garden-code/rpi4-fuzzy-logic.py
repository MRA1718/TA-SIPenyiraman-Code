def parse_kb_file(filename):
    kb_file = open(filename, 'rU')        # 'rU' is smart about line-endings
    kb_rules = []                         # to hold the list of rules

    for line in kb_file:                  # read the non-commented lines
        if not line.startswith('#') and line != '\n':
            kb_rules.append(split_and_build_literals(line.strip()))

    kb_file.close()
    return kb_rules

def split_and_build_literals(line):
    rules = []
    # Split the line of literals
    literals = line.split(' ')
    hypothesis = []
    while len(literals) > 1:
        hypothesis.append(literals.pop(0))
    rules.append(hypothesis)
    rules.append(literals.pop(0))
    return rules

def main():
    rules = parse_kb_file('/home/pi4/Github_Repo/TA-SIPenyiraman-Code/rpi4-watering-garden-code/rules.kb')

    print(rules)

if __name__ == '__main__':
    main()