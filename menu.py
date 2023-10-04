import textwrap


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

def deposito(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print("\nDepósito realizado com sucesso!")
    
    else:
        print("\nFalha na operação!")

    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    sem_saldo = valor > saldo
    sem_limite = valor > limite
    limite_saque_excedido = numero_saques > limite_saques

    if sem_saldo:
        print("Operação falhou! Saldo insuficiente.")

    elif sem_limite:
        print("Operação falhou! Valor limite de saque excedido.")

    elif limite_saque_excedido:
        print("Operação falhou! Limite de saques excedido.")
    
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque efetuado: R$ {valor:.2f}\n"

    return saldo, extrato
    
def mostrar_extrato(saldo, /, *, extrato):
    print("\n########## Extrato ##########")
    print("Sem movimentações no periodo." if not extrato else extrato)
    print(f"\nSaldo: {saldo:.2f}")
    print("*****************************")

def nova_conta(agencia, n_conta, clientes):
    cpf = input("Informe o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("Conta aberta com sucesso!")
        return {"agencia": agencia, "n_conta": n_conta, "cliente": cliente}
    
    print("\nUsuário não localizado! Erro na operação.")

def novo_cliente(clientes):
    cpf = input("Insira o CPF (Somente os números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("CPF já cadastrado!")
        return
    
    nome = input("Digite o nome completo: ")
    data_nasc = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço completo (Rua, número - bairro - cidade/sigla estado): ")

    clientes.append({"nome": nome, "data_nasc": data_nasc, "cpf":cpf, "endereco": endereco})

    print("Cliente cadastrado com sucesso!")

def filtrar_cliente(cpf, clientes):
    filtro_cliente = [cliente for cliente in clientes if cliente["cpf"] == cpf]
    return filtro_cliente[0] if filtro_cliente else None

def listar_contas(contas):
    for conta in contas:
        linha = f"""\
            Agência: {conta['agencia']}
            Conta Corrente: {conta['n_conta']}
            Titular: {conta['cliente']['nome']}
        """

        print("=" * 100)
        print(textwrap.dedent(linha))

def main():
    limite_saques = 3
    agencia = "0001"

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    clientes = []
    contas = []

    while True:

        opcao = menu()

        if opcao == "1":
            valor = float(input("Digite o valor do depósito: "))

            saldo, extrato = deposito(saldo, valor, extrato)

        elif opcao == "2":
            valor = float(input("Digite o valor do saque: "))

            saldo, extrato = sacar(
                saldo = saldo,
                valor = valor,
                extrato = extrato,
                limite = limite,
                numero_saques = numero_saques,
                limite_saques = limite_saques,
            )

        elif opcao == "3":
            mostrar_extrato(saldo, extrato = extrato)

        elif opcao == "4":
            n_conta = len(contas) + 1
            conta = nova_conta(agencia, n_conta, clientes)

        if contas:
           contas.append(conta)

        elif opcao == "5":
            novo_cliente(clientes)

        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "7":
            break

        else:
            print("Operação inválida. Por favor, selecione uma opção válida.")

main()
