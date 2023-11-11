from enum import Enum
from dataclasses import dataclass
from copy import deepcopy
from typing import Optional


class State(Enum):
    TRUTH="T"
    LIE="L"
    UNKNOWN=""


class SymbolType(Enum):
    CIRCLE="O"
    TRIANGLE = "T"


@dataclass
class Statement:
    symbol: str
    type: SymbolType
    state: State

    def get_implied_type(self):
        return self.calculate_implied_type(self.state)

    def calculate_implied_type(self, state: State):
        if state == State.UNKNOWN:
            raise ValueError
        elif state == State.TRUTH:
            return self.type
        else:
            if self.type == SymbolType.CIRCLE:
                return SymbolType.TRIANGLE
            else:
                return SymbolType.CIRCLE


@dataclass
class SymbolValue:
    symbol: str
    type: SymbolType

    def __str__(self):
        return "%s: %s" %(self.symbol, self.type.name)
    def __repr__(self):
        return self.__str__()




SymbolSet = tuple[SymbolValue, SymbolValue, SymbolValue]

@dataclass
class Statue:
    symbols: tuple[Statement, Statement, Statement]

    def reset(self):
        for symbol in self.symbols:
            symbol.state = State.UNKNOWN

    def count_states(self) -> dict[State, int]:
        counter = {state: 0 for state in State}
        for symbol in self.symbols:
            counter[symbol.state] += 1
        return counter

    def is_valid(self) -> bool:
        counter = self.count_states()
        return counter[State.TRUTH] <= 1 and counter[State.LIE] <= 2

    def is_resolved(self) -> bool:
        return self.count_states()[State.UNKNOWN] == 0

    def resolve_unknowns(self):
        counter = self.count_states()
        if self.is_valid() and counter[State.UNKNOWN] > 0:
            if counter[State.TRUTH] == 1:
                for symbol in self.symbols:
                    if symbol.state == State.UNKNOWN:
                        symbol.state = State.LIE
            elif counter[State.LIE] == 2:
                for symbol in self.symbols:
                    if symbol.state == State.UNKNOWN:
                        symbol.state = State.TRUTH

    def resolve_symbol(self, symbol: str, symbol_type: SymbolType) -> bool:
        consistent = True
        for statement in self.symbols:
            if statement.symbol == symbol:
                state = State.TRUTH if statement.type == symbol_type else State.LIE
                if statement.state != state and statement.state != State.UNKNOWN:
                    consistent = False
                statement.state = state

        if consistent and self.is_valid():
            self.resolve_unknowns()

        return consistent and self.is_valid()

    def get_possible_solutions(self) -> list[SymbolSet]:
        possibilities: list[SymbolSet] = []

        if self.is_valid():
            self.resolve_unknowns()
            counter = self.count_states()
            if counter[State.UNKNOWN] == 0:
                # This is easy - there is only one solution
                possibilities = [(
                    SymbolValue(symbol=self.symbols[0].symbol, type=self.symbols[0].get_implied_type()),
                    SymbolValue(symbol=self.symbols[1].symbol, type=self.symbols[1].get_implied_type()),
                    SymbolValue(symbol=self.symbols[2].symbol, type=self.symbols[2].get_implied_type()),
                )]
            elif counter[State.UNKNOWN] == 3:
                # This is also easy - there are exactly 3 possible solutions of True, False, False
                possibilities = [(
                    SymbolValue(symbol=self.symbols[0].symbol, type=self.symbols[0].calculate_implied_type(State.TRUTH)),
                    SymbolValue(symbol=self.symbols[1].symbol, type=self.symbols[1].calculate_implied_type(State.LIE)),
                    SymbolValue(symbol=self.symbols[2].symbol, type=self.symbols[2].calculate_implied_type(State.LIE)),
                ), (
                    SymbolValue(symbol=self.symbols[0].symbol, type=self.symbols[0].calculate_implied_type(State.LIE)),
                    SymbolValue(symbol=self.symbols[1].symbol, type=self.symbols[1].calculate_implied_type(State.TRUTH)),
                    SymbolValue(symbol=self.symbols[2].symbol, type=self.symbols[2].calculate_implied_type(State.LIE)),
                ), (
                    SymbolValue(symbol=self.symbols[0].symbol, type=self.symbols[0].calculate_implied_type(State.LIE)),
                    SymbolValue(symbol=self.symbols[1].symbol, type=self.symbols[1].calculate_implied_type(State.LIE)),
                    SymbolValue(symbol=self.symbols[2].symbol, type=self.symbols[2].calculate_implied_type(State.TRUTH)),
                )]
                pass
            elif counter[State.UNKNOWN] == 2:
                fixed: Statement = None
                unknowns: list[Statement] = []
                for symbol in self.symbols:
                    if symbol.state == State.LIE:
                        fixed = symbol
                    elif symbol.state == State.UNKNOWN:
                        unknowns.append(symbol)
                    else:
                        raise ValueError()
                possibilities = [(
                    SymbolValue(symbol=fixed.symbol, type=self.symbols[0].get_implied_type()),
                    SymbolValue(symbol=unknowns[0].symbol, type=unknowns[0].calculate_implied_type(State.TRUTH)),
                    SymbolValue(symbol=unknowns[1].symbol, type=unknowns[1].calculate_implied_type(State.LIE)),
                ), (
                    SymbolValue(symbol=fixed.symbol, type=self.symbols[0].get_implied_type()),
                    SymbolValue(symbol=unknowns[0].symbol, type=unknowns[0].calculate_implied_type(State.LIE)),
                    SymbolValue(symbol=unknowns[1].symbol, type=unknowns[1].calculate_implied_type(State.TRUTH)),
                )]
                pass
            else:
                #This shouldn't happen since we're consistent and have resolved
                raise ValueError

        return possibilities


