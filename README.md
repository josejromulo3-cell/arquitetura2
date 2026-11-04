**# Emulador da Microarquitetura Mic-1 (Modificada)**

Projeto desenvolvido para a disciplina de Arquitetura de Computadores II da Universidade Federal da Paraíba (UFPB). O objetivo central é o estudo e a implementação em software de uma microarquitetura baseada em uma versão modificada da Máquina Mic-1, capaz de receber e interpretar instruções da ISA IJVM. O projeto como um todo é dividido em apenas duas etapas.

**## Equipe Desenvolvedora**

* José Rômulo de Oliveira Silva
* Gustavo Gomes Souta da Silva
* Rafael Soares Gomes Correia Lima

**## O que fizemos na Etapa 1**
Nesta primeira parte, construímos e simulamos a Unidade Lógica e Aritmética (ULA) de 32 bits utilizando a linguagem Python.

Durante o desenvolvimento desta etapa, implementamos:

* **Simulação de Portas Lógicas:** Funções lógicas primitivas (NOT, AND, OR, XOR) para servirem de base ao circuito.


* **Estrutura de Baixo Nível:** Decodificador de instruções, unidade lógica e somador completo (com tratamento de carry-in e carry-out).


* **ULA de 1 bit e 32 bits:** Montagem da ULA de 1 bit controlada por uma palavra de 6 bits (F0, F1, ENA, ENB, INVA, INC) e sua expansão em cascata para operar com palavras de 32 bits.


* **Automação de Testes e Logs:** Criação do motor de execução que lê as palavras de controle diretamente de um arquivo de texto (`programa_etapa1.txt`), processa o chaveamento das entradas e gera automaticamente o arquivo de log (`saida_etapa1.txt`), detalhando o estado da ULA, as saídas e a linha de programa executada a cada ciclo.
