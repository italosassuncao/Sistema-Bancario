from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap
from pathlib import Path

ROOT_PATH = Path(__file__).parent


class IteradorContas:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR${conta.saldo:2f}
        """

        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0

    def transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("\nLimite diário excedido!")
            return
        transacao.registrar(conta)

    def add_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nasc, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nasc = data_nasc
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: ('{self.nome}', '{self.cpf}')"


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excede_saldo = valor > saldo

        if excede_saldo:
            print("\nOperação falhou! Saldo insuficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True

        else:
            print("\nOperação falhou. Valor informado inválido")

        return False

    def deposito(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")

        else:
            print("\nFalha na operação!")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=100, limite_saques=5):
        super().__init__(numero, cliente)
        self._limite = limite
        self.limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excede_limite = valor > self._limite
        excede_saques = numero_saques >= self._limite_saques

        if excede_limite:
            print("\nOperação falhou! Limite do valor de saque excedido.")

        elif excede_saques:
            print("\nOperação falhou! Limite da quantidade de saques excedido")

        else:
            return super().sacar(valor)

        return False

    def __repr__(self):
        return f"{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')"

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta Corrente:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def add_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime
                ("%d-%m-%Y %H:%M:%s"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_dia(self):
        date_now = datetime.now().date()
        transacoes = []
        for transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
            if date_now == data_transacao:
                transacoes.append(transacao)
        return transacoes


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.add_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.add_transacao(self)


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ROOT_PATH / "log.txt", "a") as file:
            file.write(f"[{data_hora}] Função '{func.__name__}' executada com argumentos {args} e {kwargs}. "
                       f"Retornou {resultado}\n")
        return resultado

    return envelope


def menu():
    menu = """

    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Nova conta
    [5] Novo cliente
    [6] Listar contas
    [7] Sair

    => """

    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui conta!")
        return

    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def mostrar_extrato(clientes):
    cpf = input("Informe o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    # Revisar
    print("\n===== Extrato =====")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não há movimentações no período"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")


@log_transacao
def nova_conta(n_conta, clientes, contas):
    cpf = input("Informe o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("CPF não cadastrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=n_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta cadastrada com sucesso!")


@log_transacao
def novo_cliente(clientes):
    cpf = input("Insira o CPF (Somente os números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("CPF já cadastrado!")
        return

    nome = input("Digite o nome completo: ")
    data_nasc = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço completo (Rua, número - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nasc=data_nasc, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("Usuario cadastrado com sucesso!")


def listar_contas(contas):
    for conta in IteradorContas(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:

        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            mostrar_extrato(clientes)

        elif opcao == "4":
            n_conta = len(contas) + 1
            nova_conta(n_conta, clientes, contas)

        elif opcao == "5":
            novo_cliente(clientes)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "7":
            break

        else:
            print("Operação inválida. Por favor, selecione uma opção válida.")


main()
