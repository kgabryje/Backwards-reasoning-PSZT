class BR:
    def __init__(self, knowledge_base: str):
        self._clauses = []
        self._facts = []
        self._init_proven = []  # list of premises used in chain of reasoning that need to be proven
        self._paths = []  # list of states of _init_proven
        self._false_premises = []  # list of premises proved to be false
        self._facts_used = []  # which facts where used in chain of reasoning (only used in parsing output)
        self._main_thesis = ''  # main thesis is a thesis user wants to have proven
        self._kb = knowledge_base
        self.__analyse_kb()

    # public method used to check if thesis is true, also prints chain of reasoning and stuff about knowledge base
    def check_thesis(self, thesis: str):
        self._main_thesis = thesis
        result = self.__prove_initially(thesis)
        print(self.__parse_output(result, thesis))
        print(self)
        self.__clean_up()

    # initial proving
    # thesis is a premise that we're currently proving (not necessarily equal the main thesis)
    def __prove_initially(self, thesis: str) -> bool:
        premises = []
        if thesis not in self._facts:  # if thesis is a fact, we don't need to prove it
            if thesis in self._false_premises or thesis in self._init_proven:
                # if thesis is proved to be false or is already being used in proving chain (can't use premise
                # to prove itself)
                return False
            self._init_proven += [thesis]  # mark thesis as initially proved
            self._paths.append(list(self._init_proven))
            for c in self._clauses:  # iterate over list of clauses
                if self.__contains_conclusion(c, thesis):  # if conclusion of a clause is equal to thesis
                    premises += [self.__get_premises(c)]  # list of lists of premises used to prove current thesis
            return self.__analyse_premises(premises, thesis)  # try to prove thesis using premises that lead to it
        else:
            self._facts_used += [thesis]  # _facts_used list doesn't affect reasoning chain, used only in parsing output
            return True

    # divide knowledge base into clauses and facts
    def __analyse_kb(self):
        for sentence in list(filter(None, self._kb.split(";"))):
            if "=>" in sentence:
                self._clauses += [sentence.strip()]  # example: sentence "A => B" is a clause, sentence "A" is a fact
            else:
                self._facts += [sentence.strip()]  # strip() for removing spaces

    # returns list of premises(literals) from left-hand side of a clause (example: premises of "A & B => C" are A, B)
    @staticmethod
    def __get_premises(clause: str) -> list:
        return [premise.strip() for premise in clause.split('=>')[0].split("&")]

    # try to prove thesis using list of premises
    def __analyse_premises(self, premises_list: list, thesis: str) -> bool:
        result = True
        if not premises_list:  # if list of premises is empty then thesis can't be proven, so it's false
            self._false_premises += [self._init_proven.pop()]  # remove thesis from init_proven and mark as false
            return False
        else:
            # premises_list is a list of lists
            # relation between elements within 1 list is AND
            # relation between lists is OR
            # example: premises_list = [[A,B],[C,D]]
            # result = (A AND B) OR (C AND D)
            for premises in premises_list:  # premises_list is list of lists so premises is a list
                result = True
                for premise in premises:  # premise is a literal
                    result *= self.__prove_initially(premise)  # recursive call, premise is a current thesis
                    if not result:  # if one or more premises are false then move to next list of premises
                        break
                # if at least one list of premises is true, then thesis is true
                if result:
                    return True
            # if result is false, pop thesis from init_proven list and mark it as false
            if thesis != self._main_thesis:
                self._false_premises += [self._init_proven.pop()]
            return False

    # returns true if conclusion (right-hand side) of a clause is equal to s
    @staticmethod
    def __contains_conclusion(clause: str, s: str) -> bool:
        return clause.split('=>')[1].strip() == s.strip()

    def __parse_output(self, result: bool, thesis: str) -> str:
        out = "\nKNOWLEDGE BASE\n"
        out += self._kb.replace(';', '\n') + '\n'
        if result:
            out += "THESIS " + thesis + " TRUE:\n"
        else:
            out += "THESIS " + thesis + " FALSE\n"

        for path in self._paths:  # print chain of reasoning
            out += " <= ". join(path)
            out += " <= ?\n"
        out += " <= ".join(self._init_proven)
        if not result:
            out += " <= ?"
        else:
            out += " <= " + ",".join([fact for fact in set(self._facts_used)])
        return out

    def __clean_up(self):
        self._false_premises = []
        self._init_proven = []
        self._paths = []
        self._facts_used = []

    def __str__(self):
        return "Clauses: " + str(self._clauses) + "\n" + "Facts: " + str(self._facts) + "\n" + "Init_proven: " + \
               str(self._init_proven) + "\n" + "Paths taken: " + str(self._paths) + "\n"


# read knowledge base from file
def read_kb(filename: str) -> str:
    with open(filename, 'r') as f:
        return f.read()

if __name__ == "__main__":
    br = BR("A & -B => C;"
            "A & -C => B;"
            "-B & -C => -A;"
            "B => D;"
            "-D => -B;"
            "C => D;"
            "-D => -C;"
            "-D;"
            "D;")
    br.check_thesis('-A')
    br.check_thesis('C')
    br2 = BR("A => B;"
             "-B => -A;"
             "B => A;"
             "-A => -B;"
             "A => C;"
             "-C => -A;"
             "A => D;"
             "-D => -A;"
             "B & D => E;"
             "B & -E => -D;"
             "D & -E => -B;"
             "-E;")
    br2.check_thesis("-A")
