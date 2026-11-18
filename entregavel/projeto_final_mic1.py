import os

# Arquivos da memória de dados.
# SOBRESCREVER_DADOS = False (padrão): dados.txt é só a ENTRADA (estado inicial)
#   e a memória atualizada é gravada em dados_saida.txt. Assim o programa pode
#   ser executado várias vezes partindo sempre do mesmo estado inicial.
# SOBRESCREVER_DADOS = True: cada WRITE regrava o próprio dados.txt.
SOBRESCREVER_DADOS = False
ARQUIVO_DADOS_ENTRADA = "dados.txt"
ARQUIVO_DADOS_SAIDA = "dados_saida.txt"

def arquivo_dados_saida():
    return ARQUIVO_DADOS_ENTRADA if SOBRESCREVER_DADOS else ARQUIVO_DADOS_SAIDA

# =====================================================================
# 1. CARREGAMENTO E SALVAMENTO DE ARQUIVOS (REGISTRADORES E MEMÓRIA)
# =====================================================================

ORDEM_BARRAMENTO_C = ["H", "OPC", "TOS", "CPP", "LV", "SP", "PC", "MDR", "MAR"]

def carregar_registradores(caminho="registradores.txt"):
    regs = {
        "MAR": "0" * 32,
        "MDR": "0" * 32,
        "PC":  "0" * 32,
        "MBR": "0" * 8,
        "SP":  "0" * 32,
        "LV":  "0" * 32,
        "CPP": "0" * 32,
        "TOS": "0" * 32,
        "OPC": "0" * 32,
        "H":   "0" * 32,
    }
    if not os.path.exists(caminho):
        return regs

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            if "=" in linha:
                partes = linha.split("=")
            elif ":" in linha:
                partes = linha.split(":")
            else:
                partes = linha.split()

            if len(partes) >= 2:
                nome = partes[0].strip().upper()
                valor = partes[1].strip()
                if nome in regs:
                    tamanho = 8 if nome == "MBR" else 32
                    # Aceita valor em binário ou converte se a professora mandar em decimal
                    if all(c in "01" for c in valor) and len(valor) >= 4:
                        regs[nome] = valor.zfill(tamanho)[-tamanho:]
                    else:
                        num = int(valor)
                        if num < 0:
                            num = (1 << tamanho) + num
                        regs[nome] = format(num, f"0{tamanho}b")[-tamanho:]
    return regs

def carregar_memoria(caminho="dados.txt"):
    if not os.path.exists(caminho):
        # Cria uma memória padrão de 16 linhas zeradas se não existir
        memoria = ["0" * 32 for _ in range(16)]
        salvar_memoria(memoria, caminho)
        return memoria

    memoria = []
    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                memoria.append(linha.zfill(32)[-32:])
    return memoria

def salvar_memoria(memoria, caminho="dados.txt"):
    with open(caminho, "w", encoding="utf-8") as f:
        for palavra in memoria:
            f.write(f"{palavra}\n")

# =====================================================================
# 2. ULA DE 32 BITS, DESLOCADOR E FLAGS (ETAPA 1 E 2)
# =====================================================================

def ula_32bits(a_str, b_str, ctrl_ula):
    """
    ctrl_ula (8 bits): SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC
    """
    sll8 = int(ctrl_ula[0])
    sra1 = int(ctrl_ula[1])
    f0   = int(ctrl_ula[2])
    f1   = int(ctrl_ula[3])
    ena  = int(ctrl_ula[4])
    enb  = int(ctrl_ula[5])
    inva = int(ctrl_ula[6])
    inc  = int(ctrl_ula[7])

    if sll8 == 1 and sra1 == 1:
        raise ValueError("ERRO: SLL8 e SRA1 não podem ser ativados simultaneamente (1 e 1).")

    # Habilitação das entradas A e B
    a = [int(bit) for bit in a_str] if ena == 1 else [0] * 32
    b = [int(bit) for bit in b_str] if enb == 1 else [0] * 32

    # Inversão de A (INVA)
    if inva == 1:
        a = [1 - bit for bit in a]

    # Operação selecionada por F0 e F1
    saida = [0] * 32
    vai_um = 0

    if f0 == 0 and f1 == 0:      # A AND B
        saida = [a[i] & b[i] for i in range(32)]
    elif f0 == 0 and f1 == 1:    # A OR B
        saida = [a[i] | b[i] for i in range(32)]
    elif f0 == 1 and f1 == 0:    # NOT B
        saida = [1 - b[i] for i in range(32)]
    elif f0 == 1 and f1 == 1:    # A + B + INC (Somador Completo de 32 bits)
        carry = inc
        for i in range(31, -1, -1):
            soma_bit = a[i] ^ b[i] ^ carry
            carry = (a[i] & b[i]) | (a[i] & carry) | (b[i] & carry)
            saida[i] = soma_bit
        vai_um = carry

    s_str = "".join(str(bit) for bit in saida)

    # Deslocador (SLL8 e SRA1)
    if sll8 == 1:
        sd_str = s_str[8:] + ("0" * 8)
    elif sra1 == 1:
        bit_sinal = s_str[0]
        sd_str = bit_sinal + s_str[:-1]
    else:
        sd_str = s_str

    # Cálculo das Flags Z e N (após o deslocador)
    flag_z = 1 if sd_str == ("0" * 32) else 0
    flag_n = 1 if sd_str[0] == "1" else 0

    return s_str, sd_str, vai_um, flag_z, flag_n

