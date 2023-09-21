menu = """

[1] Depositar
[2] Sacar
[3] Extrato
[4] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
limite_saques = 3

while True:

    opcao = input(menu)

    if opcao == "1":
        valor = float(input("Digite o valor do depósito: "))

        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"

        else:
            print("Erro na operação. Informe um valor válido.")

    elif opcao == "2":
        valor = float(input("Digite o valor do saque: "))

        sem_saldo = valor > saldo

        sem_limite = valor > limite

        quantidade_saque = numero_saques > limite_saques

        if sem_saldo:
            print("Não possui saldo suficiente.")

        elif sem_limite:
            print("Excede o limite do valor de saque.")

        elif quantidade_saque:
            print("Quantidade de saques do dia excedido.")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f}\n"
            numero_saques += 1

        else:
            print("Erro na operação. Valor inválido.")

    elif opcao == "3":
        print("\n########## Extrato ##########")
        print("Sem movimentações no periodo." if not extrato else extrato)
        print(f"\nSaldo: {saldo:.2f}")
        print("*****************************")

    elif opcao == "4":
        break

    else:
        print("Operação inválida. Por favor, selecione uma opção válida.")
