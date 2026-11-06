import sys

N_BITS = 32


def NOT(x):
    return 1 - x


def AND(*entradas):
    return 1 if all(entradas) else 0


def OR(*entradas):
    return 1 if any(entradas) else 0


def XOR(x, y):
    return 1 if x != y else 0


def decodificador(f0, f1):
    en_and = AND(NOT(f0), NOT(f1))
    en_or = AND(NOT(f0), f1)
    en_notb = AND(f0, NOT(f1))
    en_soma = AND(f0, f1)
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
    s = OR(
        AND(r_and, en_and),
        AND(r_or, en_or),
        AND(r_notb, en_notb),
        AND(r_soma, en_soma),
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
        a_i, b_i, s_i, vai_um = ula_1bit(
            int(a[i]), int(b[i]), f0, f1, ena, enb, inva, vem_um
        )
        a_cond[i] = str(a_i)
        b_cond[i] = str(b_i)
        s[i] = str(s_i)
        vem_um = vai_um
    return "".join(a_cond), "".join(b_cond), "".join(s), vai_um


def deslocador(s, sll8, sra1):
    if sll8 == 1:
        return s[8:] + ("0" * 8)
    elif sra1 == 1:
        return s[0] + s[:-1]
    return s


def calcular_flags(sd):
    z = 1 if sd == ("0" * N_BITS) else 0
    n = 1 if sd[0] == "1" else 0
    return z, n


def carregar_registradores(caminho):
    regs = {
        "H": "0" * 32,
        "OPC": "0" * 32,
        "TOS": "0" * 32,
        "CPP": "0" * 32,
        "LV": "0" * 32,
        "SP": "0" * 32,
        "PC": "0" * 32,
        "MDR": "0" * 32,
        "MAR": "0" * 32,
        "MBR": "0" * 8,
    }
    ordem_padrao = [
        "H",
        "OPC",
        "TOS",
        "CPP",
        "LV",
        "SP",
        "PC",
        "MDR",
        "MAR",
        "MBR",
    ]
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.strip()]
        for idx, linha in enumerate(linhas):
            if "=" in linha:
                k, v = linha.split("=", 1)
                k = k.strip().upper()
                if k == "OPS":
                    k = "OPC"
                if k in regs:
                    regs[k] = v.strip()
            elif ":" in linha:
                k, v = linha.split(":", 1)
                k = k.strip().upper()
                if k == "OPS":
                    k = "OPC"
                if k in regs:
                    regs[k] = v.strip()
            else:
                partes = linha.split()
                if len(partes) == 2:
                    k = partes[0].upper()
                    if k == "OPS":
                        k = "OPC"
                    if k in regs:
                        regs[k] = partes[1].strip()
                elif len(partes) == 1 and idx < len(ordem_padrao):
                    regs[ordem_padrao[idx]] = partes[0].strip()
    except FileNotFoundError:
        pass
    return regs


def decodificar_barramento_b(b_bits, regs):
    cod = int(b_bits, 2)
    if cod == 0:
        return regs["MDR"], "mdr"
    elif cod == 1:
        return regs["PC"], "pc"
    elif cod == 2:
        mbr = regs["MBR"].zfill(8)
        extensao = mbr[0] * 24
        return extensao + mbr, "mbr"
    elif cod == 3:
        mbr = regs["MBR"].zfill(8)
        return ("0" * 24) + mbr, "mbru"
    elif cod == 4:
        return regs["SP"], "sp"
    elif cod == 5:
        return regs["LV"], "lv"
    elif cod == 6:
        return regs["CPP"], "cpp"
    elif cod == 7:
        # No gabarito oficial da professora, 7 seleciona 'opc'
        return regs["OPC"], "opc"
    elif cod == 8:
        return regs["TOS"], "tos"
    return "0" * 32, None


def decodificar_barramento_c(c_bits):
    nomes_c = ["h", "opc", "tos", "cpp", "lv", "sp", "pc", "mdr", "mar"]
    habilitados = []
    for i in range(9):
        if c_bits[i] == "1":
            habilitados.append(nomes_c[i])
    return habilitados


def executar_programa():
    try:
        with open("programa_etapa2_tarefa2.txt", "r", encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except FileNotFoundError:
        linhas = []

    regs = carregar_registradores("registradores_etapa2_tarefa2.txt")
    saida_linhas = []

    def registrar(texto=""):
        print(texto)
        saida_linhas.append(texto)

    # Ordem exata de exibição exigida no gabarito
    ordem_exibicao = [
        "MAR",
        "MDR",
        "PC",
        "MBR",
        "SP",
        "LV",
        "CPP",
        "TOS",
        "OPC",
        "H",
    ]

    # 1. Ecoa as linhas do arquivo de instruções
    for l in linhas:
        if l.strip() != "":
            registrar(l.strip())

    # 2. Imprime o estado inicial dos registradores
    registrar("\n=====================================================")
    registrar("> Initial register states")
    for r in ordem_exibicao:
        registrar(f"{r.lower()} = {regs[r]}")

    registrar("\n=====================================================")
    registrar("Start of program")

    ciclo = 1
    for linha in linhas:
        IR = linha.strip()
        if IR == "":
            continue

        registrar("=====================================================")
        registrar(f"Cycle {ciclo}")

        ula_bits = IR[0:8]
        c_bits = IR[8:17]
        b_bits = IR[17:21]

        # Formato exigido: 'ir = 8bits 9bits 4bits'
        registrar(f"ir = {ula_bits} {c_bits} {b_bits}\n")

        sll8 = int(ula_bits[0])
        sra1 = int(ula_bits[1])
        f0 = int(ula_bits[2])
        f1 = int(ula_bits[3])
        ena = int(ula_bits[4])
        enb = int(ula_bits[5])
        inva = int(ula_bits[6])
        inc = int(ula_bits[7])

        val_b, nome_b = decodificar_barramento_b(b_bits, regs)
        val_a = regs["H"]

        habilitados_c = decodificar_barramento_c(c_bits)

        # Verificação de segurança (sinais inválidos)
        if nome_b is None or (sll8 == 1 and sra1 == 1):
            registrar("> Error, invalid control signals.")
            ciclo += 1
            continue

        registrar(f"b_bus = {nome_b}")
        nomes_c_str = ", ".join(habilitados_c) if habilitados_c else "nenhum"
        registrar(f"c_bus = {nomes_c_str}\n")

        registrar("> Registers before instruction")
        for r in ordem_exibicao:
            registrar(f"{r.lower()} = {regs[r]}")

        # Execução na ULA e no Deslocador
        a_cond, b_cond, s, co = ula_32bits(
            val_a, val_b, f0, f1, ena, enb, inva, inc
        )
        sd = deslocador(s, sll8, sra1)
        z, n = calcular_flags(sd)

        # Atualiza os registradores habilitados no Barramento C
        for r in habilitados_c:
            regs[r.upper()] = sd

        registrar("\n> Registers after instruction")
        for r in ordem_exibicao:
            registrar(f"{r.lower()} = {regs[r]}")

        ciclo += 1

    # 3. Encerramento idêntico ao gabarito da professora
    registrar("=====================================================")
    registrar(f"Cycle {ciclo - 1}")
    registrar("No more lines, EOP.")

    conteudo_final = "\n".join(saida_linhas)
    with open("saida_etapa2_tarefa2.txt", "w", encoding="utf-8") as f_sem:
        f_sem.write(conteudo_final)
    with open("saída_etapa2_tarefa2.txt", "w", encoding="utf-8") as f_com:
        f_com.write(conteudo_final)


if __name__ == "__main__":
    executar_programa()