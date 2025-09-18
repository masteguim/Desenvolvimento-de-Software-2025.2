from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from typing import List


# ======================
# Interface Transacao
# ======================
class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta: Conta) -> None:
        pass


class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta: Conta) -> None:
        conta.saldo += self.valor
        conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta: Conta) -> None:
        if conta.saldo >= self.valor:
            conta.saldo -= self.valor
            conta.historico.adicionar_transacao(self)
        else:
            print("Saldo insuficiente para saque.")


# ======================
# Historico
# ======================
class Historico:
    def __init__(self):
        self.transacoes: List[Transacao] = []

    def adicionar_transacao(self, transacao: Transacao):
        self.transacoes.append(transacao)


# ======================
# Conta
# ======================
class Conta:
    def __init__(self, numero: int, agencia: str, cliente: Cliente):
        self.saldo: float = 0.0
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = Historico()

    def saldo_atual(self) -> float:
        return self.saldo

    def sacar(self, valor: float) -> bool:
        if self.saldo >= valor:
            self.saldo -= valor
            self.historico.adicionar_transacao(Saque(valor))
            return True
        return False

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self.saldo += valor
            self.historico.adicionar_transacao(Deposito(valor))
            return True
        return False


class ContaCorrente(Conta):
    def __init__(self, numero: int, agencia: str, cliente: Cliente, limite: float, limite_saques: int):
        super().__init__(numero, agencia, cliente)
        self.limite = limite
        self.limite_saques = limite_saques


# ======================
# Cliente
# ======================
class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas: List[Conta] = []

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome: str, cpf: str, data_nascimento: date, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento


# ======================
# Simulação
# ======================
if __name__ == "__main__":
    cliente = PessoaFisica("Lucas", "123.456.789-00", date(2000, 5, 10), "Rua X")
    conta = ContaCorrente(numero=1, agencia="0001", cliente=cliente, limite=1000.0, limite_saques=3)

    cliente.adicionar_conta(conta)

    # Transações
    cliente.realizar_transacao(conta, Deposito(500))
    cliente.realizar_transacao(conta, Saque(200))

    print("Saldo final:", conta.saldo_atual())
    print("Histórico de transações:", [type(t).__name__ for t in conta.historico.transacoes])