def propagate_symbols(statues: list[Statue], symbols: Optional[SymbolSet]) -> bool:
    backup = deepcopy(statues)
    def final_sanity_check():
        for statue in statues:
            if not statue.is_valid():
                raise ValueError()

    if symbols:
        for symbol in symbols:
            for statue in statues:
                if not statue.resolve_symbol(symbol.symbol, symbol.type):
                    return False

    if len(statues) == 1:
        return statues[0].is_valid()

    for possibility in statues[0].get_possible_solutions():
        working_statues = deepcopy(statues[1:])
        if propagate_symbols(working_statues, possibility):
            for i in range(len(working_statues)):
                statues[i+1].symbols = working_statues[i].symbols
            for symbol in possibility:
                statues[0].resolve_symbol(symbol.symbol, symbol.type)
            final_sanity_check()
            return True

    return False


def main():
    symbols: list[str] = []
    statues: list[Statue] = []

    with open("data/statues") as data:
        for ln in data.readlines()[1:]:
            tokens = ln.replace("\n", "").split(",")
            statements: list[Statement] = []
            for i in range(6):
                symbol = tokens[i]
                if symbol:
                    if i < 3:
                        statements.append(Statement(symbol=symbol, type=SymbolType.TRIANGLE, state=State.UNKNOWN))
                    else:
                        statements.append(Statement(symbol=symbol, type=SymbolType.CIRCLE, state=State.UNKNOWN))
                    if symbol not in symbols:
                        symbols.append(symbol)
            statues.append(Statue(symbols=tuple(statements)))

    if propagate_symbols(statues, None):
        print("Success!")
    else:
        print("Failure!")

    solution = {}
    for statue in statues:
        if not statue.is_resolved() or not statue.is_valid():
            print("FAIL: " + statue.__str__())
        else:
            for symbol in statue.get_possible_solutions()[0]:
                if symbol.symbol not in solution:
                    solution[symbol.symbol] = symbol.type
                else:
                    if solution[symbol.symbol] != symbol.type:
                        raise ValueError

    print ("Triangles:")
    for symbol, shape in solution.items():
        if shape == SymbolType.TRIANGLE:
            print("    " + symbol)


main()