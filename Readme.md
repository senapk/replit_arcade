# Arcade

- [Questões de Fup](https://github.com/qxcodefup/arcade)
- [Questões de POO](https://github.com/qxcodepoo/arcade)
- [Questões de ED](https://github.com/qxcodeed/arcade)

Esse replit vem configurado automaticamente para POO.

Se quiser mudar para `fup` ou `ed`, basta mostrar os arquivos ocultos, abrir o arquivo [.discp.txt](.discp.txt) e trocar o texto para `fup` ou `ed`.

## Rodando via Botão Run
0. Faça o fork desse repositório para sua conta do replit.
1. Olhe no repositório qual problema quer fazer e anote o número do rótulo com 3 dígitos. Ex: Se você está tentando resolver a questão [**@003 Opala Bebedor**](https://github.com/qxcodefup/moodle/blob/master/base/003/Readme.md#003-l2---opala-bebedor) o rótulo é 003. 

2. Clique no run e informe o valor 003. Dá primeira vez que rodar, ele vai baixar a descrição do problema e os casos de teste e colocar na pasta 003.
3. Crie seu arquivo de solução **DENTRO** da pasta 003 iniciado com a palavra **solver**. Exemplo: Solver.java, solver.cpp, solver.js, solver.py.
  
4. Clique no Run, e informe 003, ou apenas aperte enter. Ele vai encontrar a pasta e seu código e rodar os testes.


## O motor de testes

Para ver mais configurações acesse https://github.com/senapk/tk

## Opções mais comuns do tk

Você pode abrir o arquivo [.tk.cfg](.tk.cfg) e alterar a primeira linha para as seguintes opções

- modo lado a lado (default)
- largura de 50 char no terminal
```
--width 50
```
- modo vertical
- largura de 40 char
```
--vertical --width 40
```
- sem visualização dos whitespaces: --raw
- mostrando todos os testes errados: --all
```
--raw -all
```