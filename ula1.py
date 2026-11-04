import sys

N_BITS = 32

A = "11111111111111111111111111111111"
B = "00000000000000000000000000000001"

def NOT(x):
    return 1 - x

def AND(*entradas):
    return 1 if all(entradas) else 0

def OR(*entradas):
    return 1 if any(entradas) else 0

def XOR(x, y):
    return 1 if x != y else 0

def decodificador(f0, f1):
    en_and = AND(NOT(f0), NOT(f1))  # os dois são 0
    en_or = AND(NOT(f0), f1)        # f0 é 0 e f1 é 1
    en_notb = AND(f0, NOT(f1))      # f0 é 1 e f1 é 0
    en_soma = AND(f0, f1)           # os dois são 1
    return en_and, en_or, en_notb, en_soma

def unidade_logica(a, b):
    return AND(a, b), OR(a, b), NOT(b)

def somador_completo(a, b, vem_um):
    a_xor_b = XOR(a, b)
    soma = XOR(a_xor_b, vem_um)
    vai_um = OR(AND(a, b), AND(a_xor_b, vem_um))
    return soma, vai_um

def ula_1bit(a, b, f0, f1, ena, enb, inva, vem_um):
    a_cond = XOR(AND(a, ena), inva)
    b_cond = AND(b, enb)
    en_and, en_or, en_notb, en_soma = decodificador(f0, f1)
    r_and, r_or, r_notb = unidade_logica(a_cond, b_cond)
    r_soma, vai_um = somador_completo(a_cond, b_cond, vem_um)
    # parte do filtro
    s = OR(
        AND(r_and, en_and),
        AND(r_or, en_or),
        AND(r_notb, en_notb),
        AND(r_soma, en_soma)
    )
    vai_um = AND(vai_um, en_soma)
    return a_cond, b_cond, s, vai_um

def ula_32bits(a, b, f0, f1, ena, enb, inva, inc):
    a_cond = [""] * N_BITS
    b_cond = [""] * N_BITS
    s = [""] * N_BITS
    vem_um = inc
    vai_um = 0
    for i in range(31, -1, -1):
        a_i, b_i, s_i, vai_um = ula_1bit(int(a[i]), int(b[i]), f0, f1, ena, enb, inva, vem_um)
        a_cond[i] = str(a_i)
        b_cond[i] = str(b_i)
        s[i] = str(s_i)
        vem_um = vai_um
    return "".join(a_cond), "".join(b_cond), "".join(s), vai_um

def executar_programa():
    with open("programa_etapa1.txt", "r", encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()

    saida_linhas = []

    def registrar(texto=""):
        print(texto)
        saida_linhas.append(texto)

    registrar("Equipe:")
    registrar("- José Rômulo de Oliveira Silva")
    registrar("- Gustavo Gomes Souta da Silva")
    registrar("- Rafael Soares Gomes Correia Lima")
    registrar("============================================================")
    registrar("")

    registrar(f"b = {B}")
    registrar(f"a = {A}")
    registrar("")
    registrar("Start of Program")

    PC = 1
    for linha in linhas:
        IR = linha.strip()
        if IR == "":
            continue
        registrar("============================================================")
        registrar(f"Cycle {PC}")
        registrar("")
        registrar(f"PC = {PC}")
        registrar(f"IR = {IR}")
        f0 = int(IR[0])
        f1 = int(IR[1])
        ena = int(IR[2])
        enb = int(IR[3])
        inva = int(IR[4])
        inc = int(IR[5])
        a_cond, b_cond, s, co = ula_32bits(A, B, f0, f1, ena, enb, inva, inc)
        registrar(f"b = {b_cond}")
        registrar(f"a = {a_cond}")
        registrar(f"s = {s}")
        registrar(f"co = {co}")
        PC += 1

    registrar("============================================================")
    registrar(f"Cycle {PC}")
    registrar("")
    registrar(f"PC = {PC}")
    registrar("> Line is empty, EOP.")
    registrar("")

    conteudo_final = "\n".join(saida_linhas)
    with open("saida_etapa1.txt", "w", encoding="utf-8") as f_sem_acento:
        f_sem_acento.write(conteudo_final)
    with open("saída_etapa1.txt", "w", encoding="utf-8") as f_com_acento:
        f_com_acento.write(conteudo_final)

if __name__ == "__main__":
    executar_programa()
