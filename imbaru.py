from enum import Enum
from dataclasses import dataclass


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

        def append_sequence(valid_sequences: list[list[SymbolValue]], new_values: list[SymbolValue]) -> list[list[SymbolValue]]:
            new_sequences = []
            for value in new_values:
                for seq in valid_sequences:
                    new_sequences.append(seq + [value])

            return new_sequences

        if self.is_valid():
            sequences = [[]]
            for symbol in self.symbols:
                values = []
                if symbol.state == State.UNKNOWN:
                    values.append(SymbolValue(symbol=symbol.symbol, type=SymbolType.CIRCLE))
                    values.append(SymbolValue(symbol=symbol.symbol, type=SymbolType.TRIANGLE))
                else:
                    for shape in (SymbolType.CIRCLE, SymbolType.TRIANGLE):
                        if (shape == symbol.type and symbol.state == State.TRUTH) or \
                           (shape != symbol.type and symbol.state == State.LIE):
                            values.append(SymbolValue(symbol=symbol.symbol, type=shape))
                sequences = append_sequence(sequences, values)
            for seq in sequences:
                possibilities.append((seq[0], seq[1], seq[2]))

        return possibilities


def main():
    symbols: list[str] = []
    statues: list[Statue] = []

    with open("data/statues") as data:
        for ln in data.readlines()[1:]:
            tokens = ln.replace("\n", "").split(",")
            print("")
            statements: list[Statement] = []
            for i in range(6):
                symbol = tokens[i]
                if symbol:
                    if i < 3:
                        statements.append(Statement(symbol=symbol, type=SymbolType.TRIANGLE, state=State.UNKNOWN))
                        print("%d: Triangle=%s" %(i, symbol))
                    else:
                        statements.append(Statement(symbol=symbol, type=SymbolType.CIRCLE, state=State.UNKNOWN))
                        print("%d: Circle=%s" %(i, symbol))
                    if symbol not in symbols:
                        symbols.append(symbol)
            statues.append(Statue(symbols=tuple(statements)))

    print(symbols)
    print(len(symbols))
    print(len(statues))
    print(statues)

    for state in State:
        print(state)

main()