# =====================================================================
# 3. BARRAMENTOS B e C (ETAPA 2)
# =====================================================================

def decodificar_barramento_b(cod_bin, regs):
    cod = int(cod_bin, 2)
    if cod == 0:
        return regs["MDR"], "MDR"
    elif cod == 1:
        return regs["PC"], "PC"
    elif cod == 2:  # MBR com extensão de sinal
        mbr = regs["MBR"].zfill(8)[-8:]
        extensao = mbr[0] * 24
        return extensao + mbr, "MBR"
    elif cod == 3:  # MBRU com extensão de zeros
        mbr = regs["MBR"].zfill(8)[-8:]
        return ("0" * 24) + mbr, "MBRU"
    elif cod == 4:
        return regs["SP"], "SP"
    elif cod == 5:
        return regs["LV"], "LV"
    elif cod == 6:
        return regs["CPP"], "CPP"
    elif cod == 7:
        return regs["TOS"], "TOS"
    elif cod == 8:
        return regs["OPC"], "OPC"
    else:
        return "0" * 32, "NENHUM"

def escrever_barramento_c(seletor_c, sd_str, regs):
    escritos = []
    for i, bit in enumerate(seletor_c):
        if bit == "1":
            nome_reg = ORDEM_BARRAMENTO_C[i]
            regs[nome_reg] = sd_str
            escritos.append(nome_reg)
    return escritos

# =====================================================================
# 4. EXECUÇÃO DE MICROINSTRUÇÃO DE 23 BITS E MEMÓRIA (ETAPA 3)
# =====================================================================

