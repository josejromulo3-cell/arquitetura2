# Emulador da Microarquitetura Mic-1 (Modificada)

Projeto prático desenvolvido para a disciplina de **Arquitetura de Computadores II** do Departamento de Sistemas de Computação (DSC) do Centro de Informática (CI) — **Universidade Federal da Paraíba (UFPB)**.

**Professora:** Sarah Pontes Madruga

## 👥 Equipe
* José Rômulo de Oliveira Silva
* Gustavo Gomes Souta da Silva
* Rafael Soares Gomes Correia Lima

---

## 💻 Sobre o Projeto

O objetivo deste projeto é o estudo e a implementação em linguagem de alto nível (Python) de uma microarquitetura correspondente a uma versão modificada da Máquina Mic-1. O simulador é capaz de processar microinstruções em formato binário, simulando o comportamento exato das portas lógicas, Unidade Lógica e Aritmética (ULA), registradores e barramentos da arquitetura original, gerando logs detalhados do estado da máquina a cada ciclo de clock.

---

## 🚀 Etapas Concluídas

### ✅ Etapa 1: Implementação da ULA (32 bits)
Construção da Unidade Lógica e Aritmética a partir de princípios básicos:
- Implementação de portas lógicas fundamentais (`AND`, `OR`, `NOT`, `XOR`).
- Construção de decodificador, unidade lógica, somador completo e ULA de 1 bit.
- Expansão para uma ULA de 32 bits.
- Recebimento de palavras de controle de 6 bits (`F0, F1, ENA, ENB, INVA, INC`).

### ✅ Etapa 2: Datapath e Controle Estendido
Expansão do caminho de dados (Datapath) e integração dos registradores:
- **Tarefa 1 (Controle e Flags):** 
  - Expansão da palavra de controle da ULA para 8 bits.
  - Implementação do circuito Deslocador (*Shifter*) operando com `SLL8` (deslocamento lógico à esquerda) e `SRA1` (deslocamento aritmético à direita).
  - Cálculo de Flags de estado: `Z` (Zero) e `N` (Negativo).
- **Tarefa 2 (Registradores e Barramentos):**
  - Implementação do banco de registradores da Mic-1: `H, OPC, TOS, CPP, LV, SP, PC, MDR, MAR` (32 bits) e `MBR` (8 bits).
  - Decodificador de 4 bits para o **Barramento B**, incluindo rotinas de extensão de sinal (`MBR`) e extensão de zeros (`MBRU`).
  - Seletor de 9 bits para escrita simultânea no **Barramento C**.
  - Processamento de microinstruções completas de 21 bits (`ULA [8] | C [9] | B [4]`).

---

## 📂 Estrutura do Repositório (Etapa 2)

* `etapa2_tarefa1.py` - Script do circuito da ULA expandida, deslocador e flags.
* `etapa2_tarefa2.py` - Script do Datapath, decodificadores de barramento e execução de ciclos.
* `programa_etapa2_tarefa1.txt` - Arquivo de entrada com as palavras de controle de 8 bits.
* `programa_etapa2_tarefa2.txt` - Arquivo de entrada com as microinstruções de 21 bits.
* `registradores_etapa2_tarefa2.txt` - Arquivo de configuração contendo o estado inicial dos registradores.
* `saída_etapa2_tarefa1.txt` - Log de execução detalhado gerado pela Tarefa 1.
* `saída_etapa2_tarefa2.txt` - Log de execução detalhado gerado pela Tarefa 2.

---

## ⚙️ Como Executar

O projeto foi desenvolvido em **Python 3** e não requer bibliotecas externas.

1. Clone o repositório:
   ```bash
   git clone [https://github.com/josejromulo3-cell/arquitetura2.git](https://github.com/josejromulo3-cell/arquitetura2.git)
   cd arquitetura2
