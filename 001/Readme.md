## @001 Calculadora & Utilizando uma calculora que gasta e recarrega bateria

![](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/001/cover.jpg)

[](toc)

- [Intro](#intro)
- [Guide](#guide)
- [Draft](#draft)
- [Shell](#shell)
[](toc)


O objetivo dessa atividade é implementar uma calculadora a bateria. Se há bateria, ela executa operações de soma, multiplicação e divisão. É possível também mostrar a quantidade de bateria e recarregar a calculadora. Ela avisa quando está sem bateria e se há tentativa de divisão por 0.


***
## Intro

- Mostrar bateria da calculadora.
- Recarregar a bateria.
- Realizar operações matemáticas de soma e divisão.
- Se o usuário tentar realizar operações e a bateria estiver vazia, deverá ser mostrada uma notificação sobre falta de bateria.
- Se for tentada divisão por zero, deve ser notificado o erro.

***
## Guide
![](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/001/diagrama.png)

***
## Draft
- [Solver.java](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/001/.cache/solver_draft.java)
- [solver.cpp](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/001/.cache/solver_draft.cpp)
- [solver.js](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/001/.cache/solver_draft.js)


***
## Shell

```bash
#__case iniciar mostrar e recarregar
# O comando "$init M" inicia uma calculadora passando por parâmetro a bateria máxima.
# O comando "$show" mostra o valor da última operação bem sucedida no display e o estado da bateria
# O comando "$charge V" recarrega a bateria de V
$init 5
$show
display = 0.00, battery = 0
$charge 3
$show
display = 0.00, battery = 3
$charge 1
$show
display = 0.00, battery = 4
$charge 2
$show
display = 0.00, battery = 5
$init 4
$charge 2
$show
display = 0.00, battery = 2
$charge 3
$show
display = 0.00, battery = 4
$end	
```	
```bash
#__case somando
$init 2
$charge 2
$sum 4 3
$show
display = 7.00, battery = 1
$sum 2 3
$show
display = 5.00, battery = 0
$sum -4 -1
fail: bateria insuficiente
$charge 1
$show
display = 5.00, battery = 1
$sum -4 -2
$show
display = -6.00, battery = 0
$end
```
```bash
#__case dividindo
$init 3
$charge 3
$div 6 3
$div 7 0
fail: divisao por zero
$show
display = 2.00, battery = 1
$div 7 2
$div 10 2
fail: bateria insuficiente
$show
display = 3.50, battery = 0
$end
```