def executar_ciclo_23bits(microinst, regs, memoria, ciclo_num, log_lines, info_extra=""):
    """
    Formato de 23 bits:
    [0:8]   -> ULA (8 bits: SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC)
    [8:17]  -> Barramento C (9 bits: H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR)
    [17:19] -> Memória (2 bits: WRITE, READ)
    [19:23] -> Barramento B (4 bits: 0000 a 1000)
    """
    ctrl_ula  = microinst[0:8]
    seletor_c = microinst[8:17]
    sinal_wr  = int(microinst[17])
    sinal_rd  = int(microinst[18])
    seletor_b = microinst[19:23]

    log_lines.append("=" * 75)
    titulo = f"CICLO {ciclo_num} | Microinstrução: {microinst}"
    if info_extra:
        titulo += f" ({info_extra})"
    log_lines.append(titulo)
    # Caso especial do enunciado: WRITE = READ = 1 indica o FETCH do BIPUSH.
    # Nesse caso os 8 primeiros bits não são sinais da ULA: são o byte do argumento.
    fetch_especial = (sinal_wr == 1 and sinal_rd == 1)
    if fetch_especial:
        log_lines.append(f"Campos -> BYTE: {ctrl_ula} | C: {seletor_c} | WR: {sinal_wr} RD: {sinal_rd} (FETCH ESPECIAL) | B: {seletor_b}")
    else:
        log_lines.append(f"Campos -> ULA: {ctrl_ula} | C: {seletor_c} | WR: {sinal_wr} RD: {sinal_rd} | B: {seletor_b}")

    # Estado dos registradores antes do ciclo
    log_lines.append("\n[Registradores ANTES do Ciclo]")
    for k, v in regs.items():
        log_lines.append(f"  {k:<3} = {v}")

    # FETCH especial: byte -> MBR e MBR (completado com zeros) -> H, sem passar pela ULA
    if fetch_especial:
        byte_fetch = ctrl_ula
        regs["MBR"] = byte_fetch
        regs["H"] = ("0" * 24) + byte_fetch
        log_lines.append(f"\n[Fluxo de Dados - FETCH ESPECIAL]")
        log_lines.append(f"  Byte recebido            : {byte_fetch}")
        log_lines.append(f"  MBR                      : {regs['MBR']}")
        log_lines.append(f"  H = MBR (zeros à esquerda): {regs['H']}  (sem passar pela ULA)")
        log_lines.append("\n[Registradores DEPOIS do Ciclo]")
        for k, v in regs.items():
            log_lines.append(f"  {k:<3} = {v}")
        return

    # 1. Busca operando no Barramento B e Entrada A (H)
    val_b, nome_b = decodificar_barramento_b(seletor_b, regs)
    val_a = regs["H"]

    # 2. Executa ULA e Deslocador
    s_str, sd_str, vai_um, flag_z, flag_n = ula_32bits(val_a, val_b, ctrl_ula)

    # 3. Escreve nos registradores pelo Barramento C
    regs_escritos = escrever_barramento_c(seletor_c, sd_str, regs)

    # 4. Operações de Memória (WRITE / READ) usando MAR e MDR
    acao_memoria = "Nenhuma (WR=0, RD=0)"
    if sinal_wr == 1:
        endereco = int(regs["MAR"], 2)
        # Expande a memória caso o endereço seja maior que o arquivo atual
        while endereco >= len(memoria):
            memoria.append("0" * 32)
        memoria[endereco] = regs["MDR"]
        salvar_memoria(memoria, arquivo_dados_saida())
        acao_memoria = f"WRITE -> Gravou MDR ({regs['MDR']}) na linha {endereco} da memória de dados"

    elif sinal_rd == 1:
        endereco = int(regs["MAR"], 2)
        if 0 <= endereco < len(memoria):
            regs["MDR"] = memoria[endereco]
        else:
            regs["MDR"] = "0" * 32
        acao_memoria = f"READ -> Leu linha {endereco} da memória de dados para MDR ({regs['MDR']})"

    # Registro detalhado no Log
    log_lines.append(f"\n[Fluxo de Dados e ULA]")
    log_lines.append(f"  Barramento B selecionado : {nome_b} ({val_b})")
    log_lines.append(f"  Entrada A (Reg H)        : {val_a}")
    log_lines.append(f"  Saída pura da ULA (S)    : {s_str}")
    log_lines.append(f"  Saída Deslocada (Sd)     : {sd_str}")
    log_lines.append(f"  Flags                    : Z = {flag_z} | N = {flag_n} | Carry = {vai_um}")
    log_lines.append(f"  Barramento C escreveu em : {', '.join(regs_escritos) if regs_escritos else 'Nenhum'}")
    log_lines.append(f"  Ação de Memória          : {acao_memoria}")

    log_lines.append("\n[Registradores DEPOIS do Ciclo]")
    for k, v in regs.items():
        log_lines.append(f"  {k:<3} = {v}")

# =====================================================================
# 5. TRADUTOR IJVM -> MICROINSTRUÇÕES DE 23 BITS (ENTREGÁVEL FINAL)
# =====================================================================

def traduzir_instrucao_ijvm(linha_ijvm):
    """
    Converte comandos IJVM (DUP, ILOAD x, BIPUSH byte) em uma lista de tuplas:
    (microinstrucao_23bits, descricao_passo)
    """
    partes = linha_ijvm.strip().split()
    if not partes:
        return []

    opcode = partes[0].upper()
    micros = []

    if opcode == "DUP":
        # 1. MAR = SP = SP + 1
        # ULA: B + 1 (00110101) | C: SP e MAR (000001001) | Mem: 00 | B: SP (0100)
        micros.append(("00110101" + "000001001" + "00" + "0100", "DUP: MAR = SP = SP + 1"))
        # 2. MDR = TOS; wr
        # ULA: B (00010100) | C: MDR (000000010) | Mem: WR=1, RD=0 (10) | B: TOS (0111)
        micros.append(("00010100" + "000000010" + "10" + "0111", "DUP: MDR = TOS; wr"))

    elif opcode == "ILOAD":
        x = int(partes[1])
        # 1. H = LV
        # ULA: B (00010100) | C: H (100000000) | Mem: 00 | B: LV (0101)
        micros.append(("00010100" + "100000000" + "00" + "0101", f"ILOAD {x}: H = LV"))

        # 2. Repete x vezes: H = H + 1
        # ULA: A + 1 (00111001) | C: H (100000000) | Mem: 00 | B: 0000
        for i in range(x):
            micros.append(("00111001" + "100000000" + "00" + "0000", f"ILOAD {x}: H = H + 1 (passo {i+1}/{x})"))

        # 3. MAR = H; rd
        # ULA: A (00011000) | C: MAR (000000001) | Mem: WR=0, RD=1 (01) | B: 0000
        micros.append(("00011000" + "000000001" + "01" + "0000", f"ILOAD {x}: MAR = H; rd"))

        # 4. MAR = SP = SP + 1
        # ULA: B + 1 (00110101) | C: SP e MAR (000001001) | Mem: 00 | B: SP (0100)
        micros.append(("00110101" + "000001001" + "00" + "0100", f"ILOAD {x}: MAR = SP = SP + 1"))

        # 5. TOS = MDR; wr
        # ULA: B (00010100) | C: TOS (001000000) | Mem: WR=1, RD=0 (10) | B: MDR (0000)
        micros.append(("00010100" + "001000000" + "10" + "0000", f"ILOAD {x}: TOS = MDR; wr"))

    elif opcode == "BIPUSH":
        arg = partes[1]
        # Aceita o byte tanto em binário (ex: 00001010) quanto em decimal (ex: 10)
        if all(c in "01" for c in arg) and len(arg) == 8:
            byte_str = arg
        else:
            val = int(arg)
            if val < 0:
                val = (1 << 8) + val
            byte_str = format(val, "08b")[-8:]

        # 1. MAR = SP = SP + 1
        # ULA: B + 1 (00110101) | C: SP e MAR (000001001) | Mem: 00 | B: SP (0100)
        micros.append(("00110101" + "000001001" + "00" + "0100", f"BIPUSH {arg}: MAR = SP = SP + 1"))

        # 2. FETCH ESPECIAL (WRITE = READ = 1): os 8 primeiros bits são o byte do argumento.
        # byte -> MBR e MBR (completado com zeros) -> H, sem passar pela ULA
        # Byte (8 bits) | C: 000000000 | Mem: 11 | B: 0000
        micros.append((byte_str + "000000000" + "11" + "0000", f"BIPUSH {arg}: fetch (byte {byte_str} -> MBR -> H)"))

        # 3. MDR = TOS = H; wr
        # ULA: A (00011000) | C: TOS e MDR (001000010) | Mem: WR=1, RD=0 (10) | B: 0000
        micros.append(("00011000" + "001000010" + "10" + "0000", f"BIPUSH {arg}: MDR = TOS = H; wr"))

    elif all(c in "01" for c in opcode) and len(opcode) == 23:
        # Permite também colocar microinstruções binárias puras de 23 bits no arquivo!
        micros.append((opcode, "Microinstrução direta de 23 bits"))

    return micros

# =====================================================================
# 6. PROGRAMA PRINCIPAL
# =====================================================================

def main():
    regs = carregar_registradores("registradores.txt")
    memoria = carregar_memoria("dados.txt")
    log_lines = []

    log_lines.append("===========================================================================")
    log_lines.append("           SIMULADOR MIC-1 (ETAPA 3 + TRADUTOR IJVM - 23 BITS)             ")
    log_lines.append("===========================================================================")

    log_lines.append("\n[ESTADO INICIAL DA MEMÓRIA DE DADOS (dados.txt)]")
    for idx, linha in enumerate(memoria):
        log_lines.append(f"  Endereço {idx:02d}: {linha}")

    caminho_inst = "instrucoes.txt"
    if not os.path.exists(caminho_inst):
        print(f"Arquivo '{caminho_inst}' não encontrado.")
        return

    ciclo = 1
    n_instrucao = 1
    with open(caminho_inst, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue

            micros = traduzir_instrucao_ijvm(linha)
            if not micros:
                continue

            log_lines.append("")
            log_lines.append("#" * 75)
            log_lines.append(f"INSTRUÇÃO IJVM {n_instrucao}: {linha}  ({len(micros)} microinstruções)")
            log_lines.append("#" * 75)

            for micro_23, desc in micros:
                executar_ciclo_23bits(micro_23, regs, memoria, ciclo, log_lines, desc)
                ciclo += 1

            log_lines.append("")
            log_lines.append("=" * 75)
            log_lines.append(f"[MEMÓRIA DE DADOS após a instrução {n_instrucao}: {linha}]")
            for idx, palavra in enumerate(memoria):
                log_lines.append(f"  Endereço {idx:02d}: {palavra}")
            n_instrucao += 1

    log_lines.append("\n===========================================================================")
    log_lines.append("[ESTADO FINAL DA MEMÓRIA DE DADOS APÓS EXECUÇÃO]")
    for idx, linha in enumerate(memoria):
        log_lines.append(f"  Endereço {idx:02d}: {linha}")
    log_lines.append("===========================================================================")

    # Garante que o arquivo de saída da memória exista mesmo sem nenhum WRITE
    salvar_memoria(memoria, arquivo_dados_saida())

    texto_final = "\n".join(log_lines)
    print(texto_final)

    with open("log_saida.txt", "w", encoding="utf-8") as f_out:
        f_out.write(texto_final)
    print(f"\n[OK] Execução concluída! Memória final em '{arquivo_dados_saida()}' e log em 'log_saida.txt'.")

if __name__ == "__main__":
    main()